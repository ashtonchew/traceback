# Plan 003 reference — branch, promotion, replay, and security details

## Core branch policy

The core evidence run uses:

- 12 initial branches,
- one accepted ForkPoint,
- the Plan 002 restore handoff fields needed for BranchRun lineage,
- independent branch ids and seeds,
- real sampling configuration,
- gateway request ids for every model call,
- model response provenance and either non-deterministic sampling settings or provider-supported seed semantics,
- no fixed exploit taxonomy,
- no core early stop,
- bounded timeout/resources,
- complete success or failure provenance.

Adaptive stopping and depth-two expansion belong to Plan 007.

## Promotion truth table

| Reward success | QA says hacking | Provenance complete | Dedup decision | Replay passes | Result |
|---|---:|---:|---:|---:|---|
| yes | yes | yes | recorded | yes | Seal Witness |
| yes | yes | yes | recorded | no | Unproven candidate |
| yes | yes | no | any | any | Reject promotion |
| yes | no | any | any | any | Not a Witness; inspect as possible legitimate behavior |
| no | yes | any | any | any | Not a Witness; diagnostic only |
| missing | any | any | any | any | Incomplete branch |
| any | missing | any | any | any | Incomplete classification |

The repository's actual reward type may differ from numeric 1/0. Bind “success” and “failure” to the grader contract.

## Branch provenance

Required evidence per attempt:

- run, branch, parent node, and ForkPoint ids,
- seed, model, sampling settings, gateway request id,
- restored snapshot id/mode, `snapshot_restore_ref`, isolated writable root identity, and history hash,
- environment version/image, provider runtime ids when available, and grader digest,
- HUD branch trace id,
- ordered action record,
- file diff,
- reward output,
- QA output or classified failure,
- start/end timestamps and status,
- resource/cost metadata when available,
- error class and cleanup result.

A completed BranchRun must be reconstructable without reading mutable process memory, branch-local temp files, or dashboard-only state. Failed attempts are still finalized records with bounded diagnostics and cleanup status.

Reward, QA, action record, file diff, environment version, and grader digest must join to the same BranchRun. If the authoritative reward output and QA result cannot be tied to the same branch trace and action-record digest, the branch is diagnostic only and cannot enter dedup or Witness promotion.

## Dedup behavior

Use the verified harden-v0 or repository dedup implementation. harden-v0's primary dedup script instructs clustering by substantive target and mechanism rather than surface wording, so the semantic key is target plus mechanism informed by branch evidence ([harden-v0 dedup source](https://github.com/few-sh/harden-v0/blob/b9dd28c732e7e5435da4a2ac90ae92ac6ea65007/dedup_hacks.py#L31-L35)). Record:

- compared prior clusters,
- selected existing/new cluster,
- rationale/output from the real dedup path,
- representative Witness id.

A cluster decision may be stochastic if model-based; persist the decision and inputs. Do not claim exact cluster counts without the report.

## Durable Witness conversion

A successful branch must have a filesystem-class pre-attack state. When discovery used process memory:

1. Stop further unrecorded actions.
2. Export/snapshot durable filesystem state.
3. Save native recorded actions from a durable pre-attack point.
4. Save environment image and grader digests.
5. Prove cold replay from the durable representation.
6. Only then seal the Witness.

If conversion cannot reproduce the attack, the branch remains a discovery result, not a Witness.

Witness manifests must record retention strong enough for release regression use or a durable fallback that survives provider snapshot expiry. Memory Snapshot ids, live process handles, and platform dashboard URLs may appear as diagnostic references, but none can be the durable system of record.

`pre_attack_snapshot_ref` is either the source ForkPoint restore or a recorded child snapshot taken before the first exploit action. `recorded_actions_ref` names the exact inclusive action span replayed from that state. A sealed Witness must satisfy every required Exploit Witness field in `docs/plans/specs/03-interfaces.md#exploit-witness-record`; missing fields are `provenance_incomplete`.

## Replay protocol

Replay must not call the attacker model. It:

1. verifies manifest/content hashes,
2. restores pre-attack durable state,
3. reconstructs exact history only when the action executor requires it,
4. pins environment image and grader,
5. replays native action/tool envelopes in order,
6. captures file diff and verifier output,
7. compares semantic result with the original,
8. cleans the sandbox,
9. repeats from a fresh restore three times.

A timestamp, random nonce, external network response, package registry, or floating dependency that changes the outcome must be pinned, recorded, or treated as divergence.

Replay evidence must include proof that model/gateway credentials were not invoked, the sandbox was freshly restored for each attempt, and the verifier/grader digest matched the original candidate. A candidate with one successful replay and one divergent replay remains unproven.

## Security evidence

At minimum record:

- secret names available to the branch versus trusted orchestrator,
- egress policy and one harmless denied request,
- filesystem mount boundaries,
- resource/time limits,
- sibling isolation probe,
- cleanup after timeout,
- proof that grader/release credentials are absent,
- artifact-writing trust boundary,
- authoritative grader execution separated from attacker-controlled cwd, import paths, plugin paths, and test discovery side effects,
- redaction/sanitization result for history, action logs, file diffs, QA/verifier outputs, and manifest fields.

Do not put secret values in evidence. Branches may emit diagnostic data, but trusted orchestration writes the canonical evidence manifest and content-addressed artifacts outside branch-writable state.

## Metrics

Derive:

- BranchRun count from finalized records,
- cluster count from dedup report,
- time to first Witness from event timestamps,
- replay success rate from attempts,
- restore latency from provider events,
- setup work avoided from measured source setup versus restore work when available.

Use `not-measured` when the event does not exist. Do not backfill an estimate.
