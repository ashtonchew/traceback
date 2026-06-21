"""Plan 007 research artifact builders."""

from __future__ import annotations

from typing import Any

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


def build_depth_two_preflight_artifact(
    *,
    plan003_manifest: dict[str, Any],
    child_selection_ref: str,
    child_selection_exists: bool,
    command_ref: str,
    recorded_at: str,
) -> dict[str, Any]:
    """Build the fail-closed integration preflight record for Plan 007."""

    checks = plan003_manifest.get("checks", [])
    sealed = any(
        check.get("name") == "Promotion and replay seal" and check.get("status") == "pass"
        for check in checks
        if isinstance(check, dict)
    )
    plan003_complete = plan003_manifest.get("status") == "complete"
    plan003_gate_status = "pass" if sealed and plan003_complete else "blocked"
    blockers = []
    if plan003_gate_status != "pass":
        blockers.append(
            "Plan 003 does not have complete sealed Witness evidence on this stack."
        )
    if not child_selection_exists:
        blockers.append("Plan 007 child-selection artifact is missing.")
    blockers.append(
        "Plan 007 has no mapped live depth-two executor and no completed depth-two BranchRun artifact."
    )

    artifact: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": "plan-007-depth-two-integration-preflight",
        "status": "blocked",
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
        "depth_two_execution": {
            "status": "blocked",
            "executor": "not-mapped",
            "completed_branch_run_ref": None,
            "required_next_artifacts": [
                "independent child re-snapshot restore evidence",
                "completed depth-two BranchRun artifact",
                "adaptive-stop decision event from a real run",
            ],
        },
        "blockers": blockers,
        "completion_claim": "not-complete",
    }
    artifact["content_digest"] = digest_json(artifact)
    return artifact
