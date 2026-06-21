"""Plan 006 demo command entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import DemoError, utc_now, with_content_digest
from .publication import validate_publication_attempt
from .report import validate_demo_report

ROOT = Path(__file__).resolve().parents[3]


def _write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(with_content_digest(record), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def validate_report(*, report: Path, output: Path | None) -> int:
    """Validate an existing report.json and optionally persist the result."""

    record = _load_json(report)
    try:
        validate_demo_report(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_report_ref": report.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": str(exc),
            "validated_at": utc_now(),
        }
        if output:
            _write_json(output, result)
            print(f"WROTE {output}")
        print(f"FAIL: {exc.error_class}: {exc}")
        return 2
    result = {
        "schema_version": 1,
        "status": "pass",
        "source_report_ref": report.as_posix(),
        "source_invocation_id": record["invocation_id"],
        "demo_mode": record["demo_mode"],
        "observed_behavior": "Report validated without creating new proof, replay, publication, or branch evidence.",
        "validated_at": utc_now(),
    }
    if output:
        _write_json(output, result)
        print(f"WROTE {output}")
    print(f"PASS: report={report} invocation={record['invocation_id']}")
    return 0


def report_replay(*, source_report: Path, output: Path) -> int:
    """Audit-only report replay validation."""

    record = _load_json(source_report)
    try:
        validate_demo_report(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "replay_type": "demo-report-replay",
            "source_report_ref": source_report.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": str(exc),
            "validated_at": utc_now(),
        }
        _write_json(output, result)
        print(f"WROTE {output}")
        print(f"FAIL: {exc.error_class}: {exc}")
        return 2
    result = {
        "schema_version": 1,
        "status": "pass",
        "replay_type": "demo-report-replay",
        "source_report_ref": source_report.as_posix(),
        "source_invocation_id": record["invocation_id"],
        "created_branch_refs": [],
        "new_replay_ref": None,
        "new_release_proof_ref": None,
        "new_publication_attempt_ref": None,
        "published_environment_ref": None,
        "observed_behavior": "Audit-only replay revalidated the source report and created no new branch, replay, ReleaseProof, publication attempt, or publish evidence.",
        "validated_at": utc_now(),
    }
    _write_json(output, result)
    print(f"WROTE {output}")
    print(f"PASS: report-replay source_invocation_id={record['invocation_id']}")
    return 0


def validate_publication(*, attempt: Path, output: Path | None) -> int:
    """Validate a PublicationAttempt artifact without invoking publish."""

    record = _load_json(attempt)
    try:
        validate_publication_attempt(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_publication_attempt_ref": attempt.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": str(exc),
            "validated_at": utc_now(),
        }
        if output:
            _write_json(output, result)
            print(f"WROTE {output}")
        print(f"FAIL: {exc.error_class}: {exc}")
        return 2
    result = {
        "schema_version": 1,
        "status": "pass",
        "source_publication_attempt_ref": attempt.as_posix(),
        "publication_attempt_id": record["publication_attempt_id"],
        "outcome": record["outcome"],
        "idempotency_key": record["idempotency_key"],
        "observed_behavior": "PublicationAttempt validated without invoking a publish API.",
        "validated_at": utc_now(),
    }
    if output:
        _write_json(output, result)
        print(f"WROTE {output}")
    print(f"PASS: publication_attempt={attempt} outcome={record['outcome']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo-preflight")
    validate_parser = sub.add_parser("validate-report")
    validate_parser.add_argument("--report", required=True, type=Path)
    validate_parser.add_argument("--output", type=Path)
    replay_parser = sub.add_parser("report-replay")
    replay_parser.add_argument("--source-report", required=True, type=Path)
    replay_parser.add_argument("--output", required=True, type=Path)
    pub_parser = sub.add_parser("validate-publication-attempt")
    pub_parser.add_argument("--attempt", required=True, type=Path)
    pub_parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "demo-preflight":
        return demo_preflight()
    if args.command == "validate-report":
        return validate_report(report=args.report, output=args.output)
    if args.command == "report-replay":
        return report_replay(source_report=args.source_report, output=args.output)
    if args.command == "validate-publication-attempt":
        return validate_publication(attempt=args.attempt, output=args.output)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
