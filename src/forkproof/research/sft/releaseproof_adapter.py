"""Compatibility wrapper for shared ReleaseProof indexing."""

from forkproof.research.canonical.releaseproof import (
    ReleaseCaseResult,
    ReleaseGateIndex,
    build_release_gate_index,
)

__all__ = ["ReleaseCaseResult", "ReleaseGateIndex", "build_release_gate_index"]
