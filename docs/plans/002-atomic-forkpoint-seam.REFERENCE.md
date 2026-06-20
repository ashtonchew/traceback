# Plan 002 reference — boundary and fidelity protocol

## Boundary protocol

Wave 1 identifies the real completed-action event. The implementation should derive a boundary token from stable HUD run/trace/action identity plus task/environment identity. HUD v6 distinguishes the `Run` lifecycle, its `Trace`, and ordered trace steps, so do not collapse those identities into a single display trace id unless the repo-bound adapter proves that is the canonical action boundary ([HUD v6 Types](https://docs.hud.ai/v6/core/types)). The exact encoding is repository-native; it must not rely on wall-clock time alone.

Atomic capture conceptually performs:

1. Observe completed action `t`.
2. Stop accepting action `t+1`.
3. Flush task-visible side effects and file evidence for `t`; HUD file diffs are acceptable only when File Tracking was enabled before the source trace, because future traces capture filesystem changes after the setting is enabled ([HUD File Tracking](https://docs.hud.ai/platform/file-tracking)).
4. Freeze the agent-visible history through `t`, including tool result.
5. Capture the selected executable state at the same quiescent point.
6. Compute/store history and state integrity data.
7. Persist all required identity fields.
8. Finalize the ForkPoint.
9. Re-enable execution or end the source run.

Any failure before finalization rolls back or marks temporary provider state for cleanup. Modal's Sandbox API exposes explicit `terminate`/`detach` lifecycle calls and `Sandbox.exec` command handles, so cleanup and quiescence checks should be observable through provider operations rather than assumed from local object disposal ([Modal Sandboxes](https://modal.com/docs/guide/sandboxes), [Modal running commands](https://modal.com/docs/guide/sandbox-spawn)).

## Fidelity probes

Choose probes that distinguish the selected MongoDB-task state from its predecessor and successor. Examples must be grounded in the real trace and may include:

- expected working-tree diff,
- installed package/plugin metadata,
- file hashes,
- process/service readiness when relevant,
- task command output,
- environment variables excluding secrets,
- grader-visible state,
- history's final action and observation.

Do not use a probe that simply reads the ForkPoint manifest back. Prefer probes that grade the world state the agent left behind, matching HUD's v6 guidance that reliable grading often checks task-visible system state rather than only the final answer ([HUD v6 Tasks & Tasksets](https://docs.hud.ai/v6/core/tasks)).

## Six required scenarios

| Scenario | Expected public behavior |
|---|---|
| Valid capture | Finalized ForkPoint with complete required fields. |
| Valid restore | Isolated environment and history reproduce task-visible probes. |
| Boundary mismatch | Restore/capture rejects before branch execution. |
| History mismatch | Hash/token mismatch rejects and identifies `history_mismatch`. |
| Grader mismatch | Evaluation cannot start under a different digest. |
| Unsupported mode | Capture refuses when core snapshot cannot cover true state. |

Also test partial capture cleanup and immutable record behavior where the repository's persistence supports it.

## Snapshot decision record

Record:

- observed task state locations, including `/app`, MongoDB `dbpath` and logs, `/tmp`, `$HOME`, virtualenv/cache paths, Python site-packages, pytest plugin/conftest discovery paths, mounted volumes, and service sockets,
- the verified `task_state_root` when Directory Snapshot is selected, or the reason no single subtree honestly contains branch-relevant mutable state,
- chosen mode,
- rejected modes and why,
- capability probe output,
- provider object id,
- retention/expiry,
- explicit expired-snapshot failure handling,
- image/runtime identity,
- restore command/result,
- network policy and resource limits,
- secret-mount exclusion,
- durable fallback where applicable.

Modal Directory Snapshots are Beta and capture a specific directory for later mounting; they are a sufficient core profile only when all branch-relevant mutable state is under that directory and the base image/runtime are pinned. Filesystem Snapshots capture the Sandbox filesystem as an Image; Memory Snapshots are Alpha; VM Sandboxes are Alpha and currently support Filesystem Snapshots but not Memory Snapshots. Treat Directory/Filesystem as the core choices and record any Memory/VM dependency as a STOP or Plan 007 research path ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots), [Modal VM Sandboxes](https://modal.com/docs/guide/vm-sandboxes), [modal.Sandbox API](https://modal.com/docs/sdk/py/latest/modal.Sandbox)).

Modal Sandboxes have no inbound access and no access to Modal resources by default, but they can make outbound public network connections unless `block_network` or outbound allowlists are configured. Snapshot evidence must therefore include the actual network setting, not only a generic "sandboxed" claim ([Modal Sandbox networking](https://modal.com/docs/guide/sandbox-networking)).

## MongoDB task snapshot probes

For the Terminal Wrench `mongodb-sales-aggregation-engine` task, do not treat `/app` as the snapshot boundary until proven. The task image seeds MongoDB under `/data/db`, starts `mongod` with `/var/log/mongodb.log`, and the verifier script installs/runs pytest and pymongo before executing the tests; the known attack family targets pytest/plugin surfaces rather than MongoDB business logic ([Terminal Wrench Dockerfile](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/original_task/environment/Dockerfile), [Terminal Wrench verifier script](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/original_task/tests/test.sh), [Terminal Wrench tests](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/original_task/tests/test_outputs.py), [Terminal Wrench hack summary](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/hack_summary.md)).

Directory Snapshot is valid only after a probe proves one of these:

- All branch-relevant mutable state is under one `task_state_root`, and trusted verifier/test assets are outside branch-writable state.
- State outside the directory is deterministic from pinned base inputs and is recreated before branch execution.
- A repository-native layout conversion moved MongoDB `dbpath`, task-local caches, virtualenvs, and branch-writable runtime state under the task state root without changing task behavior.

Use Filesystem Snapshot when any relevant state remains outside that root, including MongoDB data/log mutation, pytest plugin installation, mutated Python package files, hidden caches, or branch-writable verifier assets. STOP rather than approximating if live process state is required and cannot be converted into a durable Directory/Filesystem restore.

Required capability probes:

- Directory probe: write marker files, package/plugin markers, and Mongo-visible state under the candidate `task_state_root`; snapshot, mount into a fresh Sandbox, and verify hashes plus task-visible outputs.
- Filesystem probe: write markers inside and outside the working directory; snapshot and restore; verify both expected markers and absence of prohibited secrets.
- MongoDB probe: verify `mongod` readiness, `dbpath`, seeded collections, restart behavior, and grader-visible database state after restore.
- Pytest/plugin probe: enumerate `conftest.py`, `PYTEST_DISABLE_PLUGIN_AUTOLOAD`, pytest plugin entry points, site-packages mutability, cwd/rootdir, and import path ordering; record contamination risk for Plan 005 without patching it here.
- Security probe: record network setting, secret mounts, sibling writable roots, resource limits, and trusted-evidence write isolation.
- Expiry probe: record snapshot TTL, provider object id retention, and expired/unavailable-snapshot error mapping.

Plan 005 owns verifier hardening for this pytest/plugin attack surface, tracked in [GitHub issue #7](https://github.com/ashtonchew/hack2fix2hack/issues/7). Plan 007 owns VM and Memory research capability probes, tracked in [GitHub issue #8](https://github.com/ashtonchew/hack2fix2hack/issues/8). Do not add Plan 005 or Plan 007 implementation scope to Plan 002.

## ForkPoint minimum evidence

The evidence manifest should link, not duplicate:

- source trace and selected step,
- QA result and file diff,
- task/environment id,
- snapshot provider object,
- history artifact,
- state/history hashes,
- grader and image digests,
- fidelity probe command/output,
- failure-case test output.

## Common mistakes

- Snapshotting before the tool result enters history.
- Truncating history at a display step that does not equal the runtime action boundary.
- Patching or reading a “latest” grader during restore.
- Treating filesystem presence as proof that process state is irrelevant.
- Capturing broad home directories that contain secrets.
- Hiding a mismatched restore behind a retry from scratch.
- Assuming a provider can clean up untracked snapshots; persist provider object ids before any operation that may create an orphaned snapshot.
