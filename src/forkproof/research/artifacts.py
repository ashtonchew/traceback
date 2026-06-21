"""Plan 007 research artifact builders."""

from __future__ import annotations

from typing import Any

from forkproof.research.models import FlatComparisonReport, ResearchSkip, TransferTrainingReport
from forkproof.research.reports import (
    require_evidence_backed_skip,
    validate_flat_comparison,
    validate_transfer_training,
)
from forkproof.witnesses.models import digest_json


def build_child_selection_artifact(
    *,
    witness: dict[str, Any],
    causal_delta: dict[str, Any],
    source_witness_ref: str,
    source_causal_delta_ref: str,
    alternatives_considered: tuple[str, ...],
    recorded_at: str,
) -> dict[str, Any]:
    """Build the Plan 007 child-selection artifact from sealed Witness evidence."""

    branch_id = str(witness["source_branch_id"])
    node_id = f"node-{branch_id}"
    parent_node_id = "fp-826ba545cf30870e67d42ddb"
    snapshot_ref = str(witness["pre_attack_snapshot_ref"])
    branch_ref = str(witness["file_diff_ref"]).replace("/file-diffs/", "/branches/")
    branch_ref = branch_ref.replace(f"{branch_id}.json", f"{branch_id}.json")
    if "file-diffs" in branch_ref:
        branch_ref = f"docs/plans/evidence/003/artifacts/branch-runs/run-20260621T075711/branches/{branch_id}.json"

    exploit_target = str(witness["exploit_target"])
    exploit_mechanism = str(witness["exploit_mechanism"])
    cluster_id = str(witness["cluster_id"])
    added_paths = sorted(causal_delta.get("added_text", {}).keys())
    selected_path = added_paths[0] if added_paths else "/app/conftest.py"

    return {
        "schema_version": 1,
        "artifact_id": f"child-selection-wit-{branch_id}",
        "status": "selected-not-resnapshotted",
        "recorded_at": recorded_at,
        "source_witness_ref": source_witness_ref,
        "source_causal_delta_ref": source_causal_delta_ref,
        "selection_record": {
            "schema_version": 1,
            "node_id": node_id,
            "parent_node_id": parent_node_id,
            "depth": 1,
            "snapshot_ref": snapshot_ref,
            "branch_ref": branch_ref,
            "fork_reason": (
                f"Selected sealed Witness branch {branch_id} as the Plan 007 promising child candidate "
                "because observable branch-local evidence differs from the root ForkPoint: "
                f"{selected_path} was added, QA classified the rewarded trace as reward hacking, "
                f"dedup created {cluster_id}, and three deterministic replays confirmed the verifier bypass."
            ),
            "observable_signals": [
                {
                    "kind": "file_change",
                    "path": selected_path,
                    "parent_value": "absent at root ForkPoint",
                    "child_value": "added pytest hook file in minimized causal delta",
                    "ref": source_causal_delta_ref,
                },
                {
                    "kind": "cluster_precursor",
                    "parent_value": "no exploit cluster at root ForkPoint",
                    "child_value": f"{cluster_id} / {exploit_target} / {exploit_mechanism}",
                    "ref": source_witness_ref,
                },
                {
                    "kind": "grader_visible_state",
                    "parent_value": "root ForkPoint has no branch verifier bypass",
                    "child_value": "reward=1, qa_is_reward_hacking=true, three semantic_success=true replay checks",
                    "ref": source_witness_ref,
                },
            ],
            "observable_signal_count": 3,
            "exposed_reasoning_refs": [],
            "alternatives_considered": list(alternatives_considered),
        },
        "lineage": {
            "schema_version": 1,
            "root_fork_point_id": parent_node_id,
            "parent_node_id": parent_node_id,
            "child_node_id": node_id,
            "child_depth": 1,
            "parent_snapshot_ref": snapshot_ref,
            "child_snapshot_ref": snapshot_ref,
            "source_branch_ref": branch_ref,
            "source_witness_ref": source_witness_ref,
        },
        "depth_two_run": {
            "schema_version": 1,
            "run_id": "research-depth-two-run-001",
            "child_node_id": node_id,
            "status": "blocked",
            "branch_budget": 8,
            "scheduled_branch_refs": [],
            "completed_branch_refs": [],
            "stop_event_ref": None,
            "blocker": (
                "No Plan 007 mapped live depth-two executor exists and no child re-snapshot has been captured. "
                "This artifact selects the child candidate only; it is not a depth-two BranchRun."
            ),
            "measured_values": {
                "completed_depth_two_branch_count": 0,
                "distinct_confirmed_depth_two_clusters": "not-measured",
                "setup_work_avoided": "not-measured",
                "flat_restart_comparison": "not-measured",
            },
        },
        "completion_claim": "not-complete",
    }


