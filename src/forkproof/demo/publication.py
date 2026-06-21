"""PublicationAttempt contracts and trusted preflight policy."""

from __future__ import annotations

from typing import Any

from .models import DemoError, assert_content_digest, content_digest, require_fields, utc_now, with_content_digest

OUTCOMES = {"published", "permission-blocked", "blocked-with-proof", "failed"}
FAILURE_CLASSES = {
    "proof_mismatch",
    "unauthorized_target",
    "mixed_identity",
    "missing_artifacts",
    "trusted_context_unavailable",
    "branch_writable_evidence",
    "secret_exposure",
}
REQUIRED_ATTEMPT_FIELDS = {
    "schema_version",
    "publication_attempt_id",
    "release_proof_id",
    "release_proof_digest",
    "target_id",
    "publisher_capability_label",
    "command_key",
    "command_argv_ref",
    "trusted_context_ref",
    "idempotency_key",
    "outcome",
    "evidence_refs",
    "redaction_status",
    "created_at",
    "content_digest",
}


def idempotency_key(*, release_proof_digest: str, target_id: str) -> str:
    return content_digest({"release_proof_digest": release_proof_digest, "target_id": target_id})


def validate_publication_attempt(record: dict[str, Any]) -> None:
    """Validate a publication attempt without invoking a publish API."""

    require_fields(record, REQUIRED_ATTEMPT_FIELDS, error_class="publication_attempt_incomplete")
    if record["outcome"] not in OUTCOMES:
        raise DemoError("publication_attempt_invalid", "publication outcome is invalid")
    expected_key = idempotency_key(
        release_proof_digest=record["release_proof_digest"],
        target_id=record["target_id"],
    )
    if record["idempotency_key"] != expected_key:
        raise DemoError("publication_attempt_invalid", "idempotency key does not match proof digest and target")
    if record["redaction_status"] != "redacted":
        raise DemoError("secret_exposure", "publication attempt is not redacted")
    if not record["evidence_refs"]:
        raise DemoError("publication_attempt_incomplete", "publication attempt lacks evidence refs")
    _validate_outcome(record)
    assert_content_digest(record)


def publication_preflight(
    *,
    release_proof: dict[str, Any] | None,
    target_id: str | None,
    trusted_context_ref: str | None,
    publish_binding_ref: str | None,
    publisher_capability_label: str | None,
    release_candidate_ref: str | None,
    permission_denied: bool = False,
    evidence_refs: list[str] | None = None,
) -> dict[str, Any]:
    """Return a structured attempt/blocker without publishing anything."""

    evidence = evidence_refs or []
    base = {
        "schema_version": 1,
        "publication_attempt_id": "pubattempt-pending",
        "release_proof_id": release_proof.get("release_proof_id") if release_proof else "missing-release-proof",
        "release_proof_digest": release_proof.get("content_digest") if release_proof else "missing-release-proof-digest",
        "target_id": target_id or "missing-target",
        "publisher_capability_label": publisher_capability_label or "missing-capability",
        "command_key": "integration-publication",
        "command_argv_ref": publish_binding_ref or "missing-publish-binding",
        "trusted_context_ref": trusted_context_ref or "missing-trusted-context",
        "evidence_refs": evidence,
        "redaction_status": "redacted",
        "created_at": utc_now(),
    }
    base["idempotency_key"] = idempotency_key(
        release_proof_digest=base["release_proof_digest"],
        target_id=base["target_id"],
    )
    base["publication_attempt_id"] = "pubattempt-" + base["idempotency_key"][:16]

    failure = _preflight_failure(release_proof, target_id, trusted_context_ref, release_candidate_ref)
    if failure:
        base.update(
            {
                "outcome": "failed",
                "normalized_error_class": failure,
                "release_candidate_ref": release_candidate_ref,
            }
        )
        return with_content_digest(base)
    if permission_denied:
        base.update(
            {
                "outcome": "permission-blocked",
                "normalized_error_class": "publish_unauthorized",
                "release_candidate_ref": release_candidate_ref,
            }
        )
        return with_content_digest(base)
    if not publish_binding_ref or not publisher_capability_label:
        base.update(
            {
                "outcome": "blocked-with-proof",
                "normalized_error_class": "publish_binding_missing",
                "release_candidate_ref": release_candidate_ref,
            }
        )
        return with_content_digest(base)
    base.update(
        {
            "outcome": "failed",
            "normalized_error_class": "publish_api_not_invoked_by_contract_layer",
            "release_candidate_ref": release_candidate_ref,
        }
    )
    return with_content_digest(base)


def _preflight_failure(
    release_proof: dict[str, Any] | None,
    target_id: str | None,
    trusted_context_ref: str | None,
    release_candidate_ref: str | None,
) -> str | None:
    if not release_proof or release_proof.get("gate_status") != "pass":
        return "proof_mismatch"
    if not target_id:
        return "unauthorized_target"
    if not release_candidate_ref:
        return "missing_artifacts"
    if not trusted_context_ref:
        return "trusted_context_unavailable"
    if release_proof.get("branch_writable_evidence"):
        return "branch_writable_evidence"
    if release_proof.get("environment_v2") == release_proof.get("environment_v1"):
        return "mixed_identity"
    return None


def _validate_outcome(record: dict[str, Any]) -> None:
    outcome = record["outcome"]
    if outcome == "published" and not record.get("published_environment_ref"):
        raise DemoError("publication_attempt_invalid", "published outcome needs stable environment ref")
    if outcome in {"permission-blocked", "blocked-with-proof"}:
        if not record.get("release_candidate_ref"):
            raise DemoError("publication_attempt_invalid", f"{outcome} needs release_candidate_ref")
        if outcome == "blocked-with-proof" and record.get("release_proof_gate_status") != "pass":
            raise DemoError("publication_attempt_invalid", "blocked-with-proof requires passing ReleaseProof")
    if outcome == "failed" and record.get("normalized_error_class") not in FAILURE_CLASSES | {
        "proof_mismatch",
        "publish_api_not_invoked_by_contract_layer",
    }:
        raise DemoError("publication_attempt_invalid", "failed outcome needs normalized failure class")
