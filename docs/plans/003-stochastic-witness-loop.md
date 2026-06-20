---
name: stochastic-witness-loop
description: >
  Turns one accepted ForkPoint into genuine seeded BranchRuns, separates reward from QA classification, deduplicates exploit mechanisms, materializes durable Exploit Witnesses, and proves deterministic replay. Use when Plan 002 has merged and the real branch gateway, snapshot restore, grader, QA, storage, and security bindings are accepted; it owns src/forkproof/witnesses/**, tests/forkproof/witnesses/**, fixtures/forkproof/witnesses/**, this plan/reference, and evidence/003/**.
owns: ["docs/plans/003-stochastic-witness-loop.md", "docs/plans/003-stochastic-witness-loop.REFERENCE.md", "src/forkproof/witnesses/**", "tests/forkproof/witnesses/**", "fixtures/forkproof/witnesses/**", "docs/plans/evidence/003/**"]
depends_on: ["atomic-forkpoint-seam"]
wave: 3
---

# Stochastic Witness loop

## Goal

Run exactly 12 genuine seeded stochastic continuations from one real ForkPoint and promote at least one branch to an Exploit Witness only after complete provenance, independent reward/QA gates, target-mechanism deduplication, durable storage, and three consecutive deterministic v1 replays all pass. Done is binary when both the 12-branch count and at least one sealed three-replay Witness are evidenced.

## Context / Why

Discovery and proof are intentionally different. Discovery varies seeds and sampling to find attacks; it may fail or produce different trajectories. Proof restores saved pre-attack state and replays recorded actions against pinned versions. A suspicious or rewarded trace alone is not a durable regression test.

This slice owns the full locality of behavior from branch scheduling through Witness replay. It reuses the existing agent gateway and harden-v0 dedup behavior found in Wave 1. It does not patch the verifier. Read the sibling reference for the promotion truth table, branch budget, replay protocol, and security evidence.

## Constraints

- Start from the finalized ForkPoint produced by Plan 002; never recreate the state from scratch for core branch runs.
- Run agentic continuations with real model calls and unique branch ids/seeds. Do not feed a fixed exploit taxonomy.
- Keep reward and QA classification separate and authoritative at their own sources.
- Tag every gateway, snapshot, trace, grader, QA, and artifact operation with run/branch/node lineage.
- Reuse repository/harden-v0 target-mechanism dedup; do not count wording variants as new exploits.
- A Memory Snapshot may not be the durable Witness system of record.
- Untrusted code receives minimum secrets, scoped network, isolated writable state, and bounded resources.
- STOP before execution when isolation or grader authority is unverified. STOP Witness promotion on missing provenance, unavailable classification, expired/unrecoverable state, digest mismatch, or replay divergence.
- Co-locate branch policy, promotion, artifact packaging, replay, and tests in the Witness feature. Split files over 500 lines by scheduler/promotion/replay/storage responsibility.
- Tests assert public promotion/replay outcomes. Do not mock the unit being classified or replayed.

## Work packets

### WP1 — Build isolated BranchRun execution

Restore the ForkPoint into one isolated branch context per attempt, assign run/branch/node identity, configure model/seed/sampling from the real gateway, enforce resource/security policy, and persist bounded failure records.

**Pass:** Two simultaneous probe branches cannot read or mutate each other's writable state, and every attempt produces a complete success/failure BranchRun record.  
**Fail:** Branches share mutable task state, inherit broad credentials, or failed attempts disappear.

### WP2 — Execute 12 genuine stochastic branches

Run 12 unique branches from the same ForkPoint with sampling diversity. Preserve HUD trace links, action records, file diffs, reward, model configuration, timing, and lineage. Do not stop early in the core run even when a Witness appears; the must-ship evidence is about 12 real branches.

**Pass:** Evidence lists 12 unique branch ids and seeds with real model/gateway and trace results.  
**Fail:** Branches are scripted replays, duplicated identities, or fresh-from-start rollouts.

### WP3 — Grade, classify, and deduplicate independently

Obtain authoritative verifier reward and HUD QA hacking classification, then group qualifying candidates by target and mechanism through the verified dedup path.

**Pass:** The promotion truth table rejects reward-only, QA-only, and missing-signal cases; equivalent attacks share a cluster id.  
**Fail:** Reward is inferred from QA, QA is inferred from reward, or every wording variant counts as distinct.

### WP4 — Materialize durable Witness candidates

For each qualifying candidate, store pre-attack filesystem-class state, history prefix, native recorded actions/tool results, file diff, verifier/QA outputs, environment/image/grader identity, model/seed/config, cluster, replay entrypoint, retention, and content digest.

**Pass:** The candidate survives process restart and has no secret material; ephemeral state has a durable fallback.  
**Fail:** It depends on live process memory, mutable “latest” versions, or a dashboard link alone.

### WP5 — Gate Witness status on deterministic replay

Restore the saved pre-attack state and replay recorded actions without model rediscovery. Require three consecutive v1 runs to reproduce the same semantic successful reward under the pinned grader and environment.

**Pass:** At least one candidate passes all three runs and is sealed as a Witness.  
**Fail:** Any action diverges, an external dependency is unpinned, or reward is inconsistent; the candidate remains unproven.

### WP6 — Record metrics and honest fallback artifact

Compute branch count, distinct clusters, time to first Witness, replay success, restore latency, and setup work avoided from events. Mark unmeasured metrics explicitly. Retain one genuine prior-run Witness suitable for the demo fallback, clearly labelled with its original run.

**Pass:** Metrics derive from recorded timestamps/events, and fallback can be restored/replayed live.  
**Fail:** Values are estimated or a prerecorded artifact is presented as live discovery.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-003-tests
    python docs/plans/scripts/run_mapped.py integration-witness
    python docs/plans/scripts/run_mapped.py security-branch
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/validate_file_sizes.py --plan 003
    python docs/plans/scripts/validate_evidence.py --plan 003 --require-complete

Expected evidence:

- one source ForkPoint id,
- 12 unique BranchRun records and trace links,
- separate reward and QA outputs,
- dedup cluster report,
- at least one sealed Witness with durable state and content digest,
- three consecutive deterministic v1 replay results,
- branch-isolation negative check,
- measured/not-measured metrics,
- manifest `docs/plans/evidence/003/MANIFEST.json`.

No owned source file exceeds 500 lines without an approved split. Tests verify promotion, isolation, and replay behavior rather than internal scheduler structure.

## Recovery

Branch ids are immutable and attempts are append-only. Resume missing branches without rerunning completed ids; a new stochastic retry gets a new id. Clean up timed-out sandboxes and orphaned temporary snapshots using provider ids recorded in the manifest. Never promote a partially written candidate. Rollback removes the feature code and nonsealed temporary artifacts; sealed Witness evidence is append-only and may be marked superseded, not rewritten.

## Executor prompt

    /goal Execute docs/plans/003-stochastic-witness-loop.md after Plan 002 merges. Run 12 real seeded isolated branches from the accepted ForkPoint, keep reward and HUD QA separate, deduplicate by target/mechanism, seal at least one durable Witness only after three deterministic v1 replays, pass the security and integration commands, stay inside owned paths, update evidence/003/MANIFEST.json, and append the Living-doc log. Never substitute scripted or fresh-start runs for stochastic state branches.

## Living-doc log

### Progress

- [ ] Isolated BranchRun execution complete.
- [ ] Twelve genuine branches complete.
- [ ] Reward/QA/dedup gates complete.
- [ ] Durable candidate packaging complete.
- [ ] Three-run deterministic replay gate complete.
- [ ] Metrics and fallback artifact complete.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: co-locate stochastic discovery and deterministic Witness replay because Witness promotion is one vertical behavior boundary.

### Outcomes & Retrospective

- Pending execution.
