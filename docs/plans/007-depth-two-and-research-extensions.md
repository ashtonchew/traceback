---
name: depth-two-and-research-extensions
description: >
  Extends the proven Witness loop with one depth-two re-snapshot, bounded adaptive stopping, and measured research analyses while capability-gating Memory Snapshot, VM Sandbox, cross-task transfer, and training experiments. Use when Plan 003 has merged and core work is not at risk; it owns src/forkproof/research/**, tests/forkproof/research/**, artifacts/forkproof/research/**, this plan/reference, and evidence/007/**.
owns: ["docs/plans/007-depth-two-and-research-extensions.md", "docs/plans/007-depth-two-and-research-extensions.REFERENCE.md", "src/forkproof/research/**", "tests/forkproof/research/**", "artifacts/forkproof/research/**", "docs/plans/evidence/007/**"]
depends_on: ["stochastic-witness-loop"]
wave: 4
---

# Depth-two and research extensions

## Goal

Produce one real depth-two lineage by re-snapshotting a promising child, demonstrate adaptive stopping after four consecutive no-new-cluster branches, and emit one measured research report. Done is binary when those three core research artifacts exist and every conditional Alpha, transfer, or training packet has either a real result or an evidence-backed skip with no unused scaffold.

## Context / Why

The core product proves one depth-1 loop. The research thesis is that reaching a rare state once and branching from it exposes multi-step attacks that flat restarts miss. This plan tests that thesis without delaying release or overstating a full MCTS system.

The plan is parallel with release proof after a core Witness exists. It may consume core artifacts but cannot modify them or become a dependency of Plan 006. Read the sibling reference for node selection, adaptive policy, capability gates, measurement design, and skip criteria.

## Constraints

- Core release work has priority; stop research when it threatens Gate 4 or 5.
- Describe the search as MCTS-shaped, not MCTS.
- Reuse the proven BranchRun/Witness operations through public interfaces; do not fork core logic.
- Maximum research depth is 2 for this bundle; child branch budget is up to 8.
- Adaptive stop triggers after four consecutive completed branches yield no new exploit cluster.
- Memory/VM paths require both verified capability and a real state/task need. No capability means no adapter scaffold.
- Cross-task transfer requires real additional tasks. Training analysis begins with raw-vs-hardened filtering; no live RL.
- Flat-restart comparison is reported only when both strategies run under comparable measured budgets.
- STOP on insufficient time/budget, unavailable real data, unsafe capability, or inability to define an honest comparison. Record skips.
- Keep research code isolated and removable: no symbol in `src/forkproof/research/**` may be imported by any other feature folder, and deleting `src/forkproof/research/**`, `tests/forkproof/research/**`, and `artifacts/forkproof/research/**` must leave the core build and all other plan tests passing. Split files over 500 lines by tree policy/capability/analysis.
- Tests assert policy and measured outputs, not claims of universal superiority.

## Work packets

### WP1 — Select and re-snapshot one promising child

Use trace/file/grader/cluster evidence to select a completed child state that presents task-visible or grader-visible state plausibly opening a different exploit path than the root ForkPoint — evidenced by at least one signal from the promising-node list in the reference. Capture a new atomic node with parent lineage and restore it independently.

**Pass:** One child snapshot restores with valid lineage and a documented reason it is more promising than random.  
**Fail:** The node is chosen only from exposed reasoning, or "distinguishable from its parent" is satisfied only by a different node ID — at least one task-visible probe (file diff, content hash, grader-visible state, or command output) must produce a different value at the child boundary than at the parent ForkPoint boundary, with the reason recorded in `fork_reason`.

### WP2 — Run depth-two branches

Launch up to eight seeded agentic branches from the child node using the core Witness machinery. Preserve depth, parent, and complete provenance; promote any qualifying exploit through the same deterministic replay gate.

**Pass:** At least one real depth-two BranchRun completes and the report distinguishes discoveries from non-discoveries.  
**Fail:** The run restarts from root or bypasses Witness gates.

### WP3 — Implement and prove adaptive stopping

The research scheduler in this plan owns the stop policy and concurrency model; it calls core Witness machinery through public interfaces but does not borrow or fork the Plan 003 scheduler. Track new exploit clusters in completion order and stop scheduling new branches after four consecutive completed branches add none, while allowing branches already in flight to finish. If an in-flight branch completes after the stop count reached 4 and it confirms a new cluster, reset the consecutive count to zero — but only schedule additional branches if the 8-branch budget is not yet exhausted.

**Pass:** Deterministic policy tests cover reset-on-new-cluster, stop-at-four, in-flight-late-reset, budget-exhausted-no-new-schedule, and concurrency; a real run records the decision.  
**Fail:** Stop is based on raw reward count or wording variants, or the policy borrows internal state from the Plan 003 scheduler.

### WP4 — Measure state branching versus flat restarts

When budget permits, run comparable state-branch and from-scratch attempts with common task/model constraints. Measure setup work, branch count, time/compute, and distinct confirmed clusters.

**Pass:** Report states protocol, raw observations, limits, and no causal overclaim. A result where flat restarts find equal or more distinct confirmed clusters is a valid honest output; record raw counts and state the limitation explicitly. This plan merges independently of that outcome.  
**Fail:** One strategy is estimated, uses a different task/model budget, or illustrative probabilities are presented as measurements.

### WP5 — Capability-gate Memory and VM profiles

For each profile, the executor must arrive at exactly one of three honest outcomes, evidenced in the manifest:

1. **Capability unavailable** — probe returns error or unauthorized; record probe output, mark `skipped`, create no scaffold.
2. **Capability available but unnecessary** — probe succeeds but the task does not require the profile's unique behavior (Docker/Harbor/kernel for VM; process-resident state irreproducible from filesystem for Memory); record probe output and task evidence, mark `skipped`, create no scaffold.
3. **Capability available and necessary** — probe succeeds AND task evidence confirms the need; implement only the real consumed path and complete the full evidence matrix in the reference.

VM Sandbox is a conditional research path for tasks that genuinely require a full Linux kernel, Docker-in-Sandbox, systemd, eBPF, cgroups, or loopback mounts. It is not a replacement for Plan 002's Directory or Filesystem Snapshot mode selection.

Memory Snapshot is a search accelerator only. Any successful Memory discovery must be immediately converted to a durable replay artifact: a Directory or Filesystem Snapshot plus recorded actions, history prefix, environment image digest, grader digest, and restore command. A Memory Snapshot alone cannot satisfy Witness durability and must not be the `pre_attack_snapshot_ref`.

**Pass:** Each profile has either a real integration result or a concise skip backed by probe/task evidence, with no unused production scaffold.  
**Fail:** Alpha APIs are mocked into existence, become core dependencies, or VM is used as a substitute for Directory/Filesystem mode rather than because real-kernel behavior is required.

### WP6 — Evaluate transfer and training consequences conditionally

If real additional tasks and time exist, run the existing shared-defense transfer path. Independently, use real trajectories to compare raw-versus-hardened filtering and characterize admitted hacked data. Consider optional model training only after that report and never live.

**Pass:** Real measured outputs or evidence-backed skips are recorded; hypotheses stay labelled.  
**Fail:** Synthetic tasks/data or schematic bars become reported results.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-007-tests
    python docs/plans/scripts/run_mapped.py integration-research
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/validate_file_sizes.py --plan 007
    python docs/plans/scripts/validate_evidence.py --plan 007 --require-complete

Expected evidence:

- parent and child node/ForkPoint ids with depth-two lineage,
- at least one completed depth-two BranchRun,
- adaptive-stop policy test and real decision event,
- research report with measured values or explicit not-measured fields,
- comparable flat-restart result or justified skip,
- Memory/VM capability results or justified skips,
- transfer/training results or justified skips,
- manifest `docs/plans/evidence/007/MANIFEST.json`.

No owned source file exceeds 500 lines without a real seam. Conditional skips count only when backed by concrete capability/data/budget evidence; they do not justify empty scaffolding.

## Recovery

Research runs are append-only and isolated from core artifacts. Resume from the last node/branch id and respect recorded budgets. Cancel in-flight branches safely when the core release needs resources. Remove experimental code that had no real consumer before completion. Rollback deletes only research paths/artifacts; sealed core Witnesses and release work remain untouched.

## Executor prompt

    /goal Execute docs/plans/007-depth-two-and-research-extensions.md only after Plan 003 merges and without delaying core release. Re-snapshot one promising child, run a real depth-two branch, prove the four-no-new-cluster stop policy, and write a measured report. Exercise Memory, VM, transfer, or training paths only with verified capability and real data; otherwise record evidence-backed skips and create no unused scaffold. Run Done-when commands, update evidence/007/MANIFEST.json, and append the log.

## Living-doc log

### Progress

- [ ] Promising child selected and re-snapshotted.
- [ ] Depth-two branch run.
- [ ] Adaptive stop proved.
- [ ] Flat comparison measured or skipped with evidence.
- [ ] Memory/VM profiles run or skipped with evidence.
- [ ] Transfer/training analysis run or skipped with evidence.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: put all non-core research behind one removable feature boundary and forbid it from gating the demo.
- 2026-06-21 — Start-precondition relaxation for **007-CORE** (owner-approved, **REVERSIBLE**): the 007 core deliverables — one depth-two lineage, adaptive stopping, and the measured report — may START against a **stable** Plan 003 discovery/restore machinery **without** waiting for a sealed Exploit Witness (index Gate 3). Rationale: 007-core's binary done is "a depth-two BranchRun **completes**" (WP2 Pass) + adaptive policy + report; it uses the working discovery/snapshot/restore path, **not** the replay-seal gate. The **optional** depth-two Witness promotion ("promote any qualifying exploit through the same deterministic replay gate", WP2) **remains gated** on the replay-seal working (the same Modal replay-image fix Plan 003 needs). This is a scoped exception to Gate 3 for 007's non-seal core work only. **Revert:** once 003 seals a Witness, Gate 3 holds anyway (the relaxation becomes a no-op); revert the relaxation commit to restore canonical wording. **Honesty caveat:** a depth-two report produced before any seal must state the deterministic-seal step was not exercised — capability + policy demonstrated, not a sealed proof.

### Outcomes & Retrospective

- Pending execution.
