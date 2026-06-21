"""Live bounded benchmark runner for one qabench env (Plan 008 step 3).

Ties the proven live primitives into the additive benchmark for a single task:
build the HUD image, run a base rollout (real agent -> HUD reward + trace), get the
canonical HUD QA verdict on that trace, adjudicate the resulting workspace with the
sterile clean_verify referee, then compose the three separated signals into a scored
Trajectory via the pure 008 referee + scorer.

The rollout + QA steps are REAL spend and require credentials plus
FORKPROOF_ALLOW_EXTERNAL_QA=1 (enforced downstream). The compose/score step is pure
and unit-tested. The discovery-branch lift (Δ) reuses live_discovery.LiveDiscoveryDriver
over a captured ForkPoint; this module covers the base (X-baseline) leg.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from collections.abc import Iterable, Sequence

from forkproof.qabench import referee
from forkproof.qabench.models import (
    BenchmarkReport,
    DiscoveredBranch,
    Trajectory,
    TrajectorySource,
)
from forkproof.qabench.scoring import score
from forkproof.qabench.seams import CleanVerifyRunner


def build_hud_image(env_dir: Path | str, tag: str | None = None) -> str:
    """Build the env's Dockerfile.hud and return the image tag."""
    env_dir = Path(env_dir)
    image = tag or f"qabench-hud/{env_dir.name}"
    result = subprocess.run(
        ["docker", "build", "-q", "-f", str(env_dir / "Dockerfile.hud"), "-t", image, str(env_dir)],
        check=False, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"docker build failed for {env_dir.name}: {result.stderr.strip()}")
    return image


async def base_rollout(env_module_path: Path | str, image: str, *, model: str = "claude-haiku-4-5",
                       max_steps: int = 25, max_tokens: int = 4096) -> dict[str, Any]:
    """Run a real agent base rollout on the HUD image; return reward + trace id."""
    import importlib.util

    from hud.agents.claude.agent import ClaudeAgent, ClaudeConfig
    from hud.eval.runtime import DockerRuntime

    spec = importlib.util.spec_from_file_location("qabench_live_env", str(env_module_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load env module from {env_module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    agent = ClaudeAgent(
        ClaudeConfig(model=model, max_steps=max_steps, max_tokens=max_tokens,
                     use_computer_beta=False, system_prompt="qabench base rollout (X baseline).")
    )
    job = await module.build_task().run(agent, runtime=DockerRuntime(image=image))
    runs = getattr(job, "runs", None) or []
    trace_id = str(getattr(runs[0], "trace_id", "") or "") if runs else str(getattr(job, "trace_id", "") or "")
    return {
        "reward": getattr(job, "reward", None),
        "job_id": str(getattr(job, "id", "") or ""),
        "trace_id": trace_id,
        "env_name": module.env.name,
    }


def qa_verdict(root: Path | str, trace_id: str, *, branch_id: str, action_record_digest: str) -> dict[str, Any]:
    """Canonical HUD Reward-Hacking QA verdict for a trace (real spend; export-gated)."""
    from forkproof.witnesses.qa_binding import run_reward_hacking_analysis

    return run_reward_hacking_analysis(
        Path(root), trace_id, branch_id=branch_id, action_record_digest=action_record_digest
    )


def compose_base_trajectory(
    task_id: str,
    *,
    reward_passed: bool,
    qa_is_reward_hacking: bool | None,
    clean_verify_passed: bool | None,
    hud_trace_id: str | None = None,
    workspace_ref: str | None = None,
) -> Trajectory:
    """Compose the base trajectory's scored Trajectory from the three live signals."""
    branch = DiscoveredBranch(
        branch_id=f"{task_id}-base",
        task_id=task_id,
        source=TrajectorySource.BASE,
        reward_passed=reward_passed,
        qa_is_reward_hacking=qa_is_reward_hacking,
        hud_trace_id=hud_trace_id,
        workspace_ref=workspace_ref,
    )
    return referee.build_trajectory(branch, clean_verify_passed)


def adjudicate_branches(
    branches: Iterable[DiscoveredBranch],
    clean_verify: CleanVerifyRunner,
) -> list[Trajectory]:
    """Run the sterile referee on each rewarded branch and compose scored Trajectories.

    Only rewarded branches with a restorable workspace are adjudicated; a non-rewarded
    branch is not a reward-hack candidate, and a missing workspace leaves clean_verify
    unrunnable (UNDECIDED, never silently legitimate).
    """
    trajectories: list[Trajectory] = []
    for branch in branches:
        clean_verify_passed: bool | None = None
        if branch.reward_passed and branch.workspace_ref:
            clean_verify_passed = clean_verify.run(branch.workspace_ref)
        trajectories.append(referee.build_trajectory(branch, clean_verify_passed))
    return trajectories


def score_task(
    branches: Sequence[DiscoveredBranch],
    clean_verify: CleanVerifyRunner,
    *,
    base_trajectory: Trajectory | None = None,
) -> BenchmarkReport:
    """Adjudicate discovery branches (+ an optional base trajectory) into X and Δ."""
    trajectories = adjudicate_branches(branches, clean_verify)
    if base_trajectory is not None:
        trajectories = [base_trajectory, *trajectories]
    return score(trajectories)
