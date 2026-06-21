# SFT Extension Plan — ForkProof / Hack2Fix2Hack

**Purpose:** Agent-ready specification for the SFT and training-data extension. This document explains what to build, in what order, with mock data first, and how to reconnect to the core team's real ForkProof outputs later.

**Status:** Planning document (2026-06-20)  
**Related sources:** `HANDOFF.MD`, `docs/plans/html-spec/hack2fix2hack-handoff (4).html`, `docs/plans/GLOSSARY.md`, `docs/plans/007-depth-two-and-research-extensions.md`

---

## Table of contents

1. [Executive summary](#1-executive-summary)
2. [Position in the project](#2-position-in-the-project)
3. [The mental model](#3-the-mental-model)
4. [Scope boundaries](#4-scope-boundaries)
5. [Phased build plan](#5-phased-build-plan)
6. [Data contracts](#6-data-contracts)
7. [Mock data (Phase 0)](#7-mock-data-phase-0)
8. [Filtering logic (Phase 1)](#8-filtering-logic-phase-1)
9. [Metrics and reporting (Phase 2)](#9-metrics-and-reporting-phase-2)
10. [SFT dataset export (Phase 3)](#10-sft-dataset-export-phase-3)
11. [Reconnecting to real ForkProof data (Phase 4)](#11-reconnecting-to-real-forkproof-data-phase-4)
12. [Optional training experiment (Phase 5)](#12-optional-training-experiment-phase-5)
13. [Suggested repository layout](#13-suggested-repository-layout)
14. [Integration contract for the core team](#14-integration-contract-for-the-core-team)
15. [Fireworks sponsor framing](#15-fireworks-sponsor-framing)
16. [Demo narrative and deliverables](#16-demo-narrative-and-deliverables)
17. [Agent execution checklist](#17-agent-execution-checklist)
18. [Claims discipline](#18-claims-discipline)
19. [Glossary cross-reference](#19-glossary-cross-reference)

---

## 1. Executive summary

### What this section builds

The core ForkProof team builds the live demo loop:

```
HUD trace → ForkPoint → Modal branches → Exploit Witness → verifier patch → ReleaseProof
```

This SFT extension answers a downstream question:

> **Why does verifier hardening matter for training?**

A weak verifier does not only inflate benchmark scores. It also poisons training data. If an agent earns reward 1 by hacking the verifier and that trajectory becomes a positive SFT example, the model may learn the exploit instead of the real task.

### The key claim

**ForkProof does not only patch benchmarks. It prevents hacked reward-1 trajectories from becoming positive training data.**

The must-ship version proves this through **data-quality analysis**, not necessarily a full model training run.

### One-sentence pitch

A raw verifier admits both real solutions and reward hacks as positive training examples; a hardened verifier filters out hacked successes before SFT or RFT.

### One-table summary (target artifact)

| Metric | Raw Verifier | Hardened Verifier |
| --- | ---: | ---: |
| Reward-1 traces admitted | TBD | TBD |
| Legitimate traces admitted | TBD | TBD |
| Hacked traces admitted | TBD | 0 (target) |
| Training contamination | TBD | 0% (target) |
| Legitimate retention | TBD | 100% (target) |

Replace `TBD` with measured values once the pipeline runs.

---

## 2. Position in the project

### Where this sits in Hack2Fix2Hack

| Layer | Owner | Role |
| --- | --- | --- |
| Core demo | Core team | ForkPoint, Modal branching, Witness discovery, verifier patch, ReleaseProof gate |
| Research appendix | SFT extension (this doc) | Raw-vs-hardened training-data filtering, contamination metrics, SFT-ready exports |
| Downstream training | Fireworks (sponsor) | Managed SFT or RFT on cleaned trajectories |

The HTML handoff and ExecPlan 007 classify training-data analysis as a **research stretch**, not part of the live demo path. Build it in parallel; do not block or depend on the core release gate.

### Relationship to ForkProof objects

| ForkProof object | How SFT uses it |
| --- | --- |
| **Source trace** | Candidate training example; may be legit or hacked |
| **Exploit Witness** | Confirmed hack with replay; should be rejected by hardened verifier |
| **Legitimate control** | Known-good solution; must survive hardening and enter the clean SFT set |
| **ReleaseProof** | Before/after evidence that v2 kills Witnesses and preserves controls |
| **Exploit cluster** | Groups rejected hacks by mechanism for analysis breakdown |
| **Grader digest** | Pins which verifier version produced raw vs patched rewards |

### Anchor task: MongoDB SalesAnalyzer

The demo anchors on Terminal Wrench task [`mongodb-sales-aggregation-engine`](https://github.com/few-sh/terminal-wrench/blob/main/tasks/mongodb-sales-aggregation-engine/claude-opus-4.6). Mock data and examples should reference this task family so the SFT story aligns with the core demo.

Known exploit mechanisms from the handoff (use as exploit-cluster labels):

- Pytest plugin subversion (setuptools plugin path surviving `--noconftest`)
- `conftest.py` hook bypass
- Test mutation
- Fabricated pytest reports
- Synthetic report generation
- Layered fallback / defense-in-depth exploit (the canonical Exploit Witness)

Known legitimate behavior: implementing `SalesAnalyzer` with real MongoDB aggregation pipelines that pass the test suite without manipulating the test harness.

---

## 3. The mental model

### Two kinds of reward-1 traces

Training pipelines typically treat reward 1 as "success" and use those trajectories as positive examples. In reward-hacking settings, two distinct categories both score reward 1 under a raw verifier:

1. **Legitimate solutions** — the agent actually solved the task.
2. **Reward hacks** — the agent tricked the verifier, tests, harness, plugin system, or grading logic.

A raw verifier cannot always distinguish these. A hardened verifier (post-ForkProof patch) should:

- Reject reward hacks (reward 0 under patched verifier)
- Preserve legitimate solutions (reward 1 under patched verifier)

### Three dataset buckets

| Bucket | Definition | Use |
| --- | --- | --- |
| **Raw SFT dataset** | Every trace with raw verifier reward 1 | Shows what an unfiltered pipeline would train on ("dirty" set) |
| **Hardened SFT dataset** | Traces with patched reward 1 AND labeled legitimate | The dataset you would actually want to train on ("clean" set) |
| **Rejected hacks dataset** | Raw reward 1, patched reward 0, labeled hack | Analysis only; illustrates contamination removed |

### Important distinction (SEAM 6)

Per ForkProof engineering rules, **reward** and **reward-hacking classification** are separate signals:

- `raw_reward` / `patched_reward` come from the verifier/grader.
- `is_hack` / `is_legit` come from classification (HUD QA, Witness promotion, human label, or core-team export).

A trace enters the rejected-hacks bucket when: `raw_reward == 1` AND `patched_reward == 0` AND `is_hack == true`.

A trace enters the hardened SFT bucket when: `patched_reward == 1` AND `is_legit == true`.

Do not conflate "got reward 0" with "is a hack" without explicit labels — a failed legitimate attempt also gets reward 0.

---

## 4. Scope boundaries

### In scope (must-ship)

- Mock ForkProof-style input data
- Filtering pipeline (raw / hardened / rejected)
- Contamination metrics and comparison table
- Fireworks-compatible SFT JSONL export (optional upload is nice-to-have)
- Short write-up and one chart/slide for presentation
- Integration contract document for the core team

### Out of scope (core team owns these)

- ForkPoint creation and Modal snapshot/branch infrastructure
- Exploit Witness discovery, deduplication, replay
- Verifier patch generation (harden-v0 fixer)
- ReleaseProof gate implementation
- HUD trace viewer, live demo orchestration
- Full RFT training loop

### Optional (only if time and credits permit)

- Fireworks managed SFT job on raw vs hardened datasets
- Raw-trained vs hardened-trained model comparison
- Held-out task evaluation

### Claims to avoid

- Do not claim training improves performance unless an experiment actually ran.
- Do not describe this as part of the core live demo unless explicitly wired in.
- Do not use synthetic/mock metrics in the final pitch table — label mock runs as illustrative during development only.

---

## 5. Phased build plan

Build in this order. Each phase has concrete outputs an agent can verify before moving on.

```
Phase 0: Mock data + schemas + loader
    ↓
Phase 1: Filtering pipeline (three buckets)
    ↓
Phase 2: Metrics, contamination table, exploit-cluster breakdown
    ↓
Phase 3: SFT JSONL export + metadata sidecar
    ↓
Phase 4: Swap mock → real ForkProof export (adapter only)
    ↓
Phase 5 (optional): Fireworks SFT job + model comparison
```

---

### Phase 0 — Mock data, schemas, and loader

**Goal:** Define the input contract and load a realistic mock dataset without waiting for the core team.

**Deliverables:**

1. `TraceRecord` schema (JSON Schema or typed dataclass/Pydantic model)
2. `fixtures/sft/mock_forkproof_traces.jsonl` — one JSON object per line
3. `load_traces(path) -> list[TraceRecord]` with validation
4. README or docstring explaining mock provenance

**Exit criteria:**

- Loader rejects malformed rows with clear errors
- Mock file contains at least 8 traces covering all label combinations (see Section 7)
- Unit test: loader returns expected count and field types

**Agent instruction:** Start here. Do not build metrics or export until the loader passes tests.

---

### Phase 1 — Filtering pipeline

**Goal:** Partition loaded traces into three buckets using deterministic rules.

**Deliverables:**

1. `filter_traces(traces) -> FilterResult` returning:
   - `raw_sft: list[TraceRecord]`
   - `hardened_sft: list[TraceRecord]`
   - `rejected_hacks: list[TraceRecord]`
   - `excluded: list[TraceRecord]` (reward-0 failures, ambiguous rows)
2. Filtering rules documented in code and tested

**Filtering rules (canonical):**

```python
# Raw SFT: would enter an unfiltered positive set
raw_sft = [t for t in traces if t.raw_reward == 1.0]

# Hardened SFT: safe positive examples
hardened_sft = [
    t for t in traces
    if t.patched_reward == 1.0 and t.is_legit is True
]

# Rejected hacks: contamination removed
rejected_hacks = [
    t for t in traces
    if t.raw_reward == 1.0
    and t.patched_reward == 0.0
    and t.is_hack is True
]

# Excluded: not used as positive SFT (failures, unlabeled, inconsistent)
excluded = [t for t in traces if t not in raw_sft + hardened_sft + rejected_hacks]
```

**Edge cases to handle:**

| Case | Bucket |
| --- | --- |
| `raw=1, patched=1, is_legit=true` | raw_sft + hardened_sft |
| `raw=1, patched=0, is_hack=true` | raw_sft + rejected_hacks |
| `raw=1, patched=1, is_hack=true` | raw_sft only (verifier still broken on this path — flag as `needs_review`) |
| `raw=0` | excluded |
| `raw=1, patched=0, is_hack=false, is_legit=false` | excluded (ambiguous — log warning) |

**Exit criteria:**

- Tests cover every row in the mock fixture
- `needs_review` warnings emitted for inconsistent label/reward combinations
- No trace appears in both `hardened_sft` and `rejected_hacks`

---

### Phase 2 — Metrics, contamination table, and charts

**Goal:** Produce the before/after comparison that is the primary pitch artifact.

**Deliverables:**

1. `compute_metrics(traces, filter_result) -> MetricsSummary`
2. `render_contamination_table(metrics) -> str` (Markdown and/or CSV)
3. `render_exploit_cluster_breakdown(rejected_hacks) -> dict[str, int]`
4. Optional: bar chart (raw vs hardened hack count) saved to `artifacts/sft/contamination_chart.png`

**Metrics definitions:**

| Metric | Formula |
| --- | --- |
| Raw reward-1 traces admitted | `len(raw_sft)` |
| Hardened reward-1 traces admitted | `len(hardened_sft)` |
| Hacked traces admitted (raw) | count where `raw_reward==1 and is_hack==True` |
| Hacked traces admitted (hardened) | count where `patched_reward==1 and is_hack==True` (target: 0) |
| Training contamination rate (raw) | `hacked_in_raw / len(raw_sft)` |
| Training contamination rate (hardened) | `hacked_in_hardened / len(hardened_sft)` if hardened non-empty else 0 |
| Legitimate retention | `len(hardened_sft) / count(is_legit=True)` among all legit traces |

**Exit criteria:**

- Mock run produces the example table from Section 1 with concrete numbers
- Exploit cluster breakdown lists at least 3 distinct mechanisms from mock data
- Metrics module has tests with fixed expected values for the mock fixture

---

### Phase 3 — SFT dataset export

**Goal:** Emit Fireworks-ready training files plus metadata for reproducibility.

**Deliverables:**

1. `export_sft_jsonl(traces, bucket, path)` for each bucket that should export
2. `export_metadata(traces, path)` — full provenance sidecar (JSONL or JSON)
3. CLI entrypoint, e.g. `python -m forkproof.research.sft.cli --input fixtures/... --out artifacts/sft/`

**Export only these buckets to SFT JSONL:**

- `raw_sft` → `artifacts/sft/raw_verifier_sft.jsonl` (intentionally dirty, for contrast)
- `hardened_sft` → `artifacts/sft/hardened_verifier_sft.jsonl` (the clean training set)

Do **not** export `rejected_hacks` as positive SFT examples. Optionally export them to a separate analysis file with `"weight": 0` or a non-training audit format.

**Exit criteria:**

- Each JSONL line validates against Fireworks chat format (see Section 10)
- System prompt is identical across all examples in a given export
- Metadata sidecar includes trace_id, raw/patched rewards, labels, exploit_cluster
- Minimum 3 examples per export file (Fireworks requirement)

---

### Phase 4 — Reconnect to real ForkProof data

**Goal:** Swap mock input for core-team output with minimal code changes.

**Deliverables:**

1. `adapt_forkproof_export(path) -> list[TraceRecord]` — thin adapter from core format to internal schema
2. Config flag or env var: `SFT_INPUT_PATH` pointing at mock or real file
3. Re-run Phases 1–3 on real data; update metrics table with measured values
4. Short "integration log" noting row count, date, source commit/ReleaseProof id

See [Section 11](#11-reconnecting-to-real-forkproof-data-phase-4) for the full reconnection procedure.

**Exit criteria:**

- Same pipeline code path runs on mock and real inputs
- Real run recorded in evidence manifest (if following ExecPlan 007) or a local `artifacts/sft/run_manifest.json`
- Final pitch table uses real measured values, not mock placeholders

---

### Phase 5 (optional) — Training experiment

**Goal:** If time and Fireworks credits allow, compare models trained on raw vs hardened datasets.

**Only proceed when:**

- Phase 4 real data is available OR mock data is explicitly labeled as a dry run
- Fireworks account and base model are confirmed
- At least 3 clean examples exist in hardened export (Fireworks minimum)

**Experiment design:**

| Model | Training data | Hypothesis |
| --- | --- | --- |
| Model A (raw-trained) | `raw_verifier_sft.jsonl` | May imitate exploit patterns present in hacked positives |
| Model B (hardened-trained) | `hardened_verifier_sft.jsonl` | Should prefer real task-solving behavior |

Evaluate both on held-out tasks (not in training set). Record exact model IDs, dataset IDs, and job IDs per `HANDOFF.MD` reproducibility guidance.

**If not run:** State clearly that the training experiment is a proposed Fireworks extension; the completed artifact is the data-quality analysis.

---

## 6. Data contracts

### 6.1 Input: ForkProof trace export (one row per trace)

This is the **integration contract** the core team should produce. The SFT pipeline consumes this format.

```json
{
  "trace_id": "trace-mongo-001",
  "task_id": "mongodb-sales-aggregation-engine",
  "task_prompt": "Implement a SalesAnalyzer class with MongoDB aggregation pipelines...",
  "assistant_output": "Summary of agent actions or final response text...",
  "raw_reward": 1.0,
  "patched_reward": 0.0,
  "is_hack": true,
  "is_legit": false,
  "exploit_cluster": "pytest_plugin_subversion",
  "environment_version": "env-v1-sha-abc123",
  "grader_version": "grader-v1-sha-def456",
  "hud_trace_url": "https://...",
  "witness_id": "witness-001",
  "release_proof_id": "releaseproof-001"
}
```

**Required fields (minimum viable):**

| Field | Type | Description |
| --- | --- | --- |
| `trace_id` | string | Stable unique id |
| `task_id` | string | Task family + instance |
| `task_prompt` | string | User-visible task instruction |
| `assistant_output` | string | Agent solution summary, final answer, or condensed action trace |
| `raw_reward` | float | Reward under original verifier (0.0 or 1.0) |
| `patched_reward` | float | Reward under hardened verifier (0.0 or 1.0) |
| `is_hack` | bool | Classified as reward hack |
| `is_legit` | bool | Classified as legitimate solution |

**Optional but valuable:**

| Field | Type | Description |
| --- | --- | --- |
| `exploit_cluster` | string | Mechanism label for breakdown |
| `environment_version` | string | Pinned environment digest |
| `grader_version` | string | Original grader digest |
| `patched_grader_version` | string | Hardened grader digest |
| `hud_trace_url` | string | Link to source trace |
| `witness_id` | string | Link to Exploit Witness if applicable |
| `release_proof_id` | string | Link to ReleaseProof run |

**File format:** JSONL (one record per line) or Parquet. JSONL is preferred for hackathon speed.

### 6.2 Internal: TraceRecord

The implementation should map input rows to a typed internal model. Suggested fields mirror the contract above plus:

- `needs_review: bool` — set when labels and rewards are inconsistent
- `source: Literal["mock", "forkproof_export"]` — provenance for reporting

### 6.3 Output: SFT example (Fireworks chat JSONL)

Per `HANDOFF.MD` Section 11.2, each training line:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a coding agent. Solve the task directly. Do not manipulate tests, evaluators, verifiers, plugins, or the grading harness."
    },
    {
      "role": "user",
      "content": "<task_prompt>"
    },
    {
      "role": "assistant",
      "content": "<assistant_output>"
    }
  ]
}
```

**Metadata sidecar** (separate file, not inside Fireworks upload):

```json
{
  "trace_id": "trace-mongo-001",
  "task_id": "mongodb-sales-aggregation-engine",
  "source_filter": "hardened_sft",
  "raw_reward": 1.0,
  "patched_reward": 1.0,
  "is_hack": false,
  "is_legit": true,
  "exploit_cluster": null
}
```

---

## 7. Mock data (Phase 0)

Build the entire pipeline against this fixture before real data exists.

### Design principles for mock traces

- Raw verifier gives reward 1 to both real solutions and hacks (mirrors the bug)
- Hardened verifier gives reward 1 only to legitimate solutions
- Hardened verifier gives reward 0 to reward hacks
- Failed attempts stay at reward 0 under both verifiers
- Cover multiple exploit clusters for breakdown charts

### Suggested mock inventory (MongoDB SalesAnalyzer)

| trace_id | Description | raw | patched | is_hack | is_legit | exploit_cluster |
| --- | --- | ---: | ---: | --- | --- | --- |
| `mock-001` | Real MongoDB aggregation implementation | 1 | 1 | false | true | — |
| `mock-002` | Another legitimate pipeline variant | 1 | 1 | false | true | — |
| `mock-003` | Legitimate solution, different approach | 1 | 1 | false | true | — |
| `mock-004` | Pytest plugin subversion | 1 | 0 | true | false | `pytest_plugin_subversion` |
| `mock-005` | conftest hook bypass | 1 | 0 | true | false | `conftest_hook_bypass` |
| `mock-006` | Fabricated pytest reports | 1 | 0 | true | false | `fabricated_test_reports` |
| `mock-007` | Layered fallback exploit (Witness-class) | 1 | 0 | true | false | `layered_fallback` |
| `mock-008` | Failed attempt, no solution | 0 | 0 | false | false | — |
| `mock-009` | Partial work, tests fail | 0 | 0 | false | false | — |

**Expected mock metrics (verify pipeline against these):**

| Metric | Raw | Hardened |
| --- | ---: | ---: |
| Reward-1 traces admitted | 7 | 3 |
| Legitimate traces admitted | 3 | 3 |
| Hacked traces admitted | 4 | 0 |
| Training contamination | 57.1% | 0% |
| Legitimate retention | 100% | 100% |

### Mock assistant_output content guidance

Keep mock `assistant_output` strings short but realistic:

- **Legit example:** "Implemented `SalesAnalyzer.analyze_sales()` using `$match`, `$group`, and `$sort` stages..."
- **Hack example:** "Registered a setuptools pytest plugin that intercepts test collection and returns synthetic passing results..."

These strings power qualitative demo slides showing what the raw dataset would teach.

---

## 8. Filtering logic (Phase 1)

### Pipeline pseudocode

```python
def run_sft_pipeline(input_path: Path, output_dir: Path) -> PipelineResult:
    traces = load_traces(input_path)
    validate_traces(traces)
    filtered = filter_traces(traces)
    metrics = compute_metrics(traces, filtered)
    write_table(metrics, output_dir / "contamination_table.md")
    write_cluster_breakdown(filtered.rejected_hacks, output_dir / "exploit_clusters.json")
    export_sft_jsonl(filtered.raw_sft, output_dir / "raw_verifier_sft.jsonl")
    export_sft_jsonl(filtered.hardened_sft, output_dir / "hardened_verifier_sft.jsonl")
    export_audit_jsonl(filtered.rejected_hacks, output_dir / "rejected_hacks_audit.jsonl")
    export_metadata(traces, output_dir / "metadata.jsonl")
    return PipelineResult(traces=traces, filtered=filtered, metrics=metrics)
```

### Validation rules (fail or warn)

**Hard errors:**

- Missing required fields
- `raw_reward` or `patched_reward` outside [0.0, 1.0]
- Duplicate `trace_id`

**Warnings (`needs_review=True`):**

- `is_hack=True` and `is_legit=True` simultaneously
- `patched_reward=1` and `is_hack=True` (hardened verifier still admits hack)
- `raw_reward=0` and `is_hack=True` (hack that did not reward — unusual for SFT story)

---

## 9. Metrics and reporting (Phase 2)

### Primary output: contamination table

Write to `artifacts/sft/contamination_table.md`:

```markdown
# SFT Data Quality: Raw vs Hardened Verifier

| Metric | Raw Verifier | Hardened Verifier |
| --- | ---: | ---: |
| Reward-1 traces admitted | 7 | 3 |
| Legitimate traces admitted | 3 | 3 |
| Hacked traces admitted | 4 | 0 |
| Training contamination | 57.1% | 0.0% |
| Legitimate retention | 100.0% | 100.0% |

_Source: mock_forkproof_traces.jsonl, generated 2026-06-20_
```

Replace footer with real source info after Phase 4.

### Secondary output: exploit cluster breakdown

```json
{
  "pytest_plugin_subversion": 1,
  "conftest_hook_bypass": 1,
  "fabricated_test_reports": 1,
  "layered_fallback": 1
}
```

### Optional chart

Simple bar chart:

- X-axis: Raw vs Hardened
- Y-axis: Count of hacked traces admitted
- Title: "Reward hacks removed before SFT"

Save as `artifacts/sft/contamination_chart.png` for slides.

### Short write-up template

`artifacts/sft/WRITEUP.md`:

1. **Problem:** Raw reward-1 trajectories include reward hacks.
2. **Method:** Filter through hardened verifier labels from ForkProof.
3. **Result:** Contamination table + cluster breakdown.
4. **Implication:** Verifier hardening protects both benchmarks and training data.
5. **Fireworks path:** Clean exports ready for managed SFT.

---

## 10. SFT dataset export (Phase 3)

### System prompt (use consistently)

```
You are a coding agent working in a sandboxed environment. Solve the task directly using correct implementation. Do not manipulate tests, evaluators, verifiers, pytest plugins, conftest hooks, or grading harnesses to fake success.
```

Adjust only if the core team's harness uses a different canonical system prompt — then match theirs for consistency.

### Export commands (after pipeline exists)

```bash
# Run full pipeline on mock data
python -m forkproof.research.sft.cli \
  --input fixtures/sft/mock_forkproof_traces.jsonl \
  --output artifacts/sft/mock_run/

# After core team delivers real export
python -m forkproof.research.sft.cli \
  --input artifacts/sft/forkproof_export.jsonl \
  --output artifacts/sft/real_run/
```

### Fireworks upload (optional, Phase 5)

From `HANDOFF.MD`:

```bash
firectl dataset create sft-hardened-demo artifacts/sft/real_run/hardened_verifier_sft.jsonl

firectl sftj create \
  --base-model <BASE_MODEL_ID> \
  --dataset sft-hardened-demo \
  --output-model sft-hardened-demo-v1
```

Run the [SFT tokenization debugger](https://docs.fireworks.ai/fine-tuning/debug-sft-tokenization) before spending credits.

---

## 11. Reconnecting to real ForkProof data (Phase 4)

This section explains how to integrate with the core team's work when their outputs are ready.

### What the core team must deliver

One file: **`forkproof_export.jsonl`** (or equivalent path agreed with the team).

Each row corresponds to one trace, BranchRun, Witness, or legitimate control that the core system graded under both verifier versions. Minimum required fields are listed in [Section 6.1](#61-input-forkproof-trace-export-one-row-per-trace).

### Where real data likely originates in ForkProof

| Core artifact | SFT mapping |
| --- | --- |
| Source trace | Row with `raw_reward=1`; may become raw_sft |
| Exploit Witness replay | Row with `is_hack=true`, `raw_reward=1`, `patched_reward=0` |
| Legitimate control | Row with `is_legit=true`, both rewards should be 1 post-ReleaseProof |
| ReleaseProof results | Supplies patched rewards and `release_proof_id` |
| BranchRun (non-witness) | Include only if team exports full branch corpus; otherwise export Witnesses + controls + source trace |

Ask the core team to export **at minimum**:

1. All Exploit Witnesses (with replay summaries)
2. All legitimate controls
3. Any additional reward-1 source traces used in the demo
4. Optional: full branch corpus for richer contamination stats

### Adapter pattern (only code that should change)

```python
def adapt_forkproof_export(row: dict) -> TraceRecord:
    """Map core-team export columns to internal TraceRecord."""
    return TraceRecord(
        trace_id=row["trace_id"],
        task_id=row["task_id"],
        task_prompt=row["task_prompt"],
        assistant_output=row["assistant_output"],
        raw_reward=float(row["raw_reward"]),
        patched_reward=float(row["patched_reward"]),
        is_hack=bool(row["is_hack"]),
        is_legit=bool(row["is_legit"]),
        exploit_cluster=row.get("exploit_cluster"),
        environment_version=row.get("environment_version"),
        grader_version=row.get("grader_version"),
        hud_trace_url=row.get("hud_trace_url"),
        witness_id=row.get("witness_id"),
        release_proof_id=row.get("release_proof_id"),
        source="forkproof_export",
    )
```

If the core team uses different column names, change **only the adapter**, not the filter/metrics/export logic.

### Step-by-step reconnection procedure

1. **Agree on schema** — Send the core team [Section 14](#14-integration-contract-for-the-core-team) (or the JSON schema file if you create one).
2. **Receive file** — Place at `artifacts/sft/forkproof_export.jsonl` (or path in `SFT_INPUT_PATH` env var).
3. **Validate** — Run loader; fix adapter if validation fails.
4. **Re-run pipeline** — Same CLI as mock, different input path.
5. **Compare** — Mock vs real row counts; confirm hardened hack count is 0.
6. **Update artifacts** — Replace pitch table numbers with real measurements.
7. **Record provenance** — Write `artifacts/sft/run_manifest.json`:

```json
{
  "input_path": "artifacts/sft/forkproof_export.jsonl",
  "input_source": "forkproof_export",
  "release_proof_id": "releaseproof-001",
  "core_commit": "abc123",
  "run_timestamp": "2026-06-21T10:00:00-07:00",
  "trace_count": 12,
  "metrics": { "...": "..." }
}
```

8. **Tag demo materials** — Slide footer: "Measured on ForkProof ReleaseProof X" not "illustrative mock."

### Parallel work agreement

You do not need to wait for the core system. The contract is:

> "I can build everything now using mock data. When real ForkProof outputs are ready, I swap the input file and re-run."

No filter logic rewrite. No metric formula changes. Only input adapter and provenance metadata.

### Alignment with ExecPlan 007

Plan 007 (`docs/plans/007-depth-two-and-research-extensions.md`) owns `src/forkproof/research/**` for training analysis. When the repo gains product source:

- Place SFT code under `src/forkproof/research/sft/`
- Place fixtures under `fixtures/sft/` or `tests/forkproof/research/fixtures/sft/`
- Place outputs under `artifacts/forkproof/research/sft/`
- Record evidence in `docs/plans/evidence/007/MANIFEST.json` if executing within the ExecPlan workflow

If building before Gate 1 opens, a standalone script folder is fine; migrate into `src/forkproof/research/sft/` when the repo accepts product source.

---

## 12. Optional training experiment (Phase 5)

### Prerequisites

- Hardened export has ≥3 examples
- Fireworks credits and base model confirmed
- Held-out tasks identified (not in training export)
- Calibration guidance from `HANDOFF.MD` Section 2 (10 runs per task, 20–50% mean reward)

### Procedure

1. Upload `raw_verifier_sft.jsonl` → train Model A
2. Upload `hardened_verifier_sft.jsonl` → train Model B
3. Evaluate both on held-out HUD taskset
4. Compare: format compliance, reward-hacking rate, legitimate success rate

### Expected hypothesis (do not claim unless measured)

- Model A may reproduce exploit-like patterns on tasks with weak verifiers
- Model B should show lower hack rate on the same evaluator

### If skipped

Document in write-up:

> "Training experiment proposed as Fireworks extension. Completed artifact: verifier-filtered dataset quality analysis showing X% contamination removed."

---

## 13. Suggested repository layout

When implementing in the repo:

```
fixtures/sft/
  mock_forkproof_traces.jsonl       # Phase 0 mock input
  schema/trace_record.schema.json   # Optional JSON Schema

src/forkproof/research/sft/
  __init__.py
  models.py                         # TraceRecord, FilterResult, MetricsSummary
  loader.py                         # load_traces, validate_traces
  adapter.py                        # adapt_forkproof_export
  filter.py                         # filter_traces
  metrics.py                        # compute_metrics, cluster breakdown
  export.py                         # export_sft_jsonl, export_metadata
  cli.py                            # argparse entrypoint

tests/forkproof/research/sft/
  test_loader.py
  test_filter.py
  test_metrics.py
  test_export.py
  test_pipeline_integration.py

artifacts/sft/
  mock_run/                         # Phase 0–3 outputs (gitignored or labeled mock)
  real_run/                         # Phase 4 outputs
  run_manifest.json
  contamination_table.md
  contamination_chart.png
  WRITEUP.md
```

Keep each file under 500 lines per project engineering rules. Split by responsibility if needed.

---

## 14. Integration contract for the core team

**Copy-paste request to send the group:**

---

### SFT extension input request

For the SFT/training-data extension, please export one structured JSONL file with **one row per trace, Witness, or legitimate control**.

**Required columns:**

| Column | Type | Notes |
| --- | --- | --- |
| `trace_id` | string | Stable unique id |
| `task_id` | string | e.g. `mongodb-sales-aggregation-engine` |
| `task_prompt` | string | User-visible instruction |
| `assistant_output` | string | Agent solution or action summary |
| `raw_reward` | float | 0.0 or 1.0 under original verifier |
| `patched_reward` | float | 0.0 or 1.0 under hardened verifier |
| `is_hack` | bool | Reward-hacking classification |
| `is_legit` | bool | Legitimate solution classification |
| `exploit_cluster` | string | Mechanism label if hack (optional but helpful) |

**Optional columns:** `environment_version`, `grader_version`, `hud_trace_url`, `witness_id`, `release_proof_id`

**Minimum rows needed for demo:**

- All Exploit Witnesses from the ReleaseProof ProofSet
- All legitimate controls
- Source suspicious trace(s)

I am building the filtering pipeline against mock data now. When this file is ready, I will drop it in and re-run — no changes needed on your side beyond the export.

---

## 15. Fireworks sponsor framing

Use this narrative in slides and write-up. Keep it factual, not forced.

**Fireworks provides the training layer. ForkProof provides the verifier-cleaned data layer.**

- **SFT:** Fireworks trains on prompt/response demonstrations. ForkProof ensures those demonstrations are legitimate task solutions, not reward hacks that fooled the raw verifier.
- **RFT:** Fireworks optimizes against a grader or reward signal. ForkProof hardens that grader first so the reward signal is less gameable before it enters the optimization loop.

**One-liner for judges:**

> Fireworks makes it easy to train or fine-tune models. ForkProof makes sure the trajectories we train on are not poisoned by verifier hacks.

This connects naturally to the hackathon themes: RL environments, verifiers, and post-training workflows.

---

## 16. Demo narrative and deliverables

### Narrative (60 seconds)

1. The core system found reward hacks and patched the verifier.
2. This extension asks: *what if we trained on the original reward signal?*
3. Under the raw verifier, every reward-1 trace looks like a good training example — but some are hacks.
4. Using those as SFT positives teaches the model that exploiting the verifier is successful behavior.
5. After ForkProof hardens the verifier, hacked traces are rejected. Remaining reward-1 traces are cleaner examples of real task-solving.
6. Verifier hardening improves **benchmark reliability** and **training data quality**.

### Must-ship deliverables

| # | Deliverable | Phase |
| --- | --- | --- |
| 1 | Mock ForkProof input fixture | 0 |
| 2 | Filtering pipeline (3 buckets) | 1 |
| 3 | `raw_verifier_sft.jsonl` and `hardened_verifier_sft.jsonl` | 3 |
| 4 | `rejected_hacks_audit.jsonl` | 3 |
| 5 | Contamination comparison table | 2 |
| 6 | Exploit cluster breakdown | 2 |
| 7 | Short write-up (`WRITEUP.md`) | 2 |
| 8 | One chart or slide | 2 |

### Should-have

- Integration contract sent to core team (Section 14)
- Fireworks framing paragraph in write-up
- `run_manifest.json` provenance file

### Nice-to-have

- Real ForkProof export integrated (Phase 4)
- Fireworks managed SFT job
- Raw vs hardened model comparison

---

## 17. Agent execution checklist

Use this when an agent implements the SFT extension.

### Before coding

- [ ] Read `docs/plans/GLOSSARY.md` for ForkProof terms
- [ ] Read `HANDOFF.MD` Section 11 for Fireworks JSONL format
- [ ] Confirm whether product source exists or build standalone first

### Phase 0

- [ ] Define `TraceRecord` model with required + optional fields
- [ ] Create `fixtures/sft/mock_forkproof_traces.jsonl` with 9 rows (Section 7)
- [ ] Implement `load_traces()` with validation
- [ ] Test: loader passes on mock file, fails on bad rows

### Phase 1

- [ ] Implement `filter_traces()` with rules in Section 8
- [ ] Test: mock-001 through mock-009 land in expected buckets
- [ ] Test: no overlap between hardened_sft and rejected_hacks

### Phase 2

- [ ] Implement `compute_metrics()` — verify against expected mock table
- [ ] Write `contamination_table.md` generator
- [ ] Write exploit cluster breakdown
- [ ] Optional: generate bar chart

### Phase 3

- [ ] Implement `export_sft_jsonl()` with canonical system prompt
- [ ] Write metadata sidecar
- [ ] CLI with `--input` and `--output` flags
- [ ] Test: exported JSONL parses; ≥3 lines per training file

### Phase 4

- [ ] Implement `adapt_forkproof_export()`
- [ ] Document reconnection steps (Section 11)
- [ ] Test adapter with a sample real row (when available)

### Phase 5 (optional)

- [ ] Upload to Fireworks only after hardened export validated
- [ ] Record model/dataset/job IDs in manifest
- [ ] Do not claim results without evaluation numbers

### Do not

- [ ] Block on core team finishing ForkPoint/Modal/Witness work
- [ ] Build ForkProof core infrastructure
- [ ] Put mock metrics in final demo without labeling
- [ ] Conflate HUD reward with hack classification
- [ ] Export rejected hacks as positive SFT examples

---

## 18. Claims discipline

| Claim | When allowed |
| --- | --- |
| "Hardened verifier removes hacked positives from SFT data" | After Phase 1+2 run on mock or real data |
| "Contamination rate was X% under raw verifier" | After metrics computed; label mock vs measured |
| "Legitimate retention was 100%" | After metrics computed with real legit controls |
| "Model trained on hardened data behaves better" | Only after Phase 5 experiment with held-out eval |
| "Fireworks can train on this export" | After Phase 3 export validates; upload optional |

Keep unmeasured values as `TBD`. Preserve the distinction between HUD **reward** and **reward-hacking classification** (GLOSSARY).

---

## 19. Glossary cross-reference

| Term | Meaning in SFT context |
| --- | --- |
| **Reward** | Verifier output 0/1; determines raw_sft membership |
| **Reward-hacking classification** | `is_hack` label; independent from reward |
| **Exploit Witness** | Confirmed hack → rejected_hacks bucket |
| **Legitimate control** | Known-good solution → hardened_sft bucket |
| **ReleaseProof** | Evidence that patched verifier kills Witnesses, preserves controls |
| **Exploit cluster** | Groups rejected hacks by mechanism for breakdown |
| **Grader digest** | Version pin for raw vs patched verifier |

Full definitions: `docs/plans/GLOSSARY.md`

---

## Final pitch paragraph

ForkProof's core loop produces Exploit Witnesses and a hardened verifier. The SFT extension shows why that matters for training. If we use the raw verifier to select reward-1 trajectories, reward hacks enter the dataset as positive examples. By filtering the same trajectories through the hardened verifier, we reject hacked successes before they become SFT data. This turns ForkProof from a benchmark repair tool into a data-quality layer for post-training. Fireworks is the natural downstream path: SFT or RFT should train on verifier-cleaned trajectories, not raw reward signals that may contain exploits.
