"""Machine-readable demo report validation."""

from __future__ import annotations

from typing import Any

from .models import DemoError, assert_content_digest, require_fields

DEMO_MODES = {"acceptance", "presentation", "report-replay"}
DISCOVERY_SOURCES = {"live-new-witness", "live-no-witness", "prior-run-replay"}
STEP_STATUSES = {"passed", "displayed", "fallback", "blocked-with-proof", "failed"}
METRIC_ABSENT_KEYS = {"not-measured", "not-applicable"}
FORBIDDEN_SINGLE_RUN_CLAIMS = {
    "discovery_probability",
    "success_rate",
    "exploit_coverage",
    "reliability",
    "avoided_setup",
    "cost_savings",
}

REQUIRED_REPORT_FIELDS = {
    "schema_version",
    "invocation_id",
    "command_argv",
    "commit",
    "started_at",
    "finished_at",
    "status",
    "demo_mode",
    "discovery_source",
    "live_attempt_id",
    "live_attempt_result",
    "proof_source",
    "steps",
    "metrics",
    "release_proof_ref",
    "publication_attempt_ref",
    "content_digest",
}

STEP_LABELS = {
    1: "Open suspicious HUD trace",
    2: "Show QA verdict and file evidence",
    3: "Show selected ForkPoint",
    4: "Start genuine stochastic branches",
    5: "Show branch ids/traces populating",
    6: "Inspect one exploit and file diff",
    7: "Save Exploit Witness",
    8: "Add it to ProofSet",
    9: "Apply verifier patch",
    10: "Replay Witness against v2",
    11: "Rerun legitimate controls",
    12: "Show ReleaseProof",
    13: "Publish/display hardened version",
}


def validate_demo_report(record: dict[str, Any]) -> None:
    """Validate the Plan 006 report.json semantic contract."""

    require_fields(record, REQUIRED_REPORT_FIELDS, error_class="report_incomplete")
    if record["demo_mode"] not in DEMO_MODES:
        raise DemoError("report_invalid", "demo_mode is invalid")
    if record["discovery_source"] not in DISCOVERY_SOURCES:
        raise DemoError("report_invalid", "discovery_source is invalid")
    if record["demo_mode"] == "report-replay":
        _validate_report_replay(record)
    if record["demo_mode"] == "presentation":
        _validate_presentation(record)
    if record["demo_mode"] == "acceptance":
        _validate_acceptance(record)
    _validate_steps(record["steps"], record)
    _validate_metrics(record["metrics"])
    _reject_single_run_overclaims(record)
    assert_content_digest(record)


def _validate_steps(steps: list[dict[str, Any]], report: dict[str, Any]) -> None:
    if len(steps) != 13:
        raise DemoError("report_invalid", "report must contain exactly 13 steps")
    numbers = [step.get("step_number") for step in steps]
    if sorted(numbers) != list(range(1, 14)):
        raise DemoError("report_invalid", "step numbers must be exactly 1..13")
    for step in steps:
        require_fields(
            step,
            {"step_number", "label", "status", "evidence_refs", "observed_behavior", "started_at", "finished_at"},
            error_class="step_incomplete",
        )
        number = step["step_number"]
        if step["label"] != STEP_LABELS[number]:
            raise DemoError("step_invalid", f"step {number} label does not match Plan 006 reference")
        if step["status"] not in STEP_STATUSES:
            raise DemoError("step_invalid", f"step {number} status is invalid")
        if step["status"] != "failed":
            _require_non_screenshot_evidence(step)
        if step["status"] == "blocked-with-proof" and number != 13:
            raise DemoError("step_invalid", "blocked-with-proof is only valid for publication step 13")
    if report["discovery_source"] == "prior-run-replay":
        fallback_steps = [s for s in steps if s["status"] == "fallback"]
        if not fallback_steps or not report.get("prior_run_witness_ref") or not report.get("new_replay_ref"):
            raise DemoError("fallback_unlabeled", "prior-run replay requires fallback step and replay refs")
    if report["live_attempt_result"] in {"new-witness", "branches-launched"} and not report.get("live_branch_refs"):
        raise DemoError("fake_live_branch", "live discovery claims require persisted branch refs")


def _require_non_screenshot_evidence(step: dict[str, Any]) -> None:
    refs = step.get("evidence_refs")
    if not isinstance(refs, list) or not refs:
        raise DemoError("step_incomplete", f"step {step['step_number']} lacks evidence refs")
    non_screenshot = [
        ref for ref in refs if isinstance(ref, str) and not ref.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    if not non_screenshot:
        raise DemoError("screenshot_only_proof", f"step {step['step_number']} has screenshot-only proof")


def _validate_metrics(metrics: list[dict[str, Any]]) -> None:
    for metric in metrics:
        require_fields(metric, {"name"}, error_class="metric_incomplete")
        present = "value" in metric
        absent = [key for key in METRIC_ABSENT_KEYS if key in metric]
        if present and absent:
            raise DemoError("metric_invalid", f"metric {metric['name']} mixes value and absent status")
        if not present and len(absent) != 1:
            raise DemoError("metric_invalid", f"metric {metric['name']} needs value or one absent status")
        if metric.get("value") == "TBD":
            raise DemoError("metric_invalid", f"metric {metric['name']} uses TBD as a result")
        if present and not metric.get("evidence_ref"):
            raise DemoError("metric_invalid", f"metric {metric['name']} lacks evidence_ref")
        if absent and not metric.get("reason"):
            raise DemoError("metric_invalid", f"metric {metric['name']} lacks reason for absent value")


def _validate_report_replay(record: dict[str, Any]) -> None:
    require_fields(record, {"source_invocation_id"}, error_class="report_replay_incomplete")
    forbidden = {
        "created_branch_refs",
        "new_release_proof_ref",
        "new_publication_attempt_ref",
        "published_environment_ref",
    }
    claimed = sorted(key for key in forbidden if record.get(key))
    if claimed:
        raise DemoError("report_replay_overclaim", f"report replay cannot claim new evidence: {claimed}")


def _validate_presentation(record: dict[str, Any]) -> None:
    if not record.get("presentation_budget_seconds"):
        raise DemoError("presentation_incomplete", "presentation mode needs a bounded budget")
    if not record.get("live_attempt_id"):
        raise DemoError("presentation_incomplete", "presentation mode must launch a live attempt")
    if record["discovery_source"] == "prior-run-replay" and not record.get("fallback_reason"):
        raise DemoError("fallback_unlabeled", "presentation fallback needs fallback_reason")


def _validate_acceptance(record: dict[str, Any]) -> None:
    if record.get("accepted_branch_budget") and record.get("launched_branch_count") == record["accepted_branch_budget"]:
        return
    if record.get("resource_stop_ref"):
        return
    raise DemoError("acceptance_budget_incomplete", "acceptance needs full branch budget or resource STOP evidence")


def _reject_single_run_overclaims(record: dict[str, Any]) -> None:
    claims = set(record.get("claims") or [])
    forbidden = sorted(claims & FORBIDDEN_SINGLE_RUN_CLAIMS)
    if forbidden:
        raise DemoError("statistical_overclaim", f"single-run report cannot claim {forbidden}")
