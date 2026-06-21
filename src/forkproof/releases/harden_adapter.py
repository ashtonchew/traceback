"""Thin harden-v0 source adapter."""

from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from forkproof.witnesses.local_env import credential_presence, load_local_env

from .models import ReleaseError, digest_json, utc_now

DEFAULT_ANTHROPIC_HARDEN_MODEL = "anthropic/claude-haiku-4-5"


def inspect_harden_config(config_path: Path) -> dict[str, Any]:
    """Read harden-v0 config/result schema from source without importing it."""

    if not config_path.exists():
        raise ReleaseError("harden_unavailable", f"missing harden-v0 config: {config_path}")
    harden_root = config_path.parents[1]
    tree = ast.parse(config_path.read_text(encoding="utf-8"))
    fields: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "HardenConfig":
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields[item.target.id] = ast.unparse(item.annotation)
            break
    if not fields:
        raise ReleaseError("harden_schema_unavailable", "HardenConfig class not found")
    required = {"max_iterations", "hacker_retries", "replay_retries", "replay_enabled", "legitimate_threshold"}
    missing = sorted(required - set(fields))
    if missing:
        raise ReleaseError("harden_schema_unavailable", f"HardenConfig missing {missing}")
    return {
        "schema_version": 1,
        "config_path": str(config_path),
        "harden_config_fields": fields,
        "iteration_bounds": {
            "max_iterations": _literal_default(tree, "HardenConfig", "max_iterations"),
            "hacker_retries": _literal_default(tree, "HardenConfig", "hacker_retries"),
            "replay_retries": _literal_default(tree, "HardenConfig", "replay_retries"),
            "replay_enabled": _literal_default(tree, "HardenConfig", "replay_enabled"),
            "legitimate_threshold": _literal_default(tree, "HardenConfig", "legitimate_threshold"),
        },
        "result_json_schema": inspect_harden_result_schema(harden_root),
    }


def prepare_harden_task_source(
    *,
    task_source: Path,
    tasks_root: Path,
    task_id: str,
) -> Path:
    """Copy an explicit task source into harden-v0's tasks-dir/task-id layout."""

    if not task_source.is_dir():
        raise ReleaseError("harden_unavailable", f"harden task source is not a directory: {task_source}")
    required = ["instruction.md", "tests", "environment"]
    missing = [name for name in required if not (task_source / name).exists()]
    if missing:
        raise ReleaseError("harden_unavailable", f"harden task source missing {missing}")
    target = tasks_root / task_id
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task_source, target)
    return target


def run_harden_v0(
    *,
    repo_root: Path,
    harden_root: Path,
    task_id: str,
    task_source: Path,
    output_root: Path,
    max_iterations: int,
    timeout_seconds: int,
    hacker_model: str | None = None,
    fixer_model: str | None = None,
    solver_model: str | None = None,
) -> dict[str, Any]:
    """Run the upstream harden-v0 CLI through this repo's optional dependency boundary."""

    load_local_env(repo_root)
    selected_models = select_harden_models(
        hacker_model=hacker_model,
        fixer_model=fixer_model,
        solver_model=solver_model,
    )
    require_selected_model_credentials(selected_models)
    tasks_root = output_root / "tasks"
    task_copy = prepare_harden_task_source(task_source=task_source, tasks_root=tasks_root, task_id=task_id)
    harden_output = output_root / "harden-output"
    command = [
        "uv",
        "run",
        "--extra",
        "harden-v0",
        "python",
        "-c",
        (
            "import sys; "
            f"sys.path.insert(0, {str(harden_root)!r}); "
            "from harden.__main__ import main; "
            "main()"
        ),
        "--task-id",
        task_id,
        "--tasks-dir",
        str(tasks_root),
        "--output-dir",
        str(harden_output),
        "--max-iterations",
        str(max_iterations),
        "--replay-enabled",
        "--no-legitimate-marker",
        "--summary-model",
        "",
        "--log-level",
        "INFO",
    ]
    command.extend(["--hacker-model", selected_models["hacker_model"]])
    command.extend(["--fixer-model", selected_models["fixer_model"]])
    command.extend(["--solver-model", selected_models["solver_model"]])
    started_at = utc_now()
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        completed = subprocess.CompletedProcess(
            command,
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
        )
        timed_out = True

    result_path = harden_output / task_id / "result.json"
    result_json = None
    if result_path.exists():
        result_json = json.loads(result_path.read_text(encoding="utf-8"))
    fixer_artifact_layouts = inspect_fixer_artifact_layouts(harden_output, task_id)
    record = {
        "schema_version": 1,
        "adapter": "forkproof.releases.harden_adapter.run_harden_v0",
        "started_at": started_at,
        "completed_at": utc_now(),
        "task_id": task_id,
        "task_source": str(task_source),
        "task_copy": str(task_copy),
        "harden_root": str(harden_root),
        "output_root": str(output_root),
        "command_argv": command,
        "selected_models": selected_models,
        "credential_presence": credential_presence(
            ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY", "MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET")
        ),
        "returncode": completed.returncode,
        "timed_out": timed_out,
        "stdout_digest": digest_json({"stdout": completed.stdout}),
        "stderr_digest": digest_json({"stderr": completed.stderr}),
        "result_path": str(result_path),
        "result_json": result_json,
        "fixer_artifact_layouts": fixer_artifact_layouts,
    }
    blocker = harden_artifact_layout_blocker(result_json, fixer_artifact_layouts)
    if blocker is not None:
        record["harden_blocker"] = blocker
    record["content_digest"] = digest_json(record)
    return record


