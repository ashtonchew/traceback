---
name: demo-observability-and-publication
description: >
  Provides the operator command/report that walks the 13-step ForkProof demo, exposes branch and evidence links, reports measured metrics, labels the prior-run fallback honestly, and publishes or displays the passing hardened release. Use when Plan 005 has merged a passing ReleaseProof; it owns src/forkproof/demo/**, tests/forkproof/demo/**, scripts/forkproof-demo*, artifacts/forkproof/demo/**, this plan/reference, and evidence/006/**.
owns: ["docs/plans/006-demo-observability-and-publication.md", "docs/plans/006-demo-observability-and-publication.REFERENCE.md", "src/forkproof/demo/**", "tests/forkproof/demo/**", "scripts/forkproof-demo*", "artifacts/forkproof/demo/**", "docs/plans/evidence/006/**"]
depends_on: ["verifier-fix-and-release-proof"]
wave: 5
---

# Demo, observability, and publication

## Goal

Provide one repository-native demo invocation that produces a 13-of-13 step evidence report, starts genuine stochastic branches, can restore a clearly labelled prior-run Witness fallback, shows the passing ReleaseProof, and returns either a published environment id or an explicit permission-blocked release-candidate id. Done is binary when all 13 report entries have evidence and one of the two honest release outcomes is recorded.

## Context / Why

The judge must see a suspicious trace become a defended environment version. The demo should orchestrate existing HUD and Modal surfaces rather than hide them behind a speculative custom frontend. Every displayed claim must link to durable evidence, and live stochastic discovery must not be faked.

This slice owns operator orchestration, concise status/links, metrics aggregation, claim wording, fallback flow, and trusted publication/display. It consumes immutable artifacts from earlier plans and does not modify their contents. Read the sibling reference for the 13-step evidence matrix and fallback script.

## Constraints

- Use the repository's existing CLI/UI/report conventions. Add no standalone frontend unless Wave 1 found a directly reusable surface.
- Start a genuine stochastic search during the demo; do not guarantee it will discover a new exploit in presentation time.
- When switching to a prior-run Witness, show original run identity and label it before replay.
- Display reward and QA classification separately.
- Link trace ids, file diffs, ForkPoint, branch ids, Witness, ProofSet, patch, controls, ReleaseProof, and environment/release candidate.
- Derive metrics from stored events; use `not-measured`, never estimates.
- Publication runs in a trusted context and only for a passing ReleaseProof.
- STOP publication on proof mismatch, unauthorized target, mixed environment/grader identity, or missing release artifacts. Permission denial may still complete the “display candidate” outcome.
- Keep orchestration/reporting local. Split files over 500 lines by command/report/publisher responsibilities.
- Tests assert operator-visible steps and truthful fallback state, not terminal formatting snapshots alone.

## Work packets

### WP1 — Build the repository-native demo command

Compose existing operations into one resumable command or established UI flow. Accept immutable source trace/ForkPoint/ReleaseProof ids and expose progress without duplicating core logic.

**Pass:** A clean operator can run one documented invocation and resume from durable artifacts.  
**Fail:** The demo contains hidden one-off state or reimplements capture/search/replay/release.

### WP2 — Surface live discovery honestly

Open/link the source trace, QA result, file evidence, ForkPoint, and start real stochastic branches. Stream branch ids/status and inspect one successful exploit when available.

**Pass:** Branch activity is genuine and all displayed ids correspond to persisted records.  
**Fail:** A prerecorded branch list is shown as live execution.

### WP3 — Implement the prior-run fallback

When live discovery does not produce a Witness within the bounded presentation window, announce fallback, load a sealed prior-run Witness, restore its state, and replay it live before continuing.

**Pass:** Report/UI marks `discovery_source: prior-run`, links the original run, and shows a new replay result.  
**Fail:** The fallback is unlabeled or only plays a recording.

### WP4 — Walk proof and preservation evidence

Show Witness addition to ProofSet, patch/fixer reference, v2 Witness failure, control success, and ReleaseProof gate. Preserve separate raw and normalized results.

**Pass:** Every claim links to the immutable artifact or trace that supports it.  
**Fail:** The operator must trust a verbal summary or a manually edited slide.

### WP5 — Aggregate metrics and research-safe claims

Generate the core report: branch count, clusters, time to Witness, before/after rewards, control retention, replay rate, restore latency, setup avoided, and optional flat comparison. Use bounded wording: “MCTS-shaped,” no complete coverage claim.

**Pass:** Every numeric value has an event/artifact source; absent values are `not-measured`.  
**Fail:** Illustrative or handoff numbers appear as results.

### WP6 — Publish or display the hardened release

From a trusted context, verify ReleaseProof digest and publish environment v2 to an authorized target. If permission is unavailable, seal/display the release candidate and exact blocked action without claiming publication.

**Pass:** Output contains either a real published environment reference or a permission-blocked candidate with proof intact.  
**Fail:** Publication is attempted from an untrusted branch or success is claimed from a local file only.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-006-tests
    python docs/plans/scripts/run_mapped.py demo
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/run_mapped.py build
    python docs/plans/scripts/validate_file_sizes.py --plan 006
    python docs/plans/scripts/validate_evidence.py --plan 006 --require-complete

Expected evidence:

- exact demo invocation and exit status,
- 13-step report with 13 linked pass/display entries,
- real live branch ids,
- live-discovery or explicitly prior-run fallback status,
- Witness replay, v2 failure, and all-control preservation links,
- ReleaseProof id/digest,
- published environment or blocked release-candidate id,
- measured/not-measured metrics report,
- screenshots only where they add operator-visible evidence,
- manifest `docs/plans/evidence/006/MANIFEST.json`.

No owned source file exceeds 500 lines without a real seam. Tests verify semantic step completion and truthful labels, not cosmetic output.

## Recovery

The demo command is resumable by immutable artifact ids and never mutates sealed proof. On interruption, restart from the last report step and create a new invocation id. Live branch sandboxes are cleaned or left to recorded timeout cleanup. Publication is idempotent by ReleaseProof/content digest or must detect an existing version. Roll back demo code/report artifacts without deleting core evidence or published versions.

## Executor prompt

    /goal Implement docs/plans/006-demo-observability-and-publication.md after Plan 005 merges. Provide one resumable repository-native demo that evidences all 13 handoff steps, starts real branches, labels and live-replays any prior-run fallback, reports only measured values, and publishes the passing release or honestly displays a permission-blocked candidate. Run Done-when commands, stay inside owned paths, update evidence/006/MANIFEST.json, and append the Living-doc log.

## Living-doc log

### Progress

- [ ] Demo command/orchestration complete.
- [ ] Live discovery surface complete.
- [ ] Honest fallback complete.
- [ ] Proof/control walkthrough complete.
- [ ] Metrics and claims complete.
- [ ] Publish/display outcome complete.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: default to a repository-native CLI/report plus HUD/Modal links rather than add an unrequested custom UI.

### Outcomes & Retrospective

- Pending execution.
