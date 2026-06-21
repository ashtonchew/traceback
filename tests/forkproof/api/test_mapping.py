"""The mapped payloads carry real provenance and hold the frontend invariants.

These assert observable contract facts the frontend depends on: real digests
threaded from the committed artifacts, the React Flow layout invariants that
keep the tree from flashing/zooming, and honest ``TBD`` markers where no real
producer exists yet.
"""

from __future__ import annotations

import json
from pathlib import Path

from forkproof.api import mapping

VALID_STATUSES = {
    "pending", "running", "rewarded", "qa_review", "dead_end", "duplicate",
    "promising", "verifying", "witness", "control", "control_pass", "snapshot",
}
VALID_CLUSTERS = {"whitespace", "pytest", "control"}


def _raw(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# --- ForkPoint: real identity from the committed evidence record ------------


def test_forkpoint_threads_real_snapshot_and_grader_digests() -> None:
    record = _raw(mapping.FORKPOINT_RECORD)
    fp = mapping.build_fork_point()
    assert fp["snapshotDigest"] == record["snapshot_digest"]
    assert fp["graderDigest"] == record["grader_digest"]
    assert fp["forkPointId"] == record["fork_point_id"]
    assert fp["hudTraceId"] == record["hud_trace_id"]
    assert fp["snapshotMode"] == record["snapshot_mode"]
    # snapshotMode must be one of the frontend SnapshotMode union members.
    assert fp["snapshotMode"] in {"directory", "filesystem", "memory", "vm-filesystem"}


# --- Controls: real, frozen, path-diverse -----------------------------------


def test_controls_are_real_and_path_diverse() -> None:
    raw = _raw(mapping.CONTROLS_FILE)
    real_grader = raw["controls"][0]["grader_digest"]
    controls = mapping.build_controls()
    assert len(controls) == len(raw["controls"]) >= 3
    labels = {c["solutionPathLabel"] for c in controls}
    assert labels == {"path-a", "path-b", "path-c"}
    for c in controls:
        assert c["graderDigest"] == real_grader
        # real content digest is a 64-hex sha256, not a placeholder
        assert len(c["contentDigest"]) == 64


# --- Branches: layout invariants that keep the tree stable ------------------


def test_branches_hold_react_flow_layout_invariants() -> None:
    branches = mapping.build_branches()
    ids = {b["runId"].replace("run-", "") for b in branches}

    # Default selection target must exist (store defaults to 'layeredFallback').
    assert "layeredFallback" in ids

    for b in branches:
        bid = b["runId"].replace("run-", "")
        # runId === 'run-' + branchId-stem (store selectedBranch + buildGraph.shortId)
        assert b["runId"] == f"run-{bid}"
        # exact layout coordinates drive fit/centering; must be present integers
        assert isinstance(b["layout"]["x"], (int, float))
        assert isinstance(b["layout"]["y"], (int, float))
        assert b["status"] in VALID_STATUSES
        assert b["clusterId"] in VALID_CLUSTERS
        # non-zero seed (witness confirmation delay = 760 + (seed % 5) * 170)
        assert b["seed"] != 0
        # parentNodeId is null or references another branch stem
        parent = b["parentNodeId"]
        assert parent is None or parent in ids


def test_branches_thread_real_provenance() -> None:
    record = _raw(mapping.FORKPOINT_RECORD)
    branches = mapping.build_branches()
    for b in branches:
        assert b["graderDigest"] == record["grader_digest"]
        assert b["environmentVersion"] == record["environment_version"]
        assert b["parentForkPointId"] == record["fork_point_id"]
    # Control branches cite a real baseline run id.
    control_branches = [b for b in branches if b["status"] == "control"]
    assert control_branches
    assert any(b["notes"] and "baseline run" in b["notes"] for b in control_branches)


# --- ProofSet + release: ids line up, outcomes are the canonical demo -------


def test_proofset_references_present_controls() -> None:
    controls = {c["controlId"] for c in mapping.build_controls()}
    ps = mapping.build_proof_set()
    for cid in ps["legitimateControlIds"]:
        assert cid in controls
    # witness ids are branch stems that exist
    branch_ids = {b["runId"].replace("run-", "") for b in mapping.build_branches()}
    for wid in ps["exploitWitnessIds"]:
        assert wid in branch_ids


def test_release_bundle_gate_outcomes_resolve_a_pass_at_iteration_3() -> None:
    bundle = mapping.build_release_bundle()
    assert set(bundle["patches"]) == {"1", "2", "3"}
    # iteration 3 is the canonical pass: no surviving witness, no broken control
    assert bundle["survivingWitnessByIteration"]["3"] == []
    assert bundle["brokenControlByIteration"]["3"] == []
    # iteration-2 broken control id is a real control id
    controls = {c["controlId"] for c in mapping.build_controls()}
    assert bundle["brokenControlByIteration"]["2"][0] in controls


# --- Replay: real digests from the committed roundtrip ----------------------


def test_replay_evidence_is_real() -> None:
    rec = _raw(mapping.REPLAY_RECORD)
    replay = mapping.build_replay_evidence()
    assert replay["snapshotDigest"] == rec["snapshot_digest"]
    assert replay["replayedToolCount"] == rec["replayed_tool_count"]
    assert replay["digestMatch"] is True


# --- Honesty: unproduced values are explicitly TBD --------------------------


def test_unproduced_values_are_marked_tbd() -> None:
    bundle = mapping.build_release_bundle()
    # The patched grader v2 has no merged producer (Plan 005) -> TBD, not faked.
    assert bundle["graderV2Digest"] == "TBD"
    assert mapping.GRADER_V2 == "TBD"


def test_build_all_has_every_route() -> None:
    payloads = mapping.build_all()
    assert set(payloads) == {
        "forkpoint", "controls", "branches", "proofset", "release", "replay",
    }
