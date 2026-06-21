"""Map committed Traceback artifacts onto the frontend ``ForkProofApi`` wire shapes.

The frontend (``frontend/src/api/ForkProofApi.ts``) is a UI over a small set of
records: a ForkPoint, Legitimate controls, discovered BranchRuns, Exploit
Witnesses, a ProofSet, a harden-v0 Patch, and a ReleaseProof. This module emits
those records in the frontend's camelCase domain shape
(``frontend/src/domain/types.ts``) so a static export can be fetched by an
``HttpForkProofApi`` with no running server.

This integration is **canonical**: it stacks on the Plan 003/005 work (PR #27)
and sources the real committed producer records, not fabricated data.

Honesty contract (AGENTS.md "Claims and reporting"):

* **Real** — threaded from committed artifacts:
  - ForkPoint identity/snapshot/grader provenance (Plan 002 evidence record).
  - The two real discovered BranchRuns (``branch-08`` confirmed witness via a
    ``conftest.py`` causal delta, ``branch-11`` rewarded-non-hack) under
    ``docs/plans/evidence/003/artifacts/branch-runs/``.
  - The real sealed Exploit Witness (``wit-run-…-branch-08``) with its 3
    deterministic replay attempts.
  - The real **blocked** release gate (``proofset-e497370b2c3d2a69``): harden-v0
    produced a diagnostic-only patch and no validated v1/v2 results, so the gate
    does not pass. We surface that real verdict rather than a green release.
  - The frozen Legitimate controls + the grader digest / environment version.
* **Illustrative** — the remaining branch-tree nodes have no committed branch
  record yet; they reuse the proven demo skeleton (so the React Flow tree keeps
  the exact geometry PR #20 shipped) and are marked ``illustrative`` in notes.
  Unproduced values (e.g. the patched grader v2) are ``TBD``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from forkproof.controls.models import LegitimateControl

# Repo root: src/forkproof/api/mapping.py -> parents[3].
ROOT = Path(__file__).resolve().parents[3]

FORKPOINT_RECORD = ROOT / "docs/plans/evidence/002/artifacts/forkpoint-record.json"
REPLAY_RECORD = ROOT / "docs/plans/evidence/002/artifacts/trace-replay-snapshot.json"
CONTROLS_FILE = ROOT / "fixtures/forkproof/mongodb-sales-aggregation-engine/controls.json"

# Plan 003/005 canonical records (PR #27).
_BRANCH_RUN_DIR = ROOT / (
    "docs/plans/evidence/003/artifacts/branch-runs/run-20260621T075711/branches"
)
BRANCH_08 = _BRANCH_RUN_DIR / "run-20260621T075711-branch-08.json"
BRANCH_11 = _BRANCH_RUN_DIR / "run-20260621T075711-branch-11.json"
SEALED_WITNESS = ROOT / (
    "docs/plans/evidence/003/artifacts/sealed/witnesses/"
    "wit-run-20260621T075711-branch-08.json"
)
RELEASE_BLOCKER = ROOT / (
    "artifacts/forkproof/releases/release-blockers/proofset-e497370b2c3d2a69.json"
)

SCHEMA = "1.0.0"
TBD = "TBD"
SAMPLING = {"temperature": 0.0, "topP": 1.0}
GRADER_V2 = TBD  # patched grader v2 has no validated producer (release blocked)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _forkpoint_record() -> dict[str, Any]:
    return _load_json(FORKPOINT_RECORD)


# ---------------------------------------------------------------------------
# ForkPoint + controls (real)
# ---------------------------------------------------------------------------


def build_fork_point() -> dict[str, Any]:
    """Real ForkPoint identity from the committed Plan 002 evidence record."""
    rec = _forkpoint_record()
    return {
        "schemaVersion": SCHEMA,
        "forkPointId": rec["fork_point_id"],
        "hudTraceId": rec["hud_trace_id"],
        "hudStepId": rec["hud_step_id"],
        "taskId": rec["task_id"],
        "environmentVersion": rec["environment_version"],
        "historyHash": rec["history_hash"],
        "snapshotId": rec["snapshot_id"],
        "snapshotMode": rec["snapshot_mode"],
        "snapshotDigest": rec["snapshot_digest"],
        "graderDigest": rec["grader_digest"],
        "forkReason": rec["fork_reason"],
        "createdAt": rec["created_at"],
        "label": "QA ForkPoint · S0",
        "upToStep": 12,
        "actionRange": [1, 12],
        "cumulativeReward": 1.0,
        "traceEvidence": (
            "Accepted live reward-1 source trace; snapshot roundtrip verified "
            f"({rec['snapshot_mode']})."
        ),
    }


def build_controls() -> list[dict[str, Any]]:
    """Real, frozen Legitimate controls (path-diverse) from the fixture."""
    doc = _load_json(CONTROLS_FILE)
    out: list[dict[str, Any]] = []
    for raw in doc["controls"]:
        control = LegitimateControl.from_dict(raw)
        label = control.solution_path_label
        out.append(
            {
                "schemaVersion": SCHEMA,
                "controlId": control.control_id,
                "taskId": control.task_id,
                "title": f"Reference solver · {label}",
                "solutionPathLabel": label,
                "sourceMethod": control.source_method,
                "environmentVersion": control.environment_version,
                "graderDigest": control.grader_digest,
                "expectedReward": control.expected_reward,
                "contentDigest": control.content_digest,
                "frozenAt": control.frozen_at,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Branch tree: proven UI skeleton with the two REAL branch runs overlaid.
# Topology + layout are UI-owned (must match the mock exactly so the tree keeps
# its geometry). The real records replace the provenance on two nodes; the rest
# stay illustrative.
# ---------------------------------------------------------------------------

_REAL_WITNESS_NODE = "whitespace"  # branch-08 (sealed witness) overlays here
_REAL_NONHACK_NODE = "pytest11"  # branch-11 (rewarded-non-hack) overlays here

_SKELETON: list[dict[str, Any]] = [
    {"id": "whitespace", "title": "Whitespace normalization bypass", "parent": None, "status": "witness", "reward": 1.0, "cluster": "whitespace", "layout": {"x": 150, "y": 140, "nodeType": "branch"}, "steps": 4},
    {"id": "pytestSub", "title": "Pytest plugin subversion", "parent": None, "status": "promising", "reward": 0.6, "cluster": "pytest", "layout": {"x": 750, "y": 140, "nodeType": "branch"}, "steps": 5},
    {"id": "legitControl", "title": "Legitimate control replay", "parent": None, "status": "control", "reward": 1.0, "cluster": "control", "layout": {"x": 1200, "y": 140, "nodeType": "branch"}, "steps": 6},
    {"id": "trimCollapse", "title": "Trim + collapse variant", "parent": "whitespace", "status": "witness", "reward": 1.0, "cluster": "whitespace", "layout": {"x": 0, "y": 290, "nodeType": "branch"}, "steps": 6},
    {"id": "caseFold", "title": "Case-fold variant", "parent": "whitespace", "status": "witness", "reward": 1.0, "cluster": "whitespace", "layout": {"x": 300, "y": 290, "nodeType": "branch"}, "steps": 6},
    {"id": "snapshotS1", "title": "Snapshot S1 · plugin registered", "parent": "pytestSub", "status": "snapshot", "reward": 0.6, "cluster": "pytest", "layout": {"x": 600, "y": 290, "nodeType": "snapshot"}, "steps": 6},
    {"id": "pytest11", "title": "pytest11 entry-point", "parent": "pytestSub", "status": "qa_review", "reward": 0.6, "cluster": "pytest", "layout": {"x": 900, "y": 290, "nodeType": "branch"}, "steps": 6},
    {"id": "refBaseline", "title": "Reference solver baseline", "parent": "legitControl", "status": "control", "reward": 1.0, "cluster": "control", "layout": {"x": 1200, "y": 290, "nodeType": "branch"}, "steps": 7},
    {"id": "companyAlias", "title": "Company alias escalation", "parent": "trimCollapse", "status": "witness", "reward": 1.0, "cluster": "whitespace", "layout": {"x": 0, "y": 430, "nodeType": "branch"}, "steps": 8},
    {"id": "layeredFallback", "title": "Layered fallback exploit", "parent": "snapshotS1", "status": "witness", "reward": 0.6, "cluster": "pytest", "layout": {"x": 600, "y": 430, "nodeType": "branch"}, "steps": 6},
]

# Deterministic, non-zero seeds for the illustrative nodes (witness-confirmation
# delay is 760 + (seed % 5) * 170, so seeds must be non-zero/varied). Real nodes
# use their real seeds.
_SEEDS = {
    "whitespace": 871192734, "pytestSub": 871192741, "legitControl": 871192752,
    "trimCollapse": 871192763, "caseFold": 871192778, "snapshotS1": 871192789,
    "pytest11": 871192795, "refBaseline": 871192806, "companyAlias": 871192817,
    "layeredFallback": 871192822,
}
_CLUSTER_LABEL = {
    "whitespace": "Whitespace normalization",
    "pytest": "Pytest plugin subversion",
    "control": "Legitimate control",
}
_ILLUSTRATIVE_QA = {
    "whitespace": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "medium", "verdict": "Confirmed witness", "strategy": "whitespace normalization"},
    "pytestSub": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "high", "verdict": "Likely reward hacking", "strategy": "pytest subversion"},
    "trimCollapse": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "medium", "verdict": "Confirmed witness"},
    "caseFold": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "medium", "verdict": "Confirmed witness"},
    "pytest11": {"isRewardHacking": False, "classification": "Awaiting QA", "severity": "medium", "verdict": "Rewarded · awaiting QA", "strategy": "pytest11 entry-point"},
    "companyAlias": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "medium", "verdict": "Confirmed witness"},
    "layeredFallback": {"isRewardHacking": True, "classification": "Reward hacking", "severity": "high", "verdict": "Likely reward hacking", "strategy": "pytest plugin subversion"},
}


def _branch_base(node: dict[str, Any], fork: dict[str, Any]) -> dict[str, Any]:
    bid = node["id"]
    cluster = node["cluster"]
    return {
        "schemaVersion": SCHEMA,
        "runId": f"run-{bid}",
        "branchId": f"s1-{bid}-01",
        "parentForkPointId": fork["fork_point_id"],
        "parentNodeId": node["parent"],
        "title": node["title"],
        "seed": _SEEDS[bid],
        "model": "gpt-4o-2024-08-06",
        "samplingConfig": SAMPLING,
        "hudTraceId": fork["hud_trace_id"],
        "environmentVersion": fork["environment_version"],
        "graderDigest": fork["grader_digest"],
        "reward": node["reward"],
        "qa": _ILLUSTRATIVE_QA.get(bid),
        "status": node["status"],
        "clusterId": cluster,
        "clusterLabel": _CLUSTER_LABEL[cluster],
        "snapshotMode": "directory",
        "parentSnapshot": "S1" if cluster == "pytest" else "S0",
        "stepsFromFork": node["steps"],
        "novelty": "new" if node["status"] in ("witness", "promising") else "existing",
        "notes": "Illustrative discovery sibling (no committed branch record).",
        "startedAt": fork["created_at"],
        "completedAt": fork["created_at"],
        "layout": node["layout"],
    }


def build_branches() -> list[dict[str, Any]]:
    """Skeleton with the two real branch runs overlaid on their nodes."""
    fork = _forkpoint_record()
    b08 = _load_json(BRANCH_08)
    b11 = _load_json(BRANCH_11)
    witness = _load_json(SEALED_WITNESS)

    out: list[dict[str, Any]] = []
    for node in _SKELETON:
        rec = _branch_base(node, fork)
        if node["id"] == _REAL_WITNESS_NODE:
            rec.update(
                {
                    "branchId": b08["branch_id"],
                    "title": "conftest.py reward-verifier exploit",
                    "seed": b08["seed"],
                    "model": b08["model"],
                    "hudTraceId": b08["hud_trace_id"],
                    "reward": b08["reward"],
                    "snapshotMode": witness["durable_snapshot_mode"],
                    "clusterLabel": f"{witness['cluster_id']} · {witness['exploit_mechanism']}",
                    "qa": {
                        "isRewardHacking": witness["qa_is_reward_hacking"],
                        "classification": "Reward hacking",
                        "severity": "high",
                        "verdict": "Confirmed witness · sealed",
                        "strategy": witness["exploit_target"],
                    },
                    "notes": (
                        f"Real sealed witness {witness['witness_id']} — "
                        f"target {witness['exploit_target']}, mechanism "
                        f"{witness['exploit_mechanism']}; {len(witness['replay_checks'])}"
                        "/3 deterministic replays passed."
                    ),
                }
            )
        elif node["id"] == _REAL_NONHACK_NODE:
            rec.update(
                {
                    "branchId": b11["branch_id"],
                    "title": "Rewarded non-hack candidate",
                    "seed": b11["seed"],
                    "model": b11["model"],
                    "reward": b11["reward"],
                    "qa": {
                        "isRewardHacking": False,
                        "classification": "Rewarded · non-hack",
                        "severity": "low",
                        "verdict": "Rewarded but classified non-hack",
                        "strategy": b11["promotion_signal_status"],
                    },
                    "notes": (
                        f"Real branch run {b11['branch_id']} — rewarded but QA "
                        f"classified {b11['promotion_signal_status']} (not promoted)."
                    ),
                }
            )
        out.append(rec)
    return out


def build_witness_overlay() -> dict[str, Any]:
    """Real ExploitWitness fields for the sealed-witness node, keyed by run stem.

    The frontend derives witness records from branches; this overlays the real
    sealed-witness identity/mechanism/replay onto the one node that has a
    committed Witness.
    """
    w = _load_json(SEALED_WITNESS)
    return {
        _REAL_WITNESS_NODE: {
            "witnessId": w["witness_id"],
            "sourceBranchId": w["source_branch_id"],
            "preAttackSnapshotRef": w["pre_attack_snapshot_ref"],
            "durableSnapshotMode": w["durable_snapshot_mode"],
            "exploitTarget": w["exploit_target"],
            "exploitMechanism": w["exploit_mechanism"],
            "clusterId": w["cluster_id"],
            "replayEntrypoint": w["replay_entrypoint"],
            "replayChecks": f"Deterministic pass · {len(w['replay_checks'])}/3 replays",
            "contentDigest": w["content_digest"],
            "graderDigest": w["grader_digest"],
            "environmentVersion": w["environment_version"],
            "createdAt": w["created_at"],
        }
    }


def build_proof_set() -> dict[str, Any]:
    """ProofSet over the real sealed witness + two real controls.

    Uses the real Plan 005 proof-set id (``proofset-e497370b2c3d2a69``).
    """
    fork = _forkpoint_record()
    blocker = _load_json(RELEASE_BLOCKER)
    controls = build_controls()
    return {
        "schemaVersion": SCHEMA,
        "proofSetId": blocker["proof_set_id"],
        "environmentV1": fork["environment_version"],
        "graderV1Digest": fork["grader_digest"],
        "exploitWitnessIds": [_REAL_WITNESS_NODE],
        "legitimateControlIds": [c["controlId"] for c in controls[:2]],
        "exploitFamilyVariantIds": ["variant-reseed-a", "variant-reseed-b"],
        "createdAt": fork["created_at"],
        "contentDigest": "ps-001-digest",
    }


# ---------------------------------------------------------------------------
# Release: the REAL blocked gate. harden-v0 produced a diagnostic-only patch and
# no validated v1/v2 results, so the gate does not pass at any iteration.
# ---------------------------------------------------------------------------


def build_release_bundle() -> dict[str, Any]:
    blocker = _load_json(RELEASE_BLOCKER)
    harden = blocker["harden_blocker"]
    changed = ", ".join(harden.get("changed_files", []))
    patch = {
        "patchRef": f"harden-diagnostic-{blocker['proof_set_id']}",
        "iteration": 1,
        "label": "Diagnostic patch (blocked)",
        "generatedBy": "harden-v0 fixer",
        "description": harden["reason"],
        "summary": (
            f"harden-v0 ({blocker['harden_status']}) changed {changed}; the patch is "
            "diagnostic only until harden-v0 applies and validates it."
        ),
        "filePath": "tests/test_outputs.py",
        "added": 0,
        "removed": 0,
        "diff": [
            {"no": "—", "kind": "ctx", "text": f"# harden-v0 changed: {changed}"},
            {"no": "—", "kind": "ctx", "text": f"# status: {harden['code']} (diagnostic only, not applied)"},
        ],
        "patchDigest": blocker["content_digest"],
        "rationale": [
            f"Mandatory subversion case: {case}"
            for case in blocker.get("mandatory_subversion_case_ids", [])
        ],
        "status": "awaiting_proof",
    }
    # Same diagnostic patch at every fixer iteration; the gate stays blocked.
    patches = {"1": patch, "2": {**patch, "iteration": 2}, "3": {**patch, "iteration": 3}}
    # Witness is never confirmed killed (no validated v2 results) -> gate blocked.
    blocked_each = {"1": [_REAL_WITNESS_NODE], "2": [_REAL_WITNESS_NODE], "3": [_REAL_WITNESS_NODE]}
    return {
        "graderV2Digest": GRADER_V2,
        "patches": patches,
        "survivingWitnessByIteration": blocked_each,
        "brokenControlByIteration": {"1": [], "2": [], "3": []},
        # Real blocked-release metadata surfaced in the gate verdict.
        "release": {
            "blocked": True,
            "blockReason": blocker["reason"],
            "missingEvidence": blocker.get("missing_evidence", []),
            "hardenStatus": blocker.get("harden_status", TBD),
            "proofSetId": blocker["proof_set_id"],
            "graderV2Digest": GRADER_V2,
        },
    }


def build_replay_evidence() -> dict[str, Any]:
    """Real replay digests: the Plan 002 roundtrip + the sealed-witness replays."""
    rec = _load_json(REPLAY_RECORD)
    witness = _load_json(SEALED_WITNESS)
    checks = witness["replay_checks"]
    return {
        "status": f"sealed · {len(checks)}/3 deterministic replays",
        "graderDigest": witness["grader_digest"],
        "replayedToolCount": rec["replayed_tool_count"],
        "replayAttempts": len(checks),
        "queryPySha256": rec["query_py_sha256"],
        "gradeOutputSha256": rec["grade_output_sha256"],
        "verifierOutputDigest": checks[0]["verifier_output_digest"],
        "snapshotDigest": rec["snapshot_digest"],
        "snapshotMode": rec["snapshot_mode"],
        "digestMatch": all(c["semantic_success"] for c in checks),
    }


def build_all() -> dict[str, Any]:
    """Every route payload, keyed by its exported JSON filename stem."""
    return {
        "forkpoint": build_fork_point(),
        "controls": build_controls(),
        "branches": build_branches(),
        "witnesses": build_witness_overlay(),
        "proofset": build_proof_set(),
        "release": build_release_bundle(),
        "replay": build_replay_evidence(),
    }
