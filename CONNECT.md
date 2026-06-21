# CONNECT — SFT extension ↔ ForkProof core integration

**Purpose:** Define the honest boundary between ForkProof proof artifacts and the SFT/training-data analysis, including what works now, what is blocked, and the future adapter contract.

**Status (2026-06-21):** Mock pipeline executable; real integration blocked on at least one sealed Plan 003 Witness and a sealed Plan 005 ReleaseProof. Plan 003 has completed a 12-BranchRun live discovery batch with four sufficiently evidenced reward-hacking candidates, but none is a Witness until causal-delta minimization, durable packaging, target/mechanism deduplication, and three deterministic replays pass. Plan 004 controls are present. No real-data or model-training claim is currently authorized.

**Sources of truth:** repository code and artifacts; `docs/plans/007-depth-two-and-research-extensions.md`; `docs/plans/specs/03-interfaces.md`; `docs/plans/GLOSSARY.md`; `SFT.MD`; official Fireworks managed-SFT documentation. `HUDDOC.MD` describes a separate private-preview Training API experiment and is not the managed-SFT procedure in this document. `LORA.md` is not present in this checkout.

---

## 1. Connection states

| State | Meaning | Current status |
|---|---|---|
| **Mock executable** | Current strict JSONL schema loads and produces reports/exports. | PASS: 49 SFT tests and mock CLI passed on 2026-06-21. |
| **Proof connected** | A trusted adapter joins sealed Plans 003–005 artifacts and emits a content-verified normalized dataset plus provenance. | BLOCKED: Plan 003 is in progress but has no sealed Witness; Plan 005 cannot start its proof execution until that Witness exists. |
| **Analysis valid** | Metrics use one declared population, pinned v1/v2 evaluator identities, authoritative labels, and explicit quarantine counts. | BLOCKED: current metrics/filter semantics require revision before real claims. |
| **Training ready** | Every exported positive is a faithful demonstration, not a summary; Fireworks validation and held-out split gates pass. | BLOCKED: no real demonstrations or held-out split. |
| **Model result** | A real job ran and a frozen held-out evaluation supports a measured claim. | OPTIONAL / NOT RUN. |

“Connected” means **proof connected** and **analysis valid**. A JSONL file merely passing the current loader is not sufficient.

---

## 2. Prerequisites

The SFT owner needs a sealed artifact package, not only a flattened training-data file. Core owners should publish repository-native records; they do not need to implement the proposed SFT schema or hand-author compatibility rows.

### Required team handoff

| Owner | Required deliverable | Acceptance condition |
|---|---|---|
| Plan 003 owner | Completed Plan 003 evidence manifest and at least one sealed Witness; public BranchRun/action references; v1 verifier result; authoritative QA result and classification evidence; minimized causal delta; exploit target, mechanism, and cluster; durable package; three-replay evidence; source content digest. | Manifest status is `complete`; every referenced artifact resolves and verifies; the record is a sealed Witness rather than a candidate or diagnostic BranchRun. |
| Plan 004 owner | Completed control evidence manifest with at least three sealed, path-diverse controls; `solution_ref`; v1 baseline result; task/environment identity; content digest; and, when available, a faithful final assistant response or supported trajectory reference. | Controls are sealed and immutable. A `solution_ref` without a faithful response is analysis-eligible but not automatically SFT-eligible. |
| Plan 005 owner | Completed ProofSet and ReleaseProof; explicit membership; per-case v1/v2 outcomes over identical solution/action content; complete evaluator and environment identities; patch provenance; gate status; content digest. | ReleaseProof is sealed and passing; every required Witness fails v2 and every required control passes v1 and v2. |
| Repo-map custodian / relevant plan owner | Reconciled repository-map status, verified Plan 005 and Plan 007 command mappings, and accepted ownership for the SFT integration paths and this document. | The applicable merge gate is open, mapped commands execute rather than skip, and no path has ambiguous ownership. |

Plan 003's current four reward-hacking candidates do not satisfy this prerequisite. They still require causal-delta minimization, durable packaging, target/mechanism deduplication, and three deterministic replays before any one can be delivered as a Witness.

### Package-level requirements

The handoff package must include:

