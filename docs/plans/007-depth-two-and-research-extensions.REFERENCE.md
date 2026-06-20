# Plan 007 reference — research protocol and skip rules

## Promising-node evidence

Rank candidate child states from observable evidence:

- new or unusual file changes,
- changed test/plugin/grader interaction,
- a new exploit cluster precursor,
- verifier output suggesting a narrowed attack surface,
- task logs or process state that materially differs,
- optional exposed reasoning as one signal, never the sole dependency.

Record the selected node, alternatives, evidence, and why the state merits reuse.

## Adaptive policy

Per node:

- initial child budget: at most 8,
- maximum tree depth: 2,
- count consecutive completed branches with no new target/mechanism cluster,
- reset count to zero when a new cluster is confirmed,
- stop scheduling new branches at count 4,
- allow already-running branches to finish or cancel according to the real scheduler's safe policy,
- never classify a raw rewarded branch as “new cluster” before QA/dedup.

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
