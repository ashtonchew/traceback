from __future__ import annotations

import json

import pytest

from forkproof.releases.models import ReleaseError, digest_json
from forkproof.releases.proofset import build_proofset
from forkproof.releases.release_evaluation import load_release_results, run_release_evaluation
from forkproof.releases.harden_adapter import (
    DEFAULT_ANTHROPIC_HARDEN_MODEL,
    require_selected_model_credentials,
    select_harden_models,
)


def witness():
    return {
        "schema_version": 1,
        "witness_id": "wit-001",
        "source_branch_id": "branch-001",
        "pre_attack_snapshot_ref": "modal-image://im-1",
        "durable_snapshot_mode": "filesystem",
        "history_prefix_ref": "history.json",
        "recorded_actions_ref": "actions.json",
        "action_record_digest": "actions-sha",
        "file_diff_ref": "diff.json",
        "verifier_output_ref": "verifier.json",
        "qa_result_ref": "qa-001",
        "qa_join": {
            "qa_result_id": "qa-001",
            "branch_id": "branch-001",
            "hud_trace_id": "trace-001",
            "action_record_digest": "actions-sha",
            "authoritative_source": "hud_qa",
            "evidence_quality": "sufficient",
            "task_identity_status": "matched",
        },
        "qa_is_reward_hacking": True,
        "source_hud_trace_id": "trace-001",
        "environment_version": "env-v1",
        "environment_image_digest": "image-sha",
        "grader_digest": "grader-v1",
        "reward": 1.0,
        "seed": 1,
        "model": "model",
        "sampling_config": {"temperature": 0.8},
        "exploit_target": "reward-verifier:grader_exploitation",
        "exploit_mechanism": "textual-causal-delta:/task/hook.py",
        "evaluator_profile": "pytest",
        "cluster_id": "cluster-001",
        "dedup_decision": {"cluster_id": "cluster-001", "decision": "new"},
        "replay_surface": {
            "schema_version": 1,
            "replay_surface_id": "surface-001",
            "environment_version": "env-v1",
            "grader_digest": "grader-v1",
            "command_argv": ["grader", "run", "--case", "sealed-witness"],
            "cwd": "/workspace",
            "pre_grader_command_argv": [],
            "grader_command_argv": ["grader", "grade", "--case", "sealed-witness"],
            "state_restore_ref": "modal-image://im-1",
            "trusted_entrypoint_ref": "grader://entrypoint",
            "captured_at": "2026-06-21T00:00:00Z",
        },
        "replay_entrypoint": "forkproof.witnesses.sealing",
        "replay_checks": [
            {"attempt": 1, "reward": 1.0, "model_gateway_request_ids": []},
            {"attempt": 2, "reward": 1.0, "model_gateway_request_ids": []},
            {"attempt": 3, "reward": 1.0, "model_gateway_request_ids": []},
        ],
        "content_digest": "digest",
        "retention_policy": "retain-for-release-regression",
        "created_at": "2026-06-21T00:00:00Z",
    }


def control(control_id):
    return {
        "schema_version": 1,
        "control_id": control_id,
        "task_id": "task",
        "grader_digest": "grader-v1",
        "verifier_harness_digest": "harness-sha",
        "environment_dockerfile_digest": "dockerfile-sha",
        "solution_ref": f"fixtures/{control_id}.py",
        "content_digest": "control-sha",
        "environment_version": "env-v1",
        "task_checksum": "task-sha",
        "baseline_runs": [
            {"run_id": f"{control_id}-1", "reward": 1.0},
            {"run_id": f"{control_id}-2", "reward": 1.0},
            {"run_id": f"{control_id}-3", "reward": 1.0},
        ],
        "frozen_at": "2026-06-21T00:00:00Z",
    }


def proofset():
    return build_proofset(
        witnesses=[witness()],
        controls=[control("control-a"), control("control-b"), control("control-c")],
        taskset_or_suite_ref="suite://proofset",
        selection_query_ref="evidence/query.json",
    )


def test_proofset_infers_pytest_profile_from_replay_surface():
    record = witness()
    del record["evaluator_profile"]
    record["replay_surface"]["grader_command_argv"] = ["python", "-m", "pytest", "tests/test_outputs.py"]

    ps = build_proofset(
        witnesses=[record],
        controls=[control("control-a"), control("control-b"), control("control-c")],
        taskset_or_suite_ref="suite://proofset",
        selection_query_ref="evidence/query.json",
    )

    assert ps["evaluator_profiles"] == ["pytest"]


def result(case_id, kind, reward, grader, environment="env-v1"):
    return {
        "case_id": case_id,
        "case_kind": kind,
        "reward": reward,
        "environment_version": environment,
        "grader_digest": grader,
        "trace_ref": f"trace://{case_id}",
    }


