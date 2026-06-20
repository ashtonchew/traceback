---
name: atomic-forkpoint-seam
description: >
  Implements the trace-to-executable-state seam that creates and restores one immutable ForkPoint with matching history, snapshot, task/environment identity, file evidence, and grader digest. Use when Plan 001 has accepted the real HUD/Modal paths and commands; it owns src/forkproof/forkpoints/**, tests/forkproof/forkpoints/**, this plan/reference, and evidence/002/**.
owns: ["docs/plans/002-atomic-forkpoint-seam.md", "docs/plans/002-atomic-forkpoint-seam.REFERENCE.md", "src/forkproof/forkpoints/**", "tests/forkproof/forkpoints/**", "docs/plans/evidence/002/**"]
depends_on: ["repo-grounding-and-command-freeze"]
wave: 2
---

# Atomic ForkPoint seam

## Goal

Create one real ForkPoint whose executable state and agent history match exactly one completed-action boundary, and pass six behavior cases: successful capture, successful restore, boundary mismatch rejection, history mismatch rejection, grader mismatch rejection, and unsupported snapshot-mode rejection. Done is binary when all six pass on the accepted integration surface.

## Context / Why

A ForkPoint is the shared object between HUD's semantic trace and Modal's executable state. HUD v6 treats a `Run` as the live handle for one task and its `Trace`, and the trace is the ordered trajectory the agent fills; Plan 002 therefore binds a HUD run/trace action boundary to the matching Modal Sandbox state rather than treating a trace id alone as executable state ([HUD v6 Types](https://docs.hud.ai/v6/core/types)). If state is captured after action `t` but history is truncated before or after a different action, every continuation is contaminated: the agent remembers a world it did not restore or loses observations that the state already reflects.

This slice owns source-trace normalization, boundary selection, atomic capture, core snapshot-profile decision, immutable ForkPoint persistence, and restore fidelity. External citations in this plan are non-normative grounding only; the exact API behavior must be bound by Wave 1 repo-map evidence. No cited HUD or Modal document is treated as providing a built-in atomic "trace step plus executable snapshot" transaction. Plan 002 must prove that repository-level invariant itself. It does not run stochastic attacks. Read the sibling reference before WP2 for the boundary protocol and fidelity scenarios.

Verifier-hardening and Alpha research follow-ups are intentionally outside this plan's ownership. Track the pytest/plugin verifier hardening in [GitHub issue #7](https://github.com/ashtonchew/hack2fix2hack/issues/7) and VM/Memory research capability gates in [GitHub issue #8](https://github.com/ashtonchew/hack2fix2hack/issues/8); Plan 002 only records enough state, provenance, and STOP evidence for those later plans to consume.

## Constraints

- Start only when `docs/plans/repo-map/STATUS.json` is `accepted`, Plan 001 evidence is complete, `plan-002-tests` and `integration-forkpoint` have verified mapped argv, and this plan's ownership bindings are accepted.
- Use the real suspicious reward-1 trace and real HUD file/QA evidence; HUD task runs expose graded reward and trace/job identifiers that must be normalized from the repo-bound adapter rather than inferred from display order ([HUD v6 Tasks & Tasksets](https://docs.hud.ai/v6/core/tasks), [HUD v6 Types](https://docs.hud.ai/v6/core/types)).
- Bind to the repository's completed-action event; do not infer timing from array position alone.
- Capture state and history as one logical transaction. Partial ForkPoints are invalid and cleaned up.
- Use a verified Directory Snapshot core path when sufficient; use the verified Filesystem fallback when necessary. Directory Snapshots are a Beta Modal Sandbox feature for a specific directory, Filesystem Snapshots capture the Sandbox filesystem as an Image, Memory Snapshots remain Alpha, and VM Sandboxes have only partial snapshot compatibility; do not depend on Memory or VM Alpha capabilities for the core path ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots), [Modal VM Sandboxes](https://modal.com/docs/guide/vm-sandboxes)).
- Pin task, environment version, environment image, grader digest, and `grader_digest_source`. The digest must cover the actual evaluator surface used for reward: verifier files, command argv, execution-relevant environment/config, dependency lock or installed package digests, evaluator image/runtime identity, import/plugin discovery paths, and remote environment/grader version id when applicable. Compute it from trusted orchestration outside branch-writable state. A digest from only a path, detached checkout, mutable package install, or floating "latest" lookup is a STOP.
- Persist no secret material in the history prefix, tool results, subprocess output, file evidence/diffs, snapshot metadata, evidence manifest, or provider tags. Record redaction markers/hashes and capability labels, never secret values, and record the enforced network/secret controls because Modal Sandboxes default to no inbound access but allow outbound public network unless `block_network` or allowlists are configured ([Modal Sandbox networking](https://modal.com/docs/guide/sandbox-networking)).
- Write ForkPoint evidence only from trusted orchestration into append-only or content-addressed storage outside the captured task writable state. The task environment must not be able to overwrite finalized evidence or the manifest it is meant to prove.
- STOP on missing source trace, no quiescent boundary, unknown grader identity, state that the available core snapshot modes cannot cover, unverified secret isolation, security policy failure, shared sibling writable state, branch-writable evidence, grader execution through attacker-controlled import/plugin paths, prohibited secret mounts in snapshots, or unavailable resource limits.
- Co-locate capture, restore, contract, and behavior tests in the `forkpoints` feature. Split any file over 500 lines along capture/restore/persistence seams.
- Tests assert restored observable behavior, not internal call order or class layout.

## Work packets

### WP1 — Normalize the real source trace

Read the repo-bound HUD adapter and normalize trace identity, step/action identity, task id, environment version, reward, QA result reference, and file evidence. HUD platform QA agents can return structured reward-hacking verdicts, and HUD file tracking can expose per-step file changes only when enabled before the source trace ran; Plan 002 must bind those platform signals through repository evidence rather than treating them as inferred labels, and must STOP rather than substituting a synthetic diff or later filesystem scan ([HUD QA Agents](https://docs.hud.ai/platform/agents/qa), [HUD File Tracking](https://docs.hud.ai/platform/file-tracking)). Select a defensible completed-action boundary and record the fork reason.

**Pass:** One normalized source record links the real reward-1 trace, QA result, and step-level file diff with stable ids.  
**Fail:** Evidence is copied into a synthetic fixture or boundary identity depends only on list index.

### WP2 — Implement atomic capture

At the canonical completed-action hook, derive one boundary token, freeze the exact history prefix, quiesce task processes as required by the selected core profile, capture executable state, and finalize the ForkPoint only when all pieces succeed. The boundary is valid only after action `t` has durably produced its environment side effects, observation/tool result, HUD/file evidence, and history entry, and before any model call or action `t+1` can begin. If an in-flight `exec`, background process, pending file-tracking flush, or unacknowledged observation can affect task-visible state, the boundary is not quiescent; STOP or record that state under the selected snapshot profile.

**Pass:** Injected failure after either half leaves no finalized ForkPoint and cleans temporary state.  
**Fail:** State and history can be committed independently or later “reconciled.”

### WP3 — Select and record the core snapshot profile

Inspect where the MongoDB task's branch-relevant state lives and define a `task_state_root`: the smallest directory subtree intended to contain all branch-relevant mutable filesystem state, excluding trusted grader code, secrets, and control-plane mounts. Before capture, inventory the allowlisted capture root, `/app`, MongoDB data/log state, `/tmp`, `$HOME`, task-local virtualenv/cache locations, Python site-packages and pytest plugin discovery paths, mounted secrets, cloud metadata/config paths, service sockets, volumes, and excluded paths. The handoff anchors the demo on Terminal Wrench `mongodb-sales-aggregation-engine` and describes a layered pytest/plugin exploit, while the sourced task starts MongoDB with `/data/db`, writes `/var/log/mongodb.log`, installs verifier dependencies during `tests/test.sh`, and provides reward-hacking trajectory metadata; those facts make a narrow working-directory snapshot insufficient unless Wave 1 proves a repository-native layout conversion that keeps behavior equivalent ([Hack2Fix2Hack handoff](<html-spec/hack2fix2hack-handoff (4).html>), [Terminal Wrench Dockerfile](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/original_task/environment/Dockerfile), [Terminal Wrench verifier script](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/original_task/tests/test.sh), [Terminal Wrench task metadata](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/task.json), [Terminal Wrench hack trajectory v5](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/hack_trajectories/v5/metadata.json), [Terminal Wrench hack trajectory v5_2](../../.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6/hack_trajectories/v5_2/metadata.json)).

Choose Directory Snapshot only when all branch-relevant mutable state is under one verified `task_state_root`, or when missing state is deterministically reconstructed from pinned base inputs before branch execution. The `task_state_root` must be a purpose-built task-owned subtree, not `/`, `$HOME`, `/usr`, `/var`, or another broad system directory. Deterministic reconstruction is valid only when the reconstruction recipe, pinned inputs, command argv, environment, and output hashes are recorded in ForkPoint evidence and re-executed before every restore probe; it must not overwrite, ignore, or normalize branch-relevant mutations outside `task_state_root`. If any outside-root mutation can affect reward, QA, replay, pytest/plugin loading, MongoDB state, or history-visible behavior, use the verified Filesystem path or STOP. A valid layout conversion may move MongoDB `dbpath`, branch-relevant logs, task-local caches, virtualenvs, pytest/plugin writable surfaces, and branch-writable runtime state under the task state root only when the plan records equivalence evidence; it must keep trusted grader/test assets, secrets, provider mounts, and evidence stores outside branch-writable state.

For MongoDB-backed tasks, capture must use an explicit database quiescence protocol: record `dbpath`, process id, lock/fsync or clean shutdown strategy, journal state, restart command, and post-restore readiness check. Directory or Filesystem capture is invalid unless seeded collections and grader-visible queries survive a real restart from the captured state. Filesystem Snapshot is permitted only from a sandbox constructed without production secrets, local `.env`, host credentials, cloud metadata credentials, provider admin tokens, host Docker socket, or branch-irrelevant home/config directories. Evidence must include a harmless negative probe for a disallowed network or metadata destination, the exact Modal network setting, mounted secret names or absence markers, and CPU/memory/process/disk/wall-clock limits. Reject capture when a prohibited mount, unrelated home directory, mutable grader asset, or untracked branch-relevant path falls inside or outside the selected snapshot boundary. Record mode, provider object id, creation time, retention/expiry, task state root or Filesystem rationale, source ForkPoint id, image digest, snapshot digest when supported, network policy, resource limits, secret exclusion evidence, durable fallback reference, and rationale. Modal snapshots have TTL behavior and expired snapshot restores can fail with `NotFoundError`, so expiry handling is part of the contract, not cleanup trivia ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots), [modal.Sandbox API](https://modal.com/docs/sdk/py/latest/modal.Sandbox)).

**Pass:** A capability-backed decision is part of the ForkPoint evidence and requires no Alpha access.  
**Fail:** Mode is chosen from sponsor preference rather than task state, or process-only state is silently lost.

### WP4 — Restore with fidelity checks

Restore into an isolated environment, reconstruct the exact history prefix, verify boundary token and hashes, reject any finalized ForkPoint whose `snapshot_mode` is not a verified Directory or Filesystem mode using `state_restore_failed` with reason `unsupported_snapshot_mode`, and evaluate task-visible probes that distinguish the selected moment from adjacent steps. On boundary, history, snapshot, or grader mismatch, restore returns the semantic error and produces no branch-ready handoff. It must not recapture from the source trace, replay setup from scratch, substitute another snapshot, or mark the ForkPoint usable. The restore result must expose a branch-ready handoff for Plan 003: `fork_point_id`, `task_id`, `environment_version`, `environment_image_digest`, `snapshot_restore_ref`, `snapshot_id`, `snapshot_mode`, `snapshot_digest` when supported, `history_prefix_ref`, `history_hash`, boundary token, `parent_node_id`, isolated writable root identity, `grader_digest`, `grader_digest_source`, trusted source-evidence refs, network/secret/resource policy labels, snapshot expiry/retention, durable fallback ref when applicable, and branch-tag propagation inputs. A restored Modal Sandbox must be exercised through real commands/probes, not just created, because Sandboxes expose subprocess-like execution and stream results through `Sandbox.exec` ([Modal Sandboxes](https://modal.com/docs/guide/sandboxes), [Modal running commands](https://modal.com/docs/guide/sandbox-spawn)).

**Pass:** The restored environment and history satisfy the real fidelity probes; adjacent/mismatched artifacts fail closed.  
**Fail:** Restore success means only “sandbox started” or “files exist.”

### WP5 — Seal the ForkPoint contract

Persist the required logical fields from `specs/03-interfaces.md`, using repository-native models/storage. Make finalized records immutable and content-integrity checked. Preserve source evidence links, grader digest, and grader digest provenance. Retention must either cover Plan 003's 12-branch run plus the replay window, or provide a tested durable fallback restore path. The Plan 003 branch handoff may receive only a finalized Directory/Filesystem ForkPoint whose boundary token, history hash, snapshot digest when supported, grader digest, restore ref, parent node id, isolated workspace identity, and trusted-evidence refs re-verify after process restart.

**Pass:** A finalized ForkPoint round-trips after process restart and rejects mutation/digest mismatch.  
**Fail:** The record depends on in-memory state or mutable “latest grader” lookup.

### WP6 — Prove six public behaviors

Add behavior-level tests and one real integration scenario for capture/restore. The six required behavior cases are: valid capture, valid restore, boundary mismatch rejection, history mismatch rejection, grader mismatch rejection, and unsupported snapshot-mode rejection. Partial-capture cleanup and finalized-record mutation rejection are required additional checks.

**Pass:** Each test fails when its protected behavior is deliberately broken and survives internal refactoring.  
**Fail:** Tests mock the capture/restore unit itself or assert private call sequence.

Failure tests assert repository-native errors/results preserve the semantic classes from `specs/03-interfaces.md`, including boundary, grader, state capture/restore, snapshot expiry, and security capability failures. Negative restore tests must prove mismatches leave no `snapshot_restore_ref`, Plan 003 handoff artifact, substituted snapshot, or refreshed capture.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-002-tests
    python docs/plans/scripts/run_mapped.py integration-forkpoint
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/validate_file_sizes.py --plan 002
    python docs/plans/scripts/validate_evidence.py --plan 002 --require-complete

Expected evidence:

- real HUD trace/QA/file-evidence ids,
- one immutable ForkPoint id,
- selected snapshot profile and retention,
- snapshot expiry handling, capture-root inventory, prohibited-mount exclusion, and network/secret/resource isolation evidence,
- state/history boundary token and hashes,
- grader/environment digests and `grader_digest_source`,
- successful real restore probe after process restart,
- explicit `snapshot_expired` or unavailable-snapshot failure evidence, plus durable fallback restore evidence when the selected retention window is not enough for Plan 003,
- Plan 003 restore handoff fields: `fork_point_id`, `task_id`, `environment_version`, `environment_image_digest`, `snapshot_restore_ref`, `snapshot_id`, `snapshot_mode`, `snapshot_digest` when supported, `history_prefix_ref`, `history_hash`, boundary token, `parent_node_id`, isolated writable root identity, `grader_digest`, `grader_digest_source`, trusted source-evidence refs, network/secret/resource policy labels, snapshot expiry/retention, durable fallback ref when applicable, and branch-tag propagation inputs,
- six behavior checks, plus explicit partial-capture cleanup and finalized-record immutability checks,
- manifest `docs/plans/evidence/002/MANIFEST.json`.

The manifest must show that the finalized ForkPoint includes every required field from `docs/plans/specs/03-interfaces.md#forkpoint-record`, including history prefix ref, snapshot id/mode/digest when supported, fork reason, `created_at`, and source evidence refs.

No owned source file exceeds 500 lines without a recorded seam decision. Tests verify state/history behavior, not implementation structure.

## Recovery

Capture and restore operations must be idempotent by immutable ForkPoint id. On interruption, remove unfinalized snapshots or mark them orphaned for cleanup, then resume from the last completed packet in the manifest. Persist provider object ids before relying on provider cleanup, because snapshot expiry/deletion behavior is provider-visible and expired Modal snapshots fail when mounted or first used ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots)). Do not reuse a partially finalized ForkPoint. Rollback removes only the new feature path and temporary provider objects; it must not alter the source trace or grader.

## Executor prompt

    /goal Implement docs/plans/002-atomic-forkpoint-seam.md after confirming Plan 001 is accepted. Create and restore one real atomic ForkPoint from the suspicious HUD trace, preserve exact history/state/grader identity, pass all six behavior cases and the real integration command, stay inside this plan's owns paths, update evidence/002/MANIFEST.json, and append the Living-doc log. Stop rather than approximate a boundary or state mode.

## Living-doc log

### Progress

- At every STOP or handoff, append a timestamped entry and mirror the blocker in `docs/plans/evidence/002/MANIFEST.json`.
- [ ] Real source trace normalized.
- [ ] Atomic capture implemented.
- [ ] Core snapshot profile selected.
- [ ] Fidelity restore implemented.
- [ ] ForkPoint sealed.
- [ ] Six behavior cases and integration pass.

### Surprises & Discoveries

- 2026-06-20 — Current repo-map status is `blocked`; Plan 002 remains non-executable until Gate 1 is accepted with real trace, HUD/Modal adapters, grader, artifact store, and security controls.
- 2026-06-20 — External docs audit added inline grounding for HUD run/trace identities, Modal Directory/Filesystem/Memory/VM snapshot maturity, Modal snapshot TTL behavior, and Modal Sandbox network defaults.
- 2026-06-20 — Security/evidence audit tightened redaction scope, snapshot capture inventory, trusted evidence writing, grader digest provenance, and Plan 003 handoff rejection for non-core snapshot modes.
- 2026-06-20 — Grill-with-docs review found residual proof gaps around evaluator-surface digests, completed-action durability, Directory reconstruction, MongoDB quiescence, Python startup/plugin surfaces, Filesystem Snapshot safety, and mismatch fallback prevention.

### Decision Log

- 2026-06-20 — Planning decision: keep source-trace ingestion, capture, restore, and the ForkPoint contract in one locality-of-behavior feature slice.
- 2026-06-20 — Planning decision: Directory Snapshot is acceptable only for a purpose-built task-owned state root or a hashed deterministic reconstruction that cannot mask branch-relevant mutations; otherwise Plan 002 must use Filesystem Snapshot or STOP.

### Outcomes & Retrospective

- Pending execution.
