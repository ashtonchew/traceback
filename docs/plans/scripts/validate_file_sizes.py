#!/usr/bin/env python3
"""Check text files under the bundle or one plan's owned paths for the 500-line target."""

from __future__ import annotations

import argparse
import glob
from pathlib import Path

from common import (
    ROOT,
    ValidationError,
    load_plans,
    plan_by_number,
    print_errors,
    print_ok,
    resolve_bound_paths,
)

TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt", ".sh",
    ".js", ".jsx", ".ts", ".tsx", ".css", ".html", ".sql", ".go", ".rs",
}


def expand_pattern(pattern: str) -> list[Path]:
    absolute = ROOT / pattern
    matches = [Path(item) for item in glob.glob(str(absolute), recursive=True)]
    if not matches and not any(token in pattern for token in "*?[") and absolute.exists():
        matches = [absolute]
    files: list[Path] = []
    for match in matches:
        if match.is_file():
            files.append(match)
        elif match.is_dir():
            files.extend(path for path in match.rglob("*") if path.is_file())
    return files


def line_count(path: Path) -> int | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (UnicodeDecodeError, OSError):
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", help="Check one plan's owned paths")
    parser.add_argument("--repo-bound", action="store_true")
    parser.add_argument("--max-lines", type=int, default=500)
    args = parser.parse_args()

    try:
        plans = load_plans()
        if args.plan:
            plan = plan_by_number(plans, args.plan)
            if args.repo_bound:
                patterns = resolve_bound_paths(plans)[plan.name]
            else:
                patterns = plan.owns
        else:
            patterns = ["**/*"]

        seen: set[Path] = set()
        oversized: list[str] = []
        checked = 0
        for pattern in patterns:
            for path in expand_pattern(pattern):
                path = path.resolve()
                if path in seen or ".git" in path.parts:
                    continue
                seen.add(path)
                count = line_count(path)
                if count is None:
                    continue
                checked += 1
                if count > args.max_lines:
                    oversized.append(
                        f"{path.relative_to(ROOT)}: {count} lines > {args.max_lines}"
                    )
        if oversized:
            return print_errors(oversized)
        print_ok(f"{checked} text file(s) are at most {args.max_lines} lines")
        return 0
    except (ValidationError, ValueError) as exc:
        return print_errors([str(exc)])


if __name__ == "__main__":
    raise SystemExit(main())
