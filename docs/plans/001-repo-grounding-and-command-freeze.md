---
name: repo-grounding-and-command-freeze
description: >
  Grounds ForkProof against the real repository by binding proposed ownership paths, existing integrations, capabilities, fixtures, dependency bootstrap, environment configuration, and exact validation commands without changing product source. Use when a repository-connected executor is starting the bundle; it writes only its declared setup, spec, repo-map, plan/reference, validator, and evidence paths, and must merge before any implementation wave.
owns: [".agents/skills/**", ".claude/skills/**", ".gitignore", ".env.example", ".python-version", "pyproject.toml", "skills-lock.json", "uv.lock", "requirements/harden-v0.txt", "scripts/bootstrap_external_deps.sh", "docs/plans/scripts/validate_evidence.py", "docs/plans/specs/07-environment.md", "docs/plans/001-repo-grounding-and-command-freeze.md", "docs/plans/001-repo-grounding-and-command-freeze.REFERENCE.md", "docs/plans/repo-map/**", "docs/plans/evidence/001/**"]
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

- Write only declared setup, documentation, validator, and evidence paths.
- Do not rename or “clean up” repository code.
- Do not install or upgrade production dependencies beyond the minimal checked-in developer bootstrap needed to verify required integration inputs.
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

- [x] Repository orientation and instruction chain recorded.
- [x] Required surfaces inspected and recorded as blocked where absent.
- [ ] Real fixtures and capabilities verified.
- [x] Ownership bindings collision-checked.
- [x] Mapped commands and baseline verified.
- [x] Evidence manifest updated with blocker state.

- 2026-06-20T19:48:50Z — Executed repository-connected grounding pass on commit `99c53d2b3a27a682d67bc61a026cdc2bae16eb4e`. The repository currently contains the planning bundle and handoff only; no product source, package config, HUD/Modal/grader/harden-v0 integration, task fixture, artifact store, or sandbox policy is checked in.
- 2026-06-20T19:48:50Z — Populated `docs/plans/repo-map/` with a blocked-but-executable state: baseline command is verified, ownership bindings are accepted for future feature folders, and missing required surfaces are recorded explicitly.
- 2026-06-20T20:11:27Z — Added the Plan 001 dependency bootstrap: uv project metadata, lockfile, Python version pin, harden-v0 requirement mirror, and a pinned external checkout script for harden-v0 plus Terminal Wrench.
- 2026-06-20T20:11:27Z — Added root `.env` handling with committed `.env.example` and canonical environment-variable documentation in `docs/plans/specs/07-environment.md`.
- 2026-06-20T20:23:06Z — Addressed audit feedback by narrowing `.env` loading in the bootstrap script to `H2F2H_EXTERNAL_DIR`, removing command-line secret examples from docs, and separating verified source checkouts from completed core prerequisites in `STATUS.json`.
- 2026-06-20T20:26:54Z — Added the project-level `hud-environment-builder` skill from `https://docs.hud.ai` with `npx skills add https://docs.hud.ai --yes`; recorded the install in `skills-lock.json`.
- 2026-06-20T20:28:14Z — Added `.claude/skills/hud-environment-builder` as a symlink to the canonical `.agents/skills/hud-environment-builder` project skill so Claude Code and Codex share one skill body.

### Surprises & Discoveries

- 2026-06-20T19:48:50Z — `python docs/plans/scripts/run_all.py` is not a safe baseline in this checkout because the global file-size validator scans the 1359-line source handoff HTML. Plan-scoped file-size validation passes for Plan 001.
- 2026-06-20T19:48:50Z — No `.github` PR template, package manifest, lockfile, CI workflow, source tree, or test tree is checked in.
- 2026-06-20T20:10:00Z — Confirmed the harden-v0 upstream URL as `https://github.com/few-sh/harden-v0`. This resolves the source-location ambiguity only; the repository integration remains blocked until a pinned fork/submodule/vendor/dependency or external checkout path is recorded with command evidence.
- 2026-06-20T20:11:27Z — harden-v0 has no `pyproject.toml` at pinned revision `b9dd28c732e7e5435da4a2ac90ae92ac6ea65007`, so it is treated as a source checkout plus requirements file, not a direct Python package dependency.
- 2026-06-20T20:11:27Z — Terminal Wrench is large at the pinned revision, so the bootstrap uses sparse checkout for `tasks/mongodb-sales-aggregation-engine`. The MongoDB task source exists under `.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine`.
- 2026-06-20T20:23:06Z — A fresh sparse Terminal Wrench bootstrap updated only 8 checkout files for the MongoDB task path.
- 2026-06-20T20:26:54Z — The HUD docs skill installs as `.agents/skills/hud-environment-builder/SKILL.md` and is intended as project-local agent guidance, not a Python runtime dependency.
- 2026-06-20T20:28:14Z — OpenAI Codex docs confirm repository skills are discovered under `.agents/skills` and symlinked skill folders are supported; the Claude Code symlink is project-local compatibility glue.

### Decision Log

- 2026-06-20 — Planning decision: require a no-source-change grounding wave because repository paths and APIs were unavailable.
- 2026-06-20T19:48:50Z — Accepted the proposed `src/forkproof/**`, `tests/forkproof/**`, `fixtures/forkproof/**`, `artifacts/forkproof/**`, and `scripts/forkproof-demo*` paths as future repository-native boundaries because there is no existing implementation layout to remap into.
- 2026-06-20T19:48:50Z — Kept `STATUS.json` as `blocked` instead of `accepted`; accepting Gate 1 would require fabricating missing source trace, HUD/Modal adapters, grader identity, harden-v0 integration, real MongoDB task, artifact store, and sandbox security evidence.
- 2026-06-20T20:10:00Z — Decided not to treat the upstream harden-v0 URL as satisfying the `harden_v0` prerequisite. Gate 1 requires an executable repo-local integration contract, not only a known GitHub repository.
- 2026-06-20T20:11:27Z — Split dependency setup from adapter completion: `harden_v0` and `mongodb_task` are now verified as pinned source inputs, while HUD/Modal adapters, source trace, grader, artifact store, and security controls remain Gate 1 blockers.
- 2026-06-20T20:11:27Z — Chose committed `.env.example` plus ignored root `.env` for local development. Remote Modal execution must use Modal Secrets or service-user environment variables rather than copying local `.env` into branch sandboxes.

### Outcomes & Retrospective

- 2026-06-20T19:48:50Z — Plan 001 now gives developers a minimal local bootstrap: Python-only validation, a mapped baseline command, accepted future ownership boundaries, and an explicit list of missing surfaces required before implementation waves may begin. Gate 1 remains blocked until those real surfaces are supplied and verified.
- 2026-06-20T20:11:27Z — Developers can now run `uv sync --all-extras --all-groups` and `scripts/bootstrap_external_deps.sh` to install HUD/Modal/harden support libraries and fetch pinned harden-v0 plus sparse Terminal Wrench task sources. Gate 1 remains blocked until real adapters and proof surfaces are implemented.