- one immutable delivery/package id and the producing core commit;
- a root manifest listing every included source artifact and SHA-256 content digest;
- repository-relative or content-addressed references rather than machine-local paths;
- source task, environment, evaluator, ProofSet, ReleaseProof, Witness, control, trace, action, and solution identities where applicable;
- the raw v1 and v2 outputs plus normalized semantic success/failure supplied by the owning evaluator contract;
- authoritative classification and evidence references, preserving `unknown` or `conflicting` rather than coercing either to legitimate;
- demonstration provenance identifying content as `faithful_final`, `faithful_trajectory`, `solution_artifact`, `summary`, or unavailable;
- explicit redaction confirmation: no credentials, hidden evaluator answers, private chain-of-thought, or unrelated user data;
- a retention/location statement sufficient for every referenced artifact to remain resolvable through analysis and review.

The package is incomplete if it supplies only dashboard URLs, mutable files, summaries presented as assistant responses, detached grader results, or rows whose v1 and v2 evaluations used different solution content.

### Copy-paste request to core owners

> **SFT research integration needs sealed public artifacts, not a custom SFT schema or a hand-authored flat file.**
>
> Plan 003: provide the completed evidence manifest plus at least one sealed Witness and its public BranchRun/action, verifier, QA/classification, minimized causal delta, target/mechanism/cluster, durable package, three-replay, and content-digest references.
>
> Plan 004: provide the completed control manifest with at least three sealed controls, solution refs, baseline results, task/environment identities, content digests, and faithful response/trajectory refs when they exist.
>
> Plan 005: provide the completed ProofSet and passing ReleaseProof with membership, identical-content v1/v2 outcomes, complete evaluator/environment identities, patch provenance, gate status, and content digest.
>
> Include a root package manifest with the producing commit, immutable ids, SHA-256 digests, relative/content-addressed refs, classification status, demonstration kind, and redaction confirmation. The Plan 007 adapter will join these records without modifying core artifacts.

---

## 3. Pre-data preparation completed

The following preparation is complete without relying on real core artifacts:

| Preparation | Result |
|---|---|
| Local Python toolchain | `uv` is installed and the SFT test suite executes. |
| Local Fireworks tooling | `firectl` 1.7.24 is installed; `.env` contains a `FIREWORKS_API_KEY` variable name; the user confirmed Fireworks account setup separately. No secret value was printed or copied. |
| Mock behavior baseline | 49 SFT tests pass at core commit `cd62c1615c3fb198894f282089fbad073947e9d7` on branch `sft`. |
| Mock pipeline smoke | A fresh run completed in `/private/tmp/forkproof-sft-readiness-20260621` with 12 raw examples, 4 hardened examples, 6 rejected-hack audit records, and the expected current output set. |
| Fixture identity | `fixtures/sft/mock_forkproof_traces.jsonl` SHA-256 is `91da8b510a8ff0acd930f619df0dc2f9d73c45c606bcbec81b4fabe011275609`. |
| Metric protocol | Section 8 defines same-population admissions, classified contamination, coverage, quarantine reporting, retention, and clean-SFT count. |
| Demonstration policy | Section 7 separates analysis-eligible artifacts from faithful trainable demonstrations. |
| Launch safety | `training_recommendations.json` is explicitly advisory and cannot be consumed automatically as a job configuration. |

Fireworks setup is user-confirmed. Automated authentication, account, quota, billing, and supported-model checks were intentionally skipped in this session; recheck them only if the eventual upload or dry run reports an account-side error.

### Frozen intake runbook

When the package arrives:

1. Preserve the delivered bytes and record package location, delivery id, producing commit, receipt time, and root digest before parsing.
2. Verify the root manifest and every referenced artifact digest. Reject absolute machine-local paths, unresolved refs, mutable URL-only evidence, and unexpected files.
3. Verify Plan 003, 004, and 005 manifest completion and all join invariants from Section 5. STOP on an unsealed candidate, failed ReleaseProof, evaluator mismatch, mixed solution content, or missing classification provenance.
4. Normalize into the accepted versioned schema only after that schema and Plan 007 execution are authorized. Preserve raw values and write unknown/conflicting rows to quarantine.
5. Produce an input manifest containing source ids/digests, core and adapter commits, schema version, ProofSet, ReleaseProof, evaluator identities, and normalization output digest.
6. Compute analysis over one frozen source population. Report admissions, classified contamination, classification coverage, unknown/conflicting/quarantine counts, legitimate retention, and `clean_sft_count`.
7. Export SFT examples only for faithful legitimate demonstrations. Keep summaries, bare solution artifacts, unknown labels, and Witness exploit content out of positive training data.
8. Freeze the grouped train/held-out manifest before any upload, validate Fireworks format, review redaction, and perform a dry run before spending credits.

