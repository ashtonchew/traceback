"""Runtime compatibility patches for the upstream harden-v0 execution surface."""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def install() -> None:
    """Patch harden-v0's fixer artifact path resolution in the active process."""

    import harden.loop as harden_loop
    import harden.journal as harden_journal
    import harden.workspace as harden_workspace

    harden_workspace.apply_fixer_artifacts = apply_fixer_artifacts
    harden_workspace.extract_fixer_artifacts = extract_fixer_artifacts
    harden_workspace.update_hardened = update_hardened
    harden_loop.apply_fixer_artifacts = apply_fixer_artifacts
    harden_loop.extract_fixer_artifacts = extract_fixer_artifacts
    harden_loop.update_hardened = update_hardened
    harden_journal._write_fixer_patch = write_fixer_patch
    logger.info("Installed Plan 005 harden-v0 fixer artifact compatibility patch")


def resolve_fixer_artifacts(fixer_trial_dir: Path) -> Path:
    """Return the collected fixer artifact repo path for current Harbor layouts."""

    expected = fixer_trial_dir / "artifacts"
    if (expected / ".git").exists():
        return expected
    nested = expected / "logs" / "artifacts"
    if (nested / ".git").exists():
        return nested
    return expected


def apply_fixer_artifacts(task_dir: Path, fixer_trial_dir: Path) -> None:
    """Replace tests/ and environment/ in `task_dir` with fixer's committed versions."""

    artifacts = resolve_fixer_artifacts(fixer_trial_dir)
    for subdir in ("tests", "environment"):
        src = artifacts / subdir
        dest = task_dir / subdir
        if src.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)


def update_hardened(hardened_task_dir: Path, fixer_trial_dir: Path) -> None:
    """Update the canonical hardened state with fixer artifacts."""

    apply_fixer_artifacts(hardened_task_dir, fixer_trial_dir)
    logger.info("Updated hardened state from fixer artifacts")


def extract_fixer_artifacts(
    fixer_trial_dir: Path,
    working_copy_parent: Path,
    task_id: str,
    kernelbench_mode: bool = False,
    legitimate_marker: bool = True,
) -> str:
    """Extract fixer's committed changes from the collected artifacts git repo."""

    artifacts = resolve_fixer_artifacts(fixer_trial_dir)
    task_dir = working_copy_parent / task_id

    result = subprocess.run(
        ["git", "-c", "safe.directory=*", "-C", str(artifacts), "diff", "--name-only", "initial", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed in artifacts: {result.stderr.strip()}")

    changed_files = [line for line in result.stdout.strip().split("\n") if line]
    if not changed_files:
        logger.info("No committed changes in artifacts")
        return "no_changes"

    logger.info("Fixer changed: %s", changed_files)

    if legitimate_marker and (artifacts / ".legitimate").exists():
        logger.info("Fixer marked hack as legitimate solution")
        return "legitimate"

    apply_fixer_artifacts(task_dir, fixer_trial_dir)

    check_name = "eval_kernel.py" if kernelbench_mode else "test_outputs.py"
    check_file = task_dir / "tests" / check_name
    if check_file.exists():
        err = validate_python(check_file.read_text(encoding="utf-8"), check_name)
        if err is not None:
            raise ValueError(
                f"Extracted {check_name} has syntax errors ({check_file}): {err}"
            )

    return "applied"


def write_fixer_patch(
    jdir: Path,
    iteration: int,
    fixer_trial: Path | None,
) -> None:
    """Write harden journal fixer patch from the resolved artifacts repo."""

    if fixer_trial is None:
        return
    artifacts = resolve_fixer_artifacts(fixer_trial)
    if not artifacts.is_dir():
        return
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                "safe.directory=*",
                "-C",
                str(artifacts),
                "diff",
                "--binary",
                "initial",
                "HEAD",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except Exception as exc:
        logger.warning("Could not run git diff for iter %d patch (%s): %s", iteration, artifacts, exc)
        return
    if result.returncode != 0:
        logger.warning(
            "git diff returned non-zero for iter %d patch (%s): %s",
            iteration,
            artifacts,
            result.stderr.strip(),
        )
        return
    if not result.stdout.strip():
        return
    jdir.mkdir(parents=True, exist_ok=True)
    path = jdir / f"iter_{iteration}.patch"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(result.stdout, encoding="utf-8")
    tmp.replace(path)


def validate_python(source: str, filename: str = "<source>") -> str | None:
    """Return None for valid Python, otherwise a syntax error string."""

    try:
        compile(source, f"<{filename}>", "exec")
        return None
    except SyntaxError as exc:
        return f"{exc.msg} at line {exc.lineno}, column {exc.offset}"