def inspect_fixer_artifact_layouts(harden_output: Path, task_id: str) -> list[dict[str, Any]]:
    """Inspect harden-v0 fixer artifact repos without treating them as release proof."""

    jobs_root = harden_output / task_id / "jobs"
    if not jobs_root.is_dir():
        return []
    layouts: list[dict[str, Any]] = []
    for job_dir in sorted(p for p in jobs_root.glob("fixer_*") if p.is_dir()):
        for trial_dir in sorted(p for p in job_dir.iterdir() if p.is_dir()):
            expected = trial_dir / "artifacts"
            nested = expected / "logs" / "artifacts"
            expected_repo = _git_repo_status(expected)
            nested_repo = _git_repo_status(nested)
            layout_status = "missing"
            changed_files: list[str] = []
            patch_digest = None
            if expected_repo["is_git_repo"]:
                layout_status = "expected"
                changed_files = _git_changed_files(expected)
                patch_digest = _git_patch_digest(expected)
            elif nested_repo["is_git_repo"]:
                layout_status = "nested_logs_artifacts"
                changed_files = _git_changed_files(nested)
                patch_digest = _git_patch_digest(nested)
            layouts.append(
                {
                    "schema_version": 1,
                    "job_dir": str(job_dir),
                    "trial_dir": str(trial_dir),
                    "expected_artifacts_path": str(expected),
                    "expected_artifacts_git": expected_repo,
                    "nested_logs_artifacts_path": str(nested),
                    "nested_logs_artifacts_git": nested_repo,
                    "layout_status": layout_status,
                    "changed_files": changed_files,
                    "patch_digest": patch_digest,
                }
            )
    return layouts


