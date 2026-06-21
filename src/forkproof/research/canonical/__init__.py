"""Shared canonical ForkProof artifact loaders for research training paths."""

from forkproof.research.canonical.errors import CanonicalInputError
from forkproof.research.canonical.inputs import (
    LoadedArtifact,
    assert_manifest_lists_artifact,
    assert_manifest_complete,
    load_qabench_report,
    load_release_proof,
)
from forkproof.research.canonical.qabench import (
    QABenchTrajectory,
    iter_qabench_training_candidates,
)
from forkproof.research.canonical.releaseproof import (
    ReleaseCaseResult,
    ReleaseGateIndex,
    assert_qabench_reward_matches_release,
    build_release_gate_index,
)
from forkproof.research.canonical.types import RecordOrigin, RefereeVerdict

__all__ = [
    "CanonicalInputError",
    "LoadedArtifact",
    "QABenchTrajectory",
    "ReleaseCaseResult",
    "ReleaseGateIndex",
    "RecordOrigin",
    "RefereeVerdict",
    "assert_manifest_lists_artifact",
    "assert_manifest_complete",
    "assert_qabench_reward_matches_release",
    "build_release_gate_index",
    "iter_qabench_training_candidates",
    "load_qabench_report",
    "load_release_proof",
]
