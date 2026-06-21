"""End-to-end live benchmark runner for the qabench Δ benchmark (Plan 008 step 3).

Two phases over the 10 materialized envs:

  * ``preflight`` — capture a Modal ForkPoint per task (builds Dockerfile.hud in
    Modal + snapshots). Cheap (no agent rollouts); a task whose image fails to
    build is an honest skip, not a faked result.
  * ``batch`` — for each captured task, run the ForkProof discovery branches
    (Plan 003 ``branch_runs`` via ``LiveDiscoveryDriver``) and adjudicate each
    rewarded branch with the sterile Modal ``clean_verify`` referee, then score the
    whole trajectory population into per-task + aggregate X / Δ.

REAL Modal + Anthropic spend; requires credentials and ``FORKPROOF_ALLOW_EXTERNAL_QA=1``.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import time
from pathlib import Path

from forkproof.qabench.live_benchmark import adjudicate_branches
from forkproof.qabench.live_discovery import LiveDiscoveryDriver
from forkproof.qabench.modal_runtime import ModalCleanVerifyRunner, capture_forkpoint
from forkproof.qabench.models import Trajectory
from forkproof.qabench.scoring import score

_ARTIFACTS = Path("artifacts/forkproof/qabench")
# Per-task branch state roots (default /app); a couple of tasks also write /data.
_STATE_ROOTS: dict[str, tuple[str, ...]] = {
    "recover-corrupted-sqlite-data": ("/app", "/data"),
    "find-invalid-blockchain-transactions": ("/app", "/data"),
}


def load_env(root: Path) -> None:
    env_path = root / ".env"
    if env_path.exists():
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(
                    key.strip().removeprefix("export ").strip(), value.strip().strip("'\"")
                )
    os.environ["FORKPROOF_ALLOW_EXTERNAL_QA"] = "1"


def task_list(root: Path) -> list[str]:
    return list(json.loads((root / "envs/qabench/tasks.json").read_text())["tasks"])


def preflight(root: Path, tasks: list[str]) -> dict[str, dict]:
    """Capture a ForkPoint per task; skip (don't fail) tasks whose image won't build."""
    _ARTIFACTS.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict] = {}
    out = _ARTIFACTS / "forkpoints.json"
    for slug in tasks:
        env_dir = root / "envs/qabench" / slug
        started = time.time()
        try:
            fp = capture_forkpoint(env_dir, state_roots=_STATE_ROOTS.get(slug, ("/app",)))
            results[slug] = {"status": "ok", "snapshot_id": fp["snapshot_id"],
                             "forkpoint": fp, "seconds": round(time.time() - started, 1)}
            print(f"OK   {slug}  {fp['snapshot_id']}  ({results[slug]['seconds']}s)", flush=True)
        except Exception as exc:  # noqa: BLE001 - capture failure is an honest skip
            results[slug] = {"status": "skip", "error_class": type(exc).__name__,
                             "error": str(exc)[:600], "seconds": round(time.time() - started, 1)}
            print(f"SKIP {slug}  {type(exc).__name__}: {str(exc)[:200]}", flush=True)
        out.write_text(json.dumps(results, indent=2) + "\n")
    ok = [s for s, r in results.items() if r["status"] == "ok"]
    print(f"\nPREFLIGHT: {len(ok)}/{len(tasks)} captured -> {out}", flush=True)
    return results


def run_task(root: Path, slug: str, forkpoint: dict, *, count: int) -> list[Trajectory]:
    """Run discovery branches for one task and adjudicate them with clean_verify."""
    env_dir = root / "envs/qabench" / slug
    driver = LiveDiscoveryDriver(
        root=root, env_rel=str(Path("envs/qabench") / slug / "env.py"), forkpoint=forkpoint,
        count=count, concurrency=count, state_roots=_STATE_ROOTS.get(slug, ("/app",)),
    )
    branches = list(driver.run_discovery_tree(slug))
    return adjudicate_branches(branches, ModalCleanVerifyRunner(env_dir))


def batch(root: Path, *, count: int) -> dict:
    """Run every captured task and seal the aggregate X/Δ report."""
    forkpoints = json.loads((_ARTIFACTS / "forkpoints.json").read_text())
    captured = {s: r for s, r in forkpoints.items() if r["status"] == "ok"}
    skips = [s for s, r in forkpoints.items() if r["status"] != "ok"]
    all_trajectories: list[Trajectory] = []
    per_task: dict[str, dict] = {}
    for slug, record in captured.items():
        started = time.time()
        try:
            trajs = run_task(root, slug, record["forkpoint"], count=count)
            all_trajectories.extend(trajs)
            confirmed = sum(1 for t in trajs if t.is_confirmed_hack)
            per_task[slug] = {"branches": len(trajs), "confirmed_hacks": confirmed,
                              "seconds": round(time.time() - started, 1)}
            print(f"DONE {slug}: {len(trajs)} branches, {confirmed} confirmed hacks "
                  f"({per_task[slug]['seconds']}s)", flush=True)
        except Exception as exc:  # noqa: BLE001 - a failed batch is an honest per-task skip
            skips.append(slug)
            per_task[slug] = {"error_class": type(exc).__name__, "error": str(exc)[:600]}
            print(f"SKIP {slug} (batch): {type(exc).__name__}: {str(exc)[:200]}", flush=True)

    report = score(all_trajectories, tasks_skipped=skips)
    payload = {
        "schema_version": 1,
        "tasks_measured": report.tasks_measured,
        "tasks_skipped": skips,
        "branch_count_per_task": count,
        "depth": dataclasses.asdict(report.depth),
        "coverage": dataclasses.asdict(report.coverage),
        "per_task_summary": per_task,
        "report": dataclasses.asdict(report),
    }
    out = _ARTIFACTS / "benchmark-report.json"
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n")
    print(f"\nSEALED REPORT -> {out}\n  depth={payload['depth']}\n  coverage={payload['coverage']}"
          f"\n  measured={report.tasks_measured} skipped={skips}", flush=True)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the qabench live X/Δ benchmark.")
    parser.add_argument("--phase", choices=["preflight", "batch", "all"], default="all")
    parser.add_argument("--count", type=int, default=8, help="discovery branches per task")
    args = parser.parse_args(argv)
    root = Path.cwd()
    load_env(root)
    if args.phase in ("preflight", "all"):
        preflight(root, task_list(root))
    if args.phase in ("batch", "all"):
        batch(root, count=args.count)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
