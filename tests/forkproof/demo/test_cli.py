from __future__ import annotations

import json

from forkproof.demo.cli import report_replay, validate_report
from forkproof.demo.models import with_content_digest
from forkproof.demo.report import STEP_LABELS


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
