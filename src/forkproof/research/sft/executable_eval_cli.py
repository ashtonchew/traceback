"""CLI for paired executable Model A/B evaluation."""

from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from forkproof.research.sft.executable_eval import (
    CONDITIONS,
    FireworksChatClient,
    RolloutConfig,
    load_task_prompt,
    run_rollout,
    summarize,
)
from forkproof.research.sft.executable_eval_modal import ModalWorkspaceFactory


DEFAULT_MODELS = {
    "model_a": "accounts/desaikrrish-8x76pqk3/deployments/oqvhj92h",
    "model_b": "accounts/desaikrrish-8x76pqk3/deployments/p6ktlcy8",
}


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", required=True, help="Comma-separated qabench task ids")
    parser.add_argument(
        "--conditions",
        default="guarded,neutral,pressure",
        help="Comma-separated prompt conditions",
    )
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=12)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("artifacts/forkproof/research/sft/executable-eval/runs"),
    )
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    tasks = _csv(args.tasks)
    conditions = _csv(args.conditions)
    unknown = sorted(set(conditions) - set(CONDITIONS))
    if unknown:
        parser.error(f"unknown conditions: {', '.join(unknown)}")

    root = Path.cwd().resolve()
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    client = FireworksChatClient(api_key)
    workspaces = ModalWorkspaceFactory(root)
    run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output_dir = args.output_root / run_id
    output_dir.mkdir(parents=True, exist_ok=False)

    rows: list[dict[str, object]] = []
    for task_id in tasks:
        prompt = load_task_prompt(root, task_id)
        for condition in conditions:
            for repeat in range(args.repeats):
                for label, route in DEFAULT_MODELS.items():
                    config = RolloutConfig(
                        model_label=label,
                        model_route=route,
                        task_id=task_id,
                        condition=condition,
                        repeat=repeat,
                        max_steps=args.max_steps,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                    )
                    print(f"{task_id} {condition} repeat={repeat} {label}", flush=True)
                    row = run_rollout(
                        client=client,
                        workspace_factory=workspaces,
                        config=config,
                        task_prompt=prompt,
                    )
                    rows.append(row)
                    _write_json(output_dir / f"rollout-{len(rows):04d}.json", row)
                    _write_json(output_dir / "summary.json", summarize(rows))
    print(output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

