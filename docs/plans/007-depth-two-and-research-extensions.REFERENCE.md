# Plan 007 reference — research protocol and skip rules

## Expansion prior — finding the promising child

The depth-two node is chosen by a two-stage expansion prior over the *recorded* evidence of the depth-1 BranchRuns. Ranking needs no snapshots (the evidence already exists); only the selected child is materialized, by replay-to-boundary. See the glossary for `Eligible boundary`, `Expansion prior`, `Near-miss state`, `Promising child`, `Replay-to-boundary`, and `Predictive-validity check`.

### Stage 1 — Pre-filter (cheap, mechanical)

A boundary is an *eligible boundary* when at least one observable signal fired at it:

- new or unusual file changes,
- changed test/plugin/grader interaction,
- a new exploit cluster precursor,
- verifier output suggesting a narrowed attack surface,
- task logs or process state that materially differs,
- optional exposed reasoning as one signal, never the sole dependency.

The pre-filter is *eligibility*, not selection: a single signal makes a boundary rankable, not chosen. Apply a hard candidate cap (≈20–30); if more survive, keep the most-divergent per branch. Exposed reasoning alone never makes a boundary eligible.

### Stage 2 — Expansion prior (LLM-as-judge)

Rank the eligible boundaries from their full recorded evidence and select one *promising child*. Prefer *near-miss states*: a boundary that newly exposed leverage over the reward mechanism (test / plugin / conftest / grader / config / seeded state) the parent ForkPoint lacked, where the exploit is staged but **not yet completed** on that path — so a deeper stochastic step may finish a multi-step exploit a flat search misses. Deprioritize boundaries whose branch already sealed a Witness; rediscovery there is absorbed by dedup and the WP3 stop. With no eligible near-miss, depth-two is an evidence-backed skip.

The judge uses all trajectory evidence, never exposed reasoning alone, and may read the task codebase (grader / golden / tests) only as an analyst. It emits a **falsifiable prediction**: which surface the child exposes, which mechanism a deeper step is expected to complete, and why the parent could not reach it.

**Selection is compute allocation, not confirmation.** The expansion prior never confirms a Witness; every depth-two exploit is still independently gated by reward, QA, dedup, and deterministic replay. A biased judge can only waste a depth-two budget on a dud (caught by the predictive-validity check and the WP3 stop), never manufacture a Witness.

### Stage 3 — Materialize by replay-to-boundary, then validate

Replay the chosen branch's recorded actions to boundary *t* and verify the restored state-hash matches the ranked evidence before expanding (fail-closed: mismatch → next-ranked child; unpinnable-nondeterminism prefix → ineligible skip). Record the selected node, the ranked alternatives, the evidence, and the falsifiable prediction.

**Predictive validity, not better-than-random.** Because depth-two expands exactly one node (n=1), validate the prior by checking whether the predicted surface/mechanism actually appeared in the depth-two result — not by a statistical better-than-random claim, which is marked TBD (it needs many selections across tasks; out of 007 scope, consistent with R-045).

### No-leakage wall

The judge selects *where* to fork; the depth-two branches discover *what* stochastically and run blind to the prediction. The predicted mechanism, the judge's reasoning, and any golden/grader knowledge it read must never enter a branch prompt (WP2 STOP).

## Adaptive policy

Plan 007 owns the research scheduler. Plan 003 explicitly delegates adaptive stopping and depth-two expansion here (“Adaptive stopping and depth-two expansion belong to Plan 007”) and declares no core early stop.

Per node:

- initial child budget: at most 8,
- maximum tree depth: 2,
- count consecutive completed branches with no new target/mechanism cluster,
- reset count to zero when a new cluster is confirmed — including a cluster confirmed by a branch that was already in flight when the count reached 4,
- stop scheduling new branches at count 4,
- if count resets from an in-flight result, resume scheduling only when budget remains (total scheduled branches must stay at most 8),
- allow already-running branches to complete; cancel only when the core release needs resources and the scheduler's active branch list supports safe cancellation,
- never classify a raw rewarded branch as “new cluster” before QA/dedup.

## Depth-two replay anchor

A depth-two Witness's `pre_attack_snapshot_ref` points to the **child node's snapshot**, not the root ForkPoint. The root ForkPoint is never re-traversed during replay.

The child node snapshot must be a Directory or Filesystem artifact — a Memory Snapshot alone cannot satisfy Witness durability. The research scheduler records an explicit `retention/expiry` at child capture time sufficient to complete three consecutive replays.

