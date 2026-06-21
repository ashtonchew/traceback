from __future__ import annotations

import pytest

from forkproof.demo.models import DemoError, with_content_digest
from forkproof.demo.publication import idempotency_key, publication_preflight, validate_publication_attempt


def release_proof(**overrides):
    record = {
        "release_proof_id": "rp-001",
        "content_digest": "rp-digest",
        "gate_status": "pass",
        "environment_v1": "env-v1",
        "environment_v2": "env-v2",
    }
    record.update(overrides)
    return record


def attempt(**overrides):
    key = idempotency_key(release_proof_digest="rp-digest", target_id="target-prod")
    record = {
        "schema_version": 1,
        "publication_attempt_id": "pub-001",
        "release_proof_id": "rp-001",
        "release_proof_digest": "rp-digest",
        "target_id": "target-prod",
        "publisher_capability_label": "trusted-publisher",
        "command_key": "integration-publication",
        "command_argv_ref": "docs/plans/repo-map/COMMANDS.json:integration-publication",
        "trusted_context_ref": "trusted-ci",
        "idempotency_key": key,
        "outcome": "blocked-with-proof",
        "release_proof_gate_status": "pass",
        "release_candidate_ref": "artifacts/forkproof/releases/candidate.json",
        "normalized_error_class": "publish_binding_missing",
        "evidence_refs": ["release-proof.json", "candidate.json"],
        "redaction_status": "redacted",
        "created_at": "2026-06-21T00:00:00Z",
    }
    record.update(overrides)
    return with_content_digest(record)


def test_blocked_with_proof_requires_passing_proof_and_candidate():
    validate_publication_attempt(attempt())

    with pytest.raises(DemoError, match="passing ReleaseProof"):
        validate_publication_attempt(attempt(release_proof_gate_status="reject"))

    with pytest.raises(DemoError, match="release_candidate_ref"):
        validate_publication_attempt(attempt(release_candidate_ref=None))


def test_preflight_fails_missing_or_bad_proof_instead_of_claiming_blocked_with_proof():
    record = publication_preflight(
        release_proof=release_proof(gate_status="reject"),
        target_id="target-prod",
        trusted_context_ref="trusted-ci",
        publish_binding_ref=None,
        publisher_capability_label=None,
        release_candidate_ref="candidate.json",
        evidence_refs=["candidate.json"],
    )

    assert record["outcome"] == "failed"
    assert record["normalized_error_class"] == "proof_mismatch"
    validate_publication_attempt(record)


def test_preflight_records_blocked_with_proof_only_after_passing_proof():
    record = publication_preflight(
        release_proof=release_proof(),
        target_id="target-prod",
        trusted_context_ref="trusted-ci",
        publish_binding_ref=None,
        publisher_capability_label=None,
        release_candidate_ref="candidate.json",
        evidence_refs=["release-proof.json", "candidate.json"],
    )

    assert record["outcome"] == "blocked-with-proof"
    assert record["release_proof_gate_status"] == "pass"
    validate_publication_attempt(record)


def test_preflight_records_permission_blocked_with_stable_idempotency():
    first = publication_preflight(
        release_proof=release_proof(),
        target_id="target-prod",
        trusted_context_ref="trusted-ci",
        publish_binding_ref="COMMANDS.json:integration-publication",
        publisher_capability_label="trusted-publisher",
        release_candidate_ref="candidate.json",
        permission_denied=True,
        evidence_refs=["release-proof.json", "candidate.json"],
    )
    second = publication_preflight(
        release_proof=release_proof(),
        target_id="target-prod",
        trusted_context_ref="trusted-ci",
        publish_binding_ref="COMMANDS.json:integration-publication",
        publisher_capability_label="trusted-publisher",
        release_candidate_ref="candidate.json",
        permission_denied=True,
        evidence_refs=["release-proof.json", "candidate.json"],
    )

    assert first["outcome"] == "permission-blocked"
    assert first["idempotency_key"] == second["idempotency_key"]
    assert first["publication_attempt_id"] == second["publication_attempt_id"]
    validate_publication_attempt(first)


@pytest.mark.parametrize(
    ("kwargs", "error_class"),
    [
        ({"target_id": None}, "unauthorized_target"),
        ({"trusted_context_ref": None}, "trusted_context_unavailable"),
        ({"release_candidate_ref": None}, "missing_artifacts"),
        ({"release_proof": release_proof(branch_writable_evidence=True)}, "branch_writable_evidence"),
        ({"release_proof": release_proof(environment_v2="env-v1")}, "mixed_identity"),
    ],
)
def test_preflight_failure_semantics(kwargs, error_class):
    base = {
        "release_proof": release_proof(),
        "target_id": "target-prod",
        "trusted_context_ref": "trusted-ci",
        "publish_binding_ref": None,
        "publisher_capability_label": None,
        "release_candidate_ref": "candidate.json",
        "evidence_refs": ["candidate.json"],
    }
    base.update(kwargs)

    record = publication_preflight(**base)

    assert record["outcome"] == "failed"
    assert record["normalized_error_class"] == error_class
    validate_publication_attempt(record)


def test_published_outcome_requires_stable_environment_ref():
    with pytest.raises(DemoError, match="stable environment"):
        validate_publication_attempt(attempt(outcome="published", release_candidate_ref=None))

    validate_publication_attempt(
        attempt(
            outcome="published",
            release_candidate_ref=None,
            published_environment_ref="hud-env-version://env-v2",
            normalized_error_class=None,
        )
    )
