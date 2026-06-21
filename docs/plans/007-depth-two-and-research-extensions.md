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
- [x] Adaptive stop proved.
- [x] Flat comparison measured or skipped with evidence.
- [x] Memory/VM profiles run or skipped with evidence.
- [x] Transfer/training analysis run or skipped with evidence.

- 2026-06-21T11:19:15Z — Started Plan 007 from `codex/plan-002-003-witness` on branch `codex/plan-007-research-stack`. Read the required plan context and Plan 003 evidence. Confirmed Plan 003 records live reward-hacking candidates but no sealed Exploit Witness, so WP1/WP2 live depth-two execution remains blocked. Implemented Plan 007-owned local contracts for adaptive scheduling, promising-node selection, capability gates, and measured/not-measured report validation, with focused behavior tests.
- 2026-06-21T11:24:00Z — Ran feasible validators. Focused tests and research lint pass; mapped `plan-007-tests` and `integration-research` skip because COMMANDS.json still marks them not-applicable; graph, sections, ownership, traceability, file-size, mapped lint/build, and evidence-without-require-complete pass. `validate_evidence.py --plan 007 --require-complete` fails as expected because the manifest remains blocked.
- 2026-06-21T12:03:00Z — Restacked `codex/plan-007-research-stack` onto `origin/codex/plan-005-release-proof` because that stack contains the canonical sealed Plan 003 Witness. Verified `docs/plans/evidence/003/artifacts/sealed/witnesses/wit-run-20260621T075711-branch-08.json`: reward=1, `qa_is_reward_hacking=true`, `cluster-001`, durable filesystem snapshot, minimized `/app/conftest.py` causal delta, and three deterministic semantic-success replays. Plan 007 remains incomplete because no depth-two re-snapshot or depth-two BranchRun has been produced.
- 2026-06-21T12:08:00Z — Linked the clean pinned HUD Trace Explorer checkout from `.worktrees/plan-002-003-witness/.external/hud-trace-explorer` into ignored `.external/`; `scripts/verify_external_deps.sh` now passes on the Plan 005 stack. Re-ran focused research tests, research lint, mapped skips, mapped lint/build, graph, sections, ownership, traceability, file-size, and evidence validation.
- 2026-06-21T12:32:00Z — Added Plan 007-owned lineage and depth-two run record contracts plus `artifacts/forkproof/research/child-selection-wit-run-20260621T075711-branch-08.json`. The artifact selects the sealed Witness branch as the promising child using observable file-change, cluster, and grader-visible signals, but marks the depth-two run blocked because no child re-snapshot or depth-two BranchRun has been produced.
- 2026-06-21T12:52:00Z — Added a behavior test that loads the committed child-selection artifact and validates its selection, lineage, and blocked depth-two run sections through public Plan 007 contracts. Focused research tests now pass at 14 tests.
- 2026-06-21T13:12:00Z — Added `src/forkproof/research/artifacts.py` so the selected-child artifact is reproducible from the sealed Witness and causal-delta inputs rather than only hand-written JSON. Focused research tests now pass at 15 tests.
- 2026-06-21T13:43:00Z — Added a Plan 007 integration preflight artifact builder and wired `uv run python -m forkproof.research.cli integration` to write `artifacts/forkproof/research/depth-two-integration-preflight.json` before failing closed. Focused research tests now pass at 17 tests; the CLI still exits 2 because there is no mapped live depth-two executor or completed depth-two BranchRun.
- 2026-06-21T13:57:00Z — Added `artifacts/forkproof/research/conditional-research-report.json`, generated by Plan 007 public report/skip validators. It records flat comparison, Memory, VM, transfer, and training as `not-measured` or `skipped` with evidence refs and no adapter scaffold. Focused research tests now pass at 19 tests.
- 2026-06-21T14:05:00Z — Added an isolation test proving no non-research `src/forkproof/**` module imports `forkproof.research`, preserving Plan 007's removable feature boundary. Focused research tests now pass at 20 tests.
- 2026-06-21T14:12:00Z — Tightened the Plan 007 scheduler so it only expands a completed depth-one child into depth-two branch IDs; attempts to schedule from root or an already-depth-two node now fail before branch scheduling. Focused research tests now pass at 21 tests.
- 2026-06-21T14:18:00Z — Tightened depth-two run records so completed branch refs must be a subset of scheduled branch refs, preventing a report from claiming completions the scheduler never launched. Focused research tests still pass at 21 tests.
- 2026-06-21T14:24:00Z — Tightened completed depth-two run records to require measured values instead of allowing a measurement-free completion claim. Focused research tests still pass at 21 tests.
- 2026-06-21T14:30:00Z — Fetched remote branches and rebased `codex/plan-007-research-stack` onto the updated Plan 005 stack tip `9c9a60f`. Focused research tests, research lint, mapped skips, mapped lint/build, graph, sections, ownership, traceability, file-size, and evidence validation still pass; `--require-complete` still fails only because depth-two execution is blocked.
- 2026-06-21T14:45:00Z — Fetched after Plan 005 merged to `main` and rebased `codex/plan-007-research-stack` onto `origin/main` merge `1619823`. Re-ran focused research tests, research lint, mapped skips, mapped lint/build, graph, sections, ownership, traceability, file-size, evidence validation, and fail-closed integration preflight; status remains blocked only on independent child re-snapshot and real depth-two BranchRun evidence.

