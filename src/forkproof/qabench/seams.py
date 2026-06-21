"""Plan 003 / live-infrastructure plug-in points for the qabench benchmark.

These protocols are the ONLY coupling from Plan 008 to Plan 003's in-flux
``witnesses`` package and to live HUD/Modal infrastructure. They are stubbed as
``NotWired*`` defaults so the 003-independent scaffold (referee logic, scorer,
importer planning) builds and tests today; wire the real implementations after
Plan 003 merges and after the ``envs/qabench/**`` task envs are materialized.

Wiring map (do these when 003 lands / envs exist):
  * Deduplicator       -> Plan 003 target+mechanism dedup (forkproof.witnesses),
                          or keep TargetMechanismDeduplicator as the frozen default.
  * DiscoveryDriver    -> forkproof.witnesses.branch_runs (base + Hacker BranchRuns).
  * CleanVerifyRunner  -> the 008-owned sterile sandbox over a materialized env.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from forkproof.qabench.models import ConfirmedHack, Trajectory


class NotWiredError(NotImplementedError):
    """Raised when a deferred seam is used before it is wired."""


@runtime_checkable
class Deduplicator(Protocol):
    """Frozen, symmetric target+mechanism dedup applied identically to QA's and
    ForkProof's confirmed hacks. Reading which method surfaced a hack would be
    score-running and is forbidden."""

    def cluster_key(self, hack: ConfirmedHack) -> str: ...


@runtime_checkable
class DiscoveryDriver(Protocol):
    """Runs the Plan 003 discovery tree (base rollout + Hacker BranchRuns) for a
    task and returns its rewarded trajectory population (Plan 008 WP2)."""

    def run_discovery_tree(self, task_id: str) -> Sequence[Trajectory]: ...


@runtime_checkable
class CleanVerifyRunner(Protocol):
    """Runs the sterile clean_verify referee against a rewarded trajectory's
    resulting workspace in a clean sandbox isolated from agent-planted files
    (conftests, plugins, cached state). Returns True iff clean_verify passed."""

    def run(self, workspace_ref: str) -> bool: ...


class TargetMechanismDeduplicator:
    """Default frozen dedup: group confirmed hacks by (target, mechanism).

    Symmetric by construction — it never reads which method surfaced a hack — so
    it cannot be score-run. Swap for Plan 003's dedup behind ``Deduplicator`` if
    exact parity with the witness loop is required before scoring.
    """

    def cluster_key(self, hack: ConfirmedHack) -> str:
        target = (hack.exploit_target or "unknown-target").strip().lower()
        mechanism = (hack.exploit_mechanism or "unknown-mechanism").strip().lower()
        return f"{target}::{mechanism}"


class NotWiredDiscoveryDriver:
    """Placeholder until Plan 003 merges; raises with a clear wiring pointer."""

    def run_discovery_tree(self, task_id: str) -> Sequence[Trajectory]:
        raise NotWiredError(
            "DiscoveryDriver is not wired. After Plan 003 merges, bind this to "
            "forkproof.witnesses.branch_runs (base rollout + Hacker BranchRuns) "
            f"for task {task_id!r}."
        )


class NotWiredCleanVerifyRunner:
    """Placeholder until ``envs/qabench/**`` exists; raises a clear wiring pointer."""

    def run(self, workspace_ref: str) -> bool:
        raise NotWiredError(
            "CleanVerifyRunner is not wired. Implement the sterile clean_verify "
            "sandbox once qabench task envs are materialized (Plan 008 WP1/WP3); "
            f"workspace_ref={workspace_ref!r}."
        )
