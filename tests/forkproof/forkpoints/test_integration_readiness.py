from __future__ import annotations

import os
import subprocess
import sys

import pytest

pytestmark = pytest.mark.integration


def test_integration_readiness_probe_runs_from_mapped_command():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    completed = subprocess.run(
        [sys.executable, "-m", "forkproof.forkpoints.integration_probe"],
        check=False,
        capture_output=True,
        env=env,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PASS integration-readiness" in completed.stdout
