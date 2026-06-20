# Plan 003 reference — branch, promotion, replay, and security details

## Core branch policy

The core evidence run uses:

- 12 initial branches,
- one accepted ForkPoint,
- independent branch ids and seeds,
- real sampling configuration,
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
- restored snapshot id/mode and history hash,
- environment version/image and grader digest,
- HUD branch trace id,
- ordered action record,
- file diff,
- reward output,
- QA output or classified failure,
- start/end timestamps and status,
- resource/cost metadata when available,
- error class and cleanup result.

## Dedup behavior

Use the verified harden-v0 or repository dedup implementation. The semantic key is target plus mechanism, informed by evidence rather than surface wording. Record:

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

## Security evidence

At minimum record:

- secret names available to the branch versus trusted orchestrator,
- egress policy and one harmless denied request,
- filesystem mount boundaries,
- resource/time limits,
- sibling isolation probe,
- cleanup after timeout,
- proof that grader/release credentials are absent,
- artifact-writing trust boundary.

Do not put secret values in evidence.

## Metrics

Derive:

- BranchRun count from finalized records,
- cluster count from dedup report,
- time to first Witness from event timestamps,
- replay success rate from attempts,
- restore latency from provider events,
- setup work avoided from measured source setup versus restore work when available.

Use `not-measured` when the event does not exist. Do not backfill an estimate.
