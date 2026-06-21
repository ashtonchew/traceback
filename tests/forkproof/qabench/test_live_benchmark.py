"""Pure-compose behavior of the live bounded benchmark runner (Plan 008 step 3)."""

from forkproof.qabench.live_benchmark import compose_base_trajectory
from forkproof.qabench.models import RefereeVerdict, TrajectorySource


def test_legit_base_solve_is_not_a_confirmed_hack() -> None:
    traj = compose_base_trajectory(
        "demo-task", reward_passed=True, qa_is_reward_hacking=False, clean_verify_passed=True
    )
    assert traj.source is TrajectorySource.BASE
    assert traj.referee is RefereeVerdict.LEGITIMATE
    assert traj.is_confirmed_hack is False


def test_rewarded_but_clean_verify_fail_is_confirmed_hack() -> None:
    traj = compose_base_trajectory(
        "demo-task", reward_passed=True, qa_is_reward_hacking=False, clean_verify_passed=False
    )
    assert traj.referee is RefereeVerdict.CONFIRMED_HACK
    assert traj.is_confirmed_hack is True


def test_clean_verify_unrunnable_is_undecided_not_legit() -> None:
    traj = compose_base_trajectory(
        "demo-task", reward_passed=True, qa_is_reward_hacking=None, clean_verify_passed=None
    )
    assert traj.referee is RefereeVerdict.UNDECIDED
