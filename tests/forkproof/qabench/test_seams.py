"""The deferred 003 / live seams stay clearly not-wired and the default dedup works."""

import pytest

from forkproof.qabench.models import ConfirmedHack, TrajectorySource
from forkproof.qabench.seams import (
    Deduplicator,
    NotWiredCleanVerifyRunner,
    NotWiredDiscoveryDriver,
    NotWiredError,
    TargetMechanismDeduplicator,
)


def _hack(target: str | None, mechanism: str | None) -> ConfirmedHack:
    return ConfirmedHack(
        trajectory_id="t",
        task_id="task",
        source=TrajectorySource.BASE,
        exploit_target=target,
        exploit_mechanism=mechanism,
        qa_visible=True,
        qa_flagged=False,
        has_divergence_lineage=False,
    )


def test_discovery_driver_is_not_wired() -> None:
    with pytest.raises(NotWiredError):
        NotWiredDiscoveryDriver().run_discovery_tree("task-1")


def test_clean_verify_runner_is_not_wired() -> None:
    with pytest.raises(NotWiredError):
        NotWiredCleanVerifyRunner().run("workspace-ref")


def test_default_dedup_groups_by_target_and_mechanism_case_insensitively() -> None:
    deduper = TargetMechanismDeduplicator()
    assert deduper.cluster_key(_hack("G1", "Conftest")) == deduper.cluster_key(
        _hack("g1", "conftest")
    )
    assert deduper.cluster_key(_hack("g1", "conftest")) != deduper.cluster_key(
        _hack("g2", "conftest")
    )


def test_default_dedup_handles_missing_target_or_mechanism() -> None:
    key = TargetMechanismDeduplicator().cluster_key(_hack(None, None))
    assert key == "unknown-target::unknown-mechanism"


def test_default_dedup_satisfies_the_deduplicator_protocol() -> None:
    assert isinstance(TargetMechanismDeduplicator(), Deduplicator)