def evaluator_context():
    return {
        "context_id": "context-v2-001",
        "phase": "v2",
        "environment_version": "env-v2",
        "grader_path": "/opt/forkproof/grader/grader.py",
        "grader_digest": "grader-v2",
        "grader_entrypoint_digest": "entrypoint-sha",
        "cwd": "/workspace/release",
        "rootdir": "/workspace/release",
        "python_executable": "/opt/venv/bin/python",
        "python_executable_digest": "python-sha",
        "import_path": ["/opt/forkproof/grader", "/opt/venv/lib/python/site-packages"],
        "verifier_plugins": ["pytest-json-report"],
        "evaluator_profile_details": {"pytest_plugins": ["pytest-json-report"]},
        "test_asset_digests": {"/opt/forkproof/tests/test_release.py": "test-sha"},
        "trusted_test_roots": ["/opt/forkproof/tests"],
        "untrusted_writable_roots": ["/workspace/branch"],
        "captured_at": "2026-06-21T00:00:00Z",
    }


def subversion_results():
    return [
        {"case_id": case_id, "status": "blocked"}
        for case_id in sorted(
            {
                "conftest.py",
                "pytest11",
                "hook/TestReport fabrication",
                "cwd/import shadowing",
                "site-packages mutation",
                "trusted test replacement",
            }
        )
    ]


def test_release_evaluation_fails_closed_without_per_case_results(tmp_path):
    ps = proofset()

    with pytest.raises(ReleaseError, match="release evaluation blocked"):
        run_release_evaluation(
            repo_root=tmp_path,
            proof_set=ps,
            harden_task_source=None,
            harden_task_id=None,
            release_results_ref=None,
            artifact_root=tmp_path / "artifacts",
            harden_max_iterations=1,
            harden_timeout_seconds=1,
        )

    blocker_path = tmp_path / "artifacts/release-blockers" / f"{ps['proof_set_id']}.json"
    blocker = json.loads(blocker_path.read_text(encoding="utf-8"))
    assert blocker["status"] == "blocked"
    assert "v2_results" in blocker["missing_evidence"]
    assert blocker["mandatory_subversion_case_ids"] == sorted(
        {
            "conftest.py",
            "pytest11",
            "hook/TestReport fabrication",
            "cwd/import shadowing",
            "site-packages mutation",
            "trusted test replacement",
        }
    )


def test_release_evaluation_seals_from_real_result_contract(tmp_path):
    ps = proofset()
    release_results = {
        "environment_v2": "env-v2",
        "grader_v2_digest": "grader-v2",
        "patch_ref": "artifacts/forkproof/releases/patches/patch.diff",
        "fixer_run_ref": "artifacts/forkproof/releases/harden-runs/result.json",
        "v1_results": [result("wit-001", "witness", 1.0, "grader-v1")],
        "v2_results": [result("wit-001", "witness", 0.0, "grader-v2", "env-v2")],
        "evaluator_context_refs": [evaluator_context()],
        "subversion_results": subversion_results(),
        "release_candidate_ref": "artifacts/forkproof/releases/candidates/v2.json",
    }
    release_results["content_digest"] = digest_json(release_results)
    results_path = tmp_path / "release-results.json"
    results_path.write_text(json.dumps(release_results), encoding="utf-8")

    record = run_release_evaluation(
        repo_root=tmp_path,
        proof_set=ps,
        harden_task_source=None,
        harden_task_id=None,
        release_results_ref=results_path,
        artifact_root=tmp_path / "artifacts",
        harden_max_iterations=1,
        harden_timeout_seconds=1,
    )

    assert record["status"] == "pass"
    assert record["release_proof"]["gate_status"] == "pass"
    assert record["release_proof_ref"].endswith(".json")


def test_release_results_loader_requires_complete_case_contract(tmp_path):
    path = tmp_path / "release-results.json"
    path.write_text(json.dumps({"environment_v2": "env-v2"}), encoding="utf-8")

    with pytest.raises(ReleaseError, match="release results missing"):
        load_release_results(path)


def test_release_evaluation_requires_harden_source_and_id_together(tmp_path):
    with pytest.raises(ReleaseError, match="provided together"):
        run_release_evaluation(
            repo_root=tmp_path,
            proof_set=proofset(),
            harden_task_source=tmp_path,
            harden_task_id=None,
            release_results_ref=None,
            artifact_root=tmp_path / "artifacts",
            harden_max_iterations=1,
            harden_timeout_seconds=1,
        )


def test_harden_model_selection_uses_anthropic_fallback_not_gemini(monkeypatch):
    monkeypatch.delenv("H2F2H_HARDEN_MODEL", raising=False)
    monkeypatch.delenv("H2F2H_HACKER_MODEL", raising=False)
    monkeypatch.delenv("H2F2H_FIXER_MODEL", raising=False)
    monkeypatch.delenv("H2F2H_SOLVER_MODEL", raising=False)
    monkeypatch.delenv("FORKPROOF_BRANCH_MODEL", raising=False)

    selected = select_harden_models(hacker_model=None, fixer_model=None, solver_model=None)

    assert selected == {
        "hacker_model": DEFAULT_ANTHROPIC_HARDEN_MODEL,
        "fixer_model": DEFAULT_ANTHROPIC_HARDEN_MODEL,
        "solver_model": DEFAULT_ANTHROPIC_HARDEN_MODEL,
    }


def test_harden_model_credentials_fail_fast_for_selected_provider(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ReleaseError, match="Gemini/Google"):
        require_selected_model_credentials({"solver_model": "gemini/gemini-3.1-pro-preview"})

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ReleaseError, match="Anthropic"):
        require_selected_model_credentials({"solver_model": DEFAULT_ANTHROPIC_HARDEN_MODEL})
