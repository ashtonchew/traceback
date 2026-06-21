from __future__ import annotations

import pytest

from forkproof.demo.models import DemoError, with_content_digest
from forkproof.demo.report import REQUIRED_METRICS, STEP_LABELS, validate_demo_report


def step(number: int, *, status: str = "passed", refs: list[str] | None = None):
    return {
        "step_number": number,
        "label": STEP_LABELS[number],
        "status": status,
        "evidence_refs": refs or [f"docs/plans/evidence/006/artifacts/step-{number}.json"],
        "observed_behavior": f"observed step {number}",
        "started_at": "2026-06-21T00:00:00Z",
        "finished_at": "2026-06-21T00:00:01Z",
    }


def report(**overrides):
    metrics = [{"name": "branch_count", "value": 12, "evidence_ref": "branch-run-batch.json"}]
    metrics.extend(
        {
            "name": name,
            "not-measured": True,
            "reason": "Not measured before full Acceptance Demo Run evidence exists",
        }
        for name in sorted(REQUIRED_METRICS - {"branch_count"})
    )
    record = {
        "schema_version": 1,
        "invocation_id": "demo-001",
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
        "metrics": metrics,
        "release_proof_ref": "blocked:plan-005",
        "publication_attempt_ref": "blocked:publish-binding",
        "accepted_branch_budget": 12,
        "launched_branch_count": 12,
        "claims": [],
    }
    record.update(overrides)
    return with_content_digest(record)


def test_acceptance_report_requires_thirteen_evidence_backed_steps():
    validate_demo_report(report())


def test_report_rejects_invalid_status_and_live_attempt_result():
    with pytest.raises(DemoError, match="report status"):
        validate_demo_report(report(status="skipped"))

    with pytest.raises(DemoError, match="live_attempt_result"):
        validate_demo_report(report(live_attempt_result="pretend-live"))


def test_report_rejects_screenshot_only_step_evidence():
    steps = [step(i) for i in range(1, 14)]
    steps[0] = step(1, refs=["screenshots/trace.png"])

    with pytest.raises(DemoError, match="screenshot-only"):
        validate_demo_report(report(steps=steps))


def test_acceptance_report_rejects_fake_live_branch_claims():
    with pytest.raises(DemoError, match="live discovery claims"):
        validate_demo_report(report(live_branch_refs=[]))

    with pytest.raises(DemoError, match="live-new-witness"):
        validate_demo_report(report(discovery_source="live-new-witness", live_attempt_result="branches-launched"))

    with pytest.raises(DemoError, match="cannot claim a new Witness"):
        validate_demo_report(report(discovery_source="live-no-witness", live_attempt_result="new-witness"))


def test_prior_run_fallback_requires_visible_label_and_replay_refs():
    with pytest.raises(DemoError, match="prior-run replay requires"):
        validate_demo_report(report(discovery_source="prior-run-replay"))

    steps = [step(i) for i in range(1, 14)]
    steps[5] = step(6, status="fallback")
    validate_demo_report(
        report(
            discovery_source="prior-run-replay",
            live_attempt_result="timeout",
            steps=steps,
            prior_run_witness_ref="wit-001.json",
            new_replay_ref="replay-001.json",
        )
    )


def test_report_replay_is_audit_only():
    replay = report(
        demo_mode="report-replay",
        source_invocation_id="demo-source",
        accepted_branch_budget=None,
        launched_branch_count=None,
        live_attempt_result="audit-only",
        live_branch_refs=[],
        resource_stop_ref="not-required-for-report-replay",
    )
    validate_demo_report(replay)

    with pytest.raises(DemoError, match="cannot claim new evidence"):
        validate_demo_report(
            report(
                demo_mode="report-replay",
                live_attempt_result="audit-only",
                source_invocation_id="demo-source",
                new_publication_attempt_ref="pub-new.json",
            )
        )

    with pytest.raises(DemoError, match="cannot claim new evidence"):
        validate_demo_report(
            report(
                demo_mode="report-replay",
                live_attempt_result="audit-only",
                source_invocation_id="demo-source",
                new_replay_ref="replay-new.json",
            )
        )

    with pytest.raises(DemoError, match="audit-only"):
        validate_demo_report(report(demo_mode="report-replay", source_invocation_id="demo-source"))


def test_presentation_mode_requires_bounded_live_attempt_before_fallback():
    with pytest.raises(DemoError, match="bounded budget"):
        validate_demo_report(report(demo_mode="presentation"))

    steps = [step(i) for i in range(1, 14)]
    steps[5] = step(6, status="fallback")
    validate_demo_report(
        report(
            demo_mode="presentation",
            discovery_source="prior-run-replay",
            live_attempt_result="timeout",
            presentation_budget_seconds=30,
            fallback_reason="presentation timeout",
            prior_run_witness_ref="wit-001.json",
            new_replay_ref="replay-001.json",
            steps=steps,
        )
    )


def test_metrics_reject_tbd_and_single_run_statistical_overclaims():
    metrics = [{"name": name, "not-measured": True, "reason": "not measured"} for name in sorted(REQUIRED_METRICS)]
    metrics[0] = {"name": metrics[0]["name"], "value": "TBD", "evidence_ref": "x"}
    with pytest.raises(DemoError, match="TBD"):
        validate_demo_report(report(metrics=metrics))

    with pytest.raises(DemoError, match="single-run"):
        validate_demo_report(report(claims=["success_rate"]))


def test_metrics_require_core_metric_set():
    with pytest.raises(DemoError, match="missing required metric"):
        validate_demo_report(report(metrics=[{"name": "branch_count", "value": 12, "evidence_ref": "branch-run-batch.json"}]))
