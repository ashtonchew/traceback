"""Create a ForkPoint from an orchestrated accepted-trace rerun."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from .core import (
    ForkPointStore,
    boundary_token,
    capture_forkpoint,
    digest_json,
    load_source_trace,
    restore_forkpoint,
)
from .replay_probe import _exec, _image, _replay, _setup_command, _trace_events

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs" / "plans" / "evidence" / "002" / "artifacts"
HUD_STEP_ID = "completed-action:accepted-trace-rerun-before-scenario-evaluate"


def _history_prefix(replay: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "role": "system",
            "content_sha256": digest_json(
                {
                    "source": "accepted HUD trace export",
                    "boundary": HUD_STEP_ID,
                    "raw_history_committed": False,
                }
            ),
        },
        {
            "role": "tool_replay_summary",
            "replayed_tool_count": len(replay["replayed"]),
            "skipped_tool_count": len(replay["skipped"]),
            "replayed_tools_sha256": digest_json(replay),
        },
    ]


def _last_replayed_id(replay: dict[str, Any]) -> str:
    last = replay["replayed"][-1]
    return str(last.get("id") or last.get("seq") or HUD_STEP_ID)


def _quiesce(sb: Any) -> dict[str, str]:
    before = _exec(sb, "pgrep -x mongod >/dev/null && echo running || echo stopped").strip()
    _exec(
        sb,
        "python3 - <<'PY'\n"
        "from pymongo import MongoClient\n"
        "MongoClient('mongodb://localhost:27017').admin.command({'fsync': 1})\n"
        "PY\n"
        "sync",
        timeout=60,
    )
    after = _exec(sb, "pgrep -x mongod >/dev/null && echo running || echo stopped").strip()
    return {
        "mongod_before_quiesce": before,
        "mongod_after_quiesce": after,
        "strategy": "trusted orchestrator MongoDB fsync plus filesystem sync before snapshot",
    }


def _security_probe(sb: Any) -> dict[str, str]:
    script = (
        "python3 - <<'PY'\n"
        "from pathlib import Path\n"
        "import json, socket\n"
        "result = {\n"
        "  'root_env': 'present' if Path('/root/.env').exists() else 'absent',\n"
        "  'docker_sock': 'present' if Path('/var/run/docker.sock').exists() else 'absent',\n"
        "}\n"
        "try:\n"
        "    socket.create_connection(('169.254.169.254', 80), timeout=2).close()\n"
        "    result['metadata_network'] = 'reachable'\n"
        "except OSError:\n"
        "    result['metadata_network'] = 'blocked'\n"
        "print(json.dumps(result, sort_keys=True))\n"
        "PY"
    )
    return json.loads(_exec(sb, script, timeout=20).strip())


class ModalForkPointProvider:
    def __init__(self, sandbox: Any, app: Any):
        self._sandbox = sandbox
        self._app = app
        self._snapshots: dict[str, Any] = {}
        self._restored: Any | None = None

    def capture(self, state: dict[str, Any], mode: str) -> dict[str, Any]:
        if mode != "filesystem":
            raise ValueError("Modal live boundary probe supports filesystem mode only")
        snapshot = self._sandbox.snapshot_filesystem()
        self._snapshots[snapshot.object_id] = snapshot
        return {
            "snapshot_id": snapshot.object_id,
            "snapshot_mode": "filesystem",
            "snapshot_digest": digest_json(
                {
                    "snapshot_id": snapshot.object_id,
                    "query_sha": state["query_py_sha256"],
                    "history_hash": state["history_prefix_sha256"],
                }
            ),
            "snapshot_restore_ref": f"modal-image://{snapshot.object_id}",
            "snapshot_retention": "modal-default-ttl",
            "network_policy": "block_network=True",
            "secret_policy": "secrets=[]",
            "resource_policy": "cpu=0.5,memory=1024,timeout=900",
        }

    def restore(self, snapshot_id: str) -> dict[str, Any]:
        if snapshot_id not in self._snapshots:
            raise KeyError(snapshot_id)
        import modal

        self._restored = modal.Sandbox.create(
            image=self._snapshots[snapshot_id],
            app=self._app,
            block_network=True,
            secrets=[],
            cpu=0.5,
            memory=1024,
            timeout=300,
            workdir="/app",
            tags={"forkproof_plan": "002", "purpose": "live_boundary_restore"},
        )
        _exec(self._restored, "mongod --fork --logpath /var/log/mongodb.log --dbpath /data/db", timeout=60)
        query_sha = _exec(self._restored, "sha256sum /app/query.py | awk '{print $1}'").strip()
        grader = _exec(
            self._restored,
            "python3 -m pytest task_assets/test_outputs.py -q > /tmp/grade.log 2>&1; "
            "rc=$?; tail -20 /tmp/grade.log; exit $rc",
            timeout=180,
        )
        security = _security_probe(self._restored)
        return {
            "task_state_root": "/",
            "query_py_sha256": query_sha,
            "restored_grade_output_sha256": digest_json(grader),
            "restored_sandbox_probe": "query hash and pytest grader executed after restore",
            "security_probe": security,
        }

    def cleanup(self, snapshot_id: str) -> None:
        self._snapshots.pop(snapshot_id, None)

    def close(self) -> None:
        if self._restored is not None:
            self._restored.terminate()


def run_live_boundary_probe() -> dict[str, Any]:
    import modal

    source = load_source_trace(ROOT / "docs" / "plans" / "repo-map" / "STATUS.json")
    events = _trace_events()
    app = modal.App.lookup("forkproof-plan-002", create_if_missing=True)
    sb = modal.Sandbox.create(
        image=_image(),
        app=app,
        block_network=True,
        secrets=[],
        cpu=0.5,
        memory=1024,
        timeout=900,
        workdir="/app",
        tags={"forkproof_plan": "002", "purpose": "live_boundary_capture"},
    )
    provider = ModalForkPointProvider(sb, app)
    try:
        _exec(sb, _setup_command(), timeout=180)
        replay = _replay(events, sb)
        query_sha = _exec(sb, "sha256sum /app/query.py | awk '{print $1}'").strip()
        quiesce = _quiesce(sb)
        history = _history_prefix(replay)
        task_state = {
            "task_state_root": "/",
            "query_py_sha256": query_sha,
            "history_prefix_sha256": digest_json(history),
            "completed_action_boundary": HUD_STEP_ID,
            "last_replayed_tool_id": _last_replayed_id(replay),
            "quiesce": quiesce,
        }
        with tempfile.TemporaryDirectory(prefix="forkpoint-live-boundary-") as tmp:
            store = ForkPointStore(Path(tmp))
            record = capture_forkpoint(
                source=source,
                hud_step_id=HUD_STEP_ID,
                history_prefix=history,
                task_state=task_state,
                snapshot_mode="filesystem",
                provider=provider,
                store=store,
            )
            handoff = restore_forkpoint(
                record=record,
                provider=provider,
                expected_boundary_token=boundary_token(source, HUD_STEP_ID),
                history_prefix=history,
                grader_digest=source["grader_digest"],
            )
        result = {
            "status": "live-boundary-rerun-forkpoint-pass",
            "hud_trace_id": source["hud_trace_id"],
            "fork_point_id": record["fork_point_id"],
            "hud_step_id": HUD_STEP_ID,
            "boundary_token": record["boundary_token"],
            "history_hash": record["history_hash"],
            "history_prefix_ref": record["history_prefix_ref"],
            "snapshot_id": record["snapshot_id"],
            "snapshot_mode": record["snapshot_mode"],
            "snapshot_digest": record["snapshot_digest"],
            "snapshot_restore_ref": record["snapshot_restore_ref"],
            "snapshot_retention": record["snapshot_retention"],
            "query_py_sha256": query_sha,
            "restored_query_py_sha256": handoff["task_visible_probe"]["query_py_sha256"],
            "restored_grade_output_sha256": handoff["task_visible_probe"]["restored_grade_output_sha256"],
            "environment_image_digest": handoff["environment_image_digest"],
            "replayed_tool_count": len(replay["replayed"]),
            "skipped_tool_count": len(replay["skipped"]),
            "replayed_tools_sha256": digest_json(replay),
            "quiesce": quiesce,
            "handoff_keys": sorted(handoff),
            "network_policy": record["network_policy"],
            "secret_policy": record["secret_policy"],
            "resource_policy": record["resource_policy"],
            "source_evidence_refs": record["source_evidence_refs"],
            "security_probe": handoff["task_visible_probe"]["security_probe"],
            "limitations": [
                "This is an orchestrated rerun from the accepted trace export with a retained Modal sandbox handle.",
                "It is not the already-finished historical sandbox instance from the original HUD run.",
                "Raw tool commands and outputs are not committed; history and replay evidence are hash-only.",
                "Environment image identity is a deterministic source-tree digest, not a registry manifest digest.",
            ],
        }
        EVIDENCE.mkdir(parents=True, exist_ok=True)
        path = EVIDENCE / "live-boundary-forkpoint.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return result
    finally:
        provider.close()
        sb.terminate()


def main() -> int:
    result = run_live_boundary_probe()
    print(
        "PASS live-boundary-forkpoint "
        f"fork_point={result['fork_point_id']} snapshot={result['snapshot_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
