"""Plan 006 demo command entrypoints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .models import DemoError, utc_now, with_content_digest
from .publication import publication_preflight, validate_publication_attempt
from .readiness import validate_readiness_pack
from .redaction import redact_record
from .report import validate_demo_report

ROOT = Path(__file__).resolve().parents[3]


def _write_json(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(with_content_digest(record), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DemoError("input_unavailable", f"input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DemoError("input_invalid", f"input is not valid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise DemoError("input_invalid", "input JSON must be an object")
    return value


def _safe_observed_behavior(exc: DemoError) -> str:
    return str(redact_record(str(exc)))


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

    try:
        record = _load_json(report)
        validate_demo_report(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_report_ref": report.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": _safe_observed_behavior(exc),
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

    try:
        record = _load_json(source_report)
        validate_demo_report(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "replay_type": "demo-report-replay",
            "source_report_ref": source_report.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": _safe_observed_behavior(exc),
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

    try:
        record = _load_json(attempt)
        validate_publication_attempt(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_publication_attempt_ref": attempt.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": _safe_observed_behavior(exc),
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


def publication_preflight_command(
    *,
    release_proof: Path,
    target_id: str | None,
    trusted_context_ref: str | None,
    publish_binding_ref: str | None,
    publisher_capability_label: str | None,
    release_candidate_ref: str | None,
    permission_denied: bool,
    evidence_refs: list[str],
    output: Path,
) -> int:
    """Write a PublicationAttempt preflight artifact without invoking publish."""

    try:
        proof = _load_json(release_proof)
        attempt = publication_preflight(
            release_proof=proof,
            target_id=target_id,
            trusted_context_ref=trusted_context_ref,
            publish_binding_ref=publish_binding_ref,
            publisher_capability_label=publisher_capability_label,
            release_candidate_ref=release_candidate_ref,
            permission_denied=permission_denied,
            evidence_refs=evidence_refs or [release_proof.as_posix()],
        )
        validate_publication_attempt(attempt)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_release_proof_ref": release_proof.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": _safe_observed_behavior(exc),
            "validated_at": utc_now(),
        }
        _write_json(output, result)
        print(f"WROTE {output}")
        print(f"FAIL: {exc.error_class}: {exc}")
        return 2
    _write_json(output, attempt)
    print(f"WROTE {output}")
    if attempt["outcome"] == "failed":
        print(f"FAIL: publication-preflight {attempt['normalized_error_class']} id={attempt['publication_attempt_id']}")
        return 2
    print(f"PASS: publication-preflight outcome={attempt['outcome']} id={attempt['publication_attempt_id']}")
    return 0


def validate_readiness(*, pack: Path, output: Path | None) -> int:
    """Validate a demo readiness pack without probing live systems."""

    try:
        record = _load_json(pack)
        validate_readiness_pack(record)
    except DemoError as exc:
        result = {
            "schema_version": 1,
            "status": "failed",
            "source_readiness_pack_ref": pack.as_posix(),
            "error_class": exc.error_class,
            "observed_behavior": _safe_observed_behavior(exc),
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
        "source_readiness_pack_ref": pack.as_posix(),
        "readiness_pack_id": record["readiness_pack_id"],
        "readiness_status": record["status"],
        "observed_behavior": "Readiness pack validated without probing live auth, network, quota, HUD, Modal, or publish systems.",
        "validated_at": utc_now(),
    }
    if output:
        _write_json(output, result)
        print(f"WROTE {output}")
    print(f"PASS: readiness_pack={pack} status={record['status']}")
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
    preflight_parser = sub.add_parser("publication-preflight")
    preflight_parser.add_argument("--release-proof", required=True, type=Path)
    preflight_parser.add_argument("--target-id")
    preflight_parser.add_argument("--trusted-context-ref")
    preflight_parser.add_argument("--publish-binding-ref")
    preflight_parser.add_argument("--publisher-capability-label")
    preflight_parser.add_argument("--release-candidate-ref")
    preflight_parser.add_argument("--permission-denied", action="store_true")
    preflight_parser.add_argument("--evidence-ref", action="append", default=[])
    preflight_parser.add_argument("--output", required=True, type=Path)
    readiness_parser = sub.add_parser("validate-readiness-pack")
    readiness_parser.add_argument("--pack", required=True, type=Path)
    readiness_parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "demo-preflight":
        return demo_preflight()
    if args.command == "validate-report":
        return validate_report(report=args.report, output=args.output)
    if args.command == "report-replay":
        return report_replay(source_report=args.source_report, output=args.output)
    if args.command == "validate-publication-attempt":
        return validate_publication(attempt=args.attempt, output=args.output)
    if args.command == "publication-preflight":
        return publication_preflight_command(
            release_proof=args.release_proof,
            target_id=args.target_id,
            trusted_context_ref=args.trusted_context_ref,
            publish_binding_ref=args.publish_binding_ref,
            publisher_capability_label=args.publisher_capability_label,
            release_candidate_ref=args.release_candidate_ref,
            permission_denied=args.permission_denied,
            evidence_refs=args.evidence_ref,
            output=args.output,
        )
    if args.command == "validate-readiness-pack":
        return validate_readiness(pack=args.pack, output=args.output)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
