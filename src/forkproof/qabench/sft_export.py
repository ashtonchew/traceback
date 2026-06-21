"""Export Plan 008 discovery trajectories for the Plan 007 SFT/RFT consumer (PR #26).

Emits a qabench report whose ``trajectories[]`` rows match the canonical shape
``forkproof.research.canonical.qabench.parse_qabench_training_candidate`` consumes:
each rewarded discovery branch becomes a row with the v1 ``hud_reward`` (1), the
sterile ``referee_verdict`` (the patched/hardened signal: a confirmed hack does NOT
survive the clean re-grade), the HUD QA verdict, the exploit cluster, and divergence
lineage. That is exactly the raw-vs-hardened data-quality split PR #26's SFT needs:
raw reward-positive demonstrations include the confirmed hacks; the hardened set keeps
only the legitimate ones.

Standalone module (no import from run_benchmark) so it can be added/run without
touching a live benchmark batch. ``assistant_output`` is fetched best-effort from the
HUD trace; it is optional in the consumer, so a fetch failure does not block export.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from forkproof.qabench.witness_loop_adapter import to_discovered_branch

_ART = Path("artifacts/forkproof/qabench")
_BRANCH_RUNS = Path("docs/plans/evidence/003/artifacts/branch-runs")


def _verdict_value(referee: str) -> str:
    """'RefereeVerdict.CONFIRMED_HACK' -> 'confirmed_hack' (the consumer's vocabulary)."""
    return referee.rsplit(".", 1)[-1].strip().lower()


def _instruction(root: Path, slug: str) -> str | None:
    path = root / "envs/qabench" / slug / "task_assets" / "instruction.md"
    return path.read_text(encoding="utf-8") if path.exists() else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _branch_records(branch_id: str) -> tuple[dict, dict, dict]:
    """Load the (branch, qa, file-diff) triple for a branch id from its 003 run dir."""
    run = branch_id.rsplit("-branch-", 1)[0]
    base = _BRANCH_RUNS / run
    return (
        _load_json(base / "branches" / f"{branch_id}.json"),
        _load_json(base / "qa" / f"{branch_id}.json"),
        _load_json(base / "file-diffs" / f"{branch_id}.json"),
    )


def fetch_trace_text(trace_id: str | None, *, limit: int = 8000) -> str | None:
    """Best-effort: concatenate the agent's messages from a HUD trace as the response."""
    if not trace_id:
        return None
    try:
        import httpx

        api_key = os.environ["HUD_API_KEY"]
        base = os.environ.get("HUD_API_URL", "https://api.beta.hud.ai").rstrip("/")
        resp = httpx.get(
            f"{base}/v2/trace/{trace_id}/events",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        resp.raise_for_status()
        events = (resp.json() or {}).get("events") or []
        parts = [str(e.get("text", "")).strip() for e in events if e.get("kind") == "agent_message"]
        text = "\n".join(p for p in parts if p)
        return (text[:limit] or None) if text else None
    except Exception:  # noqa: BLE001 - optional enrichment; never block the export
        return None


def trajectory_rows(root: Path, *, fetch_traces: bool = True) -> list[dict[str, Any]]:
    """Build canonical qabench trajectory rows from the per-task benchmark results."""
    rows: list[dict[str, Any]] = []
    for task_file in sorted((_ART / "tasks").glob("*.json")):
        result = _load_json(task_file)
        slug = result["slug"]
        prompt = _instruction(root, slug)
        for branch in result.get("branches", []):
            bid = branch["id"]
            brec, qarec, fdiff = _branch_records(bid)
            db = to_discovered_branch(brec, qarec, fdiff, slug)
            trace_id = db.hud_trace_id or bid
            cluster = None
            if db.exploit_target or db.exploit_mechanism:
                cluster = f"{db.exploit_target or '?'}::{db.exploit_mechanism or '?'}"
            verdict = _verdict_value(branch["referee"])
            rows.append({
                "trajectory_id": bid,
                "trace_id": trace_id,
                "task_id": slug,
                "task_prompt": prompt,
                "assistant_output": fetch_trace_text(db.hud_trace_id) if fetch_traces else None,
                "origin": "branch",
                "hud_reward": 1.0 if branch["reward"] else 0.0,
                "referee_verdict": verdict,
                "patched_reward": 0.0 if verdict == "confirmed_hack" else 1.0,
                "is_hack": verdict == "confirmed_hack",
                "is_legit": verdict == "legitimate",
                "hud_qa_verdict": {"is_reward_hacking": branch["qa"]},
                "cluster_id": cluster,
                "environment_version": f"{slug.replace('-', '_')}_v1",
                "lineage": _lineage_dict(db),
            })
    return rows


def _lineage_dict(db: Any) -> dict[str, Any] | None:
    lin = getattr(db, "lineage", None)
    if lin is None:
        return None
    return {
        "parent_fork_point_id": getattr(lin, "parent_fork_point_id", None),
        "seed": getattr(lin, "seed", None),
        "divergent_action": getattr(lin, "divergent_action", None),
    }


def write_export(root: Path, *, fetch_traces: bool = True, out: Path | None = None) -> Path:
    rows = trajectory_rows(root, fetch_traces=fetch_traces)
    confirmed = sum(1 for r in rows if r["is_hack"])
    legit = sum(1 for r in rows if r["is_legit"])
    payload = {
        "schema_version": 1,
        "plan_id": "008",
        "source": "forkproof.qabench discovery branches (sterile-referee labeled)",
        "trajectory_count": len(rows),
        "confirmed_hacks": confirmed,
        "legitimate": legit,
        "raw_reward_positive": len(rows),
        "hardened_reward_positive": legit,
        "trajectories": rows,
    }
    out = out or (_ART / "sft_export.qabench_report.json")
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export qabench trajectories for SFT (PR #26).")
    parser.add_argument("--no-fetch-traces", action="store_true", help="skip HUD trace text fetch")
    parser.add_argument("--out", default=str(_ART / "sft_export.qabench_report.json"))
    args = parser.parse_args(argv)
    root = Path.cwd()
    if (root / ".env").exists():
        for raw in (root / ".env").read_text().splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip().removeprefix("export ").strip(), v.strip().strip("'\""))
    out = write_export(root, fetch_traces=not args.no_fetch_traces, out=Path(args.out))
    payload = json.loads(out.read_text())
    print(f"exported {payload['trajectory_count']} trajectories "
          f"({payload['confirmed_hacks']} hacks / {payload['legitimate']} legit) -> {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