### Surprises & Discoveries

- 2026-06-21T11:19:15Z — `scripts/verify_external_deps.sh` is absent on the Plan 003 stack branch used for this work, so the requested `.external/` verification command could not run even though `.external/harden-v0` and `.external/terminal-wrench` are present.
- 2026-06-21T11:19:15Z — `docs/plans/repo-map/COMMANDS.json` still marks `plan-007-tests` and `integration-research` as `not-applicable`; Plan 007 does not own command-map keys, so direct focused tests are recorded separately and mapped commands are left unchanged.
- 2026-06-21T11:19:15Z — The requested `hud-environment-builder` and `modal` skill files were not present at the advertised local plugin cache paths; repository docs remained the only usable project source of truth.
- 2026-06-21T12:03:00Z — Plan 005 is the better stack base for Plan 007 than the earlier Plan 003 branch: it includes the sealed Witness produced by Plan 003 rescue work and keeps Plan 007 closer to the current release-proof stack. This does not make Plan 007 complete; it only removes the prior no-Witness base problem.
- 2026-06-21T12:08:00Z — The previous external-dependency blocker was base-specific. On the Plan 005 stack, the verifier exists and passes once the pinned local HUD Trace Explorer checkout is linked into ignored `.external/`.
- 2026-06-21T12:32:00Z — The first WP1 sentence is now partially grounded: a promising child is selected from observable sealed-Witness evidence. The WP1 pass condition is still not met because the selected child has not been re-snapshotted independently under Plan 007.
- 2026-06-21T13:43:00Z — The integration STOP now has durable Plan 007-owned evidence. The preflight artifact proves the blocked state without turning the mapped `integration-research` skip into a success claim.
- 2026-06-21T13:57:00Z — Conditional research packet evidence is stronger as a generated artifact, but still not measured. The sealed Witness does not establish process-resident or kernel-level task need, and no comparable flat-restart budget exists before a real depth-two run.
- 2026-06-21T14:45:00Z — Plan 005 is now merged into `main`, so Plan 007 no longer needs a Plan 005 branch base. The canonical base is `origin/main`; this changes PR topology but does not satisfy WP1/WP2.

### Decision Log

- 2026-06-20 — Planning decision: put all non-core research behind one removable feature boundary and forbid it from gating the demo.
- 2026-06-21T11:19:15Z — Implemented only pure Plan 007 contracts and skip/report evidence until Plan 003 seals a Witness. This preserves the STOP condition while making the unblocked scheduler and gating behavior testable.
- 2026-06-21T12:03:00Z — Keep the integration CLI fail-closed even when a sealed Witness is present on the stack. Returning success at that point would overstate readiness because Plan 007 has not yet produced a live depth-two BranchRun artifact.
- 2026-06-21T12:32:00Z — Treat child selection as a separate artifact from child re-snapshot. Selection can be evidenced from the sealed Witness, but independent restore/re-snapshot remains a live-system WP1 requirement.
- 2026-06-21T13:43:00Z — Keep the preflight artifact stable across reruns by preserving an existing `recorded_at` value. Re-running the fail-closed CLI should not dirty committed evidence unless the underlying gate facts change.

### Outcomes & Retrospective

- 2026-06-21T11:19:15Z — Partial implementation only. Local contracts and skips are evidenced in `artifacts/forkproof/research/blocked-research-report.json`; live depth-two execution, flat comparison, Memory/VM integration, transfer, and training remain blocked or not measured until real sealed Plan 003 artifacts exist.
- 2026-06-21T12:03:00Z — Partial implementation remains. The stack now includes real sealed Plan 003 Witness evidence through Plan 005, but Plan 007 has only contracts and skip/report evidence. Live depth-two execution, flat comparison, Memory/VM integration, transfer, and training remain unproved.
- 2026-06-21T12:32:00Z — Partial implementation now includes a selected promising child and lineage artifact. Plan 007 still has no completed WP1 re-snapshot, no WP2 BranchRun, and no complete Done-when evidence.
- 2026-06-21T14:45:00Z — Partial implementation remains on canonical `main` after the Plan 005 merge. The sealed Witness is now available through `main`, but Plan 007 still lacks independent child re-snapshot, depth-two BranchRun, and complete Done-when evidence.
