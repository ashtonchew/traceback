# Plan 002 reference — boundary and fidelity protocol

## Boundary protocol

Wave 1 identifies the real completed-action event. The implementation should derive a boundary token from stable trace/action identity plus task/environment identity. The exact encoding is repository-native; it must not rely on wall-clock time alone.

Atomic capture conceptually performs:

1. Observe completed action `t`.
2. Stop accepting action `t+1`.
3. Flush task-visible side effects and file evidence for `t`.
4. Freeze the agent-visible history through `t`, including tool result.
5. Capture the selected executable state at the same quiescent point.
6. Compute/store history and state integrity data.
7. Persist all required identity fields.
8. Finalize the ForkPoint.
9. Re-enable execution or end the source run.

Any failure before finalization rolls back or marks temporary provider state for cleanup.

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

Do not use a probe that simply reads the ForkPoint manifest back.

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
- image/runtime identity,
- restore command/result,
- secret-mount exclusion,
- durable fallback where applicable.

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
