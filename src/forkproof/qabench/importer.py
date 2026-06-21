"""Terminal-Wrench-to-HUD importer template (Plan 008 WP1).

003-independent: plans and materializes the per-task env layout (env + v1 grader
+ a sterile clean_verify referee entrypoint) plus a content-addressed provenance
record. It targets the stable Plan 001 env pattern and Plan 002 ForkPoint
contract — not Plan 003's in-flux witnesses code. The live HUD *deploy* of a
planned env is the deferred boundary and is intentionally not performed here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

# Sterile referee entrypoint: re-run the task's own verification with plugin
# autoload disabled and conftest discovery suppressed, so agent-planted
# conftest.py / pytest11 plugins / cache cannot influence the verdict.
CLEAN_VERIFY_TEMPLATE = """#!/usr/bin/env bash
# Sterile clean_verify referee entrypoint (Plan 008). Re-runs the task's own v1
# verification isolated from agent-planted conftest.py / pytest plugins / cache.
set -euo pipefail
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
exec python -m pytest --noconftest -p no:cacheprovider -q "$@"
"""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class TerminalWrenchTask:
    """A pinned Terminal Wrench task source on disk."""

    task_id: str
    revision: str
    grader_path: Path
    tests_path: Path
    instruction_path: Path
    dockerfile_path: Path

    def slug(self) -> str:
        return self.task_id.strip().lower().replace(" ", "-").replace("_", "-")


@dataclass
class ImportedEnvPlan:
    """A planned env layout plus provenance; ``write()`` materializes it to disk."""

    task_id: str
    dest: Path
    files: dict[str, Path]
    clean_verify_entrypoint: str
    provenance: dict[str, str] = field(default_factory=dict)

    def write(self) -> Path:
        """Materialize the env layout idempotently and return the env directory."""
        self.dest.mkdir(parents=True, exist_ok=True)
        for rel, src in self.files.items():
            target = self.dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(src.read_bytes())
        (self.dest / "provenance.json").write_text(
            json.dumps(self.provenance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        entrypoint = self.dest / self.clean_verify_entrypoint
        entrypoint.write_text(CLEAN_VERIFY_TEMPLATE, encoding="utf-8")
        entrypoint.chmod(0o755)
        return self.dest


def _content_digest(provenance: dict[str, str]) -> str:
    payload = {k: v for k, v in provenance.items() if k != "content_digest"}
    canonical = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def plan_env(task: TerminalWrenchTask, dest_root: Path) -> ImportedEnvPlan:
    """Plan one ``envs/qabench/<slug>/`` env layout with stable provenance.

    Pure planning: it reads the pinned source files to compute digests but writes
    nothing until ``ImportedEnvPlan.write()`` is called. Re-planning the same
    pinned source yields the same ``content_digest`` (idempotent).
    """
    slug = task.slug()
    files = {
        "task_assets/grader.py": task.grader_path,
        "task_assets/tests.py": task.tests_path,
        "task_assets/instruction.md": task.instruction_path,
        "Dockerfile": task.dockerfile_path,
    }
    provenance = {
        "task_id": task.task_id,
        "task_slug": slug,
        "terminal_wrench_revision": task.revision,
        "grader_digest": _sha256(task.grader_path),
        "tests_digest": _sha256(task.tests_path),
        "instruction_digest": _sha256(task.instruction_path),
        "dockerfile_digest": _sha256(task.dockerfile_path),
    }
    provenance["content_digest"] = _content_digest(provenance)
    return ImportedEnvPlan(
        task_id=task.task_id,
        dest=dest_root / slug,
        files=files,
        clean_verify_entrypoint="clean_verify.sh",
        provenance=provenance,
    )