### Frozen split policy

- Group records so the same task instance, source lineage, solution/template family, or near-duplicate demonstration cannot cross train and held-out sets.
- Keep all variants derived from one Witness, control, BranchRun parent, or demonstration artifact in one split.
- Use immutable source ids and content digests to detect exact duplication; add an explicit family key for semantic/template variants.
- Record the grouping fields, assignment algorithm, seed if any, row ids, group ids, and split-manifest digest.
- Do not choose a train/held-out ratio until real group counts are known; the value remains `TBD` rather than inventing a statistically weak split.
- If the package contains too few independent groups for a defensible held-out set, stop at data-quality analysis and do not claim a model comparison.

No sealed-artifact adapter, proposed-v2 schema implementation, real metric run, or training launch was performed during preparation because the Plan 007 dependency and ownership gate remains closed.

---

## 4. Current executable contract (schema v1)

The current implementation reads `fixtures/sft/schema/trace_record.schema.json` through:

```text
load_traces() → filter_traces() → compute_metrics() → report/export
```

Current required fields are exactly:

| Field | Current accepted value |
|---|---|
| `trace_id` | Non-empty normalized row id; unique in the file. It is not necessarily a HUD trace id. |
| `task_id` | Non-empty task identifier. |
| `task_prompt` | Non-empty user-visible instruction. |
| `assistant_output` | Non-empty string exported verbatim as a weight-1 assistant turn. |
| `raw_reward` | Numeric `0.0` or `1.0`. |
| `patched_reward` | Numeric `0.0` or `1.0`. |
| `is_hack` | Boolean. |
| `is_legit` | Boolean. |

The schema rejects unknown fields. Optional v1 fields are `exploit_cluster`, `environment_version`, `grader_version`, `patched_grader_version`, `hud_trace_url`, `witness_id`, and `release_proof_id`.

### Current limitations

These limitations are implementation facts, not future design choices:

1. Rewards are hard-coded to numeric `0/1`; repository interfaces permit grader-specific semantic success/failure representations.
2. Labels are booleans, so unknown and conflicting classifications cannot be represented cleanly.
3. Ambiguous raw-positive rows remain in `raw_sft`; they are warned about, not quarantined.
4. `hardened_sft` means `patched_reward == 1 AND is_legit`, while `hardened_hacks_admitted` counts all patched-positive hacks. The current hardened contamination denominator therefore does not describe the same population.
5. The report prints one legitimate-retention value in both raw and hardened columns.
6. `run_manifest.json` records input/output paths and metrics but does not aggregate the ReleaseProof id, core commit, exporter version, or input content digest.
7. `assistant_output` is always emitted with assistant `weight: 1`. A concise summary placed there becomes training data.
8. `training_recommendations.json` contains local heuristics derived mainly from example count. It is not a provider-validated launch configuration and must not be applied automatically.

Therefore schema v1 is acceptable for mock development and for a tightly controlled sealed/fully-labelled compatibility export. It is not sufficient for unclassified branch corpora or final real-data claims without the gates below.

---

## 5. Future source contract: sealed artifacts, not invented rows

The SFT extension must consume public immutable artifacts after their owning plans complete:

| Owner | Required source |
|---|---|
| Plan 003 | Sealed Witness manifest, source BranchRun/action references, v1 reward/verifier result, QA classification, exploit target/mechanism/cluster, content digest, replay evidence. |
| Plan 004 | Sealed control manifest, `solution_ref`, path label, v1 baseline runs, environment/task identities, content digest. |
| Plan 005 | Sealed ProofSet membership and ReleaseProof with per-case v1/v2 outcomes, evaluator/environment identities, patch provenance, gate status, content digest. |

Plan 007 owns the integration adapter under `src/forkproof/research/**`. It reads those public records and must not import Plans 003–005 internals or ask those plans to mutate their artifacts. Plan 007 execution is not currently authorized because its Plan 003 dependency has not completed. Preparatory implementation already present under this path is not Plan 007 completion evidence and requires an explicit ownership exception or accepted plan update before further source work.

A core-owned exporter is optional. If one exists, Plan 007 still verifies its manifest and content digests. A hand-assembled file cannot support measured claims because it bypasses reproducible joins and integrity checks.

### Required join invariants

For every normalized row:

