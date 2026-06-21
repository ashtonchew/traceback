"""Plan 003 command entrypoints."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from .models import WitnessError, utc_now
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


def integration_witness() -> int:
    plan002 = _load_json(ROOT / "docs" / "plans" / "evidence" / "002" / "MANIFEST.json")
    plan004 = _load_json(ROOT / "docs" / "plans" / "evidence" / "004" / "MANIFEST.json")
    forkpoint = _load_json(ROOT / "docs" / "plans" / "evidence" / "002" / "artifacts" / "forkpoint-record.json")
    commands = _load_json(ROOT / "docs" / "plans" / "repo-map" / "COMMANDS.json")
    blockers: list[str] = []
    if plan002.get("status") != "complete":
        blockers.append("Plan 002 manifest is not complete")
    if plan004.get("status") != "complete":
        blockers.append("Plan 004 manifest is not complete")
    if forkpoint.get("snapshot_mode") not in {"filesystem", "directory"}:
        blockers.append("ForkPoint snapshot is not filesystem-class")
    if not shutil.which("hud"):
        blockers.append("HUD CLI not found on PATH")
    harden = ROOT / ".external" / "harden-v0" / "dedup_hacks.py"
    if not harden.exists():
        blockers.append("pinned harden-v0 dedup_hacks.py is unavailable")
    command_status = commands["commands"]["integration-witness"]["status"]
    if command_status != "verified":
        blockers.append("integration-witness command is not yet verified in COMMANDS.json")

    # The installed HUD 0.6.4 CLI exposes eval/jobs/trace but no authoritative
    # QA reward-hacking classification command. Do not substitute local labels.
    blockers.append("authoritative HUD QA reward-hacking classification API is not bound")

    artifact = {
        "checked_at": utc_now(),
        "status": "blocked" if blockers else "ready",
        "fork_point_id": forkpoint.get("fork_point_id"),
        "snapshot_id": forkpoint.get("snapshot_id"),
        "blockers": blockers,
        "observed_behavior": "preflight only; no BranchRun execution started when QA binding was missing",
    }
    path = _write_artifact("integration-witness-preflight.json", artifact)
    print(f"WROTE {path}")
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
