"""Plan 005 command entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .harden_adapter import inspect_harden_config
from .models import ReleaseError
from .proofset import build_proofset, load_controls_manifest
from .release_evaluation import run_release_evaluation

ROOT = Path(__file__).resolve().parents[3]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sealed_witnesses() -> list[dict]:
    roots = [
        ROOT / "docs/plans/evidence/003/artifacts/sealed/witnesses",
        ROOT / "docs/plans/evidence/003/artifacts/sealed-witnesses/witnesses",
    ]
    records = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.glob("*.json")):
            records.append(_load_json(path))
    return records


def integration(
    *,
    controls_manifest: Path,
    taskset_or_suite_ref: str,
    selection_query_ref: str,
    harden_task_source: Path | None = None,
    harden_task_id: str | None = None,
    release_results_ref: Path | None = None,
    harden_max_iterations: int = 1,
    harden_timeout_seconds: int = 1200,
    harden_hacker_model: str | None = None,
    harden_fixer_model: str | None = None,
    harden_solver_model: str | None = None,
) -> int:
    blockers: list[str] = []
    try:
        harden_schema = inspect_harden_config(ROOT / ".external/harden-v0/harden/config.py")
    except ReleaseError as exc:
        harden_schema = {"status": "blocked", "error_class": exc.error_class, "observed_behavior": str(exc)}
        blockers.append(str(exc))

    witnesses = _sealed_witnesses()
    controls = load_controls_manifest(controls_manifest)
    proofset = None
    if not witnesses:
        blockers.append("no sealed Plan 003 Exploit Witness records found")
    else:
        try:
            proofset = build_proofset(
                witnesses=witnesses,
                controls=controls,
                taskset_or_suite_ref=taskset_or_suite_ref,
                selection_query_ref=selection_query_ref,
            )
        except ReleaseError as exc:
            blockers.append(str(exc))
    release_evaluation = None
    if proofset is not None:
        try:
            release_evaluation = run_release_evaluation(
                repo_root=ROOT,
                proof_set=proofset,
                harden_task_source=harden_task_source,
                harden_task_id=harden_task_id,
                release_results_ref=release_results_ref,
                artifact_root=ROOT / "artifacts/forkproof/releases",
                harden_max_iterations=harden_max_iterations,
                harden_timeout_seconds=harden_timeout_seconds,
                harden_hacker_model=harden_hacker_model,
                harden_fixer_model=harden_fixer_model,
                harden_solver_model=harden_solver_model,
            )
            if release_evaluation["status"] != "pass":
                blockers.append(f"release gate did not pass: {release_evaluation['status']}")
        except ReleaseError as exc:
            release_evaluation = {
                "status": "blocked",
                "error_class": exc.error_class,
                "observed_behavior": str(exc),
            }
            blockers.append(str(exc))

    artifact = {
        "schema_version": 1,
        "status": "blocked" if blockers else "complete",
        "harden_schema": harden_schema,
        "sealed_witness_count": len(witnesses),
        "control_count": len(controls),
        "controls_manifest": controls_manifest.as_posix(),
        "taskset_or_suite_ref": taskset_or_suite_ref,
        "selection_query_ref": selection_query_ref,
        "proofset": proofset,
        "release_evaluation": release_evaluation,
        "blockers": blockers,
        "observed_behavior": (
            "Plan 005 integration binds harden-v0 schema, closes ProofSet membership, "
            "then seals ReleaseProof only from real per-case v1/v2 evaluator results."
        ),
    }
    path = ROOT / "docs/plans/evidence/005/integration-release-preflight.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"WROTE {path}")
    if blockers:
        for blocker in blockers:
            print(f"STOP: {blocker}")
        return 2
    print(f"COMPLETE proof_set_id={proofset['proof_set_id']} release_proof={release_evaluation['release_proof_ref']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    integration_parser = sub.add_parser("integration")
    integration_parser.add_argument("--controls-manifest", required=True, type=Path)
    integration_parser.add_argument("--taskset-or-suite-ref", required=True)
    integration_parser.add_argument("--selection-query-ref", required=True)
    integration_parser.add_argument("--harden-task-source", type=Path)
    integration_parser.add_argument("--harden-task-id")
    integration_parser.add_argument("--release-results-ref", type=Path)
    integration_parser.add_argument("--harden-max-iterations", type=int, default=1)
    integration_parser.add_argument("--harden-timeout-seconds", type=int, default=1200)
    integration_parser.add_argument("--harden-hacker-model")
    integration_parser.add_argument("--harden-fixer-model")
    integration_parser.add_argument("--harden-solver-model")
    args = parser.parse_args()
    if args.command == "integration":
        return integration(
            controls_manifest=args.controls_manifest,
            taskset_or_suite_ref=args.taskset_or_suite_ref,
            selection_query_ref=args.selection_query_ref,
            harden_task_source=args.harden_task_source,
            harden_task_id=args.harden_task_id,
            release_results_ref=args.release_results_ref,
            harden_max_iterations=args.harden_max_iterations,
            harden_timeout_seconds=args.harden_timeout_seconds,
            harden_hacker_model=args.harden_hacker_model,
            harden_fixer_model=args.harden_fixer_model,
            harden_solver_model=args.harden_solver_model,
        )
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
