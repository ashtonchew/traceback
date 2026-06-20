"""Plan 002 mapped integration probe.

This command binds the ForkPoint contract to checked-in Plan 001 evidence and
records an honest readiness artifact. It exits non-zero in --require-real mode
until the real HUD completed-action boundary and Modal task snapshot adapter are
available.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from .core import (
    ForkPointError,
    ForkPointStore,
    InMemorySnapshotProvider,
    boundary_token,
    capture_forkpoint,
    load_source_trace,
    restore_forkpoint,
)

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "plans" / "evidence" / "002" / "artifacts"


def _sample_history() -> list[dict[str, str]]:
    return [
        {"role": "user", "content": "Implement SalesAnalyzer using aggregation pipelines."},
        {"role": "assistant", "content": "Created query.py and ran the grader."},
        {"role": "tool", "content": "pytest task_assets/test_outputs.py: 13 passed"},
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-real", action="store_true")
    args = parser.parse_args()

    source = load_source_trace(ROOT / "docs" / "plans" / "repo-map" / "STATUS.json")
    provider = InMemorySnapshotProvider()
    try:
        with tempfile.TemporaryDirectory(prefix="forkpoint-readiness-") as tmp:
            store = ForkPointStore(Path(tmp))
            hud_step_id = "completed-action:accepted-live-reward1-final"
            task_state = {
                "task_state_root": "/app",
                "query_py": "present in accepted live trace; exact file evidence unavailable",
                "mongodb_dbpath": "/data/db requires real Modal filesystem snapshot",
                "mongo_log": "/var/log/mongodb.log requires real Modal filesystem snapshot",
                "pytest_plugin_surface": "/app/task_assets is branch-writable verifier surface",
            }
            record = capture_forkpoint(
                source=source,
                hud_step_id=hud_step_id,
                history_prefix=_sample_history(),
                task_state=task_state,
                snapshot_mode="filesystem",
                provider=provider,
                store=store,
            )
            handoff = restore_forkpoint(
                record=record,
                provider=provider,
                expected_boundary_token=boundary_token(source, hud_step_id),
                history_prefix=_sample_history(),
                grader_digest=source["grader_digest"],
            )
    except ForkPointError as exc:
        print(f"ERROR {exc.error_class}: {exc}")
        return 1

    artifact = {
        "status": "readiness-pass",
        "scope": "checked-in-trace-evidence plus local provider contract",
        "fork_point_id": record["fork_point_id"],
        "handoff_keys": sorted(handoff),
        "remaining_real_system_gaps": [
            "HUD completed-action boundary export is not checked in",
            "real Modal task filesystem snapshot capture/restore is not implemented",
            "security controls/resource limits remain located-owned outside Plan 002",
            "environment image digest remains TBD",
        ],
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE / "integration-readiness.json"
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS integration-readiness artifact={path}")
    if args.require_real:
        print("STOP real ForkPoint capture is not proven by this readiness probe")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