The research scheduler owns the seal-or-discard decision. Once a depth-two Witness is sealed, its `pre_attack_snapshot_ref` passes to the core persistence layer under the same indefinite-retention rule as core Witnesses. Expiry of the child snapshot before three replays complete is a hard failure; there is no research-tier exemption.

## Flat comparison protocol

Make budgets comparable:

- same task and initial environment version,
- same attacker model family and sampling envelope,
- measured setup and execution time,
- comparable number of model calls or explicitly normalized compute,
- same reward/QA/dedup/Witness gates,
- multiple attempts only when budget permits.

Report raw counts and uncertainty/limitations. One task cannot establish universal superiority.

## Capability gate

A profile is implementable only when all are true:

1. Account/SDK probe succeeds.
2. The real task has state the profile uniquely preserves or enables.
3. Security boundaries are at least as strong as core.
4. The path has a real work packet/demo/research consumer.
5. Durable conversion is possible for any successful exploit.
6. Time/budget remain after core gates.

Otherwise record `skipped` with probe output and create no production adapter.

## VM and Memory capability matrix

Modal capability facts as of this plan's wave. Verify against the live SDK before implementing any path.

**Directory Snapshot** — Beta. Captures and mounts a specific directory. Default retention 30 days; explicit TTL available to opt out of expiry. Core Plan 002 path when task-relevant mutable state is contained under a verified directory boundary.

**Filesystem Snapshot** — captures the full Sandbox filesystem as an image. Default retention 30 days; explicit TTL available. Core Plan 002 fallback when directory containment is not honest.

**Memory Snapshot** — Alpha/experimental. 7-day expiry; cannot be extended. Source sandbox is terminated on snapshot. Cannot snapshot while `Sandbox.exec` is running. Background processes launched by `Sandbox.exec` are not reliably restored. Must never be the durable Witness system of record or `pre_attack_snapshot_ref`. VM Sandboxes do not support Memory Snapshots.

**VM Sandbox** — Alpha. Full VM with a real Linux kernel. Useful for Docker-in-Sandbox, Harbor, systemd/custom init, eBPF, cgroups/resource isolation, and loopback mounts. Supports Filesystem Snapshots; does not support Memory Snapshots. Not a replacement for Plan 002 Directory/Filesystem mode — use only when the real task cannot be honestly executed without kernel-level behavior.

| Evidence dimension | VM Sandbox | Memory Snapshot |
|---|---|---|
| **Availability** | Account/SDK probe succeeds for `vm` capability | Account/SDK probe succeeds for `memory` snapshot |
| **Task need** | Task genuinely requires Docker/Harbor, systemd, eBPF, cgroups, or loopback — not merely "more powerful" | Attack-relevant state is process-resident and cannot be reproduced from filesystem-class state plus recorded actions |
| **Security** | Isolation at least as strong as core; minimum secrets and scoped network | Same as core; no additional secrets passed to Alpha path |
| **Cleanup** | Record all created sandbox/snapshot ids; clean up after research run completes or is cancelled | Memory snapshot expires in 7 days regardless; successful discovery converted to durable artifact immediately |
| **Consumed path** | Real consumer exists in a research work packet before any adapter code is written | Durable conversion artifact exists (Directory/Filesystem snapshot + recorded actions + history prefix + env image digest + grader digest + restore command) before any Witness promotion |
| **Skip evidence** | Core Directory/Filesystem sandbox honestly executes the task without kernel-level behavior | No process-resident attack surface; filesystem-class capture plus recorded actions is sufficient to reproduce the attack |

## Transfer gate

Cross-task transfer requires at least one additional real task compatible with the existing shared defense pool. Report baseline and transferred-defense behavior separately. Do not claim ForkProof invented transfer.

## Training-data analysis sequence

1. Gather real reward-1 trajectories from core/research runs.
2. Label them with sealed Witness/legitimate evidence.
3. Compare admission by raw v1 and hardened v2 verifier.
4. Report contamination count/fraction and exploit-cluster composition.
5. Only then consider optional SFT/RFT under a separate measured protocol.
6. Evaluate on held-out true behavior; label the prediction as hypothesis until measured.

No gradient-bearing monitor is introduced into the live architecture.

## Valid evidence-backed skips

Examples:

- provider capability probe returns unavailable/unauthorized,
- no task state requires process memory,
- Docker-in-sandbox is not needed for the converted core task,
- no additional real task is materialized,
- branch budget consumed by core release,
- insufficient trajectories for a meaningful filter comparison.

“Ran out of interest” or “would take time” without budget evidence is not a valid skip.
