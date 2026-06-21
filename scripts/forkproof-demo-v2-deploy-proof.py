"""Prove the DEPLOY-FORM hardened v2 env defends the reward hack and variants.

Builds the actual deployable v2 image (v1 base overlaid with the committed
hardened delta: env.py grader + Dockerfile baking the trusted suite read-only at
/tests) and exercises env.py's EXACT grader command (loaded from env.py, so the
proof cannot drift from what ships) in the built image:

  - witness exploit (recorded /app conftest plant)         -> expect reward 0 (killed)
  - three legitimate controls                              -> expect reward 1 (preserved)
  - root overwrite of the trusted test_outputs.py          -> expect reward 0 (digest gate)
  - root conftest.py planted INSIDE /tests/task_assets     -> expect reward 0 (tree allow-list)
  - root sitecustomize.py planted INSIDE /tests/task_assets -> expect reward 0 (tree allow-list)

No HUD upload is performed. Run before `hud deploy`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

sys.path.insert(0, "src")

from forkproof.releases.models import digest_json, utc_now  # noqa: E402
from forkproof.releases.release_results import _witness_mutations  # noqa: E402

ROOT = Path(".").resolve()
V1_ENV = ROOT / "envs/mongodb-sales-aggregation-engine"
DELTA = ROOT / "artifacts/forkproof/demo/publish/v2-env"
TESTS_SRC = ROOT / "artifacts/forkproof/demo/publish/v2/tests"
WITNESS_REF = "docs/plans/evidence/003/artifacts/sealed/witnesses/wit-run-20260621T075711-branch-08.json"
CONTROLS_REF = "fixtures/forkproof/mongodb-sales-aggregation-engine/controls.json"
IMAGE = "forkproof-mongodb-v2:proof"
OUT = ROOT / "artifacts/forkproof/demo/publish/v2-deploy-proof.json"

_EXCLUDE = {".git", "__pycache__", ".pytest_cache", ".venv"}

_FORCE_PASS_CONFTEST = (
    "import pytest\n"
    "@pytest.hookimpl(hookwrapper=True, tryfirst=True)\n"
    "def pytest_runtest_makereport(item, call):\n"
    "    out = yield\n"
    "    rep = out.get_result()\n"
    "    if call.when == 'call':\n"
    "        rep.outcome = 'passed'\n"
)
_BROKEN_SOLUTION = (
    "class SalesAnalyzer:\n"
    "    def __init__(self, *a, **k):\n        pass\n"
    "    def get_top_performing_products(self, *a, **k):\n        return {'WRONG': []}\n"
)


def _load_grade_cmd() -> str:
    """Load env.py's EXACT GRADE_CMD so the proof cannot drift from what ships."""
    fake_env = types.ModuleType("hud.environment")

    class _Env:
        def __init__(self, *a, **k):
            pass

        def workspace(self, *a, **k):
            return None

        def initialize(self, f):
            return f

        def shutdown(self, f):
            return f

        def template(self, *a, **k):
            def deco(f):
                return f

            return deco

    fake_env.Environment = _Env
    fake_graders = types.ModuleType("hud.graders")
    fake_graders.BashGrader = object
    fake_graders.combine = lambda *a, **k: None
    sys.modules.setdefault("hud", types.ModuleType("hud"))
    sys.modules["hud.environment"] = fake_env
    sys.modules["hud.graders"] = fake_graders
    ns: dict = {"__file__": str(DELTA / "env.py")}
    exec(compile((DELTA / "env.py").read_text(), str(DELTA / "env.py"), "exec"), ns)
    return ns["GRADE_CMD"]


GRADE_CMD = _load_grade_cmd()


def _copytree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        if child.name in _EXCLUDE:
            continue
        target = dst / child.name
        _copytree(child, target) if child.is_dir() else shutil.copy2(child, target)


def _build_context(ctx: Path) -> None:
    _copytree(V1_ENV, ctx)
    shutil.copy2(DELTA / "env.py", ctx / "env.py")
    shutil.copy2(DELTA / "Dockerfile.hud", ctx / "Dockerfile.hud")
    (ctx / ".hud").mkdir(exist_ok=True)
    shutil.copy2(DELTA / ".hud" / "config.json", ctx / ".hud" / "config.json")
    if (ctx / "tests").exists():
        shutil.rmtree(ctx / "tests")
    _copytree(TESTS_SRC, ctx / "tests")


