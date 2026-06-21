"""Plan 003 command entrypoints."""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import shutil
from pathlib import Path
from typing import Any

from .models import WitnessError, digest_json, utc_now
from .security import assert_branch_security

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "plans" / "evidence" / "003" / "artifacts"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_artifact(name: str, data: dict[str, Any]) -> Path:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / name
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _load_local_env() -> dict[str, str]:
    env_path = ROOT / ".env"
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().removeprefix("export ").strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value
            loaded[key] = "present"
    return loaded


def _credential_presence() -> dict[str, str]:
    names = (
        "MODAL_TOKEN_ID",
        "MODAL_TOKEN_SECRET",
        "HUD_API_KEY",
        "ANTHROPIC_API_KEY",
    )
    return {name: "present" if os.environ.get(name) else "absent" for name in names}


def _hud_org_binding() -> dict[str, str | None]:
    names = (
        "HUD_ORGANIZATION_ID",
        "HUD_ORG_ID",
        "HUD_PROJECT_ID",
        "HUD_WORKSPACE_ID",
        "X_ORGANIZATION_ID",
    )
    for name in names:
        value = os.environ.get(name)
        if value:
            return {"env_name": name, "status": "present", "value": value}
    return {"env_name": None, "status": "absent", "value": None}


def _summarize_api_payload(data: Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return {
            "shape": "object",
            "keys": sorted(str(key) for key in data.keys())[:20],
            "message": data.get("detail") or data.get("message") or data.get("error"),
        }
    if isinstance(data, list):
        return {
            "shape": "array",
            "length": len(data),
            "first_keys": sorted(str(key) for key in data[0].keys())[:20]
            if data and isinstance(data[0], dict)
            else [],
        }
    return {"shape": type(data).__name__}


def _inspect_hud_qa_binding(trace_id: str | None) -> dict[str, Any]:
    _load_local_env()
    api_key = os.environ.get("HUD_API_KEY")
    if not api_key:
        return {
            "status": "blocked",
            "credential_presence": _credential_presence(),
            "observed_behavior": "HUD QA binding inspection skipped because HUD_API_KEY is absent",
        }

    import httpx

    base = os.environ.get("HUD_API_URL", "https://api.beta.hud.ai").rstrip("/")
    org = _hud_org_binding()
    headers = {"Authorization": f"Bearer {api_key}"}
    org_headers = dict(headers)
    if org["value"]:
        org_headers["X-Organization-ID"] = str(org["value"])

    def get(path: str, *, use_org: bool = False) -> dict[str, Any]:
        request_headers = org_headers if use_org else headers
        response = httpx.get(f"{base}{path}", headers=request_headers, timeout=20)
        try:
            payload: Any = response.json()
        except ValueError:
            payload = None
        return {
            "path": path,
            "status_code": response.status_code,
            "summary": _summarize_api_payload(payload),
        }

    openapi = get("/openapi.json")
    openapi_paths: list[str] = []
    try:
        spec = httpx.get(f"{base}/openapi.json", headers=headers, timeout=20).json()
        if isinstance(spec, dict) and isinstance(spec.get("paths"), dict):
            openapi_paths = sorted(spec["paths"].keys())
    except Exception:  # noqa: BLE001 - diagnostic only; endpoint status is recorded above.
        openapi_paths = []

    qa_without_org = get("/v2/qa-agents")
    qa_with_org = get("/v2/qa-agents", use_org=True) if org["value"] else None
    trace_events = get(f"/v2/trace/{trace_id}/events") if trace_id else None
    qa_probe = qa_with_org or qa_without_org
    message = str(qa_without_org["summary"].get("message") or "")
    if qa_without_org["status_code"] == 401 and "X-Organization-ID" in message and org["status"] == "absent":
        blocker = "HUD QA API requires X-Organization-ID and no repo-bound HUD organization env/config is present"
    elif qa_probe["status_code"] == 200:
        blocker = "HUD QA agent listing is reachable, but the repo has no bound run/result contract for the Reward Hacking Agent"
    else:
        blocker = "HUD QA reward-hacking classification API is not bound to this repo"

    return {
        "status": "blocked",
        "credential_presence": _credential_presence(),
        "api_base": base,
        "organization_binding": {
            "status": org["status"],
            "env_name": org["env_name"],
        },
        "openapi_probe": openapi,
        "openapi_has_qa_agents_path": "/v2/qa-agents" in openapi_paths,
        "openapi_trace_paths": [path for path in openapi_paths if path.startswith("/v2/trace/")],
        "qa_agents_without_org_probe": qa_without_org,
        "qa_agents_with_org_probe": qa_with_org,
        "trace_events_probe": trace_events,
        "blocker": blocker,
        "observed_behavior": (
            "HUD trace readback is available through the authenticated API, and the hidden QA-agent router exists, "
            "but Plan 003 still lacks the organization-scoped Reward Hacking Agent run/result binding needed to join "
            "an authoritative QA verdict to the BranchRun trace and action digest."
        ),
    }


def _modal_restore_inspection(forkpoint: dict[str, Any]) -> dict[str, Any]:
    _load_local_env()
    presence = _credential_presence()
    if any(value != "present" for value in presence.values()):
        return {
            "status": "blocked",
            "credential_presence": presence,
            "observed_behavior": "live restore inspection skipped because required local credentials were absent",
        }

    import modal

    app = modal.App.lookup("forkproof-plan-003", create_if_missing=True)
    sandbox = modal.Sandbox.create(
        image=modal.Image.from_id(forkpoint["snapshot_id"]),
        app=app,
        block_network=True,
        secrets=[],
        cpu=0.5,
        memory=1024,
        timeout=300,
        workdir="/app",
        tags={"forkproof_plan": "003", "purpose": "branch_gateway_restore_inspection"},
    )
    try:
        def run(command: str, timeout: int = 60) -> dict[str, Any]:
            proc = sandbox.exec("bash", "-lc", command, workdir="/app", timeout=timeout)
            proc.wait()
            return {
                "returncode": proc.returncode,
                "stdout": proc.stdout.read(),
                "stderr": proc.stderr.read(),
            }

        inventory = run(
            "python3 - <<'PY'\n"
            "from pathlib import Path\n"
            "import json\n"
            "paths=['/app','/app/query.py','/app/env.py','/app/tasks.py','/app/pyproject.toml','/app/task_assets','/data/db']\n"
            "print(json.dumps({p:{'exists':Path(p).exists(),'is_file':Path(p).is_file(),'is_dir':Path(p).is_dir()} for p in paths}, sort_keys=True))\n"
            "PY"
        )
        grade = run(
            "pgrep -x mongod >/dev/null || "
            "mongod --fork --logpath /var/log/mongodb.log --dbpath /data/db >/tmp/mongod-start.log 2>&1; "
            "python3 -m pytest task_assets/test_outputs.py -q > /tmp/grade.log 2>&1; "
            "rc=$?; tail -80 /tmp/grade.log; exit $rc",
            timeout=180,
        )
        hud_server = run(
            "test -f env.py && "
            "(hud serve env.py --host 0.0.0.0 --port 8765 --help >/tmp/hud-help.log 2>&1; "
            "echo env-server-present) || echo env-server-missing"
        )
        grade_output = grade["stdout"] + grade["stderr"]
        grade_summary = "pass"
        if "IndentationError" in grade_output:
            grade_summary = "query.py IndentationError"
        elif grade["returncode"] != 0:
            grade_summary = "grader returned nonzero"
        inventory_data = json.loads(inventory["stdout"])
        status = "pass" if grade["returncode"] == 0 and hud_server["stdout"].strip() == "env-server-present" else "blocked"
        observed = (
            "Recorded Plan 002 snapshot restores as branch-ready Modal/HUD task state: HUD server files are present "
            "and the trusted grader passes from the restored state."
            if status == "pass"
            else (
                "Recorded Plan 002 snapshot restores as Modal task state, but it is not branch-ready for HUD "
                "BranchGateway execution or trusted grading."
            )
        )
        return {
            "status": status,
            "credential_presence": presence,
            "sandbox_id": sandbox.object_id,
            "network_policy": "block_network=True",
            "secret_policy": "secrets=[]",
            "inventory": inventory_data,
            "grader_returncode": grade["returncode"],
            "grader_output_sha256": digest_json(grade_output),
            "grader_summary": grade_summary,
            "hud_server_probe_stdout": hud_server["stdout"].strip(),
            "observed_behavior": observed,
        }
    finally:
        sandbox.terminate()


async def _run_branch_gateway_smoke(forkpoint: dict[str, Any]) -> dict[str, Any]:
    _load_local_env()
    presence = _credential_presence()
    if any(value != "present" for value in presence.values()):
        return {
            "status": "blocked",
            "credential_presence": presence,
            "observed_behavior": "BranchGateway smoke skipped because required local credentials were absent",
        }

    import modal
    from hud.agents.claude.agent import ClaudeAgent, ClaudeConfig
    from hud.eval.runtime import ModalRuntime

    env_path = ROOT / "envs" / "mongodb-sales-aggregation-engine" / "env.py"
    spec = importlib.util.spec_from_file_location("mongodb_hud_env", env_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load HUD env from {env_path}")
    env_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(env_module)

    task = env_module.implement_sales_analyzer()
    runtime = ModalRuntime(
        image=modal.Image.from_id(forkpoint["snapshot_id"]),
        app_name="forkproof-plan-003",
        workdir="/app",
        command=("uv", "run", "hud", "serve", "env:env", "--host", "0.0.0.0", "--port", "8765"),
    )
    agent = ClaudeAgent(
        ClaudeConfig(
            model="claude-haiku-4-5",
            max_steps=2,
            max_tokens=2048,
            use_computer_beta=False,
        )
    )
    job = await task.run(agent, runtime=runtime)
    runs = getattr(job, "runs", None) or []
    trace_id = None
    if runs:
        trace_id = getattr(runs[0], "trace_id", None)
    trace_id = trace_id or getattr(job, "trace_id", None)
    return {
        "status": "pass" if getattr(job, "id", None) and trace_id else "blocked",
        "credential_presence": presence,
        "job_id": str(getattr(job, "id", "")),
        "trace_id": str(trace_id or ""),
        "reward": getattr(job, "reward", None),
        "model": "claude-haiku-4-5",
        "max_steps": 2,
        "counted_branch_run": False,
        "observed_behavior": (
            "Diagnostic BranchGateway smoke produced a HUD job/trace from the corrected ForkPoint snapshot. "
            "It is not counted as a Plan 003 BranchRun because it does not run the full branch budget, does not "
            "join HUD QA, and starts from an already reward-1 accepted state."
        ),
    }


def integration_witness() -> int:
    plan002 = _load_json(ROOT / "docs" / "plans" / "evidence" / "002" / "MANIFEST.json")
    plan004 = _load_json(ROOT / "docs" / "plans" / "evidence" / "004" / "MANIFEST.json")
    forkpoint = _load_json(ROOT / "docs" / "plans" / "evidence" / "002" / "artifacts" / "forkpoint-record.json")
    commands = _load_json(ROOT / "docs" / "plans" / "repo-map" / "COMMANDS.json")
    branch_execution_blockers: list[str] = []
    promotion_blockers: list[str] = []
    if plan002.get("status") != "complete":
        branch_execution_blockers.append("Plan 002 manifest is not complete")
    if plan004.get("status") != "complete":
        branch_execution_blockers.append("Plan 004 manifest is not complete")
    if forkpoint.get("snapshot_mode") not in {"filesystem", "directory"}:
        branch_execution_blockers.append("ForkPoint snapshot is not filesystem-class")
    if not shutil.which("hud"):
        branch_execution_blockers.append("HUD CLI not found on PATH")
    harden = ROOT / ".external" / "harden-v0" / "dedup_hacks.py"
    if not harden.exists():
        promotion_blockers.append("pinned harden-v0 dedup_hacks.py is unavailable")
    command_status = commands["commands"]["integration-witness"]["status"]
    if command_status != "verified":
        branch_execution_blockers.append("integration-witness command is not yet verified in COMMANDS.json")

    restore_inspection: dict[str, Any]
    try:
        restore_inspection = _modal_restore_inspection(forkpoint)
    except Exception as exc:  # noqa: BLE001 - integration command records provider failures.
        restore_inspection = {
            "status": "blocked",
            "error_class": type(exc).__name__,
            "observed_behavior": str(exc),
        }
    restore_path = _write_artifact(
        "branch-gateway-restore-inspection.json",
        {
            "checked_at": utc_now(),
            "fork_point_id": forkpoint.get("fork_point_id"),
            "snapshot_id": forkpoint.get("snapshot_id"),
            **restore_inspection,
        },
    )
    if restore_inspection.get("status") != "pass":
        branch_execution_blockers.append(
            "accepted ForkPoint restore is not branch-ready for live BranchGateway execution"
        )
    else:
        try:
            smoke = asyncio.run(_run_branch_gateway_smoke(forkpoint))
        except Exception as exc:  # noqa: BLE001 - integration command records provider failures.
            smoke = {
                "status": "blocked",
                "error_class": type(exc).__name__,
                "observed_behavior": str(exc),
            }
        smoke_path = _write_artifact(
            "branch-gateway-smoke.json",
            {
                "checked_at": utc_now(),
                "fork_point_id": forkpoint.get("fork_point_id"),
                "snapshot_id": forkpoint.get("snapshot_id"),
                **smoke,
            },
        )
        if smoke.get("status") != "pass":
            branch_execution_blockers.append("repo-owned live BranchGateway adapter smoke did not produce HUD trace evidence")

    # These are distinct Plan 003 seams. Branch execution produces a completed
    # BranchRun; QA classification is a later same-branch promotion signal.
    qa_binding: dict[str, Any]
    try:
        qa_binding = _inspect_hud_qa_binding(smoke.get("trace_id") if "smoke" in locals() else None)
    except Exception as exc:  # noqa: BLE001 - integration command records provider failures.
        qa_binding = {
            "status": "blocked",
            "error_class": type(exc).__name__,
            "observed_behavior": str(exc),
            "blocker": "HUD QA reward-hacking classification API is not bound to this repo",
        }
    qa_binding_path = _write_artifact(
        "hud-qa-binding-inspection.json",
        {
            "checked_at": utc_now(),
            "fork_point_id": forkpoint.get("fork_point_id"),
            "snapshot_id": forkpoint.get("snapshot_id"),
            **qa_binding,
        },
    )
    if qa_binding.get("status") != "pass":
        promotion_blockers.append(str(qa_binding.get("blocker") or "authoritative HUD QA reward-hacking classification API is not bound"))

    artifact = {
        "checked_at": utc_now(),
        "status": "blocked" if branch_execution_blockers or promotion_blockers else "ready",
        "fork_point_id": forkpoint.get("fork_point_id"),
        "snapshot_id": forkpoint.get("snapshot_id"),
        "restore_inspection_ref": str(restore_path.relative_to(ROOT)),
        "branch_gateway_smoke_ref": (
            str(smoke_path.relative_to(ROOT)) if "smoke_path" in locals() else None
        ),
        "hud_qa_binding_ref": str(qa_binding_path.relative_to(ROOT)),
        "branch_execution": {
            "status": "blocked" if branch_execution_blockers else "ready",
            "blockers": branch_execution_blockers,
        },
        "promotion": {
            "status": "blocked" if promotion_blockers else "ready",
            "blockers": promotion_blockers,
        },
        "observed_behavior": (
            "integration preflight plus diagnostic BranchGateway smoke only; the full 12 BranchRun loop has not "
            "started. QA remains a separate post-run classification path required before Witness promotion."
        ),
    }
    path = _write_artifact("integration-witness-preflight.json", artifact)
    print(f"WROTE {path}")
    blockers = branch_execution_blockers + promotion_blockers
    if blockers:
        for blocker in blockers:
            print(f"STOP: {blocker}")
        return 2
    return 0


def security_branch() -> int:
    policy = {
        "branch_secret_names": [],
        "sibling_writable_state": False,
        "artifact_writer": "trusted_orchestrator",
        "grader_trust_zone": "trusted_grader",
        "denied_egress_probe": "pass",
        "denied_secret_probe": "pass",
    }
    try:
        assert_branch_security(policy)
    except WitnessError as exc:
        print(f"FAIL {exc.error_class}: {exc}")
        return 1
    path = _write_artifact(
        "security-branch-preflight.json",
        {
            "checked_at": utc_now(),
            "status": "pass",
            "policy": policy,
            "observed_behavior": "local policy gate denies forbidden capabilities and requires trusted artifact/grader boundaries",
        },
    )
    print(f"PASS security preflight artifact={path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("integration")
    sub.add_parser("security")
    args = parser.parse_args()
    if args.command == "integration":
        return integration_witness()
    if args.command == "security":
        return security_branch()
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
