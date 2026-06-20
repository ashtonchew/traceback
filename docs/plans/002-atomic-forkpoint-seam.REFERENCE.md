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

- observed task state locations,
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
