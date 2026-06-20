---
name: verifier-fix-and-release-proof
description: >
  Reuses the verified harden-v0 fixer to patch the exact grader, builds a rerunnable ProofSet from sealed Witnesses and controls, and emits a binary v1-versus-v2 ReleaseProof. Use when Plans 003 and 004 have merged with at least one replayable Witness and three frozen controls; it owns src/forkproof/releases/**, tests/forkproof/releases/**, artifacts/forkproof/releases/**, this plan/reference, and evidence/005/**.
owns: ["docs/plans/005-verifier-fix-and-release-proof.md", "docs/plans/005-verifier-fix-and-release-proof.REFERENCE.md", "src/forkproof/releases/**", "tests/forkproof/releases/**", "artifacts/forkproof/releases/**", "docs/plans/evidence/005/**"]
depends_on: ["stochastic-witness-loop", "legitimate-control-fixtures"]
wave: 4
---

# Verifier fix and ReleaseProof

## Goal

Produce one harden-v0-derived verifier patch and one sealed ReleaseProof for a ProofSet containing every available core Witness and at least three controls; done is binary only when v1 rewards all cases, v2 rewards zero Witnesses, and v2 preserves every control.

## Context / Why

Finding an exploit is not the product outcome. The patch must target the exact grader that issued the original reward, and it may ship only when it removes all known attacks without narrowing legitimate behavior. The handoff explicitly reuses harden-v0's fixer loop rather than inventing another patch generator.

This slice owns the adapter to the existing fixer, ProofSet construction, immutable v1/v2 evaluation, patch iteration, and ReleaseProof artifact. It does not publish the environment or build the operator demo. Read the sibling reference for the gate matrix, patch-loop rules, and artifact evidence.

## Constraints

- Consume only sealed Witnesses and controls; do not alter their evidence.
- Bind the existing harden-v0 fixer/replay/legitimate behavior through a thin repository-native adapter. No parallel fixer framework.
- Patch the exact grader execution surface and record v1/v2 digests.
- Run v1 baselines and v2 results from clean restored states.
- Gate per case, not by average: one surviving Witness or one broken control rejects release.
- Keep optional re-seeded exploit-family variants separate from sealed exact Witness replays.
- STOP when the patch is applied to a detached copy, any case lacks immutable identity, the grader digest changes mid-run, or the real integration cannot be executed.
- Co-locate fixer adapter, ProofSet, gate, and ReleaseProof in the release feature.
- Split files over 500 lines by adapter/evaluator/artifact responsibilities.
- Tests assert release decisions and observable rewards, not patch text or internal call counts.

## Work packets

### WP1 — Bind the harden-v0 fixer

Use the Wave 1 mapping to invoke the existing fixer with Witness trajectory/evidence and legitimate context. Capture input ids, configuration, output patch, logs, and provenance.

**Pass:** A reviewer can trace the patch to a real fixer run targeting the actual grader.  
**Fail:** The implementation re-creates fixer logic or edits a separate illustrative verifier.

### WP2 — Build and seal the ProofSet

Assemble all core Witness ids, at least three sealed control ids, and any optional family variants into a repository-native HUD taskset/suite plus immutable manifest.

**Pass:** One command can rerun every member and the set has a content digest.  
**Fail:** Cases are copied into mutable ad hoc scripts or omitted after failure.

### WP3 — Establish v1 baseline

Replay every Witness and control against pinned environment/grader v1 from clean state.

**Pass:** Every Witness reproduces success and every control succeeds; results link traces and digests.  
**Fail:** Any exact Witness no longer reproduces or a control is unstable; stop and return to owning plan.

### WP4 — Apply patch to the exact v2 grader

Create environment/grader v2 through the repository's real versioning path, verify the changed digest, and ensure replay loads v2 rather than a detached file.

**Pass:** Runtime evidence shows v2's grader digest and patch provenance.  
**Fail:** The evaluator still loads v1 or an unrelated copy.

### WP5 — Iterate the binary release gate

Run exact Witness replays first and controls second or in a safe equivalent order. A surviving Witness widens the fix; a broken control relaxes it through the existing loop. Repeat from clean state until pass or bounded failure.

**Pass:** All Witnesses score failure and all controls score success under one immutable v2 digest.  
**Fail:** Results are averaged, skipped, manually relabelled, or produced under mixed grader versions.

### WP6 — Emit sealed ReleaseProof

Persist v1/v2 identities, ProofSet, patch/fixer references, per-case results, trace links, killed/preserved counts, gate status, and release-candidate reference.

**Pass:** The artifact round-trips, content-verifies, and independently explains why release passed.  
**Fail:** It contains only a summary claim or mutable dashboard state.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-005-tests
    python docs/plans/scripts/run_mapped.py integration-release
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/run_mapped.py build
    python docs/plans/scripts/validate_file_sizes.py --plan 005
    python docs/plans/scripts/validate_evidence.py --plan 005 --require-complete

Expected evidence:

- harden-v0 fixer run and patch reference,
- sealed ProofSet/taskset id,
- pinned v1 and v2 grader/environment digests,
- per-case v1 and v2 results,
- zero surviving Witnesses,
- all controls preserved,
- one content-verified ReleaseProof,
- manifest `docs/plans/evidence/005/MANIFEST.json`.

No owned source file exceeds 500 lines without an approved seam. Tests prove gate behavior, including one-Witness and one-control rejection cases, without asserting patch implementation details.

## Recovery

Every evaluation is keyed by ProofSet and grader digest, so reruns are append-only and comparable. Resume fixer iteration from the last rejected ReleaseProof candidate; do not overwrite prior results. Clean temporary grader builds/sandboxes after recording ids. Roll back by discarding v2 candidate and adapter changes; v1 artifacts, Witnesses, and controls remain immutable.

## Executor prompt

    /goal Implement docs/plans/005-verifier-fix-and-release-proof.md after Plans 003 and 004 merge. Reuse the real harden-v0 fixer, patch the exact grader, seal a ProofSet of every core Witness plus at least three controls, and produce a ReleaseProof only when all v2 Witness rewards are failure and all controls remain success. Run every Done-when command, stay inside owned paths, update evidence/005/MANIFEST.json, and append the Living-doc log.

## Living-doc log

### Progress

- [ ] harden-v0 fixer bound.
- [ ] ProofSet sealed.
- [ ] v1 baseline complete.
- [ ] Exact v2 grader created.
- [ ] Binary release gate passes.
- [ ] ReleaseProof sealed.

### Surprises & Discoveries

- None yet.

### Decision Log

- 2026-06-20 — Planning decision: combine fixer integration and release proof because the patch is not meaningful outside its preservation/attack gate.

### Outcomes & Retrospective

- Pending execution.