def harden_artifact_layout_blocker(
    result_json: dict[str, Any] | None,
    layouts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Classify the Harbor/harden-v0 artifact-layout drift seen after fixer failure."""

    if not result_json or not layouts:
        return None
    iterations = result_json.get("iterations")
    if not isinstance(iterations, list):
        return None
    has_fix_failed = any(isinstance(item, dict) and item.get("outcome") == "fix_failed" for item in iterations)
    if not has_fix_failed:
        return None
    drifted = [
        item for item in layouts
        if item.get("layout_status") == "nested_logs_artifacts" and item.get("changed_files")
    ]
    if not drifted:
        return None
    return {
        "code": "harden_fixer_artifact_layout_drift",
        "status": "blocked",
        "reason": (
            "harden-v0 expected the fixer git repo at trial_dir/artifacts, but Harbor "
            "exported the committed /logs/artifacts repo at trial_dir/artifacts/logs/artifacts; "
            "the observed patch is diagnostic only until harden-v0 applies and validates it."
        ),
        "affected_trial_dirs": [item["trial_dir"] for item in drifted],
        "changed_files": sorted({path for item in drifted for path in item.get("changed_files", [])}),
    }


def select_harden_models(
    *,
    hacker_model: str | None,
    fixer_model: str | None,
    solver_model: str | None,
) -> dict[str, str]:
    """Select harden-v0 models without falling back to Gemini/Google."""

    import os

    fallback = (
        os.environ.get("H2F2H_HARDEN_MODEL")
        or os.environ.get("H2F2H_HACKER_MODEL")
        or os.environ.get("FORKPROOF_BRANCH_MODEL")
        or DEFAULT_ANTHROPIC_HARDEN_MODEL
    )
    return {
        "hacker_model": hacker_model or os.environ.get("H2F2H_HACKER_MODEL") or fallback,
        "fixer_model": fixer_model or os.environ.get("H2F2H_FIXER_MODEL") or fallback,
        "solver_model": solver_model or os.environ.get("H2F2H_SOLVER_MODEL") or fallback,
    }


def require_selected_model_credentials(models: dict[str, str]) -> None:
    """Fail before harden-v0 if the selected provider credentials are absent."""

    import os

    for role, model in models.items():
        lowered = model.lower()
        if ("gemini" in lowered or lowered.startswith("google/")) and not (
            os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        ):
            raise ReleaseError("harden_credentials_missing", f"{role} selected Gemini/Google model without key")
        if ("anthropic" in lowered or "claude" in lowered) and not os.environ.get("ANTHROPIC_API_KEY"):
            raise ReleaseError("harden_credentials_missing", f"{role} selected Anthropic model without key")


def inspect_harden_result_schema(harden_root: Path) -> dict[str, Any]:
    """Read harden-v0 result.json shape from loop.py and CLAUDE.md."""

    loop_path = harden_root / "harden" / "loop.py"
    docs_path = harden_root / "CLAUDE.md"
    if not loop_path.exists():
        raise ReleaseError("harden_schema_unavailable", f"missing harden-v0 loop: {loop_path}")
    if not docs_path.exists():
        raise ReleaseError("harden_schema_unavailable", f"missing harden-v0 docs: {docs_path}")
    loop_tree = ast.parse(loop_path.read_text(encoding="utf-8"))
    implementation_fields = _assigned_dict_keys(loop_tree, "result")
    status_values = sorted(_subscript_string_assignments(loop_tree, "result", "status") | {"unknown"})
    docs_text = docs_path.read_text(encoding="utf-8")
    documented_fields = sorted(set(re.findall(r'^\s*"([a-zA-Z_][a-zA-Z0-9_]*)":', docs_text, flags=re.MULTILINE)))
    output_paths = sorted(set(re.findall(r"<output_dir>[^`\n]*", docs_text)))
    required = {"task_id", "status", "iterations", "oracle", "kernelbench_mode"}
    missing = sorted(required - set(implementation_fields))
    if missing:
        raise ReleaseError("harden_schema_unavailable", f"harden result skeleton missing {missing}")
    return {
        "schema_version": 1,
        "loop_path": str(loop_path),
        "docs_path": str(docs_path),
        "implementation_fields": implementation_fields,
        "documented_fields": documented_fields,
        "status_values": status_values,
        "output_paths": output_paths,
    }


def _git_repo_status(path: Path) -> dict[str, Any]:
    if not (path / ".git").exists():
        return {"is_git_repo": False, "has_initial_ref": False}
    return {
        "is_git_repo": True,
        "has_initial_ref": _git_has_ref(path, "initial"),
    }


def _git_has_ref(repo: Path, ref: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", ref],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _git_changed_files(repo: Path) -> list[str]:
    if not _git_has_ref(repo, "initial"):
        return []
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--name-only", "initial", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return sorted(line for line in result.stdout.splitlines() if line)


def _git_patch_digest(repo: Path) -> str | None:
    if not _git_has_ref(repo, "initial"):
        return None
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--binary", "initial", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        return None
    return digest_json({"patch": result.stdout})


def _assigned_dict_keys(tree: ast.AST, name: str) -> list[str]:
    for node in ast.walk(tree):
        value = None
        matches = False
        if isinstance(node, ast.Assign):
            value = node.value
            matches = any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
        elif isinstance(node, ast.AnnAssign):
            value = node.value
            matches = isinstance(node.target, ast.Name) and node.target.id == name
        if matches and isinstance(value, ast.Dict):
            keys = [key.value for key in value.keys if isinstance(key, ast.Constant) and isinstance(key.value, str)]
            return sorted(keys)
    return []


def _subscript_string_assignments(tree: ast.AST, name: str, key: str) -> set[str]:
    values: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == name
                and isinstance(target.slice, ast.Constant)
                and target.slice.value == key
            ):
                values.add(node.value.value)
    return values


def _literal_default(tree: ast.AST, class_name: str, field_name: str) -> Any:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if (
                    isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                    and item.target.id == field_name
                    and item.value is not None
                ):
                    return ast.literal_eval(item.value)
    return None
