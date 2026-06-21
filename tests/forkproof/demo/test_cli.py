from __future__ import annotations

import json

from forkproof.demo.cli import publication_preflight_command, report_replay, validate_publication, validate_report
from forkproof.demo.models import with_content_digest
from forkproof.demo.publication import idempotency_key
from forkproof.demo.report import STEP_LABELS
from forkproof.releases.models import digest_json


def step(number: int, *, refs: list[str] | None = None):
    return {
        "step_number": number,
        "label": STEP_LABELS[number],
        "status": "passed",
        "evidence_refs": refs or [f"artifact-{number}.json"],
        "observed_behavior": f"step {number}",
        "started_at": "2026-06-21T00:00:00Z",
        "finished_at": "2026-06-21T00:00:01Z",
    }


def report(**overrides):
    record = {
        "schema_version": 1,
        "invocation_id": "demo-cli-source",
        "command_argv": ["forkproof-demo", "acceptance"],
        "commit": "abc123",
        "started_at": "2026-06-21T00:00:00Z",
        "finished_at": "2026-06-21T00:02:00Z",
        "status": "blocked",
        "demo_mode": "acceptance",
        "discovery_source": "live-no-witness",
        "live_attempt_id": "live-001",
        "live_attempt_result": "branches-launched",
        "live_branch_refs": ["branch-run-001.json"],
        "proof_source": "release-proof-pending",
        "steps": [step(i) for i in range(1, 14)],
        "metrics": [{"name": "branch_count", "value": 12, "evidence_ref": "branch-run-batch.json"}],
        "release_proof_ref": "blocked:plan-005",
        "publication_attempt_ref": "blocked:publish-binding",
        "accepted_branch_budget": 12,
        "launched_branch_count": 12,
        "claims": [],
    }
    record.update(overrides)
    return with_content_digest(record)


def publication_attempt(**overrides):
    key = idempotency_key(release_proof_digest="rp-digest", target_id="target-prod")
    record = {
        "schema_version": 1,
        "publication_attempt_id": "pub-001",
        "release_proof_id": "rp-001",
        "release_proof_digest": "rp-digest",
        "target_id": "target-prod",
        "publisher_capability_label": "trusted-publisher",
        "command_key": "integration-publication",
        "command_argv_ref": "COMMANDS.json:integration-publication",
        "trusted_context_ref": "trusted-ci",
        "idempotency_key": key,
        "outcome": "permission-blocked",
        "release_proof_gate_status": "pass",
        "release_candidate_ref": "candidate.json",
        "normalized_error_class": "publish_unauthorized",
        "evidence_refs": ["release-proof.json", "candidate.json"],
        "redaction_status": "redacted",
        "created_at": "2026-06-21T00:00:00Z",
    }
    record.update(overrides)
    return with_content_digest(record)


def release_proof(**overrides):
    record = {
        "schema_version": 1,
        "release_proof_id": "rp-cli-001",
        "proof_set_id": "proof-set-cli",
        "environment_v1": "env-v1",
        "grader_v1_digest": "grader-v1",
        "environment_v2": "env-v2",
        "grader_v2_digest": "grader-v2",
        "patch_ref": "artifacts/forkproof/releases/patch.json",
        "fixer_run_ref": "artifacts/forkproof/releases/harden-result.json",
        "v1_results": [{"case_id": "witness-001", "kind": "witness", "reward": 1.0}],
        "v2_results": [{"case_id": "witness-001", "kind": "witness", "reward": 0.0}],
        "subversion_results": [],
        "evaluator_context_refs": ["artifacts/forkproof/releases/context.json"],
        "rejection_history": [],
        "family_variant_results": [],
        "witnesses_killed": ["witness-001"],
        "controls_preserved": ["control-001"],
        "gate_status": "pass",
        "trace_links": ["trace://source"],
        "release_candidate_ref": "artifacts/forkproof/releases/candidate.json",
        "created_at": "2026-06-21T00:00:00Z",
    }
    record.update(overrides)
    record["content_digest"] = digest_json(record)
    return record


def write_json(path, record):
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_validate_report_cli_writes_pass_artifact(tmp_path):
    source = tmp_path / "report.json"
    output = tmp_path / "validation.json"
    write_json(source, report())

    assert validate_report(report=source, output=output) == 0

    result = read_json(output)
    assert result["status"] == "pass"
    assert result["source_invocation_id"] == "demo-cli-source"
    assert result["content_digest"]


