---
name: verifier-fix-and-release-proof
description: >
  Reuses the verified harden-v0 fixer to patch the exact grader, builds a rerunnable ProofSet from sealed Witnesses and controls, and emits a binary v1-versus-v2 ReleaseProof. Use when Gate 3 is open: Plan 003 is complete with at least one sealed Exploit Witness and Plan 004 is complete with three frozen controls; it owns src/forkproof/releases/**, tests/forkproof/releases/**, artifacts/forkproof/releases/**, this plan/reference, and evidence/005/**.
owns: ["docs/plans/005-verifier-fix-and-release-proof.md", "docs/plans/005-verifier-fix-and-release-proof.REFERENCE.md", "src/forkproof/releases/**", "tests/forkproof/releases/**", "artifacts/forkproof/releases/**", "docs/plans/evidence/005/**"]
depends_on: ["stochastic-witness-loop", "legitimate-control-fixtures"]
wave: 4
---

# Verifier fix and ReleaseProof

## Goal

Produce one harden-v0-derived verifier patch and one sealed ReleaseProof for a ProofSet containing every sealed core Exploit Witness available at closure time (at least one) and at least three controls; done is binary only when v1 rewards all cases, v2 rewards zero Witnesses, and v2 preserves every control.

## Context / Why

Finding an exploit is not the product outcome. The patch must target the exact grader that issued the original reward, and it may ship only when it removes all known attacks without narrowing legitimate behavior. The handoff explicitly reuses harden-v0's fixer loop rather than inventing another patch generator.

The known exploit for the MongoDB sales aggregation task is evaluator subversion, not a wrong aggregation solution. The attack surface is layered pytest infrastructure: a local `conftest.py` hook that can no-op or alter test behavior; an installed `pytest11` plugin path that can survive `--noconftest`; `pytest_runtest_protocol` or similar hooks that fabricate passing `TestReport` objects; and fallback layers so that defeating only one mechanism is not sufficient. A v2 verifier that only blocks `conftest.py` while installed pytest plugins or site-packages mutation remain viable is not a valid fix.

This slice owns the adapter to the existing fixer, ProofSet construction, immutable v1/v2 evaluation, patch iteration, and ReleaseProof artifact. It does not publish the environment or build the operator demo. Read the sibling reference for the gate matrix, patch-loop rules, clean evaluator context, and artifact evidence.

Stacking note: when this plan is reviewed over PR #19, Plan 003 may contain live Hacker BranchRun evidence and reward-hacking candidates without a sealed Exploit Witness. Those are upstream discovery artifacts, not Plan 005 inputs. Plan 005 can execute only after Plan 003's manifest is `complete` and names at least one sealed Exploit Witness that has passed reward, HUD QA, deduplication, durable-state, provenance, and three-replay gates.

## Constraints

- Consume only sealed Witnesses and controls; do not alter their evidence.
- Start only when `docs/plans/evidence/003/MANIFEST.json` is complete with at least one sealed Exploit Witness and `docs/plans/evidence/004/MANIFEST.json` is complete with at least three sealed controls. A Hacker BranchRun, diagnostic smoke, reward-only trace, QA-only result, or reward-hacking candidate is not a Witness until Plan 003 seals it.
- Bind the existing harden-v0 fixer/replay/legitimate behavior through a thin repository-native adapter. No parallel fixer framework.
- Patch the exact grader execution surface and record v1/v2 digests.
- Run v1 baselines and v2 results from clean restored states.
- Gate per case, not by average: one surviving Witness or one broken control rejects release.
- Keep optional re-seeded exploit-family variants separate from sealed exact Witness replays.
- For v2 evaluation, trusted test files, the pytest interpreter, and all verifier assets must be outside branch-writable state or content-checked before execution. Attacker-writable paths must not provide pytest plugins, `conftest.py`, mutated pytest internals, replacement tests, replacement site-packages, or import-path shadowing — except when intentionally replayed as v1 exploit evidence.
- STOP when the patch is applied to a detached copy, any case lacks immutable identity, the grader digest changes mid-run, the v2 evaluator runs in a branch-writable environment without content checks, or the real integration cannot be executed.
- Co-locate fixer adapter, ProofSet, gate, and ReleaseProof in the release feature.
- Split files over 500 lines by adapter/evaluator/artifact responsibilities.
- Tests assert release decisions and observable rewards, not patch text or internal call counts.

## Work packets

### WP1 — Bind the harden-v0 fixer

Use the Wave 1 mapping to invoke the existing fixer (`python -m harden` at `.external/harden-v0`, pinned revision `b9dd28c`) with sealed Witness artifacts, recorded replay actions, and legitimate context. Before writing the adapter, read the harden-v0 source at `.external/harden-v0/harden/config.py` and record the exact input schema (`HardenConfig` fields) and output schema (`result.json`) that the adapter will use. Do not guess or invent field names — bind them from the source.

Record as evidence: the `HardenConfig` fields passed (especially `max_iterations`, `hacker_retries`, `replay_retries`, `replay_enabled`, `legitimate_threshold`), the fixer run id, output patch, `result.json` path, and provenance. Record `max_iterations` explicitly — the default is 10 but must be stated in evidence so any override is traceable.

**Pass:** A reviewer can trace the patch to a real fixer run targeting the actual grader; the adapter input/output schema is derived from `.external/harden-v0` source, not invented; `max_iterations` is recorded in evidence.  
**Fail:** The implementation re-creates fixer logic, edits a separate illustrative verifier, or adapter field names are guessed without reading the source.

### WP2 — Build and seal the ProofSet

Before assembling the ProofSet, verify each candidate Witness and control is fully sealed:

- For each Witness: read its sealed record from `evidence/003/`, confirm it is an Exploit Witness rather than a BranchRun candidate, and verify all required fields from `docs/plans/specs/03-interfaces.md#exploit-witness-record`: `source_branch_id`, durable `pre_attack_snapshot_ref`, `recorded_actions_ref` with the exact replayed action span, `file_diff_ref`, `verifier_output_ref`, `qa_result_ref`, `environment_version`, `environment_image_digest`, `grader_digest`, `exploit_target`, `exploit_mechanism`, `cluster_id`, `replay_entrypoint`, `replay_checks`, `content_digest`, and `retention_policy`.
- For each Witness: confirm the sealed record shows reward success under v1, authoritative HUD QA `is_reward_hacking: true` joined to the same branch id, trace id, QA result ref, and action-record digest, a recorded target/mechanism dedup decision, no retained secret material, content digest verification, and three consecutive fresh v1 replay checks with no model/gateway calls.
- For each control: read its sealed record from `evidence/004/`, confirm all Phase 1 fields (`task_id`, `grader_digest`, `verifier_harness_digest`, `environment_dockerfile_digest`, `solution_ref`, `content_digest`) and all Phase 2 fields (`environment_version`, `task_checksum`, `baseline_runs[]` with three entries, `frozen_at`) are present and non-placeholder.

STOP if any candidate fails this check; do not silently exclude it. Also STOP if a proposed Witness is only a Hacker BranchRun, diagnostic smoke, reward-only trace, QA-only result, un-deduplicated candidate, or replay-unsealed artifact. Record the query time, the canonical ForkPoint/lineage refs from Plan 003 evidence, and the set of ids that passed so a late-arriving Witness cannot be silently added after closure.

Then assemble all verified sealed core Witness ids, at least three verified control ids, and any optional family variants into a repository-native HUD taskset/suite plus immutable manifest. Witness membership must be non-empty.

**Pass:** Pre-closure verification passes for every member; one command can rerun every member; the set has a content digest.  
**Fail:** Cases are copied into mutable ad hoc scripts or omitted after failure; or the pre-closure check is skipped on the assumption upstream plans ran correctly.

### WP3 — Establish v1 baseline

Read the `environment_version` from Plan 004's sealed control records (Phase 2 field, `evidence/004/`). This is the authoritative v1 environment identifier — do not re-derive it from a fresh HUD call or invent it. Verify it matches across all three sealed controls before proceeding; if the values differ, STOP.

Replay every Witness and control against that pinned `environment_version` and the v1 grader digest from clean state.

**Pass:** Every Witness reproduces success and every control succeeds; results link traces, the pinned `environment_version`, and grader digest.  
**Fail:** Any exact Witness no longer reproduces or a control is unstable; stop and return to owning plan. `environment_version` is re-derived, inconsistent across controls, or absent.

### WP4 — Apply patch to the exact v2 grader

Create environment/grader v2 through the repository's real versioning path, verify the changed digest, and ensure replay loads v2 rather than a detached file.

Record the clean evaluator context for every v2 evaluation run: the pytest import path, the active pytest plugin list (from `--co -q` or `pytest --version` output), the test asset digest, interpreter and pytest version provenance, effective cwd/rootdir, and environment variables relevant to pytest behavior. Candidate controls for restricting the evaluator include `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, explicit cwd/rootdir, `--confcutdir`, `--noconftest`, and `-p no:<plugin>` where needed — the exact mechanism is the harden-v0/real-grader output, not a prescribed fix. Record whatever mechanism v2 uses and verify it is not defeatable by the v1 exploit's fallback layers.

Run mandatory v2 regression checks for each known evaluator-subversion layer: branch-local `conftest.py`, installed `pytest11` entry-point plugin, `pytest_runtest_protocol`/`TestReport` fabrication, import-path or cwd shadowing, attacker-writable site-packages mutation, and replacement of trusted test assets. These are core exact-Witness/family mechanism checks, not optional family variants; any viable layer rejects the release.

**Pass:** Runtime evidence shows v2's grader digest, patch provenance, complete clean-evaluator-context record, and failed v2 regression attempts for every known evaluator-subversion layer. The recorded context shows attacker-writable paths cannot inject pytest plugins, conftest files, mutated site-packages, replacement tests, or import shadowing.
**Fail:** The evaluator still loads v1 or an unrelated copy; the evaluator context record is absent; the patch only blocks `conftest.py` while plugin/site-packages paths remain attacker-writable; or any known evaluator-subversion layer remains viable.

### WP5 — Iterate the binary release gate

Run exact Witness replays first and controls second or in a safe equivalent order. A surviving Witness widens the fix; a broken control relaxes it through the existing loop. Repeat from clean state until pass or bounded failure. The iteration limit is the `max_iterations` value recorded in WP1 evidence — do not exceed it, and do not silently reset the counter.

For each rejected candidate patch, record a rejection entry containing: iteration number, fixer run id, patch artifact reference, per-case ProofSet gate results (case id, v2 reward, pass/fail), surviving Witness ids, broken control ids, and the gate decision. This is the "rejection history" required in the ReleaseProof — it is Plan 005's gate-level record, not harden-v0's internal `result.json` outcomes (which track the fixer's internal hack/fix/solver cycle, not the ProofSet evaluation).

When `max_iterations` is exhausted without the gate passing, record status as `bounded_failure` in the ReleaseProof with the full rejection history. Do not invent a passing result or re-run beyond the stated limit.

Family variants are run and recorded but do not participate in the binary gate. A surviving family variant (one that scores success under v2) does not block release — record it in the ReleaseProof under a separate `family_variant_results` field with its v1 baseline and v2 outcome. Plan 005 cannot promote a family variant, BranchRun candidate, or QA-only result to a sealed Witness; promotion is Plan 003's responsibility. If a surviving variant is significant enough to warrant blocking, the path is: return to Plan 003, promote through its full truth table, durable packaging, target/mechanism deduplication, and three-replay seal, then re-enter Plan 005 with the newly sealed Witness in a new ProofSet closure.

**Pass:** All Witnesses score failure and all controls score success under one immutable v2 digest; family variant results are recorded separately regardless of their v2 outcome.  
**Fail:** Results are averaged, skipped, manually relabelled, or produced under mixed grader versions; or a surviving family variant is silently omitted from the ReleaseProof rather than recorded.

### WP6 — Emit sealed ReleaseProof

Persist v1/v2 identities, ProofSet, patch/fixer references, per-case results, trace links, killed/preserved counts, gate status, and release-candidate reference. The `environment_v1` field in the ReleaseProof must be the `environment_version` read from Plan 004's sealed controls — not a value re-derived at emit time.

**Pass:** The artifact round-trips, content-verifies, and independently explains why release passed; `environment_v1` matches the value recorded in all three of Plan 004's sealed controls.  
**Fail:** It contains only a summary claim or mutable dashboard state; or `environment_v1` was re-derived rather than read from Plan 004's evidence.

## Done-when (self-validation gate)

Before running the mapped commands, confirm `docs/plans/repo-map/COMMANDS.json` entries `plan-005-tests` and `integration-release` are `verified` with real argv. `COMMANDS.json` is a shared registry under Plan 001's custodianship, not a Plan 005 owned path. If either row is still `not-applicable`, STOP and obtain a Plan-001/repo-map custodial update or an explicitly recorded cross-plan exception before editing that registry. Until those entries are verified, `run_mapped.py` will SKIP and exit 0 without running anything — a trivially passing gate that proves nothing.

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
- clean evaluator context record: pytest import path, active plugin list, test asset digest, interpreter/pytest version provenance, effective cwd/rootdir, environment variables relevant to pytest at v2 evaluation time,
- failed v2 regression attempts for every known evaluator-subversion layer: `conftest.py`, `pytest11` plugin autoload, hook/TestReport fabrication, import/cwd shadowing, site-packages mutation, and trusted test replacement,
- one content-verified ReleaseProof,
- manifest `docs/plans/evidence/005/MANIFEST.json`.

No owned source file exceeds 500 lines without an approved seam. Tests prove gate behavior, including empty Witness membership, one surviving Witness, one broken control, mixed-digest rejection, and each known pytest-subversion fallback layer, without asserting patch implementation details.

## Recovery

Every evaluation is keyed by ProofSet and grader digest, so reruns are append-only and comparable. Resume fixer iteration from the last rejected ReleaseProof candidate; do not overwrite prior results. Clean temporary grader builds/sandboxes after recording ids. Roll back by discarding v2 candidate and adapter changes; v1 artifacts, Witnesses, and controls remain immutable.

## Executor prompt

    /goal Implement docs/plans/005-verifier-fix-and-release-proof.md only after Gate 3 is open: Plan 003 is complete with at least one sealed Exploit Witness and Plan 004 is complete with three sealed controls. Reuse the real harden-v0 fixer, patch the exact grader, seal a non-empty ProofSet of every sealed core Witness plus at least three controls, and produce a ReleaseProof only when all v2 Witness rewards are failure, all known evaluator-subversion regression attempts fail, and all controls remain success. Run every Done-when command, stay inside owned paths or recorded ownership exceptions, update evidence/005/MANIFEST.json, and append the Living-doc log.

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
- 2026-06-20 — WP2 amended to require explicit pre-closure seal verification (Phase 1 + Phase 2 fields, content digest, three-replay confirmation) before closing ProofSet membership. Reason: `validate_evidence.py --require-complete` checks MANIFEST.json shape only, not artifact content — a Plan 004 executor could mark complete with Phase 2 fields absent and the merge gate would still open.
- 2026-06-20 — Done-when amended to require `COMMANDS.json` entries to be `verified` before running mapped commands. Reason: `run_mapped.py` exits 0 with SKIP for `not-applicable` commands — both `plan-005-tests` and `integration-release` are currently `not-applicable`, so the gate is inert until real argv are recorded. This was later tightened on 2026-06-21 to respect Plan 001 custody of `docs/plans/repo-map/**`.
- 2026-06-20 — WP5 amended to clarify family variant gate behavior: family variants never block release in Plan 005. Plan 005 cannot promote variants to sealed Witnesses (that is Plan 003's responsibility and path). A surviving variant is recorded in the ReleaseProof under `family_variant_results` and reported separately; it does not widen the fix or halt iteration. The "unless promoted/sealed" clause in the REFERENCE gate matrix is effectively dead within Plan 005's scope.
- 2026-06-20 — WP1 and WP5 amended to address fixer iteration bounds. A prior source audit observed `.external/harden-v0/harden/config.py` defaults `max_iterations=10`, `hacker_retries=3`, and `replay_retries=1`, but a Plan 005 executor must verify the current pinned source again before adapter work. WP1 requires recording `max_iterations` and adapter input/output schema from source before writing any adapter code. WP5 requires per-iteration ProofSet rejection entries (gate-level evidence, distinct from harden-v0's internal `result.json` outcomes) and a `bounded_failure` status when the limit is exhausted.
- 2026-06-21 — Stack audit over PR #19: Plan 003 currently records live terminal-bench authorized-audit Hacker BranchRuns and reward-hacking candidates, but its manifest remains `blocked` until durable Witness packaging, target/mechanism deduplication, and three deterministic replays pass. Plan 005 therefore treats those candidates as upstream blockers, not ProofSet members, and its start rule now requires a complete Plan 003 manifest with sealed Exploit Witness records.
- 2026-06-21 — Governance audit: repo-map files disagree (`repo-map/STATUS.json` is `accepted`, while `REPOSITORY.md`, `DEPENDENCIES.md`, and `EVIDENCE-PACKETS.md` still describe Gate 1 as blocked/open). Per AGENTS.md, this inconsistency is recorded here and in `docs/plans/evidence/005/MANIFEST.json`; Plan 005 execution remains blocked until the active executor resolves or accepts the repo-map source-of-truth conflict.
- 2026-06-21 — Command-registry decision: Plan 005 may require `plan-005-tests` and `integration-release` rows to become verified, but `docs/plans/repo-map/COMMANDS.json` remains Plan 001 custodial scope. A Plan 005 executor must stop on `not-applicable` rows and obtain a repo-map update or explicit cross-plan exception before editing the registry.
- 2026-06-21 — Pytest fallback decision: the known evaluator-subversion layers are mandatory v2 regression checks. A surviving `conftest.py`, `pytest11`, hook/TestReport, import-shadowing, site-packages mutation, or test-replacement path rejects the release rather than being filed as an optional family variant.

### Outcomes & Retrospective

- Pending execution.