- one stable normalized record id maps to explicit source artifact ids;
- the same solution/action artifact is evaluated under v1 and v2;
- v1 and v2 environment and complete evaluator identities are pinned;
- hack/legitimate classification has an authoritative evidence reference;
- Witness rows are members of the sealed ProofSet;
- control rows are members of the sealed ProofSet;
- ReleaseProof gate status and content digest verify;
- source and normalized artifact content digests are recorded;
- unknown or conflicting classifications are quarantined, never coerced to `false`;
- no mutable dashboard URL substitutes for an immutable id or artifact.

STOP if any join uses a detached grader copy, mismatched solution content, mixed ReleaseProofs, missing classification provenance, or unverifiable source artifact.

---

## 6. Proposed normalized dataset v2 target

This section is a proposed integration contract, not an accepted repository interface. Its fields are not yet normative in Plan 007, a checked-in schema, or an applicable specification. Before implementation, incorporate the accepted form into the owning ExecPlan and schema/specification, then validate it against the sealed source artifacts.

The future adapter should preserve richer semantics before projecting safe rows into the current `TraceRecord` shape.

| Field | Requirement |
|---|---|
| `record_id` | Stable normalized id distinct from HUD/Witness/control ids. |
| `record_kind` | `witness`, `control`, `source_trace`, or `branch_run`. |
| `task_id`, `task_prompt` | Stable task identity and public instruction. |
| `v1_reward_raw`, `v1_status` | Raw output plus normalized semantic success/failure. |
| `v2_reward_raw`, `v2_status` | Raw output plus normalized semantic success/failure. |
| `classification` | `hack`, `legitimate`, `unknown`, or `conflicting`. |
| `classification_ref` | Sealed Witness/control/QA/human-review evidence. |
| `demonstration_kind` | `faithful_final`, `faithful_trajectory`, `solution_artifact`, `summary`, or `none`. |
| `demonstration_ref` | Immutable source for the trainable response/trajectory. |
| `environment_v1`, `environment_v2` | Authoritative environment versions. |
| `evaluator_v1_ref`, `evaluator_v2_ref` | Complete evaluator identities, not only one test-file hash. |
| `witness_id`, `control_id`, `proof_set_id`, `release_proof_id` | Applicable proof identities. |
| `hud_trace_id`, `action_record_ref`, `solution_ref` | Applicable source evidence. |
| `exploit_target`, `exploit_mechanism`, `cluster_id` | Applicable dedup evidence. |
| `source_content_digest`, `normalized_content_digest` | Integrity. |

The compatibility projection into schema v1 is allowed only for rows with:

- normalized v1/v2 success/failure available as `0.0/1.0`,
- classification exactly one of `hack` or `legitimate`; the v1 booleans must be exclusive (`is_hack XOR is_legit`),
- no conflicting evidence,
- all required proof joins verified.

Unknown rows remain in a quarantine/audit artifact outside current `TraceRecord` until the implementation supports tri-state classification.

---

## 7. Analysis rows versus training demonstrations

An artifact can be valid for contamination analysis but invalid for SFT.

| Content | Analysis eligible | Training eligible |
|---|---:|---:|
| Sealed Witness with proof outcomes and only an action summary | yes | no |
| Sealed control with verified solution artifact but no faithful assistant response | yes | only after an explicit, reproducible conversion policy |
| Original faithful final assistant response | yes | potentially yes |
| Faithful tool/action trajectory represented in the target model's supported chat/tool schema | yes | potentially yes |
| Human-written concise summary | yes | no |
| Unknown/conflicting label | quarantined | no |

Do not put a summary into `assistant_output` and call the resulting file training-ready. The current exporter assigns that string weight 1.

The future clean SFT set is:

```text
v2 semantic success
AND authoritative legitimate classification
AND faithful supported demonstration
AND no unresolved provenance/review warning
```

It is narrower than the v2 verifier-positive admission set.

---

## 8. Metric contract

Freeze one common source population before comparing verifiers.

```text
v1_admission = rows with semantic success under evaluator v1
v2_admission = the same rows with semantic success under evaluator v2
classified_v1 = exclusively hack-or-legitimate rows in v1_admission
classified_v2 = exclusively hack-or-legitimate rows in v2_admission

v1_classified_contamination = hacks in classified_v1 / size(classified_v1)
v2_classified_contamination = hacks in classified_v2 / size(classified_v2)
legitimate_retention = legitimate rows in v2_admission / legitimate rows in v1_admission
```

