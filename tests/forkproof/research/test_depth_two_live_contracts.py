"""Plan 007 depth-two contracts: fail-closed gates and real-artifact validation.

The fail-closed and builder tests always run. The committed-artifact tests skip
until a live run has produced the child snapshot and completed depth-two run
artifacts, then validate those real artifacts through the public contracts.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from forkproof.research.depth_two import build_child_forkpoint, run_depth_two
from forkproof.research.models import DepthTwoRunRecord
from forkproof.research.resnapshot import (
    ResnapshotError,
    build_child_snapshot_artifact,
    capture_child_snapshot,
)
from forkproof.witnesses.branch_task_profile import hud_task_profile

ROOT = Path(__file__).resolve().parents[3]
SEALED_WITNESS = ROOT / "docs/plans/evidence/003/artifacts/sealed/witnesses/wit-run-20260621T075711-branch-08.json"
SEALED_CAUSAL_DELTA = ROOT / "docs/plans/evidence/003/artifacts/sealed/causal-deltas/run-20260621T075711-branch-08.json"
PARENT_FORKPOINT = ROOT / "docs/plans/evidence/002/artifacts/forkpoint-record.json"
CHILD_SNAPSHOT_ARTIFACT = ROOT / "artifacts/forkproof/research/depth-two-child-snapshot.json"
DEPTH_TWO_RUN_ARTIFACT = ROOT / "artifacts/forkproof/research/depth-two-run.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _witness() -> dict:
    return _load(SEALED_WITNESS)


def _causal_delta() -> dict:
    return _load(SEALED_CAUSAL_DELTA)


def _good_verification(causal_delta: dict) -> dict:
    verification = {}
    for path, text in (causal_delta.get("added_text") or {}).items():
        verification[path] = {
            "status": "present",
            "sha256": hashlib.sha256(str(text).encode("utf-8")).hexdigest(),
            "size": len(str(text).encode("utf-8")),
        }
    return verification


def _build_valid_child_snapshot(child_snapshot_id: str = "im-CHILDTEST0000000000000000"):
    causal_delta = _causal_delta()
    return build_child_snapshot_artifact(
        witness=_witness(),
        causal_delta=causal_delta,
        source_witness_ref="docs/plans/evidence/003/artifacts/sealed/witnesses/wit-run-20260621T075711-branch-08.json",
        source_causal_delta_ref="docs/plans/evidence/003/artifacts/sealed/causal-deltas/run-20260621T075711-branch-08.json",
        child_snapshot_id=child_snapshot_id,
        runtime_identity={"provider": "modal", "base_image_id": "im-01KVKYBWZYVZSD79CX5P9SNPXR"},
        applied_delta_verification=_good_verification(causal_delta),
        recorded_at="2026-06-21T16:00:00Z",
    )


def test_child_snapshot_artifact_records_filesystem_lineage_from_sealed_witness():
    artifact = _build_valid_child_snapshot()

    assert artifact["status"] == "captured"
    assert artifact["child_snapshot"]["snapshot_mode"] == "filesystem"
    assert artifact["child_snapshot"]["snapshot_ref"] == "modal-image://im-CHILDTEST0000000000000000"
    assert artifact["child_snapshot"]["source_pre_attack_snapshot_ref"] == "modal-image://im-01KVKYBWZYVZSD79CX5P9SNPXR"
    lineage = artifact["lineage"]
    assert lineage["child_depth"] == 1
    assert lineage["parent_snapshot_ref"] == "modal-image://im-01KVKYBWZYVZSD79CX5P9SNPXR"
    assert lineage["child_snapshot_ref"] == "modal-image://im-CHILDTEST0000000000000000"
    assert artifact["completion_claim"] == "child-snapshot-captured"
    assert artifact["content_digest"]


def test_child_snapshot_artifact_requires_filesystem_durable_snapshot():
    witness = _witness()
    witness["durable_snapshot_mode"] = "memory"
    with pytest.raises(ResnapshotError):
        build_child_snapshot_artifact(
            witness=witness,
            causal_delta=_causal_delta(),
            source_witness_ref="w",
            source_causal_delta_ref="d",
            child_snapshot_id="im-CHILD",
            runtime_identity={},
            applied_delta_verification=_good_verification(_causal_delta()),
            recorded_at="2026-06-21T16:00:00Z",
        )


def test_child_snapshot_artifact_requires_grader_identity():
    witness = _witness()
    witness.pop("grader_digest", None)
    with pytest.raises(ResnapshotError):
        build_child_snapshot_artifact(
            witness=witness,
            causal_delta=_causal_delta(),
            source_witness_ref="w",
            source_causal_delta_ref="d",
            child_snapshot_id="im-CHILD",
            runtime_identity={},
            applied_delta_verification=_good_verification(_causal_delta()),
            recorded_at="2026-06-21T16:00:00Z",
        )


def test_child_snapshot_artifact_requires_verified_applied_delta():
    causal_delta = _causal_delta()
    bad_verification = {path: {"status": "present", "sha256": "deadbeef"} for path in causal_delta["included_paths"]}
    with pytest.raises(ResnapshotError):
        build_child_snapshot_artifact(
            witness=_witness(),
            causal_delta=causal_delta,
            source_witness_ref="w",
            source_causal_delta_ref="d",
            child_snapshot_id="im-CHILD",
            runtime_identity={},
            applied_delta_verification=bad_verification,
            recorded_at="2026-06-21T16:00:00Z",
        )


def test_capture_child_snapshot_fails_closed_without_credentials(monkeypatch):
    monkeypatch.setattr(
        "forkproof.research.resnapshot.credential_presence",
        lambda names: {name: "absent" for name in names},
    )
    result = capture_child_snapshot(
        root=ROOT,
        witness=_witness(),
        causal_delta=_causal_delta(),
        source_witness_ref="w",
        source_causal_delta_ref="d",
    )
    assert result["status"] == "blocked"
    assert result["completion_claim"] == "not-complete"
    assert "child_snapshot" not in result


def test_build_child_forkpoint_mirrors_parent_and_swaps_snapshot():
    parent = _load(PARENT_FORKPOINT)
    child_snapshot = {"snapshot_id": "im-CHILD", "child_node_id": "node-x", "snapshot_mode": "filesystem"}

    forkpoint = build_child_forkpoint(
        parent_forkpoint=parent, child_snapshot=child_snapshot, child_node_id="node-x"
    )

    assert forkpoint["snapshot_id"] == "im-CHILD"
    assert forkpoint["snapshot_restore_ref"] == "modal-image://im-CHILD"
    assert forkpoint["snapshot_mode"] == "filesystem"
    assert forkpoint["node_id"] == "node-x"
    assert forkpoint["parent_node_id"] == "node-x"
    # grader and environment identity are preserved verbatim from the accepted ForkPoint.
    assert forkpoint["grader_digest"] == parent["grader_digest"]
    assert forkpoint["environment_version"] == parent["environment_version"]
    # The mirrored forkpoint is executable by the proven task loader.
    profile = hud_task_profile(forkpoint)
    assert profile["trusted_entrypoint_ref"] == "env:env"
    assert profile["task_factory"] == "implement_sales_analyzer"


def test_run_depth_two_fails_closed_without_external_qa_approval(monkeypatch):
    monkeypatch.setattr(
        "forkproof.research.depth_two.credential_presence",
        lambda names: {name: "present" for name in names},
    )
    monkeypatch.delenv("FORKPROOF_ALLOW_EXTERNAL_QA", raising=False)
    child_snapshot_artifact = {
        "status": "captured",
        "lineage": {"child_depth": 1},
        "child_snapshot": {
            "child_node_id": "node-run-20260621T075711-branch-08",
            "snapshot_id": "im-CHILD",
            "snapshot_ref": "modal-image://im-CHILD",
            "snapshot_mode": "filesystem",
        },
    }

    result = asyncio.run(
        run_depth_two(
            root=ROOT,
            child_snapshot_artifact=child_snapshot_artifact,
            child_snapshot_artifact_ref="artifacts/forkproof/research/depth-two-child-snapshot.json",
            branch_budget=8,
        )
    )

    assert result["status"] == "blocked"
    assert result["depth_two_run"]["status"] == "blocked"
    assert "external QA" in (result["depth_two_run"]["blocker"] or "")
    assert result["branch_results"] == []
    assert result["completion_claim"] == "not-complete"


# --- Real committed-artifact contracts (skip until the live run has produced them) ---


def test_committed_child_snapshot_artifact_is_durable_and_reprovable():
    if not CHILD_SNAPSHOT_ARTIFACT.exists():
        pytest.skip("child re-snapshot artifact not yet produced by a live run")
    artifact = _load(CHILD_SNAPSHOT_ARTIFACT)

    assert artifact["status"] == "captured"
    child = artifact["child_snapshot"]
    assert child["snapshot_mode"] == "filesystem"
    assert child["snapshot_ref"].startswith("modal-image://")
    assert child["grader_digest"]
    assert artifact["lineage"]["child_depth"] == 1

    # The committed provenance still passes the fail-closed builder gate.
    reproven = build_child_snapshot_artifact(
        witness=_witness(),
        causal_delta=_causal_delta(),
        source_witness_ref=artifact["source_witness_ref"],
        source_causal_delta_ref=artifact["source_causal_delta_ref"],
        child_snapshot_id=child["snapshot_id"],
        runtime_identity=artifact["runtime_identity"],
        applied_delta_verification=child["applied_delta_verification"],
        recorded_at=artifact["recorded_at"],
    )
    assert reproven["child_snapshot"]["snapshot_ref"] == child["snapshot_ref"]
    assert reproven["lineage"] == artifact["lineage"]


def test_committed_depth_two_run_is_completed_with_measured_values_and_stop_event():
    if not DEPTH_TWO_RUN_ARTIFACT.exists():
        pytest.skip("depth-two run artifact not yet produced by a live run")
    artifact = _load(DEPTH_TWO_RUN_ARTIFACT)

    assert artifact["status"] == "completed"
    run = artifact["depth_two_run"]
    assert run["status"] == "completed"
    assert run["completed_branch_refs"], "completed run must record completed branch refs"
    assert set(run["completed_branch_refs"]).issubset(set(run["scheduled_branch_refs"]))
    assert run["measured_values"], "completed run must record measured values"
    assert artifact["stop_event"], "a completed adaptive run records a real stop event"
    assert artifact["scheduler_decisions"], "a real run records scheduler decision events"

    # Branch sub-artifacts live under Plan 007-owned evidence, never Plan 003's.
    assert artifact["branch_artifact_root"].startswith("docs/plans/evidence/007/")

    # The committed run still satisfies the public depth-two record invariants.
    rebuilt = DepthTwoRunRecord(
        run_id=run["run_id"],
        child_node_id=run["child_node_id"],
        status="completed",
        branch_budget=run["branch_budget"],
        scheduled_branch_refs=tuple(run["scheduled_branch_refs"]),
        completed_branch_refs=tuple(run["completed_branch_refs"]),
        stop_event_ref=run["stop_event_ref"],
        measured_values=run["measured_values"],
        recorded_at=run["recorded_at"],
    ).to_record()
    assert rebuilt["status"] == "completed"
