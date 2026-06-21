from __future__ import annotations

import pytest

from forkproof.research.capability import CapabilityGateError, classify_capability_gate
from forkproof.research.models import (
    ChildCandidate,
    DepthTwoRunRecord,
    FlatComparisonReport,
    ResearchSkip,
    ResearchLineage,
    SchedulerConfig,
    TransferTrainingReport,
)
from forkproof.research.reports import (
    ReportError,
    require_evidence_backed_skip,
    validate_flat_comparison,
    validate_transfer_training,
)
from forkproof.research.scheduler import ResearchScheduler
from forkproof.research.selection import ResearchError, select_promising_child


def test_scheduler_stops_after_four_completed_no_new_cluster_branches():
    scheduler = ResearchScheduler(node_id="node-child")

    for _ in range(4):
        decision = scheduler.schedule_next()
        assert decision is not None
        scheduler.complete_branch(decision.branch_id or "", confirmed_cluster_id=None)

    assert scheduler.can_schedule() is False
    stop = scheduler.stop_event()
    assert stop is not None
    assert stop.reason == "adaptive-stop-four-no-new-cluster"
    assert stop.scheduled_count == 4
    assert scheduler.consecutive_no_new_cluster == 4


def test_scheduler_resets_on_new_cluster_and_respects_eight_branch_budget():
    scheduler = ResearchScheduler(node_id="node-child")

    for _ in range(3):
        branch = scheduler.schedule_next()
        assert branch is not None
        scheduler.complete_branch(branch.branch_id or "", confirmed_cluster_id=None)
    branch = scheduler.schedule_next()
    assert branch is not None
    scheduler.complete_branch(branch.branch_id or "", confirmed_cluster_id="cluster-a")

    assert scheduler.consecutive_no_new_cluster == 0
    while scheduler.can_schedule():
        branch = scheduler.schedule_next()
        assert branch is not None
        scheduler.complete_branch(branch.branch_id or "", confirmed_cluster_id=None)

    stop = scheduler.stop_event()
    assert stop is not None
    assert stop.reason == "budget-exhausted"
    assert stop.scheduled_count == 8


def test_scheduler_allows_in_flight_completion_and_late_new_cluster_reset():
    scheduler = ResearchScheduler(node_id="node-child", config=SchedulerConfig(concurrency=5))
    branches = []
    for _ in range(5):
        decision = scheduler.schedule_next()
        assert decision is not None
        branches.append(decision.branch_id or "")

    for branch_id in branches[:4]:
        scheduler.complete_branch(branch_id, confirmed_cluster_id=None)
    assert scheduler.can_schedule() is False
    assert scheduler.stop_event() is None

    scheduler.complete_branch(branches[4], confirmed_cluster_id="late-cluster")
    assert scheduler.consecutive_no_new_cluster == 0
    assert scheduler.can_schedule() is True


def test_scheduler_never_counts_raw_reward_as_new_cluster():
    scheduler = ResearchScheduler(node_id="node-child")
    branch = scheduler.schedule_next()
    assert branch is not None
    scheduler.complete_branch(branch.branch_id or "", confirmed_cluster_id=None)

    assert scheduler.consecutive_no_new_cluster == 1
    assert all(decision.new_cluster_id is None for decision in scheduler.decisions)


def test_promising_child_requires_observable_signal_not_reasoning_only():
    reasoning_only = ChildCandidate(
        node_id="node-child",
        parent_node_id="node-root",
        depth=1,
        snapshot_ref="snapshot://child",
        branch_ref="branch.json",
        observable_signals=(),
        exposed_reasoning_refs=("reasoning.txt",),
    )

    with pytest.raises(ResearchError):
        select_promising_child([reasoning_only])


def test_promising_child_records_observable_fork_reason_and_alternatives():
    candidate = ChildCandidate(
        node_id="node-child",
        parent_node_id="node-root",
        depth=1,
        snapshot_ref="snapshot://child",
        branch_ref="branch.json",
        observable_signals=(
            {
                "kind": "file_change",
                "parent_value": "sha-parent",
                "child_value": "sha-child",
                "ref": "diff.json",
            },
        ),
        alternatives_considered=("node-other",),
    )

    record = select_promising_child([candidate])

    assert record["node_id"] == "node-child"
    assert record["observable_signal_count"] == 1
    assert "file_change" in str(record["fork_reason"])
    assert record["alternatives_considered"] == ["node-other"]