Always report classification coverage (`size(classified) / size(admission)`) plus unknown, conflicting, and quarantined counts next to these denominators. If total-admission contamination bounds are useful, label them separately and state how unknown rows are treated. Also report `clean_sft_count` separately. Never divide a hack count from all v2 positives by the count of legitimate-only clean SFT rows.

Targets for a passing ReleaseProof population are:

- every sealed Witness: v1 success, v2 failure;
- every sealed control: v1 success, v2 success;
- zero sealed Witnesses in `v2_admission`;
- all required controls retained.

These are release-gate facts. Broader contamination rates depend on the declared source population and must not be generalized beyond it.

---

## 9. Ownership and handoff

### Core owners

- Plan 003 seals Witnesses and their replay/classification evidence.
- Plan 004 seals legitimate controls and baseline evidence.
- Plan 005 seals ProofSet membership and v1/v2 ReleaseProof outcomes.
- Plan 006 may consume measured reports for the demo but does not own training-data truth.

### Plan 007 / SFT owner

- validates source manifests and digests;
- implements the public-artifact adapter;
- writes normalized/quarantine/provenance artifacts;
- computes same-population metrics;
- exports SFT JSONL only from faithful clean demonstrations;
- records evidence under Plan 007 paths;
- does not modify core proof artifacts.

`CONNECT.md` is currently an untracked root document and is not listed in an ExecPlan ownership declaration. Under project governance it is therefore advisory, not a source of truth. Before merge, move it into a plan-owned documentation path or update an applicable plan's declared ownership and check it in through that plan.

Canonical future paths:

```text
artifacts/forkproof/research/sft/input_manifest.json
artifacts/forkproof/research/sft/normalized.jsonl
artifacts/forkproof/research/sft/quarantine.jsonl
artifacts/forkproof/research/sft/real_run/
```

The current CLI accepts any output directory, so existing `artifacts/sft/mock_run/` remains a labelled development artifact. New Plan 007 evidence should use the owned `artifacts/forkproof/research/**` boundary.

---

## 10. Current commands

### Verified mock tests

```bash
uv run pytest tests/forkproof/research/sft/ -q
```

Observed 2026-06-21: `49 passed`. In restricted sandboxes, set a writable cache such as `UV_CACHE_DIR=/private/tmp/h2f-uv-cache`; ordinary developer environments need not.

### Verified mock pipeline

```bash
uv run python -m forkproof.research.sft.cli \
  --input fixtures/sft/mock_forkproof_traces.jsonl \
  --output artifacts/sft/mock_run/
```

Fresh current-code outputs include reports, raw/hardened SFT JSONL, metadata sidecars, rejected-hack audit, run manifest, and `training_recommendations.json`.

The checked-in `artifacts/sft/mock_run/` fixture predates the current recommendation output and does not contain `training_recommendations.json`. Treat it as stale illustrative output until it is regenerated and reviewed; do not use the committed directory to prove current output completeness.

### Future real run

Do not run this as measured evidence until the adapter, metric, quarantine, and provenance gates are implemented:

```bash
uv run python -m forkproof.research.sft.cli \
  --input artifacts/forkproof/research/sft/normalized.compat-v1.jsonl \
  --output artifacts/forkproof/research/sft/real_run/
```

Before Plan 007 completion, `plan-007-tests` and `integration-research` in `docs/plans/repo-map/COMMANDS.json` must contain verified argv. They are currently `not-applicable`; a mapped SKIP is not evidence.

---

## 11. Real-integration acceptance

Integration is complete only when:

1. Plans 003, 004, and 005 source manifests required by the join are complete and content-verified.
2. Input manifest pins core commit, source artifact ids/digests, adapter version/commit, ProofSet, ReleaseProof, and v1/v2 evaluator identities.
3. Every sealed ProofSet Witness appears exactly once and is rejected by v2.
4. Every required sealed control appears exactly once and succeeds under both versions.
5. Every normalized row points to the same artifact content under both evaluations.
6. Unknown/conflicting rows are quarantined and excluded from training.
7. Metric numerators and denominators use the declared common population.
8. The clean SFT export contains only faithful legitimate demonstrations.
9. Fireworks-format validation passes and the training file has at least three faithful examples before upload. The presence of three Plan 004 controls alone does not prove this requirement because a control `solution_ref` is not automatically a supported assistant demonstration.
10. `plan-007-tests`, `integration-research`, lint, build, file-size, and evidence gates execute rather than skip.

Warnings involving identity, classification, evaluator mismatch, content mismatch, or demonstration fidelity are STOP conditions for training. They may be reported as analysis limitations but cannot be silently dropped.

