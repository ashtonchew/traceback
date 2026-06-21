"""Plan 006 demo command entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import with_content_digest

ROOT = Path(__file__).resolve().parents[3]


def _write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(with_content_digest(record), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def demo_preflight() -> int:
    """Record why the full demo cannot complete before Gate 4."""

    path = ROOT / "artifacts/forkproof/demo/preflight-blockers/plan-006-demo.json"
    record = {
        "schema_version": 1,
        "status": "blocked",
        "blockers": [
            {
                "type": "DEPENDENCY_GATE",
                "reason": "Plan 005/Gate 4 is incomplete; no sealed ReleaseProof or real v1/v2 release results exist.",
                "evidence_refs": ["docs/plans/evidence/005/MANIFEST.json"],
            },
            {
                "type": "PUBLISH_BINDING",
                "reason": "No repository-bound publish primitive and authorized target are available for Plan 006.",
                "evidence_refs": ["docs/plans/repo-map/INTERFACES.md"],
            },
        ],
        "observed_behavior": "Demo preflight refuses to claim an Acceptance Demo Run before ReleaseProof and publish binding exist.",
    }
    _write_json(path, record)
    print(f"WROTE {path}")
    for blocker in record["blockers"]:
        print(f"STOP: {blocker['type']}: {blocker['reason']}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo-preflight")
    args = parser.parse_args()
    if args.command == "demo-preflight":
        return demo_preflight()
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
