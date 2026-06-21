"""Plan 007 research CLI.

The live depth-two command intentionally fails closed until a real depth-two
executor and completed BranchRun artifact exist. Pure policy validation is
covered by unit tests.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from forkproof.research.artifacts import build_depth_two_preflight_artifact
from forkproof.witnesses.models import utc_now


ROOT = Path(__file__).resolve().parents[3]
PLAN003_MANIFEST = ROOT / "docs/plans/evidence/003/MANIFEST.json"
DEFAULT_CHILD_SELECTION = (
    ROOT / "artifacts/forkproof/research/child-selection-wit-run-20260621T075711-branch-08.json"
)
DEFAULT_PREFLIGHT = ROOT / "artifacts/forkproof/research/depth-two-integration-preflight.json"


def _load_plan003_manifest() -> dict[str, object]:
    return json.loads(PLAN003_MANIFEST.read_text(encoding="utf-8"))


def _existing_recorded_at(path: Path) -> str:
    if not path.exists():
        return utc_now()
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return utc_now()
    recorded_at = existing.get("recorded_at")
    return recorded_at if isinstance(recorded_at, str) and recorded_at else utc_now()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def integration(*, output_path: Path = DEFAULT_PREFLIGHT, child_selection_path: Path = DEFAULT_CHILD_SELECTION) -> int:
    manifest = _load_plan003_manifest()
    artifact = build_depth_two_preflight_artifact(
        plan003_manifest=manifest,
        child_selection_ref=_display_path(child_selection_path),
        child_selection_exists=child_selection_path.exists(),
        command_ref="uv run python -m forkproof.research.cli integration",
        recorded_at=_existing_recorded_at(output_path),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    sealed = any(
        check.get("name") == "Promotion and replay seal" and check.get("status") == "pass"
        for check in manifest.get("checks", [])
        if isinstance(check, dict)
    )
    if sealed and manifest.get("status") == "complete":
        print(
            "STOP: Plan 003 has sealed Witness evidence on this stack, but Plan 007 has no "
            "mapped live depth-two executor or completed depth-two BranchRun artifact yet. "
            f"Preflight artifact: {_display_path(output_path)}"
        )
        return 2
    print(
        "STOP: Plan 007 live depth-two execution is blocked because Plan 003 has no sealed "
        "Exploit Witness with durable packaging, dedup clustering, and three deterministic replays. "
        f"Preflight artifact: {_display_path(output_path)}"
    )
    return 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["integration"])
    parser.add_argument("--output", type=Path, default=DEFAULT_PREFLIGHT)
    args = parser.parse_args()
    if args.command == "integration":
        return integration(output_path=args.output)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
