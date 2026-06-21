"""Live BranchRun executor for Plan 003."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

import httpx

from .models import digest_json, utc_now
from .promotion import branch_signal_status
from .qa_binding import run_reward_hacking_analysis

EVIDENCE_SUBDIR = Path("docs/plans/evidence/003/artifacts")


def _load_local_env(root: Path) -> None:
    env_path = root / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def _credential_presence() -> dict[str, str]:
    names = ("MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET", "HUD_API_KEY", "ANTHROPIC_API_KEY")
    return {name: "present" if os.environ.get(name) else "absent" for name in names}


def _artifact_root(root: Path, run_id: str) -> Path:
    path = root / EVIDENCE_SUBDIR / "branch-runs" / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _write_json(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root))


def _load_hud_task(root: Path) -> Any:
    env_path = root / "envs" / "mongodb-sales-aggregation-engine" / "env.py"
    spec = importlib.util.spec_from_file_location("mongodb_hud_env", env_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load HUD env from {env_path}")
    env_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env_module)
    return env_module.implement_sales_analyzer()


def _trace_readback(trace_id: str) -> dict[str, Any]:
    api_key = os.environ["HUD_API_KEY"]
    base = os.environ.get("HUD_API_URL", "https://api.beta.hud.ai").rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}"}
    trace = httpx.get(f"{base}/v2/trace/{trace_id}", headers=headers, timeout=30)
    events = httpx.get(f"{base}/v2/trace/{trace_id}/events", headers=headers, timeout=30)
    trace.raise_for_status()
    events.raise_for_status()
    return {"trace": trace.json(), "events": events.json()}


def _action_record(branch_id: str, job_id: str, trace_id: str, reward: Any) -> dict[str, Any]:
    trace_data = _trace_readback(trace_id) if trace_id else {"trace": {}, "events": {}}
    return {
        "schema_version": 1,
        "branch_id": branch_id,
        "job_id": job_id,
        "hud_trace_id": trace_id,
        "reward": reward,
        "trace_readback": trace_data,
    }


async def _run_one_branch(
    *,
    root: Path,
    forkpoint: dict[str, Any],
    task: Any,
    run_id: str,
    branch_index: int,
    artifact_root: Path,
) -> dict[str, Any]:
    import modal
    from hud.agents.claude.agent import ClaudeAgent, ClaudeConfig
    from hud.eval.runtime import ModalRuntime

    branch_id = f"{run_id}-branch-{branch_index:02d}"
    seed = 7300 + branch_index
    model = os.environ.get("FORKPROOF_BRANCH_MODEL") or os.environ.get("H2F2H_HACKER_MODEL") or "claude-haiku-4-5"
    max_steps = int(os.environ.get("FORKPROOF_BRANCH_MAX_STEPS", "8"))
    max_tokens = int(os.environ.get("FORKPROOF_BRANCH_MAX_TOKENS", "4096"))
    sampling_config = {
        "max_steps": max_steps,
        "max_tokens": max_tokens,
        "requested_seed": seed,
        "provider_seed_support": "not-supported-by-ClaudeConfig",
        "parallelism": "12-concurrent-branches",
    }
    started_at = utc_now()
    job_id = ""
    trace_id = ""
    reward: Any = None
    status = "success"
    error_class: str | None = None
    error_message: str | None = None
    try:
        runtime = ModalRuntime(
            image=modal.Image.from_id(forkpoint["snapshot_id"]),
            app_name="forkproof-plan-003",
            workdir="/app",
            command=("uv", "run", "hud", "serve", "env:env", "--host", "0.0.0.0", "--port", "8765"),
        )
        agent = ClaudeAgent(
            ClaudeConfig(
                model=model,
                max_steps=max_steps,
                max_tokens=max_tokens,
                use_computer_beta=False,
                system_prompt=f"Plan 003 BranchRun {branch_id}; requested_seed={seed}.",
            )
        )
        job = await task.run(agent, runtime=runtime)
        runs = getattr(job, "runs", None) or []
        if runs:
            trace_id = str(getattr(runs[0], "trace_id", "") or "")
        trace_id = trace_id or str(getattr(job, "trace_id", "") or "")
        job_id = str(getattr(job, "id", "") or "")
        reward = getattr(job, "reward", None)
        if not job_id or not trace_id:
            status = "agent-error"
            error_class = "missing_hud_provenance"
            error_message = "HUD job did not expose both job_id and trace_id"
    except Exception as exc:  # noqa: BLE001 - counted BranchRuns record provider failures.
        status = "agent-error"
        error_class = type(exc).__name__
        error_message = str(exc)

    action_record = _action_record(branch_id, job_id, trace_id, reward) if trace_id else {
        "schema_version": 1,
        "branch_id": branch_id,
        "job_id": job_id,
        "hud_trace_id": trace_id,
        "reward": reward,
        "error_class": error_class,
        "error_message": error_message,
    }
    action_record_digest = digest_json(action_record)
    action_path = _write_json(artifact_root / "actions" / f"{branch_id}.json", action_record)
    file_diff = {
        "schema_version": 1,
        "branch_id": branch_id,
        "status": "not-captured-from-HUD-trace",
        "observed_behavior": "HUD trace/action evidence was captured; filesystem diff capture remains a promotion gate.",
    }
    file_diff_path = _write_json(artifact_root / "file-diffs" / f"{branch_id}.json", file_diff)

    qa_result: dict[str, Any] | None = None
    if trace_id:
        qa_result = await asyncio.to_thread(
            run_reward_hacking_analysis,
            root,
            trace_id,
            branch_id=branch_id,
            action_record_digest=action_record_digest,
        )
        qa_path = _write_json(artifact_root / "qa" / f"{branch_id}.json", qa_result)
        qa_result_ref = qa_result.get("qa_result_id") if qa_result.get("status") == "pass" else "missing"
    else:
        qa_path = _write_json(
            artifact_root / "qa" / f"{branch_id}.json",
            {"status": "blocked", "branch_id": branch_id, "observed_behavior": "no HUD trace id available"},
        )
        qa_result_ref = "missing"

    branch = {
        "schema_version": 1,
        "run_id": run_id,
        "branch_id": branch_id,
        "parent_fork_point_id": forkpoint.get("fork_point_id"),
        "parent_node_id": forkpoint.get("node_id") or forkpoint.get("parent_node_id") or "accepted-forkpoint",
        "seed": seed,
        "model": model,
        "sampling_config": sampling_config,
        "gateway_request_ids": [f"hud-job:{job_id}"] if job_id else [f"branch-boundary:{branch_id}"],
        "model_response_refs": [f"hud-trace:{trace_id}"] if trace_id else [],
        "hud_trace_id": trace_id,
        "environment_version": "mongodb_sales_aggregation_engine_v1",
        "environment_image_digest": f"modal-image:{forkpoint.get('snapshot_id')}",
        "grader_digest": "trusted-pytest-task_assets/test_outputs.py",
        "grader_digest_source": "envs/mongodb-sales-aggregation-engine/env.py::GRADE_CMD",
        "reward": reward,
        "qa_result_ref": qa_result_ref,
        "lineage": {
            "fork_point_id": forkpoint.get("fork_point_id"),
            "snapshot_id": forkpoint.get("snapshot_id"),
            "branch_index": branch_index,
        },
        "snapshot_restore_ref": f"modal-image://{forkpoint.get('snapshot_id')}",
        "snapshot_id": forkpoint.get("snapshot_id"),
        "snapshot_mode": forkpoint.get("snapshot_mode"),
        "history_hash": digest_json({"fork_point_id": forkpoint.get("fork_point_id"), "branch_id": branch_id}),
        "action_record_ref": _relative(root, action_path),
        "action_record_digest": action_record_digest,
        "file_diff_ref": _relative(root, file_diff_path),
        "started_at": started_at,
        "completed_at": utc_now(),
        "status": status,
        "cleanup_result": "runtime-owned-cleanup",
        "execution_boundary_crossed": True,
    }
    if error_class:
        branch["error_class"] = error_class
        branch["error_message"] = error_message

    signal_status = "incomplete-classification"
    if qa_result and qa_result.get("status") == "pass":
        try:
            signal_status = branch_signal_status(branch, qa_result)
        except Exception as exc:  # noqa: BLE001 - summarize gate failures in the run artifact.
            signal_status = f"gate-error:{type(exc).__name__}:{exc}"
    branch["promotion_signal_status"] = signal_status
    branch_path = _write_json(artifact_root / "branches" / f"{branch_id}.json", branch)
    return {
        "branch": branch,
        "qa": qa_result,
        "branch_ref": _relative(root, branch_path),
        "qa_ref": _relative(root, qa_path),
        "action_record_ref": _relative(root, action_path),
        "file_diff_ref": _relative(root, file_diff_path),
    }


async def run_live_branch_batch(
    root: Path,
    forkpoint: dict[str, Any],
    *,
    count: int = 12,
    concurrency: int = 12,
) -> dict[str, Any]:
    _load_local_env(root)
    presence = _credential_presence()
    if any(value != "present" for value in presence.values()):
        return {
            "status": "blocked",
            "credential_presence": presence,
            "observed_behavior": "12-branch batch skipped because required local credentials were absent",
        }
    if os.environ.get("FORKPROOF_ALLOW_EXTERNAL_QA") != "1":
        return {
            "status": "blocked",
            "credential_presence": presence,
            "observed_behavior": "12-branch batch skipped because external QA export is not approved",
        }

    run_id = "run-" + utc_now().replace("-", "").replace(":", "").removesuffix("Z")
    artifact_root = _artifact_root(root, run_id)
    task = _load_hud_task(root)
    sem = asyncio.Semaphore(concurrency)

    async def guarded(index: int) -> dict[str, Any]:
        async with sem:
            return await _run_one_branch(
                root=root,
                forkpoint=forkpoint,
                task=task,
                run_id=run_id,
                branch_index=index,
                artifact_root=artifact_root,
            )

    started_at = utc_now()
    results = await asyncio.gather(*(guarded(index) for index in range(count)))
    branches = [item["branch"] for item in results]
    qa_results = [item["qa"] for item in results if item["qa"]]
    candidates = [branch for branch in branches if branch.get("promotion_signal_status") == "candidate"]
    summary = {
        "schema_version": 1,
        "run_id": run_id,
        "status": "pass" if len(branches) == count else "blocked",
        "started_at": started_at,
        "completed_at": utc_now(),
        "fork_point_id": forkpoint.get("fork_point_id"),
        "snapshot_id": forkpoint.get("snapshot_id"),
        "requested_branch_count": count,
        "executed_branch_count": len(branches),
        "concurrency": concurrency,
        "credential_presence": presence,
        "branch_refs": [item["branch_ref"] for item in results],
        "qa_refs": [item["qa_ref"] for item in results],
        "unique_branch_ids": len({branch["branch_id"] for branch in branches}),
        "unique_seeds": len({branch["seed"] for branch in branches}),
        "hud_trace_count": sum(1 for branch in branches if branch.get("hud_trace_id")),
        "reward_success_count": sum(1 for branch in branches if branch.get("reward") in (1, 1.0, True)),
        "qa_pass_count": sum(1 for qa in qa_results if qa.get("status") == "pass"),
        "reward_hacking_count": sum(1 for qa in qa_results if qa.get("is_reward_hacking") is True),
        "candidate_branch_ids": [branch["branch_id"] for branch in candidates],
        "promotion_signal_counts": {
            status: sum(1 for branch in branches if branch.get("promotion_signal_status") == status)
            for status in sorted({str(branch.get("promotion_signal_status")) for branch in branches})
        },
        "observed_behavior": (
            "Executed 12 live BranchRuns concurrently from the same accepted ForkPoint, then ran user-approved "
            "repo-bound Reward Hacking QA classification for every branch with a HUD trace."
        ),
    }
    summary_path = _write_json(artifact_root / "branch-run-batch.json", summary)
    return {**summary, "artifact_ref": _relative(root, summary_path)}
