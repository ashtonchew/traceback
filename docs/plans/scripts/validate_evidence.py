#!/usr/bin/env python3
"""Validate per-plan evidence-manifest presence and optional completion."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from common import (
    PLAN_DIR,
    ValidationError,
    load_json,
    load_plans,
    plan_by_number,
    print_errors,
    print_ok,
)

REQUIRED_KEYS = {
    "schema_version",
    "plan_id",
    "plan_name",
    "wave",
    "status",
    "started_at",
    "updated_at",
    "completed_at",
    "commit",
    "commands",
    "checks",
    "artifacts",
    "screenshots",
    "skips",
    "blockers",
    "notes",
}


def validate_manifest(plan: Any, require_complete: bool) -> list[str]:
    path = PLAN_DIR / "evidence" / plan.number / "MANIFEST.json"
    errors: list[str] = []
    try:
        data = load_json(path)
    except ValidationError as exc:
        return [str(exc)]

    if not isinstance(data, dict):
        return [f"{path}: root must be an object"]
    missing = REQUIRED_KEYS - set(data)
    if missing:
        errors.append(f"{path}: missing keys {sorted(missing)}")
    if str(data.get("plan_id")) != plan.number:
        errors.append(f"{path}: plan_id does not match {plan.number}")
    if data.get("plan_name") != plan.name:
        errors.append(f"{path}: plan_name does not match {plan.name}")
    if data.get("wave") != plan.wave:
        errors.append(f"{path}: wave does not match {plan.wave}")
    if data.get("status") not in {"not-started", "in-progress", "blocked", "complete"}:
        errors.append(f"{path}: invalid status {data.get('status')!r}")
    for key in ("commands", "checks", "artifacts", "screenshots", "skips", "blockers", "notes"):
        if key in data and not isinstance(data[key], list):
            errors.append(f"{path}: {key} must be a list")

    if require_complete:
        if data.get("status") != "complete":
            errors.append(f"{path}: status must be complete")
        if not data.get("completed_at"):
            errors.append(f"{path}: completed_at is required")
        if not data.get("commands"):
            errors.append(f"{path}: at least one executed command is required")
        if not data.get("checks"):
            errors.append(f"{path}: at least one behavior check is required")
        if not data.get("artifacts"):
            errors.append(f"{path}: at least one artifact is required")
        if data.get("blockers"):
            errors.append(f"{path}: complete manifest cannot have blockers")

        for index, command in enumerate(data.get("commands", [])):
            if not isinstance(command, dict):
                errors.append(f"{path}: commands[{index}] must be an object")
                continue
            if not command.get("argv"):
                errors.append(f"{path}: commands[{index}] lacks argv")
            if not isinstance(command.get("exit_code"), int):
                errors.append(f"{path}: commands[{index}] lacks integer exit_code")
            if command.get("exit_code") != 0:
                errors.append(f"{path}: commands[{index}] did not exit 0")

        for index, check in enumerate(data.get("checks", [])):
            if not isinstance(check, dict):
                errors.append(f"{path}: checks[{index}] must be an object")
                continue
            if check.get("status") not in {"pass", "skipped"}:
                errors.append(f"{path}: checks[{index}] must pass or be evidence-backed skipped")
            if check.get("status") == "skipped" and not check.get("evidence"):
                errors.append(f"{path}: checks[{index}] skip lacks evidence")

        for index, artifact in enumerate(data.get("artifacts", [])):
            if not isinstance(artifact, dict) or not artifact.get("ref"):
                errors.append(f"{path}: artifacts[{index}] lacks ref")

    plan_text = plan.path.read_text(encoding="utf-8")
    expected = f"docs/plans/evidence/{plan.number}/MANIFEST.json"
    if expected not in plan_text:
        errors.append(f"{plan.path}: does not reference its evidence manifest")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", help="Three-digit or integer plan number")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()

    try:
        plans = load_plans()
        selected = [plan_by_number(plans, args.plan)] if args.plan else plans
        errors: list[str] = []
        for plan in selected:
            errors.extend(validate_manifest(plan, args.require_complete))
        if errors:
            return print_errors(errors)
        mode = "complete" if args.require_complete else "present/structured"
        print_ok(f"{len(selected)} evidence manifest(s) are {mode}")
        return 0
    except ValidationError as exc:
        return print_errors([str(exc)])


if __name__ == "__main__":
    raise SystemExit(main())
