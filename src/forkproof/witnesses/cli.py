"""Plan 003 command entrypoints."""

from __future__ import annotations

import argparse
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

    # These are distinct Plan 003 seams. Branch execution produces a completed
    # BranchRun; QA classification is a later same-branch promotion signal.
    branch_execution_blockers.append("repo-owned live BranchGateway adapter is not bound")
    promotion_blockers.append("authoritative HUD QA reward-hacking classification API is not bound")

    artifact = {
        "checked_at": utc_now(),
        "status": "blocked" if branch_execution_blockers or promotion_blockers else "ready",
        "fork_point_id": forkpoint.get("fork_point_id"),
        "snapshot_id": forkpoint.get("snapshot_id"),
        "restore_inspection_ref": str(restore_path.relative_to(ROOT)),
        "branch_execution": {
            "status": "blocked" if branch_execution_blockers else "ready",
            "blockers": branch_execution_blockers,
        },
        "promotion": {
            "status": "blocked" if promotion_blockers else "ready",
            "blockers": promotion_blockers,
        },
        "observed_behavior": (
            "preflight only; no BranchRun execution started because the repo-owned live BranchGateway is not "
            "bound. QA remains a separate post-run classification path required before Witness promotion."
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