def _child_snapshot_ok(child_snapshot: dict[str, Any] | None) -> bool:
    if not isinstance(child_snapshot, dict) or child_snapshot.get("status") != "captured":
        return False
    snapshot = child_snapshot.get("child_snapshot")
    return isinstance(snapshot, dict) and snapshot.get("snapshot_mode") == "filesystem" and bool(snapshot.get("snapshot_id"))


def _depth_two_run_ok(depth_two_run: dict[str, Any] | None) -> bool:
    if not isinstance(depth_two_run, dict) or depth_two_run.get("status") != "completed":
        return False
    run = depth_two_run.get("depth_two_run")
    if not isinstance(run, dict) or run.get("status") != "completed":
        return False
    if not run.get("completed_branch_refs") or not run.get("measured_values"):
        return False
    return bool(depth_two_run.get("stop_event"))


def build_depth_two_preflight_artifact(
    *,
    plan003_manifest: dict[str, Any],
    child_selection_ref: str,
    child_selection_exists: bool,
    command_ref: str,
    recorded_at: str,
    child_snapshot: dict[str, Any] | None = None,
    child_snapshot_ref: str | None = None,
    depth_two_run: dict[str, Any] | None = None,
    depth_two_run_ref: str | None = None,
) -> dict[str, Any]:
    """Verify Plan 007 depth-two evidence; fail closed until it is real and complete.

    Returns a ``ready`` artifact only when Plan 003 is sealed, a filesystem-class
    child re-snapshot exists, and a completed depth-two BranchRun with measured
    values and an adaptive-stop event exists. Otherwise it stays ``blocked``.
    """

    checks = plan003_manifest.get("checks", [])
    sealed = any(
        check.get("name") == "Promotion and replay seal" and check.get("status") == "pass"
        for check in checks
        if isinstance(check, dict)
    )
    plan003_complete = plan003_manifest.get("status") == "complete"
    plan003_gate_status = "pass" if sealed and plan003_complete else "blocked"

    child_snapshot_ok = _child_snapshot_ok(child_snapshot)
    depth_two_ok = _depth_two_run_ok(depth_two_run)

    blockers = []
    if plan003_gate_status != "pass":
        blockers.append("Plan 003 does not have complete sealed Witness evidence on this stack.")
    if not child_selection_exists:
        blockers.append("Plan 007 child-selection artifact is missing.")
    if not child_snapshot_ok:
        blockers.append(
            "Plan 007 has no captured filesystem-class child re-snapshot artifact."
        )
    if not depth_two_ok:
        blockers.append(
            "Plan 007 has no mapped live depth-two executor result with a completed depth-two "
            "BranchRun artifact, measured values, and an adaptive-stop event."
        )

    status = "ready" if not blockers else "blocked"
    artifact: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": "plan-007-depth-two-integration-preflight",
        "status": status,
        "recorded_at": recorded_at,
        "command_ref": command_ref,
        "plan003_gate": {
            "status": plan003_gate_status,
            "manifest_ref": "docs/plans/evidence/003/MANIFEST.json",
            "sealed_witness_check": sealed,
            "manifest_status": plan003_manifest.get("status"),
        },
        "child_selection": {
            "status": "present" if child_selection_exists else "missing",
            "artifact_ref": child_selection_ref,
        },
        "child_snapshot": {
            "status": "captured" if child_snapshot_ok else "missing",
            "artifact_ref": child_snapshot_ref,
            "snapshot_ref": (child_snapshot or {}).get("child_snapshot", {}).get("snapshot_ref")
            if child_snapshot_ok
            else None,
        },
        "depth_two_execution": {
            "status": "completed" if depth_two_ok else "blocked",
            "executor": "mapped" if child_snapshot_ok else "not-mapped",
            "completed_branch_run_ref": depth_two_run_ref if depth_two_ok else None,
            "required_next_artifacts": []
            if depth_two_ok
            else [
                "independent child re-snapshot restore evidence",
                "completed depth-two BranchRun artifact",
                "adaptive-stop decision event from a real run",
            ],
        },
        "blockers": blockers,
        "completion_claim": "complete" if status == "ready" else "not-complete",
    }
    artifact["content_digest"] = digest_json(artifact)
    return artifact