def test_validate_report_cli_writes_failure_artifact(tmp_path):
    source = tmp_path / "report.json"
    output = tmp_path / "validation.json"
    bad = report(metrics=[{"name": "restore_latency", "value": "TBD", "evidence_ref": "metrics.json"}])
    write_json(source, bad)

    assert validate_report(report=source, output=output) == 2

    result = read_json(output)
    assert result["status"] == "failed"
    assert result["error_class"] == "metric_invalid"


def test_validate_report_cli_writes_failure_artifact_for_malformed_json(tmp_path):
    source = tmp_path / "report.json"
    output = tmp_path / "validation.json"
    source.write_text("{not-json", encoding="utf-8")

    assert validate_report(report=source, output=output) == 2

    result = read_json(output)
    assert result["status"] == "failed"
    assert result["error_class"] == "input_invalid"


def test_validate_report_cli_writes_failure_artifact_for_non_object_json(tmp_path):
    source = tmp_path / "report.json"
    output = tmp_path / "validation.json"
    write_json(source, ["not", "an", "object"])

    assert validate_report(report=source, output=output) == 2

    result = read_json(output)
    assert result["status"] == "failed"
    assert result["error_class"] == "input_invalid"


def test_report_replay_cli_is_audit_only(tmp_path):
    source = tmp_path / "report.json"
    output = tmp_path / "replay-validation.json"
    write_json(source, report())

    assert report_replay(source_report=source, output=output) == 0

    result = read_json(output)
    assert result["status"] == "pass"
    assert result["replay_type"] == "demo-report-replay"
    assert result["source_invocation_id"] == "demo-cli-source"
    assert result["created_branch_refs"] == []
    assert result["new_replay_ref"] is None
    assert result["new_release_proof_ref"] is None
    assert result["new_publication_attempt_ref"] is None
    assert result["published_environment_ref"] is None


def test_validate_publication_attempt_cli_writes_pass_artifact(tmp_path):
    source = tmp_path / "publication-attempt.json"
    output = tmp_path / "publication-validation.json"
    write_json(source, publication_attempt())

    assert validate_publication(attempt=source, output=output) == 0

    result = read_json(output)
    assert result["status"] == "pass"
    assert result["publication_attempt_id"] == "pub-001"
    assert result["outcome"] == "permission-blocked"
    assert result["content_digest"]


def test_validate_publication_attempt_cli_writes_failure_artifact(tmp_path):
    source = tmp_path / "publication-attempt.json"
    output = tmp_path / "publication-validation.json"
    write_json(source, publication_attempt(redaction_status="unsafe"))

    assert validate_publication(attempt=source, output=output) == 2

    result = read_json(output)
    assert result["status"] == "failed"
    assert result["error_class"] == "secret_exposure"


def test_publication_preflight_cli_writes_blocked_with_proof_attempt(tmp_path):
    proof_path = tmp_path / "release-proof.json"
    output = tmp_path / "publication-attempt.json"
    write_json(proof_path, release_proof())

    assert (
        publication_preflight_command(
            release_proof=proof_path,
            target_id="target-prod",
            trusted_context_ref="trusted-ci",
            publish_binding_ref=None,
            publisher_capability_label=None,
            release_candidate_ref="candidate.json",
            permission_denied=False,
            evidence_refs=["release-proof.json", "candidate.json"],
            output=output,
        )
        == 0
    )

    result = read_json(output)
    assert result["outcome"] == "blocked-with-proof"
    assert result["normalized_error_class"] == "publish_binding_missing"
    assert result["release_proof_gate_status"] == "pass"
    assert result["content_digest"]


def test_publication_preflight_cli_writes_failure_artifact_for_bad_proof(tmp_path):
    proof_path = tmp_path / "release-proof.json"
    output = tmp_path / "publication-attempt.json"
    write_json(proof_path, {"release_proof_id": "incomplete"})

    assert (
        publication_preflight_command(
            release_proof=proof_path,
            target_id="target-prod",
            trusted_context_ref="trusted-ci",
            publish_binding_ref=None,
            publisher_capability_label=None,
            release_candidate_ref="candidate.json",
            permission_denied=False,
            evidence_refs=["release-proof.json", "candidate.json"],
            output=output,
        )
        == 2
    )

    result = read_json(output)
    assert result["outcome"] == "failed"
    assert result["normalized_error_class"] == "proof_mismatch"
    assert result["content_digest"]
