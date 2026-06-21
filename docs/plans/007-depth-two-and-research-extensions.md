---
name: depth-two-and-research-extensions
description: >
  Extends the proven Witness loop with one replay-materialized depth-two child, bounded adaptive stopping, and measured research analyses while capability-gating Memory Snapshot, VM Sandbox, transfer, and training experiments. Use when Plan 003 has merged and core work is not at risk; it owns the research feature, artifacts, tests, shared glossary updates, this plan/reference, and evidence/007/**.
owns: ["docs/plans/007-depth-two-and-research-extensions.md", "docs/plans/007-depth-two-and-research-extensions.REFERENCE.md", "docs/plans/GLOSSARY.md", "src/forkproof/research/**", "tests/forkproof/research/**", "artifacts/forkproof/research/**", "docs/plans/evidence/007/**"]
depends_on: ["stochastic-witness-loop"]
wave: 4
---

# Depth-two and research extensions

## Goal

Produce one real depth-two child lineage by replaying a selected near-miss boundary into a validated snapshot, complete at least one depth-two BranchRun, demonstrate adaptive stopping after four consecutive finalized no-new-cluster outcomes, and emit one measured research report. Done is binary only when those core artifacts exist. A lack of an eligible or replay-stable near-miss is an honest blocked research outcome, not completion; only the explicitly conditional comparison, Alpha-capability, transfer, and training packets may complete through evidence-backed skips with no unused scaffold.

## Context / Why

The core product proves one depth-1 loop. The research thesis is that reaching a rare state once and branching from it exposes multi-step attacks that flat restarts miss. This plan tests that thesis without delaying release or overstating a full MCTS system.

The plan is parallel with release proof after a core Witness exists. It may consume sealed core artifacts through public interfaces but cannot modify them or become a dependency of Plan 006. Read the sibling reference for the deterministic candidate reduction, expansion-prior record, boundary-state evidence, adaptive policy, capability gates, measurement design, and skip criteria.

## Constraints

- Start only after Plan 003 has merged with a complete manifest and public operations for reading finalized BranchRuns, replaying action prefixes, classifying/deduplicating outcomes, and promoting/replaying Witnesses. Do not import Plan 003 internals.
- Before WP1, verify that intermediate boundaries expose stable boundary ids, ordered action-prefix ranges, parent state refs, history/action digests, declared task-visible and grader-visible probe evidence, environment/evaluator identity, and redaction metadata. STOP if these cannot support replay-to-boundary validation.
- Core release work has priority; stop research when it threatens Gate 4 or 5.
- Describe the search as MCTS-shaped, not MCTS.
- Reuse proven BranchRun/Witness public operations; do not fork core promotion, deduplication, replay, or security logic.
- Maximum research depth is 2; the child-node budget is at most 8 executed BranchRuns with at most 2 concurrently in flight.
- Adaptive stop triggers after four consecutive finalized classification outcomes add no new exploit cluster. Pending, unavailable, or incomplete classification does not advance the counter.
- Revalidate the inherited branch gateway, trusted grader, artifact-writer boundary, secret scope, egress policy, sibling isolation, resource limits, and cleanup behavior before depth-two execution. STOP if the child path weakens any Plan 003 control.
- Memory/VM paths require both verified capability and a real state/task need. No capability or need means an evidenced skip and no adapter scaffold.
- Cross-task transfer requires real additional tasks. Training analysis begins with real raw-vs-hardened admission sets; no live RL.
- Flat-restart comparison is reported only when both strategies run under comparable measured budgets.
- STOP on insufficient core inputs, no eligible/replay-stable near-miss, unavailable real data, unsafe capability, or inability to define an honest comparison. Record the outcome; do not convert a core STOP into Plan 007 completion.
- Keep research code isolated and removable: no symbol in `src/forkproof/research/**` may be imported by another feature folder, and deleting the research source, tests, and artifacts must leave the core build and all other plan tests passing. Split files over 500 lines by selection, scheduler, capability, or analysis responsibility.
- Tests assert public policy and measured outputs, not claims of universal superiority.

## Work packets

### WP1 — Select and materialize one promising child

Select the depth-two boundary through a deterministic pre-filter followed by an auditable expansion prior over finalized depth-1 BranchRun evidence. Do not snapshot every boundary.

1. **Pre-filter.** Evaluate every intermediate completed-action boundary using the mechanical signal rules in the reference. A boundary is eligible only when at least one non-reasoning signal fires. Keep at most two candidates per BranchRun by the declared divergence tuple, then cap the global candidate set at exactly 24 using the declared stable tie-break.
2. **Expansion prior.** Rank eligible boundaries from their recorded evidence, preferring near-miss states and deprioritizing completed-Witness paths. Record judge model/version, prompt and tool-schema digests, sampling settings, every input artifact digest, the full ranked output, exclusions, tie-breaks, and a falsifiable prediction. The prediction states which surface is newly present relative to the parent boundary, which deeper mechanism may complete, and the evidence for that claim; it must not claim the parent could never reach the state.
3. **Replay-to-boundary.** Replay the chosen BranchRun's recorded action prefix from its parent state and compare the resulting versioned boundary-state evidence bundle with the bundle ranked by the judge. Every required declared probe and identity must match. On mismatch, record the divergence and try the next-ranked candidate. If no candidate is replay-stable, STOP with a blocked outcome.
4. **Materialize.** Capture the validated boundary as a child node with parent lineage, explicit retention, durable fallback, evaluator identity, and `fork_reason` linked to the selection and replay evidence.

No eligible near-miss is an honest research finding but does not satisfy this plan's core Goal.

**Pass:** The pre-filter artifact, full expansion-prior record, selected-boundary evidence, replay match, and materialized child snapshot all content-verify; at least one task-visible or grader-visible probe differs from the parent boundary; and the prediction record contains separate `predicted_surface_observed`, `predicted_mechanism_confirmed`, `new_cluster_confirmed`, and `witness_promoted` fields initialized for later completion.
**Fail:** Selection relies on exposed reasoning alone; cap/tie-break behavior is not deterministic; judge provenance is missing; one generic filesystem hash substitutes for declared state evidence; a mismatched replay is expanded; parent reachability is overstated; or no eligible/replay-stable candidate is reported as completion.

### WP2 — Run depth-two branches

Schedule up to eight genuine stochastic BranchRuns incrementally from the child node, with at most two concurrently in flight. Each executed branch has a new immutable branch id, lineage, model and sampling provenance, and a provider seed only where meaningful seed semantics are supported. Preflight failures are recorded separately and replaced with new identities; executed failures still consume budget under the Plan 003 execution-boundary rule.

The branches run blind to the expansion prior: the judge selects where to fork; branches discover what stochastically. Build branch prompts from the approved core template without attaching the prediction, judge reasoning, ranking artifact, or privileged golden/grader knowledge. Record prompt/template digests and a no-leakage check before launch.

**Pass:** At least one real depth-two BranchRun completes; no more than two are ever in flight; all executed branches carry complete provenance and inherited security evidence; prompt digests and inspection prove no expansion-prior leakage; and the report distinguishes discoveries, non-discoveries, and infrastructure/classification failures.
**Fail:** A run restarts from root, reuses an id, bypasses Witness gates, weakens Plan 003 security, exceeds concurrency/budget, or seeds a branch with predicted exploit information.

### WP3 — Implement and prove adaptive stopping

Plan 007 owns only the research scheduler and calls Plan 003 through public operations. Schedule incrementally while fewer than two branches are in flight and budget remains. Append one ordering event only when an executed BranchRun reaches a finalized classification/dedup outcome: `new_cluster` resets the counter to zero; `no_new_cluster` increments it; pending, unavailable, or incomplete classification consumes branch budget but does not change the counter. Stop scheduling at count 4 while allowing already-running branches to finish. A late in-flight `new_cluster` resets the counter and permits scheduling to resume only when total executed budget remains below 8.

**Pass:** Deterministic policy tests cover preflight replacement, executed-budget accounting, max-two concurrency, reset-on-new-cluster, stop-at-four, pending classification, in-flight late reset, exhausted-budget no-resume, and stable event ordering; a real run records the same scheduler state transitions.
**Fail:** Stop is based on raw reward, wording variants, BranchRun completion before classification finalizes, mutable event order, or borrowed Plan 003 scheduler state.

### WP4 — Measure state branching versus flat restarts

When a comparable budget remains, run state-branch and from-scratch attempts under the same task, initial environment/evaluator identity, model family, sampling envelope, security gate, and Witness criteria. Measure setup work, executed branches, model calls or normalized compute, elapsed time, and distinct confirmed clusters. Treat the result as descriptive for this task; no minimum sample supports a universal or causal claim.

**Pass:** The report states protocol, raw observations, normalization, sample counts, limits, and no causal overclaim. Equal or better flat-restart results are valid.
**Fail:** One strategy is estimated, identities or budgets differ without normalization, or illustrative probabilities are presented as measurements.

### WP5 — Capability-gate Memory and VM profiles

For each profile, record exactly one outcome: unavailable, available-but-unnecessary, or available-and-necessary. The first two are evidenced skips with no scaffold. The third requires a real consumed path and the full reference evidence matrix.

VM Sandbox is an execution profile only for tasks requiring real-kernel behavior such as Docker-in-Sandbox, systemd, eBPF, cgroups, or loopback mounts. It is not a snapshot mode or a substitute for Plan 002's core path. Memory Snapshot is a search accelerator only. Any successful Memory discovery must be converted to a retained filesystem-class state or durable fallback with recorded actions, history, environment and evaluator identities, content digest, replay entrypoint, and explicit retention; Witness promotion still requires three fresh deterministic replays.

**Pass:** Each profile has a real integration result or a concise probe/task-backed skip, and every successful Memory discovery has a sealed durable conversion.
**Fail:** Alpha APIs are mocked, become core dependencies, VM substitutes for an adequate core sandbox, or Memory state becomes the Witness system of record.

### WP6 — Evaluate cross-task transfer conditionally

Run the existing shared-defense transfer path only when at least one additional real compatible task and comparable baseline exist. Preserve baseline and transferred-defense results separately.

**Pass:** A real measured transfer report exists, or a concrete task/data/budget probe supports a skip.
**Fail:** Synthetic tasks, changed evaluators, or schematic outcomes are reported as transfer evidence.

### WP7 — Measure training-data consequences

Build v1 and v2 training admission sets from the same real trajectory population using semantic verifier success under pinned evaluator identities. Label rows only from sealed Witness/control evidence or another explicit authoritative classification source; quarantine unknown or conflicting labels. Report raw and hardened admitted counts, same-population contamination fractions, legitimate retention, and exploit-cluster composition. Keep the v2 verifier-positive set distinct from the clean SFT set (`v2 success AND sealed legitimate`). Do not report mock or synthetic values as measured results.

**Pass:** The report identifies the common source population, evaluator identities, classification provenance, quarantine count, exact formulas, numerators/denominators, and observed values; or insufficient real trajectories are evidenced as a skip.
**Fail:** Reward representation is assumed to be numeric, numerator and denominator use different populations, unknowns are coerced to non-hacks, clean-SFT filtering is conflated with v2 admission, or mock bars are reported as measurements.

### WP8 — Run optional SFT/RFT only after analysis

Consider model training only after WP7 produces sufficient real data and a frozen held-out split, account/credit access, exact base model, and an evaluation protocol. Record dataset, job, model/checkpoint, deployment, split, and evaluator ids. Training never runs live in the demo, and behavioral-improvement claims require held-out measured results.

**Pass:** A reproducible measured experiment exists, or prerequisite evidence supports a skip.
**Fail:** Training uses mock data without a dry-run label, lacks held-out evaluation, mixes training products/ids, or claims improvement without measurements.

## Done-when (self-validation gate)

Before running this gate, change `plan-007-tests` and `integration-research` in `docs/plans/repo-map/COMMANDS.json` from `not-applicable` to `verified` with real argv and rerun them. A mapped SKIP with exit 0 is not evidence.

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-007-tests
    python docs/plans/scripts/run_mapped.py integration-research
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/run_mapped.py build
    python docs/plans/scripts/validate_file_sizes.py --plan 007
    python docs/plans/scripts/validate_evidence.py --plan 007 --require-complete

Expected evidence:

- complete Plan 003 dependency and intermediate-boundary input audit,
- deterministic pre-filter artifact with signal rules, cap, scores, and tie-breaks,
- full expansion-prior provenance and ranked candidates,
- selected boundary-state evidence bundle and replay-to-boundary match,
- parent/child ids, depth-two lineage, retention, durable fallback, and evaluator identities,
- no-leakage prompt/template check,
- at least one completed depth-two BranchRun,
- scheduler event log with scheduled/preflight/executed/finalized counts, concurrency, budget, and adaptive-stop decision; depth-two branches counted as executed BranchRuns under Plan 003's executed-vs-scheduled accounting (replaced preflight failures recorded separately),
- four-field prediction-check result (predicted surface, mechanism, new-cluster, and witness-promoted versus depth-two outcome; better-than-random not-measured at n=1),
- measured research report with explicit populations/formulas or not-measured fields,
- comparable flat-restart result or justified conditional skip,
- Memory/VM capability results or justified conditional skips,
- independent transfer, training-data, and model-training results or justified conditional skips,
- manifest `docs/plans/evidence/007/MANIFEST.json`.

No owned source file exceeds 500 lines without a real seam. Conditional skips count only with concrete capability/data/budget evidence and never substitute for the child lineage, real BranchRun, or adaptive-stop core Goal. Behavioral tests assert the promising-child contract through public outcomes — pre-filter eligibility, deterministic ranking for fixed recorded evidence, replay-to-boundary hash-verification with fall-back to the next-ranked child, and the no-leakage wall — reusing the Plan 003 replay/dedup gates rather than re-implementing or asserting internal judge structure.

## Recovery

Research artifacts and scheduler events are append-only. Persist the scheduler cursor, finalized event order, consecutive no-new-cluster counter, active branch ids, executed count, and remaining budget after every transition. Resume from that state without reusing branch ids, reordering finalized events, or rescheduling completed work. Safely cancel only scheduler-confirmed active branches when core release needs resources, and record cleanup. Remove experimental code with no real consumer before completion. Rollback deletes only Plan 007-owned research paths; sealed core artifacts remain untouched.

## Executor prompt

    /goal Execute docs/plans/007-depth-two-and-research-extensions.md only after Plan 003 merges and without delaying core release. Deterministically pre-filter intermediate boundaries, record an auditable expansion-prior ranking, materialize one replay-stable near-miss with complete boundary-state evidence, and run genuine depth-two branches blind to the prediction with max-two concurrency. Prove finalized-classification adaptive stopping, no leakage, inherited security, and measured research outputs. Exercise comparison, Alpha, transfer, or training paths only with real prerequisites; otherwise record justified conditional skips. Core child/BranchRun/stop artifacts cannot be skipped. Verify mapped commands execute, run every Done-when command, update evidence/007/MANIFEST.json, and append the log.

## Living-doc log

### Progress

- [ ] Plan 003 boundary-evidence and security inputs audited.
- [ ] Deterministic pre-filter and expansion-prior record produced.
- [ ] Promising child replayed, state-validated, and materialized.
- [ ] Depth-two BranchRun completed with no-leakage evidence.
- [ ] Adaptive scheduler proved with finalized event ordering.
- [ ] Flat comparison measured or conditionally skipped with evidence.
- [ ] Memory/VM profiles run or conditionally skipped with evidence.
- [ ] Transfer, training-data, and optional training packets independently resolved.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: put all non-core research behind one removable feature boundary and forbid it from gating the demo.
- 2026-06-21 — Decision (ADR, grilling): promising-child selection (WP1) is a two-stage expansion prior over recorded depth-1 evidence, materialized by replay-to-boundary with fail-closed state validation. Ranking terminal states only and snapshotting many live boundaries were rejected because they either open no new search or pay snapshot cost before selection. Better-than-random remains TBD; the single selection receives only a falsifiable prediction check and cannot bypass Witness gates.
- 2026-06-21 — Quality revision: made the core child/BranchRun/adaptive-stop outcome non-skippable; fixed the candidate cap at 24 with deterministic reduction; required judge, state-evidence, no-leakage, scheduler, security, and contamination provenance; split transfer/data/training outcomes; and required mapped commands to execute rather than pass by SKIP.

### Outcomes & Retrospective

- Pending execution.
