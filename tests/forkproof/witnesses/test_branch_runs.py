from __future__ import annotations

import asyncio
import sys
import types

import forkproof.witnesses.branch_runs as branch_runs


def forkpoint(**overrides):
    base = {
        "fork_point_id": "fp-001",
        "parent_node_id": "node-001",
        "snapshot_id": "im-1",
        "snapshot_restore_ref": "modal-image://im-1",
        "snapshot_mode": "filesystem",
        "snapshot_digest": "snapshot-sha",
        "environment_version": "env-v1",
        "environment_image_digest": "image-sha",
        "grader_digest": "grader-sha",
        "grader_digest_source": "status.json:grader",
        "history_prefix_ref": "history-ref",
        "history_hash": "history-sha",
        "boundary_token": "boundary-token",
        "network_policy": "block_network=True",
        "secret_policy": "secrets=[]",
        "resource_policy": "cpu=0.5,memory=1024,timeout=900",
        "snapshot_retention": "modal-default-ttl",
        "source_evidence_refs": ["status.json"],
    }
    base.update(overrides)
    return base


def install_fake_hud_modules(monkeypatch, *, runtime_raises=False):
    modal = types.ModuleType("modal")

    class Image:
        @staticmethod
        def from_id(image_id):
            return f"image:{image_id}"

    modal.Image = Image
    monkeypatch.setitem(sys.modules, "modal", modal)

    agent_module = types.ModuleType("hud.agents.claude.agent")

    class ClaudeAgent:
        def __init__(self, config):
            self.config = config

    class ClaudeConfig:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

    agent_module.ClaudeAgent = ClaudeAgent
    agent_module.ClaudeConfig = ClaudeConfig
    monkeypatch.setitem(sys.modules, "hud", types.ModuleType("hud"))
    monkeypatch.setitem(sys.modules, "hud.agents", types.ModuleType("hud.agents"))
    monkeypatch.setitem(sys.modules, "hud.agents.claude", types.ModuleType("hud.agents.claude"))
    monkeypatch.setitem(sys.modules, "hud.agents.claude.agent", agent_module)

    runtime_module = types.ModuleType("hud.eval.runtime")

    class ModalRuntime:
        def __init__(self, *args, **kwargs):  # noqa: ARG002
            if runtime_raises:
                raise RuntimeError("runtime setup failed")

    runtime_module.ModalRuntime = ModalRuntime
    monkeypatch.setitem(sys.modules, "hud.eval", types.ModuleType("hud.eval"))
    monkeypatch.setitem(sys.modules, "hud.eval.runtime", runtime_module)


def test_branch_runtime_setup_failure_is_not_counted_as_executed(monkeypatch, tmp_path):
    install_fake_hud_modules(monkeypatch, runtime_raises=True)

    result = asyncio.run(
        branch_runs._run_one_branch(
            root=tmp_path,
            forkpoint=forkpoint(),
            task=object(),
            run_id="run-001",
            branch_index=0,
            artifact_root=tmp_path / "artifacts",
        )
    )

    record = result["branch"]
    assert record["execution_boundary_crossed"] is False
    assert record["gateway_request_ids"] == []
    assert record["status"] == "agent-error"


def test_branch_records_preserve_forkpoint_identity(monkeypatch, tmp_path):
    install_fake_hud_modules(monkeypatch)
    monkeypatch.setattr(
        branch_runs,
        "_trace_readback",
        lambda trace_id: {"trace": {"id": trace_id}, "events": {"events": []}},
    )
    monkeypatch.setattr(
        branch_runs,
        "run_reward_hacking_analysis",
        lambda root, trace_id, *, branch_id, action_record_digest: {
            "status": "pass",
            "qa_result_id": "qa-001",
            "branch_id": branch_id,
            "hud_trace_id": trace_id,
            "action_record_digest": action_record_digest,
            "authoritative_source": "repo_bound_hud_qa",
            "is_reward_hacking": False,
        },
    )

    class Job:
        id = "job-001"
        trace_id = "trace-001"
        reward = 1.0
        runs = []

    class Task:
        async def run(self, agent, runtime):  # noqa: ARG002
            return Job()

    source = forkpoint(environment_image_digest="image-real", grader_digest="grader-real")
    result = asyncio.run(
        branch_runs._run_one_branch(
            root=tmp_path,
            forkpoint=source,
            task=Task(),
            run_id="run-001",
            branch_index=0,
            artifact_root=tmp_path / "artifacts",
        )
    )

    record = result["branch"]
    assert record["execution_boundary_crossed"] is True
    assert record["environment_image_digest"] == "image-real"
    assert record["grader_digest"] == "grader-real"
    assert record["history_hash"] == source["history_hash"]
    assert record["snapshot_digest"] == source["snapshot_digest"]
    assert record["provenance_status"] == "incomplete"


def test_branch_batch_status_blocks_on_incomplete_provenance(monkeypatch, tmp_path):
    monkeypatch.setenv("MODAL_TOKEN_ID", "present")
    monkeypatch.setenv("MODAL_TOKEN_SECRET", "present")
    monkeypatch.setenv("HUD_API_KEY", "present")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "present")
    monkeypatch.setenv("FORKPROOF_ALLOW_EXTERNAL_QA", "1")
    monkeypatch.setattr(branch_runs, "_load_hud_task", lambda root: object())

    async def fake_run_one_branch(**kwargs):
        branch = {
            "branch_id": f"branch-{kwargs['branch_index']}",
            "seed": kwargs["branch_index"],
            "hud_trace_id": f"trace-{kwargs['branch_index']}",
            "reward": 1.0,
            "promotion_signal_status": "rewarded-non-hack",
            "execution_boundary_crossed": True,
            "provenance_blockers": ["filesystem diff capture remains a promotion gate"],
        }
        return {
            "branch": branch,
            "qa": {"status": "pass", "is_reward_hacking": False},
            "branch_ref": "branch.json",
            "qa_ref": "qa.json",
            "action_record_ref": "action.json",
            "file_diff_ref": "diff.json",
        }

    monkeypatch.setattr(branch_runs, "_run_one_branch", fake_run_one_branch)
    result = asyncio.run(branch_runs.run_live_branch_batch(tmp_path, forkpoint(), count=2, concurrency=2))
    assert result["live_execution_status"] == "pass"
    assert result["provenance_status"] == "incomplete"
    assert result["status"] == "blocked"
    assert result["executed_branch_count"] == 2
