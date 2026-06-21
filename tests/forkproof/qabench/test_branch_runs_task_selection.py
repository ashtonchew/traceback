"""The discovery-loop task-selection contract Plan 008 depends on (Plan 003 seam).

Plan 008's live discovery driver points Plan 003's branch_runs loop at a
materialized qabench env via FORKPROOF_TASK_ENV / FORKPROOF_TASK_FACTORY, without
disturbing the mongodb default. This pins that contract.
"""

from pathlib import Path

import pytest

from forkproof.witnesses.branch_runs import _resolve_task_env


def test_defaults_to_mongodb(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FORKPROOF_TASK_ENV", raising=False)
    monkeypatch.delenv("FORKPROOF_TASK_FACTORY", raising=False)
    path, factory = _resolve_task_env(Path("/repo"))
    assert path == Path("/repo/envs/mongodb-sales-aggregation-engine/env.py")
    assert factory == "implement_sales_analyzer"


def test_env_vars_redirect_to_qabench(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FORKPROOF_TASK_ENV", "envs/qabench/solve-ode-with-sympy/env.py")
    monkeypatch.setenv("FORKPROOF_TASK_FACTORY", "build_task")
    path, factory = _resolve_task_env(Path("/repo"))
    assert path == Path("/repo/envs/qabench/solve-ode-with-sympy/env.py")
    assert factory == "build_task"


def test_absolute_env_path_is_used_verbatim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FORKPROOF_TASK_ENV", "/abs/path/env.py")
    monkeypatch.delenv("FORKPROOF_TASK_FACTORY", raising=False)
    path, factory = _resolve_task_env(Path("/repo"))
    assert path == Path("/abs/path/env.py")
    assert factory == "implement_sales_analyzer"  # factory still defaults independently