---

## 12. Fireworks managed SFT boundary

Managed SFT is the optional downstream path here. It is distinct from:

- Fireworks managed RFT jobs; and
- the private-preview Fireworks Training API custom loop described in `HUDDOC.MD`.

Current official managed-SFT requirements include OpenAI-compatible chat JSONL, at least three examples, `system`/`user`/`assistant` roles, and optional assistant-message `weight` values of `0` or `1`. The current exporter emits assistant `weight: 1`, which is supported.

Before upload:

1. Confirm the base model is tunable and the intended training shape supports the desired tuning mode.
2. Validate chat template/tokenization using the current Fireworks SFT tooling or UI.
3. Freeze train/held-out splits by task/entity/template family, not random near-duplicates.
4. Confirm no hidden evaluator answers, exploit summaries, unknown labels, or secrets are in the clean file.
5. Run a CLI dry-run or review the UI request before spending credits.

Current CLI shape:

```bash
firectl dataset create forkproof-hardened-demo \
  artifacts/forkproof/research/sft/real_run/hardened_verifier_sft.jsonl

firectl supervised-fine-tuning-job create \
  --base-model <SUPPORTED_BASE_MODEL_ID> \
  --dataset forkproof-hardened-demo \
  --output-model forkproof-hardened-demo-v1 \
  --dry-run
```

Remove `--dry-run` only after validating the request, credentials, quota, dataset, held-out evaluation, and cost.

`training_recommendations.json` is advisory and must not be consumed automatically as a launch configuration. Its rank, batch, epoch, and learning-rate values are not justified solely by example count and are not guaranteed to match a Fireworks training shape. Use provider-supported parameters and measured sweeps/calibration instead. The Thinking Machines “LoRA Without Regret” results support testing all-layer LoRA and larger LoRA learning rates in comparable regimes; they do not justify the current file's exact count-to-rank thresholds as universal settings.

Official references:

- [Fireworks managed SFT guide](https://docs.fireworks.ai/fine-tuning/fine-tuning-models)
- [Fireworks managed fine-tuning overview](https://docs.fireworks.ai/fine-tuning/managed-finetuning-intro)
- [Fireworks SFT CLI reference](https://docs.fireworks.ai/tools-sdks/firectl/commands/supervised-fine-tuning-job-create)
- [Fireworks Training API introduction](https://docs.fireworks.ai/fine-tuning/training-api/introduction)
- [LoRA Without Regret](https://thinkingmachines.ai/blog/lora/)

---

## 13. Current blockers and next implementation steps

| Priority | Blocker | Required action |
|---|---|---|
| P0 | Plan 003 has candidates but no sealed Witness | Minimize causal deltas, package durable candidates, run target/mechanism deduplication, and pass three deterministic replays before sealing public artifacts. |
| P0 | Plan 005 ReleaseProof absent | After Plan 003 seals a Witness, complete v1/v2 proof and evaluator identities. |
| P0 | Plan 005 command/repository maps are inconsistent | Verify `plan-005-tests` and `integration-release` mappings and reconcile repo-map status before Plan 005 execution. |
| P0 | Current metric populations mismatch | Separate v2 admission from clean SFT and compute denominators from the same population. |
| P0 | No tri-state quarantine | Add normalized classification and quarantine before accepting broader real exports. |
| P0 | Plan 007 dependency and ownership gate closed | Do not execute Plan 007 source work until Plan 003 completes and all target paths, including this document, have accepted ownership. |
| P0 | No sealed-artifact adapter | After the gate opens, implement the Plan 007 adapter over public manifests. |
| P0 | Demonstration fidelity unspecified | Add faithful-vs-summary classification and block summaries from SFT. |
| P1 | Provenance not aggregated | Emit input/normalization manifests with content digests and core/adapter commits. |
| P1 | Plan 007 mapped commands skip | Bind real test/integration argv before execution. |
| P1 | Checked-in mock artifact stale | Regenerate and review it, or explicitly retain it as a version-labelled historical fixture. |
| P1 | Training recommendations over-specific | Convert to clearly labelled hypotheses or provider-validated configuration; never feed the current file directly into job launch. |
| P2 | Optional Fireworks job | Run only after all analysis/training gates and held-out split exist. |

If the real proof artifacts do not arrive before the demo, retain mock outputs as **illustrative** and record the integration as blocked. Never relabel mock metrics, manual rows, or unverified summaries as measured ForkProof results.