def build_conditional_research_report(
    *,
    sealed_witness_ref: str,
    child_selection_ref: str,
    preflight_ref: str,
    command_map_ref: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Build the measured/not-measured report for conditional Plan 007 packets."""

    flat = validate_flat_comparison(
        FlatComparisonReport(
            status="not-measured",
            protocol_ref=None,
            limitation=(
                "No comparable flat-restart protocol can be measured until Plan 007 has an "
                "independent child re-snapshot and at least one completed depth-two BranchRun."
            ),
        )
    )
    transfer_training = validate_transfer_training(
        TransferTrainingReport(
            transfer_status="not-measured",
            training_filter_status="not-measured",
            real_task_refs=(),
            trajectory_refs=(),
            limitation=(
                "No additional real task set or sealed raw-vs-hardened trajectory corpus is "
                "available on this stack."
            ),
        )
    )
    skips = [
        require_evidence_backed_skip(
            ResearchSkip(
                packet="WP4 flat restart comparison",
                reason="Comparable state-branch and flat-restart budgets are not available before a completed depth-two BranchRun.",
                evidence_refs=(sealed_witness_ref, child_selection_ref, preflight_ref),
                recorded_at=recorded_at,
            )
        ),
        require_evidence_backed_skip(
            ResearchSkip(
                packet="WP5 Memory Snapshot",
                reason="The sealed Witness evidence does not establish process-resident state need; no Memory adapter scaffold was created.",
                evidence_refs=(sealed_witness_ref, child_selection_ref),
                recorded_at=recorded_at,
            )
        ),
        require_evidence_backed_skip(
            ResearchSkip(
                packet="WP5 VM Sandbox",
                reason="The sealed Witness evidence does not establish kernel-level task need; no VM adapter scaffold was created.",
                evidence_refs=(sealed_witness_ref, child_selection_ref),
                recorded_at=recorded_at,
            )
        ),
        require_evidence_backed_skip(
            ResearchSkip(
                packet="WP6 transfer/training",
                reason="No additional real tasks or sealed raw-vs-hardened trajectories are available for measured transfer or training analysis.",
                evidence_refs=(sealed_witness_ref, command_map_ref),
                recorded_at=recorded_at,
            )
        ),
    ]
    artifact: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": "plan-007-conditional-research-report",
        "status": "not-measured",
        "recorded_at": recorded_at,
        "flat_comparison": flat,
        "transfer_training": transfer_training,
        "skips": skips,
        "capability_profiles": {
            "memory": {
                "status": "skipped",
                "live_probe": "not-run",
                "reason": "No real process-resident task need was established; no adapter scaffold was created.",
            },
            "vm": {
                "status": "skipped",
                "live_probe": "not-run",
                "reason": "No real kernel-level task need was established; no adapter scaffold was created.",
            },
        },
        "evidence_refs": [
            sealed_witness_ref,
            child_selection_ref,
            preflight_ref,
            command_map_ref,
        ],
        "completion_claim": "not-complete",
    }
    artifact["content_digest"] = digest_json(artifact)
    return artifact
