---
name: repo-grounding-and-command-freeze
description: >
  Grounds ForkProof against the real repository by binding proposed ownership paths, existing integrations, capabilities, fixtures, and exact validation commands without changing product source. Use when a repository-connected executor is starting the bundle; it writes only docs/plans/repo-map/**, this plan/reference, and evidence/001/**, and must merge before any implementation wave.
owns: ["docs/plans/001-repo-grounding-and-command-freeze.md", "docs/plans/001-repo-grounding-and-command-freeze.REFERENCE.md", "docs/plans/repo-map/**", "docs/plans/evidence/001/**"]
depends_on: []
wave: 1
---

# Repository grounding and command freeze

## Goal

Produce one accepted repo map that binds 100% of proposed implementation globs, all nine required integration/fixture surfaces, and every mapped command used by Plans 002–007; the binary done condition is that repo-bound ownership validation and the real baseline command both pass with evidence.

## Context / Why

This bundle was authored without repository access. The handoff defines product behavior but not the actual package root, callable APIs, test runner, persistence backend, task materialization, credentials, or existing harden-v0/HUD/Modal adapters. Guessing any of those would poison every later plan.

This plan is the mandatory grounding seam. It inspects the real tree, maps semantic operations to existing code, verifies capabilities, and records exact commands in `docs/plans/repo-map/`. It does not implement ForkProof and does not modify product source. Read `001-repo-grounding-and-command-freeze.REFERENCE.md` for the map schemas and inspection checklist.

## Constraints

- Write only declared documentation and evidence paths.
- Do not rename or “clean up” repository code.
- Do not install or upgrade production dependencies.
- Do not mark an interface verified from docs alone; cite code path plus observed command/output.
- Preserve proposed feature-folder ownership when compatible. Remap only to repository-native feature boundaries, not broad shared-layer globs.
- Record every unresolved codebase claim in `ASSUMPTIONS.md` or the repo map; do not silently resolve by invention.
- STOP when the repository is unavailable, baseline cannot be run, the source trace/task/grader cannot be located, or required security capabilities are unknowable. Record the blocker and evidence.
- Keep generated map files below 500 lines. Tests/validators assert map behavior, not formatting trivia.

## Work packets

### WP1 — Orient the repository

Inspect the root tree, project configuration, package/test layout, CI, agent instructions, and existing feature conventions. Populate `repo-map/STATUS.json` repository identity and `repo-map/REPOSITORY.md`.

**Pass:** The map names the project root, language/toolchain, package roots, test roots, build system, current branch/commit, and relevant nested `AGENTS.md` files with code evidence.  
**Fail:** Any entry is inferred only from the handoff or library familiarity.

### WP2 — Bind the nine required surfaces

Locate and record real paths and public entrypoints for: HUD environment/trace/file evidence, HUD QA, Modal runtime/snapshots, agent gateway, grader/verifier, harden-v0 fixer/replay/dedup, persistence/artifact storage, MongoDB task materialization, and environment version publishing.

**Pass:** `repo-map/INTERFACES.md` gives each semantic operation a real path, symbol or executable entrypoint, input/output evidence, and status.  
**Fail:** A missing surface is replaced by an invented signature or speculative adapter.

### WP3 — Verify fixtures and capabilities

Identify one real suspicious reward-1 source trace, its QA/file evidence, the real MongoDB task, available snapshot profiles, sandbox isolation controls, branch model/gateway, and publication authorization.

**Pass:** Stable ids/locations and capability observations are recorded; unavailable Alpha features are labelled unavailable without blocking core.  
**Fail:** A synthetic trace/task is accepted as core evidence, or security capability is assumed.

### WP4 — Bind collision-free ownership

Fill `repo-map/OWNERSHIP-BINDINGS.json` for every proposed non-document glob. Accept a proposed new path or map it to an exact repository-relative glob. Preserve one feature owner per path and no same-wave overlap.

**Pass:** `validate_ownership.py --repo-bound` passes.  
**Fail:** A binding is null, broad enough to capture another plan, or resolves two same-wave owners to overlapping paths.

### WP5 — Freeze exact commands and baseline

Fill `repo-map/COMMANDS.json` with argv arrays, working directories, and applicability for baseline, lint/type checks, build, each plan's tests, core integrations, security check, research check, and demo. Run the real baseline without source modifications.

**Pass:** `run_mapped.py baseline` exits 0 and its output is recorded; every later command key is verified or explicitly not-applicable with a defensible repository-specific reason.  
**Fail:** Commands are shell prose, guessed, or marked passing without execution.

### WP6 — Close assumptions and emit gate evidence

Update only assumption entries that the repository evidence resolves. Leave unresolved entries tagged. Complete the manifest with commit, commands, map artifacts, and blockers/skips.

**Pass:** Gate 1 in `000-index.md` is mechanically and evidentially satisfied.  
**Fail:** `STATUS.json` says accepted while any core prerequisite remains unresolved.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/validate_graph.py
    python docs/plans/scripts/validate_sections.py
    python docs/plans/scripts/validate_ownership.py
    python docs/plans/scripts/validate_traceability.py
    python docs/plans/scripts/validate_ownership.py --repo-bound
    python docs/plans/scripts/run_mapped.py baseline
    python docs/plans/scripts/validate_file_sizes.py --plan 001
    python docs/plans/scripts/validate_evidence.py --plan 001 --require-complete

Expected evidence:

- accepted `STATUS.json`,
- complete interface and ownership bindings,
- real baseline command with exit code 0,
- stable source-trace/task/grader locations,
- capability/security observations,
- manifest `docs/plans/evidence/001/MANIFEST.json`.

No map file exceeds 500 lines. Completion is a verified repository map, not a plausible narrative.

## Recovery

All edits are additive documentation. Resume by reading the manifest's last successful work packet and rerunning only the affected probes. Never overwrite an accepted binding without a dated Decision Log entry and a fresh collision check. To roll back, restore the prior map files; no product source should need reverting.

## Executor prompt

    /goal Ground the real repository exactly as specified in docs/plans/001-repo-grounding-and-command-freeze.md. Do not modify product source. Bind every path, interface, capability, fixture, and command with code/runtime evidence; run the baseline and all Done-when validators; update docs/plans/evidence/001/MANIFEST.json and append the Living-doc log. Do not mark STATUS accepted while a core prerequisite is unresolved.

## Living-doc log

### Progress

- [ ] Repository orientation and instruction chain recorded.
- [ ] Required surfaces bound.
- [ ] Real fixtures and capabilities verified.
- [ ] Ownership bindings collision-checked.
- [ ] Mapped commands and baseline verified.
- [ ] Evidence manifest complete.

### Surprises & Discoveries

- None yet. Append observations with concise evidence.

### Decision Log

- 2026-06-20 — Planning decision: require a no-source-change grounding wave because repository paths and APIs were unavailable.

### Outcomes & Retrospective

- Pending execution.
