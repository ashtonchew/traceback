"""Plan 007 research CLI.

The live depth-two command intentionally fails closed while Plan 003 has no
sealed Witness. Pure policy validation is covered by unit tests.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PLAN003_MANIFEST = ROOT / "docs/plans/evidence/003/MANIFEST.json"


def _load_plan003_manifest() -> dict[str, object]:
    return json.loads(PLAN003_MANIFEST.read_text(encoding="utf-8"))


def integration() -> int:
    manifest = _load_plan003_manifest()
    sealed = any(
        check.get("name") == "Promotion and replay seal" and check.get("status") == "pass"
        for check in manifest.get("checks", [])
        if isinstance(check, dict)
    )
    if sealed and manifest.get("status") == "complete":
        print(
            "STOP: Plan 003 has sealed Witness evidence on this stack, but Plan 007 has no "
            "mapped live depth-two executor or completed depth-two BranchRun artifact yet."
        )
        return 2
    print(
        "STOP: Plan 007 live depth-two execution is blocked because Plan 003 has no sealed "
        "Exploit Witness with durable packaging, dedup clustering, and three deterministic replays."
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["integration"])
    args = parser.parse_args()
    if args.command == "integration":
        return integration()
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
