---
name: demo-observability-and-publication
description: >
  Provides the operator command/report that walks the 13-step ForkProof demo, exposes branch and evidence links, reports measured metrics, labels the prior-run fallback honestly, and publishes or displays the passing hardened release through a thin trusted publisher wrapper. Use when Plan 005 has merged a passing ReleaseProof and Wave 1 has bound the publish primitive; it owns src/forkproof/demo/**, tests/forkproof/demo/**, scripts/forkproof-demo*, artifacts/forkproof/demo/**, this plan/reference, and evidence/006/**.
owns: ["docs/plans/006-demo-observability-and-publication.md", "docs/plans/006-demo-observability-and-publication.REFERENCE.md", "src/forkproof/demo/**", "tests/forkproof/demo/**", "scripts/forkproof-demo*", "artifacts/forkproof/demo/**", "docs/plans/evidence/006/**"]
depends_on: ["verifier-fix-and-release-proof"]
wave: 5
---

# Demo, observability, and publication

## Goal

Provide one repository-native demo invocation that produces a 13-of-13 step evidence report, starts genuine stochastic branches, can restore a clearly labelled prior-run Witness fallback, shows the passing ReleaseProof, and returns either a published environment id or an explicit permission-blocked release-candidate id. Done is binary when all 13 report entries have non-screenshot evidence, the machine-readable report validates, all required mapped commands run without `SKIP`, and one honest release outcome is recorded.

## Context / Why

The judge must see a suspicious trace become a defended environment version. The demo should orchestrate existing HUD and Modal surfaces rather than hide them behind a speculative custom frontend. Every displayed claim must link to durable evidence, and live stochastic discovery must not be faked. Current agent-evaluation guidance treats traces and structured eval runs as the durable basis for debugging and repeatability, while HUD frames environments as controlled worlds that can reset and reproduce task state exactly ([OpenAI agent evals](https://developers.openai.com/api/docs/guides/agent-evals), [HUD introduction](https://docs.hud.ai/v6/start)).

This slice owns operator orchestration, concise status/links, metrics aggregation, claim wording, fallback flow, the thin trusted publisher wrapper, and trusted publication/display report integration. It consumes immutable artifacts from earlier plans and does not modify their contents. Plan 005 owns ReleaseProof creation and release-candidate sealing; Wave 1 owns discovery and binding of the real HUD/environment publish primitive. Plan 006 owns the final verified invocation and honest presentation of that bound primitive. Read the sibling reference for the 13-step evidence matrix, fallback script, machine-readable report, and publication attempt schema.

## Constraints

- Use the repository's existing CLI/UI/report conventions. Add no standalone frontend unless Wave 1 found a directly reusable surface.
- Start a genuine stochastic search during the demo; do not guarantee it will discover a new exploit in presentation time.
- When switching to a prior-run Witness, show original run identity and label it before replay.
- Display reward and QA classification separately.
- Link trace ids, file diffs, ForkPoint, branch ids, Witness, ProofSet, patch, controls, ReleaseProof, and environment/release candidate.
- Derive metrics from stored events; use `not-measured`, never estimates.
- Completion proof is noninteractive and machine-readable. The judge-visible demo may add UI and screenshots, but `report.json`, evidence refs, command results, and the manifest are the merge-gate source of truth.
- Publication runs in a trusted context and only for a passing ReleaseProof.
- The branch runner, fixer sandbox, and untrusted demo surfaces must not hold publication authority. Modal documents Sandboxes as secure containers for untrusted user or agent code, so publish credentials remain outside those execution contexts ([Modal Sandboxes](https://modal.com/docs/guide/sandboxes)).
- STOP publication on absent Wave 1 publish binding, proof mismatch, unauthorized target, mixed environment/grader identity, missing release artifacts, or unavailable trusted context. Permission denial may still complete the “display candidate” outcome.
- Any `SKIP` from `plan-006-tests`, `demo`, or publication-specific mapped commands is a failed Plan 006 validation, not evidence.
- Keep orchestration/reporting local. Split files over 500 lines by command/report/publisher responsibilities.
- Tests assert operator-visible steps, truthful fallback state, publication failure semantics, and report schema validity, not terminal formatting snapshots alone.

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

Implement a thin trusted publisher wrapper and report integration under `src/forkproof/demo/**`. The wrapper must not invent the HUD/environment publication API: Wave 1 must have bound the real publish primitive and authorized target in the repo map. Plan 006 verifies the sealed ReleaseProof digest, v1/v2 environment and grader identities, target identity, publisher capability label, release artifact refs, and trusted execution context before invoking the bound primitive.

Expose the publish/display operation both as step 13 of the full demo and as an independently runnable operation by ReleaseProof id/digest. Publication is idempotent by ReleaseProof content digest plus target: rerunning the same request returns the existing published ref or the same blocked candidate without mutating sealed proof or creating duplicate versions. If the publish primitive is unbound, STOP with `blocked-with-proof`. If credentials deny publication, record `permission-blocked` with the sealed candidate id, attempted command, target, and normalized authorization error without claiming publication.

**Pass:** Output contains `published`, `permission-blocked`, or `blocked-with-proof`, each backed by ReleaseProof digest, target identity, trusted command evidence, idempotency evidence, and stable artifact refs.
**Fail:** Plan 006 guesses a publish API, publishes from an untrusted branch/demo UI context, mutates ReleaseProof, creates duplicate versions on retry, or treats a local candidate as published.

## Self-validation contract

Self-validation is deterministic even when live discovery is stochastic. The demo may start genuine stochastic branches, but completion is proven by replayable artifacts, stable ids, machine-readable checks, and trace/event evidence. This follows agent-eval guidance to start from traces while debugging behavior and move to repeatable datasets/eval runs once success criteria are known ([OpenAI agent evals](https://developers.openai.com/api/docs/guides/agent-evals)). It also follows current agent-evaluation guidance to run multiple trials or repeated checks for nondeterministic behavior and to evaluate outcomes/state changes rather than only the path taken ([Anthropic agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), [LangChain agent evaluation checklist](https://www.langchain.com/blog/agent-evaluation-readiness-checklist)).

Screenshots are supplementary only. Auditability requires report rows, trace ids, metric evidence refs, command outputs, artifact digests, and provenance-like records for inputs and outputs. Evidence should be safe to retain: collect only observability data needed for the proof and never record secret values ([OpenTelemetry sensitive data guidance](https://opentelemetry.io/docs/security/handling-sensitive-data/), [SLSA provenance](https://slsa.dev/spec/v1.0/provenance)).

## Done-when (self-validation gate)

Before running completion commands, STOP unless:

- `repo-map/STATUS.json` is `accepted`;
- Gate 4 has merged with complete Plan 005 evidence;
- `plan-006-tests`, `demo`, and all publication-specific command keys in `COMMANDS.json` are `verified`, have non-empty `argv`, and do not print `SKIP`;
- the bound publish primitive and authorized target are recorded, or the absence is recorded as `blocked-with-proof` with a sealed release candidate and passing ReleaseProof.

Run from repository root:

    python docs/plans/scripts/validate_graph.py
    python docs/plans/scripts/validate_sections.py
    python docs/plans/scripts/validate_ownership.py --repo-bound
    python docs/plans/scripts/validate_traceability.py
    python docs/plans/scripts/run_mapped.py plan-006-tests
    python docs/plans/scripts/run_mapped.py integration-publication
    python docs/plans/scripts/run_mapped.py publication-idempotency
    python docs/plans/scripts/run_mapped.py publication-permission-denied
    python docs/plans/scripts/run_mapped.py publication-trust-boundary
    python docs/plans/scripts/run_mapped.py demo
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/run_mapped.py build
    python docs/plans/scripts/validate_file_sizes.py --plan 006
    python docs/plans/scripts/validate_evidence.py --plan 006 --require-complete

Expected evidence:

- exact demo invocation and exit status,
- `artifacts/forkproof/demo/<invocation_id>/report.json` with exactly 13 linked pass/display/fallback/blocked-with-proof entries,
- proof that `plan-006-tests`, `demo`, and publication-specific mapped commands did not return `SKIP`,
- real live branch ids,
- live-discovery or explicitly prior-run fallback status,
- unlabeled fallback rejection check,
- fake-live-branch rejection check,
- Witness replay, v2 failure, and all-control preservation links,
- ReleaseProof id/digest,
- repository-bound publish primitive and command key,
- trusted publisher invocation id, publisher capability label, target identity, idempotency key, and duplicate-run result,
- permission-denied run with normalized authorization error,
- trust-boundary negative check proving untrusted branch/fixer/demo contexts lack publish authority,
- published environment ref or permission-blocked/blocked-with-proof release-candidate id,
- proof that preflight stops do not mutate sealed ReleaseProof or claim publication,
- measured/not-measured metrics report,
- screenshots only where they add operator-visible evidence,
- manifest `docs/plans/evidence/006/MANIFEST.json`.

No owned source file exceeds 500 lines without a real seam. Tests verify semantic step completion, truthful labels, report schema validity, publisher idempotency, proof/target mismatch rejection, and permission semantics, not cosmetic output.

## Recovery

The demo command is resumable by immutable artifact ids and never mutates sealed proof. On interruption, restart from the last report step and create a new invocation id. Live branch sandboxes are cleaned or left to recorded timeout cleanup. Publication is idempotent by ReleaseProof/content digest plus target and must detect an existing version or blocked candidate. Roll back demo code/report artifacts without deleting core evidence, release candidates, publication attempts, or published versions.

## Executor prompt

    /goal Implement docs/plans/006-demo-observability-and-publication.md after Plan 005 merges and Wave 1 has bound the publish primitive. Provide one resumable repository-native demo that emits a validating 13-step report.json, starts real branches, labels and live-replays any prior-run fallback, reports only measured values, and uses the thin trusted publisher wrapper to publish the passing release or honestly display a permission-blocked/blocked-with-proof candidate. Run Done-when commands, treat SKIP as failure, stay inside owned paths, update evidence/006/MANIFEST.json, and append the Living-doc log.

## Living-doc log

### Progress

- 2026-06-20 — Planning hardening pass added deterministic self-validation, machine-readable report, thin trusted publisher ownership, and publication-specific negative checks.
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
- 2026-06-20 — Planning decision: Plan 006 owns the thin trusted publisher wrapper and report integration because this slice owns publication/display. Wave 1 binds the real publish primitive and Plan 005 owns ReleaseProof creation.
- 2026-06-20 — Planning decision: Plan 006 completion requires a noninteractive `report.json` and manifest-backed evidence. Judge-visible UI/screenshots are supplementary, not merge-gate proof.
- 2026-06-20 — Planning decision: `SKIP` from `plan-006-tests`, `demo`, or publication-specific mapped commands fails validation because skipped commands cannot prove Plan 006 behavior.

### Outcomes & Retrospective

- Pending execution.
