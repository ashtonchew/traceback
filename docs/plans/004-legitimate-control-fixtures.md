---
name: legitimate-control-fixtures
description: >
  Materializes the real Terminal Wrench MongoDB sales aggregation task and freezes at least three path-diverse legitimate solutions as immutable controls for verifier-preservation testing. Use when Plan 001 has verified the task, grader, solver/reference mechanism, and test commands; it owns src/forkproof/controls/**, tests/forkproof/controls/**, fixtures/forkproof/mongodb-sales-aggregation-engine/**, this plan/reference, and evidence/004/**.
owns: ["docs/plans/004-legitimate-control-fixtures.md", "docs/plans/004-legitimate-control-fixtures.REFERENCE.md", "src/forkproof/controls/**", "tests/forkproof/controls/**", "fixtures/forkproof/mongodb-sales-aggregation-engine/**", "docs/plans/evidence/004/**"]
depends_on: ["repo-grounding-and-command-freeze"]
wave: 2
---

# Legitimate control fixtures

## Goal

Reproducibly materialize one real `mongodb-sales-aggregation-engine` task and freeze at least three genuinely path-diverse legitimate controls, each scoring successful reward in three baseline runs under the pinned v1 environment and grader. Done is binary when at least nine successful clean baseline evaluations and three sealed control digests are evidenced.

## Context / Why

A patch that kills an exploit by rejecting real solutions is not a fix. The ReleaseProof therefore needs legitimate controls frozen before patch iteration. They must be generated from the real task and repository-approved solver/reference hints, not hand-authored to mirror one implementation or fabricated as cosmetic variations.

This plan runs in parallel with ForkPoint work because it owns separate fixture/control paths. It does not patch the verifier or create Witnesses. Read the sibling reference for diversity criteria and freezing rules.

## Constraints

- Use the real task through the approved repository/dataset mechanism and record provenance/license.
- Pin task revision, environment v1, grader digest, dependencies, and solver/reference inputs.
- Generate controls through a legitimate solver or verified reference-hinted path. Do not manually edit outputs after grading.
- “Path-diverse” means observably different valid solution strategies or implementation structures, not renamed variables or reordered text.
- Freeze controls before Plan 005 patch evaluation.
- STOP when the real task cannot be materialized, the grader is not pinned, or fewer than three honest distinct solutions can be produced. Record the constraint; do not fabricate diversity.
- Keep materialization, generation, validation, and immutable control records local to the feature.
- Split files over 500 lines by task adapter/generator/validation responsibilities.
- Tests assert task success and frozen immutability, not private solver calls.

## Work packets

### WP1 — Materialize and pin the real task

Use the repo-bound Terminal Wrench mechanism to obtain the MongoDB sales aggregation task. Record upstream identity/revision, license/provenance, dependency lock, grader digest, and reproducible preparation command.

**Pass:** A clean worktree can materialize the same task and verify content identity.  
**Fail:** Third-party files are copied ad hoc or depend on an unpinned mutable branch.

### WP2 — Generate legitimate solutions

Run the verified solver/reference-hinted workflow multiple times or strategies to obtain valid implementations. Preserve generation provenance and do not expose exploit instructions.

**Pass:** Candidate solutions are produced through a real legitimate path and pass the task under v1.  
**Fail:** Solutions are hand-coded solely to satisfy the plan or are derived from the known pytest exploit.

### WP3 — Establish path diversity

Compare candidates by observable implementation strategy, touched files, behavior, and solver trajectory. Select at least three that exercise meaningfully different valid paths.

**Pass:** A reviewer can explain each control's distinct legitimate strategy from evidence.  
**Fail:** Differences are formatting, naming, or nondeterministic noise.

### WP4 — Freeze immutable controls

Store solution artifacts, task/environment/grader identity, expected reward, source method, path label, content digest, and baseline results. Prevent mutation in place.

**Pass:** Each control survives process restart and content verification.  
**Fail:** A control reads mutable “latest” task/grader or can be silently overwritten.

### WP5 — Prove baseline stability

Run each control three times in clean v1 environments and capture reward and trace evidence. Include a negative corrupt-control check that fails as expected.

**Pass:** At least three controls score success in all three runs; corrupt input fails.  
**Fail:** Controls are flaky, share dirty state, or are validated only by unit mocks.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-004-tests
    python docs/plans/scripts/run_mapped.py integration-controls
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/validate_file_sizes.py --plan 004
    python docs/plans/scripts/validate_evidence.py --plan 004 --require-complete

Expected evidence:

- task provenance/revision and reproducible materialization,
- pinned v1 environment and grader digest,
- at least three distinct control ids and diversity rationales,
- nine successful baseline evaluations minimum,
- corrupt-control negative result,
- immutable content digests,
- manifest `docs/plans/evidence/004/MANIFEST.json`.

No owned source file exceeds 500 lines without a real seam. Tests verify valid-task behavior and immutability rather than solver internals.

## Recovery

Task materialization and control generation write to content-addressed staging before finalization. Resume from the last sealed control; do not mutate one to create another. Clean partial task workspaces and retain generator logs without secrets. Rollback removes only generated fixtures/control feature code; upstream task sources remain untouched.

## Executor prompt

    /goal Implement docs/plans/004-legitimate-control-fixtures.md after Plan 001 accepts the task, solver, grader, and commands. Materialize the real MongoDB task, generate and justify at least three genuinely path-diverse legitimate controls, prove each passes v1 three times, freeze immutable artifacts, stay inside owned paths, update evidence/004/MANIFEST.json, and append the Living-doc log. Stop rather than fake diversity.

## Living-doc log

### Progress

- [ ] Real task pinned and materialized.
- [ ] Legitimate candidates generated.
- [ ] Path diversity established.
- [ ] Controls sealed.
- [ ] Three-run baseline and negative check pass.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: isolate legitimate controls from patch work so preservation evidence exists before fixer iteration.

### Outcomes & Retrospective

- Pending execution.
