"""Behavior of the Terminal-Wrench-to-HUD importer planner (Plan 008 WP1)."""

import json
from pathlib import Path

from forkproof.qabench.importer import TerminalWrenchTask, plan_env

_REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE = _REPO_ROOT / "fixtures" / "forkproof" / "qabench" / "sample-task"


def _task() -> TerminalWrenchTask:
    return TerminalWrenchTask(
        task_id="sample_task",
        revision="deadbeef",
        grader_path=FIXTURE / "grader.py",
        tests_path=FIXTURE / "tests.py",
        instruction_path=FIXTURE / "instruction.md",
        dockerfile_path=FIXTURE / "Dockerfile",
    )


def test_plan_env_materializes_layout_and_clean_verify(tmp_path: Path) -> None:
    plan = plan_env(_task(), tmp_path)
    env_dir = plan.write()

    assert env_dir == tmp_path / "sample-task"
    assert (env_dir / "task_assets" / "grader.py").exists()
    assert (env_dir / "task_assets" / "tests.py").exists()
    assert (env_dir / "task_assets" / "instruction.md").exists()
    assert (env_dir / "Dockerfile").exists()
    clean_verify = env_dir / "clean_verify.sh"
    assert clean_verify.exists()
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1" in clean_verify.read_text(encoding="utf-8")


def test_provenance_records_pinned_digests(tmp_path: Path) -> None:
    plan = plan_env(_task(), tmp_path)
    plan.write()
    provenance = json.loads(
        (plan.dest / "provenance.json").read_text(encoding="utf-8")
    )
    assert provenance["task_id"] == "sample_task"
    assert provenance["terminal_wrench_revision"] == "deadbeef"
    for digest_field in ("grader_digest", "tests_digest", "dockerfile_digest"):
        assert len(provenance[digest_field]) == 64  # sha256 hex


def test_planning_is_idempotent_per_pinned_source(tmp_path: Path) -> None:
    first = plan_env(_task(), tmp_path).provenance["content_digest"]
    second = plan_env(_task(), tmp_path).provenance["content_digest"]
    assert first == second


def test_slug_normalizes_task_id() -> None:
    assert _task().slug() == "sample-task"
