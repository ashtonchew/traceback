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

A ForkPoint is the shared object between HUD's semantic trace and Modal's executable state. If state is captured after action `t` but history is truncated before or after a different action, every continuation is contaminated: the agent remembers a world it did not restore or loses observations that the state already reflects.

This slice owns source-trace normalization, boundary selection, atomic capture, core snapshot-profile decision, immutable ForkPoint persistence, and restore fidelity. It does not run stochastic attacks. Read the sibling reference before WP2 for the boundary protocol and fidelity scenarios.

## Constraints

- Start only when repo-map status and this plan's ownership bindings are accepted.
- Use the real suspicious reward-1 trace and real HUD file/QA evidence.
- Bind to the repository's completed-action event; do not infer timing from array position alone.
- Capture state and history as one logical transaction. Partial ForkPoints are invalid and cleaned up.
- Use a verified Directory Snapshot core path when sufficient; use the verified Filesystem fallback when necessary. Do not depend on Memory or VM Alpha capabilities.
- Pin task, environment version, environment image, and grader digest.
- Persist no secret material in history or snapshot metadata.
- STOP on missing source trace, no quiescent boundary, unknown grader identity, state that the available core snapshot modes cannot cover, or unverified secret isolation.
- Co-locate capture, restore, contract, and behavior tests in the `forkpoints` feature. Split any file over 500 lines along capture/restore/persistence seams.
- Tests assert restored observable behavior, not internal call order or class layout.

## Work packets

### WP1 — Normalize the real source trace

Read the repo-bound HUD adapter and normalize trace identity, step/action identity, task id, environment version, reward, QA result reference, and file evidence. Select a defensible completed-action boundary and record the fork reason.

**Pass:** One normalized source record links the real reward-1 trace, QA result, and step-level file diff with stable ids.  
**Fail:** Evidence is copied into a synthetic fixture or boundary identity depends only on list index.

### WP2 — Implement atomic capture

At the canonical completed-action hook, derive one boundary token, freeze the exact history prefix, quiesce task processes as required by the selected core profile, capture executable state, and finalize the ForkPoint only when all pieces succeed.

**Pass:** Injected failure after either half leaves no finalized ForkPoint and cleans temporary state.  
**Fail:** State and history can be committed independently or later “reconciled.”

### WP3 — Select and record the core snapshot profile

Inspect where the MongoDB task's branch-relevant state lives. Choose Directory Snapshot when the working directory is sufficient, otherwise the verified Filesystem path. Record mode, provider object id, retention, image digest, and rationale.

**Pass:** A capability-backed decision is part of the ForkPoint evidence and requires no Alpha access.  
**Fail:** Mode is chosen from sponsor preference rather than task state, or process-only state is silently lost.

### WP4 — Restore with fidelity checks

Restore into an isolated environment, reconstruct the exact history prefix, verify boundary token and hashes, and evaluate task-visible probes that distinguish the selected moment from adjacent steps.

**Pass:** The restored environment and history satisfy the real fidelity probes; adjacent/mismatched artifacts fail closed.  
**Fail:** Restore success means only “sandbox started” or “files exist.”

### WP5 — Seal the ForkPoint contract

Persist the required logical fields from `specs/03-interfaces.md`, using repository-native models/storage. Make finalized records immutable and content-integrity checked. Preserve source evidence links and grader digest.

**Pass:** A finalized ForkPoint round-trips after process restart and rejects mutation/digest mismatch.  
**Fail:** The record depends on in-memory state or mutable “latest grader” lookup.

### WP6 — Prove six public behaviors

Add behavior-level tests and one real integration scenario for capture/restore. Cover success plus the four mismatch/mode failures named in the Goal.

**Pass:** Each test fails when its protected behavior is deliberately broken and survives internal refactoring.  
**Fail:** Tests mock the capture/restore unit itself or assert private call sequence.

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
- state/history boundary token and hashes,
- grader/environment digests,
- successful real restore probe,
- six behavior checks,
- manifest `docs/plans/evidence/002/MANIFEST.json`.

No owned source file exceeds 500 lines without a recorded seam decision. Tests verify state/history behavior, not implementation structure.

## Recovery

Capture and restore operations must be idempotent by immutable ForkPoint id. On interruption, remove unfinalized snapshots or mark them orphaned for cleanup, then resume from the last completed packet in the manifest. Do not reuse a partially finalized ForkPoint. Rollback removes only the new feature path and temporary provider objects; it must not alter the source trace or grader.

## Executor prompt

    /goal Implement docs/plans/002-atomic-forkpoint-seam.md after confirming Plan 001 is accepted. Create and restore one real atomic ForkPoint from the suspicious HUD trace, preserve exact history/state/grader identity, pass all six behavior cases and the real integration command, stay inside this plan's owns paths, update evidence/002/MANIFEST.json, and append the Living-doc log. Stop rather than approximate a boundary or state mode.

## Living-doc log

### Progress

- [ ] Real source trace normalized.
- [ ] Atomic capture implemented.
- [ ] Core snapshot profile selected.
- [ ] Fidelity restore implemented.
- [ ] ForkPoint sealed.
- [ ] Six behavior cases and integration pass.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: keep source-trace ingestion, capture, restore, and the ForkPoint contract in one locality-of-behavior feature slice.

### Outcomes & Retrospective

- Pending execution.
