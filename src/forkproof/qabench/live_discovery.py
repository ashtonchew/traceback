"""Live in-loop discovery driver (Plan 008 WP6).

Wires the benchmark's ``DiscoveryDriver`` seam to Plan 003's real branch loop for a
materialized qabench env: it points ``branch_runs`` at the env (via the
``FORKPROOF_TASK_ENV`` / ``FORKPROOF_TASK_FACTORY`` / ``FORKPROOF_BRANCH_STATE_ROOTS``
contract), runs a live seeded BranchRun batch from a captured ForkPoint, then maps
the batch's recorded artifacts to ``DiscoveredBranch`` records using the SAME,
already-validated offline mapper (``witness_loop_adapter.load_branches``) — so the
live and recorded paths produce identical records, with NO referee verdict (the 008
sterile referee adjudicates separately).

This module DOES import the live ``forkproof.witnesses`` package; the offline
``witness_loop_adapter`` deliberately does not. The Modal/HUD batch is real spend and
requires credentials plus ``FORKPROOF_ALLOW_EXTERNAL_QA=1`` (enforced by branch_runs).
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from forkproof.qabench.models import DiscoveredBranch
from forkproof.qabench.witness_loop_adapter import load_branches
from forkproof.witnesses.branch_runs import _artifact_root, run_live_branch_batch

BatchRunner = Callable[..., dict[str, Any]]
ArtifactResolver = Callable[[Path, str], Path]


class LiveDiscoveryBlocked(RuntimeError):
    """Raised when the live batch is blocked (missing creds / unapproved QA export)."""

    def __init__(self, message: str, summary: dict[str, Any]) -> None:
        super().__init__(message)
        self.summary = summary


def _default_batch_runner(
    root: Path, forkpoint: dict[str, Any], *, count: int, concurrency: int
) -> dict[str, Any]:
    return asyncio.run(
        run_live_branch_batch(root, forkpoint, count=count, concurrency=concurrency)
    )


@dataclass
class LiveDiscoveryDriver:
    """Run a live BranchRun batch for one qabench env and return DiscoveredBranches.

    ``env_rel`` is the env.py path (repo-root-relative, e.g.
    ``envs/qabench/<slug>/env.py``); ``forkpoint`` is the task's captured ForkPoint
    record. ``batch_runner`` / ``artifact_resolver`` are injectable for testing.
    """

    root: Path
    env_rel: str
    forkpoint: dict[str, Any]
    factory: str = "build_task"
    count: int = 12
    concurrency: int = 12
    state_roots: tuple[str, ...] = field(default_factory=tuple)
    batch_runner: BatchRunner = _default_batch_runner
    artifact_resolver: ArtifactResolver = _artifact_root

    def _apply_task_selection(self) -> None:
        os.environ["FORKPROOF_TASK_ENV"] = self.env_rel
        os.environ["FORKPROOF_TASK_FACTORY"] = self.factory
        if self.state_roots:
            os.environ["FORKPROOF_BRANCH_STATE_ROOTS"] = ",".join(self.state_roots)

    def run_discovery_tree(self, task_id: str) -> Sequence[DiscoveredBranch]:
        self._apply_task_selection()
        summary = self.batch_runner(
            self.root, self.forkpoint, count=self.count, concurrency=self.concurrency
        )
        if summary.get("status") == "blocked":
            raise LiveDiscoveryBlocked(
                summary.get("observed_behavior") or "live branch batch blocked", summary
            )
        run_id = summary["run_id"]
        artifact_dir = self.artifact_resolver(self.root, run_id)
        return load_branches(artifact_dir, task_id=task_id)