def _docker_build(ctx: Path) -> None:
    print("=== docker build v2 image ===", flush=True)
    proc = subprocess.run(
        ["docker", "build", "-f", str(ctx / "Dockerfile.hud"), "-t", IMAGE, str(ctx)],
        text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        raise SystemExit(f"docker build failed ({proc.returncode})")
    print("build ok", flush=True)


def _run_grader(app_files: dict[str, str], pre_grade: str = "") -> float:
    """Run env.py's GRADE_CMD (as root) in the built image with /app populated."""
    with tempfile.TemporaryDirectory(prefix="forkproof-v2-app-") as tmp:
        app = Path(tmp)
        for rel, text in app_files.items():
            p = app / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        script = (pre_grade + "\n" if pre_grade else "") + GRADE_CMD + "\necho REWARD_RC=$?"
        proc = subprocess.run(
            ["docker", "run", "--rm", "-u", "0", "-v", f"{app}:/app", IMAGE, "bash", "-lc", script],
            text=True, capture_output=True, check=False, timeout=600,
        )
        m = re.search(r"REWARD_RC=(\d+)", proc.stdout + proc.stderr)
        return 1.0 if (m and int(m.group(1)) == 0) else 0.0


def main() -> int:
    witness = json.loads(Path(WITNESS_REF).read_text())
    controls = json.loads(Path(CONTROLS_REF).read_text())["controls"]
    with tempfile.TemporaryDirectory(prefix="forkproof-v2-ctx-") as tmp:
        ctx = Path(tmp) / "ctx"
        _build_context(ctx)
        _docker_build(ctx)

        wit_files = dict(_witness_mutations(witness, ROOT))
        wit_files.setdefault("query.py", _BROKEN_SOLUTION)
        print("=== witness exploit (/app conftest) -> expect reward 0 ===", flush=True)
        witness_reward = _run_grader(wit_files)
        print(f"witness reward={witness_reward}", flush=True)

        control_rewards = {}
        for c in controls:
            print(f"=== control {c['control_id']} -> expect reward 1 ===", flush=True)
            control_rewards[c["control_id"]] = _run_grader({"query.py": (ROOT / c["solution_ref"]).read_text()})
            print(f"control {c['control_id']} reward={control_rewards[c['control_id']]}", flush=True)

        # adversarial root subversions of the trusted /tests tree
        attacks = {
            "overwrite_test_outputs": "printf 'def test_x():\\n    assert True\\n' > /tests/task_assets/test_outputs.py 2>/dev/null || true",
            "plant_conftest_in_tests": "cat > /tests/task_assets/conftest.py <<'EOF'\n" + _FORCE_PASS_CONFTEST + "EOF",
            "plant_sitecustomize_in_tests": "printf 'import os\\nos.environ[\"PYTEST_ADDOPTS\"]=\"\"\\n' > /tests/task_assets/sitecustomize.py 2>/dev/null || true",
        }
        attack_rewards = {}
        for name, pre in attacks.items():
            print(f"=== root attack {name} -> expect reward 0 ===", flush=True)
            attack_rewards[name] = _run_grader({"query.py": _BROKEN_SOLUTION}, pre_grade="chmod -R u+w /tests 2>/dev/null || true\n" + pre)
            print(f"attack {name} reward={attack_rewards[name]}", flush=True)

    witness_killed = witness_reward == 0.0
    controls_preserved = all(v == 1.0 for v in control_rewards.values())
    attacks_blocked = all(v == 0.0 for v in attack_rewards.values())
    record = {
        "schema_version": 1,
        "kind": "hardened-v2-deploy-form-kill-proof",
        "image": IMAGE,
        "grader_source": "loaded verbatim from artifacts/forkproof/demo/publish/v2-env/env.py GRADE_CMD",
        "agent_runs_as_root": True,
        "trusted_test_digest": "ad132b324e84c2ab09460b73f4a74284bbe28b4e5c34fde80a22e0015e10c7f1",
        "witness_id": witness["witness_id"],
        "witness_reward": witness_reward,
        "witness_killed": witness_killed,
        "control_rewards": control_rewards,
        "controls_preserved": controls_preserved,
        "root_subversion_rewards": attack_rewards,
        "root_subversions_blocked": attacks_blocked,
        "deploy_form_pass": witness_killed and controls_preserved and attacks_blocked,
        "upload_performed": False,
        "verified_at": utc_now(),
    }
    record["content_digest"] = digest_json(record)
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"\nWROTE {OUT.relative_to(ROOT)}")
    print(f"DEPLOY_FORM_PASS={record['deploy_form_pass']} (witness_killed={witness_killed}, "
          f"controls_preserved={controls_preserved}, root_subversions_blocked={attacks_blocked})")
    return 0 if record["deploy_form_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