def test_research_lineage_requires_depth_one_child_and_snapshot_refs():
    lineage = ResearchLineage(
        root_fork_point_id="fp-001",
        parent_node_id="fp-001",
        child_node_id="node-child",
        child_depth=1,
        parent_snapshot_ref="modal-image://root",
        child_snapshot_ref="modal-image://child",
        source_branch_ref="branch.json",
        source_witness_ref="witness.json",
    )

    record = lineage.to_record()
    assert record["child_depth"] == 1
    assert record["source_witness_ref"] == "witness.json"

    with pytest.raises(ValueError):
        ResearchLineage(
            root_fork_point_id="fp-001",
            parent_node_id="fp-001",
            child_node_id="node-too-deep",
            child_depth=2,
            parent_snapshot_ref="modal-image://root",
            child_snapshot_ref="modal-image://child",
            source_branch_ref="branch.json",
        )


def test_depth_two_run_record_distinguishes_blocked_from_completed_runs():
    blocked = DepthTwoRunRecord(
        run_id="research-run-001",
        child_node_id="node-child",
        status="blocked",
        branch_budget=8,
        blocker="no mapped live executor",
    ).to_record()

    assert blocked["status"] == "blocked"
    assert blocked["completed_branch_refs"] == []
    assert blocked["content_digest"]

    completed = DepthTwoRunRecord(
        run_id="research-run-002",
        child_node_id="node-child",
        status="completed",
        branch_budget=8,
        scheduled_branch_refs=("branch-00.json",),
        completed_branch_refs=("branch-00.json",),
        measured_values={"completed_depth_two_branch_count": 1},
    ).to_record()
    assert completed["measured_values"]["completed_depth_two_branch_count"] == 1

    with pytest.raises(ValueError):
        DepthTwoRunRecord(
            run_id="research-run-003",
            child_node_id="node-child",
            status="completed",
            branch_budget=8,
        )


def test_capability_gate_returns_exact_unavailable_outcome_without_scaffold_refs():
    record = classify_capability_gate(
        profile="memory",
        probe_succeeded=False,
        probe_ref="artifacts/probe.json",
    )

    assert record.outcome == "unavailable"
    assert record.consumed_path_ref is None
    assert record.durable_conversion_ref is None


def test_capability_gate_records_available_unneeded_with_task_evidence():
    record = classify_capability_gate(
        profile="vm",
        probe_succeeded=True,
        probe_ref="artifacts/vm-probe.json",
        task_need_ref="artifacts/task-need.json",
        task_need_unique=False,
        security_ref="artifacts/security.json",
    )

    assert record.outcome == "available-unneeded"
    assert record.task_need_ref == "artifacts/task-need.json"


def test_capability_gate_requires_consumed_path_and_memory_conversion_when_needed():
    with pytest.raises(CapabilityGateError):
        classify_capability_gate(
            profile="memory",
            probe_succeeded=True,
            probe_ref="artifacts/memory-probe.json",
            task_need_ref="artifacts/task-need.json",
            task_need_unique=True,
            security_ref="artifacts/security.json",
            security_sufficient=True,
            consumed_path_ref="artifacts/consumer.json",
        )

    record = classify_capability_gate(
        profile="memory",
        probe_succeeded=True,
        probe_ref="artifacts/memory-probe.json",
        task_need_ref="artifacts/task-need.json",
        task_need_unique=True,
        security_ref="artifacts/security.json",
        security_sufficient=True,
        consumed_path_ref="artifacts/consumer.json",
        durable_conversion_ref="artifacts/durable-conversion.json",
    )
    assert record.outcome == "available-needed"


def test_reports_require_measurements_or_explicit_not_measured_limits():
    with pytest.raises(ReportError):
        validate_flat_comparison(FlatComparisonReport(status="not-measured", protocol_ref=None))

    flat = validate_flat_comparison(
        FlatComparisonReport(
            status="not-measured",
            protocol_ref=None,
            limitation="No sealed Witness exists, so no comparable depth-two budget can run.",
        )
    )
    assert flat["status"] == "not-measured"
    assert flat["content_digest"]

    transfer = validate_transfer_training(
        TransferTrainingReport(
            transfer_status="not-measured",
            training_filter_status="not-measured",
            real_task_refs=(),
            trajectory_refs=(),
            limitation="No additional real tasks and no sealed raw-vs-hardened trajectories exist.",
        )
    )
    assert transfer["transfer_status"] == "not-measured"


def test_skip_must_be_backed_by_evidence_refs():
    with pytest.raises(ReportError):
        require_evidence_backed_skip(ResearchSkip(packet="WP2", reason="blocked", evidence_refs=()))

    record = require_evidence_backed_skip(
        ResearchSkip(
            packet="WP2",
            reason="Plan 003 has candidates but no sealed Witness.",
            evidence_refs=("docs/plans/evidence/003/MANIFEST.json",),
        )
    )
    assert record["packet"] == "WP2"
