---
name: stochastic-witness-loop
description: >
  Turns one accepted ForkPoint into genuine seeded BranchRuns, separates reward from QA classification, deduplicates exploit mechanisms, materializes durable Exploit Witnesses, and proves deterministic replay. Use when Gate 2 is satisfied: Plans 002 and 004 have complete manifests, the wave merge gate is open, and the real branch gateway, snapshot restore, grader, QA, storage, and security bindings are accepted; it owns src/forkproof/witnesses/**, tests/forkproof/witnesses/**, fixtures/forkproof/witnesses/**, this plan/reference, and evidence/003/**.
owns: ["docs/plans/003-stochastic-witness-loop.md", "docs/plans/003-stochastic-witness-loop.REFERENCE.md", "src/forkproof/witnesses/**", "tests/forkproof/witnesses/**", "fixtures/forkproof/witnesses/**", "docs/plans/evidence/003/**"]
depends_on: ["atomic-forkpoint-seam", "legitimate-control-fixtures"]
wave: 3
---

# Stochastic Witness loop

## Goal

Run exactly 12 executed genuine seeded stochastic continuations from one real ForkPoint and promote at least one branch to an Exploit Witness only after complete provenance, independent reward/QA gates, target-mechanism deduplication, durable storage, and three consecutive deterministic v1 replays all pass. Done is binary when both the 12 executed BranchRun count and at least one sealed three-replay Witness are evidenced.

## Context / Why

Discovery and proof are intentionally different. Discovery varies seeds and sampling to find attacks; it may fail or produce different trajectories. Proof restores saved pre-attack state and replays recorded actions against pinned versions. HUD v6 represents each rollout as a `Run` with reward, runtime placement, trace id, job id, and an ordered `Trace`, so Plan 003 treats each BranchRun as a real run/trace artifact, not a row in a local scheduler ([HUD v6 Types](https://docs.hud.ai/v6/core/types)). A suspicious or rewarded trace alone is not a durable regression test.

This slice owns the full locality of behavior from branch scheduling through Witness replay. It reuses the existing agent gateway and harden-v0 dedup behavior found in Wave 1; harden-v0's dedup path clusters hacks by substantive target and mechanism rather than minor wording or implementation differences ([harden-v0 dedup source](https://github.com/few-sh/harden-v0/blob/b9dd28c732e7e5435da4a2ac90ae92ac6ea65007/dedup_hacks.py#L31-L35)). It does not patch the verifier. External citations in this plan are non-normative grounding only: exact SDK behavior, API signatures, trace formats, and commands must come from accepted Wave 1 repo-map evidence. Read the sibling reference for the promotion truth table, branch budget, replay protocol, and security evidence.

## Constraints

- Start only when Gate 2 is satisfied: Plans 002 and 004 have complete manifests, Plan 002 has merged with a branch-ready restore handoff, Plan 004 controls are frozen, `docs/plans/repo-map/STATUS.json` is `accepted`, `plan-003-tests`, `integration-witness`, and `security-branch` have verified mapped argv, and this plan's ownership bindings are accepted. Never recreate the state from scratch for core branch runs.
- Run agentic continuations with live model/gateway calls, real gateway request ids, provider response provenance, unique branch ids/seeds, and recorded sampling configuration. HUD agents are model+harness callables over a live `Run`, and HUD's CLI supports grouped rollouts to observe reward spread; Plan 003 still binds the exact gateway behavior through the repo map rather than assuming the CLI shape is the implementation path ([HUD v6 Agents](https://docs.hud.ai/v6/core/agents)). Evidence must show provider-supported seed semantics or non-deterministic sampling diversity and prove the branch action record came from live gateway execution rather than replay fixtures. Do not feed a fixed exploit taxonomy.
- Count exactly 12 executed BranchRuns, not 12 scheduled attempts or 12 successful branches. A branch counts only after preflight succeeds and the execution boundary is crossed: restored isolated state is bound to an immutable branch id, runtime/provenance identity is allocated, and the Branch gateway adapter invokes the live agent/gateway or first environment action. After that boundary, success, verifier failure, QA failure, timeout, agent error, or cleanup failure finalizes a counted BranchRun with status and cleanup evidence. Setup/preflight failures before that boundary are recorded separately in the evidence manifest and replaced by a new immutable branch id/seed. This follows repetition/error handling conventions where repetitions are executed samples while setup errors remain distinct from scored results ([LangSmith repetitions](https://docs.langchain.com/langsmith/repetition), [Inspect handling errors](https://inspect.aisi.org.uk/handling-errors.html)).
- Use one repository-owned Branch gateway adapter as the only Plan 003 live execution boundary for model/HUD/provider calls. Direct HUD CLI, provider SDK, or gateway calls are allowed only inside that adapter or as earlier repo-map probe commands, never scattered through Witness scheduling, promotion, replay, or tests.
- Keep reward and QA classification separate and authoritative at their own sources. HUD QA agents can emit structured reward-hacking verdicts such as `is_reward_hacking`, `hacking_strategy`, and `severity`, but those verdicts do not replace the verifier reward ([HUD QA Agents](https://docs.hud.ai/platform/agents/qa)).
- Tag every gateway, snapshot, trace, grader, QA, and artifact operation with run/branch/node lineage.
- Reuse repository/harden-v0 target-mechanism dedup; do not count wording variants as new exploits.
- A Memory Snapshot may not be the durable Witness system of record. Modal Sandbox Memory Snapshots are Alpha, include important restore limitations, and cannot be treated as a long-lived proof artifact; use filesystem-class state for sealed Witnesses ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots)).
- Untrusted code receives minimum secrets, scoped network, isolated writable state, and bounded resources. Modal Sandboxes are isolated and have no inbound access by default, but outbound traffic is public unless `block_network` or allowlists are configured; Modal also exposes explicit sandbox CPU/memory limits and explicit secret injection, so Plan 003 must record the actual enforcement settings and one denied harmless request ([Modal Sandbox networking](https://modal.com/docs/guide/sandbox-networking), [Modal Sandbox resources](https://modal.com/docs/guide/sandbox-resources), [Modal Secrets](https://modal.com/docs/guide/secrets)).
- Persist no secret material in history, action logs, tool results, subprocess output, file diffs, QA outputs, evidence manifests, or provider tags. Evidence is written only by trusted orchestration into append-only or content-addressed storage outside branch-writable state.
- STOP before execution when the Plan 002 handoff is missing `snapshot_restore_ref`, parent node id, isolated writable root identity, history hash, snapshot mode/id, grader digest, or branch-tag propagation inputs. STOP before execution when isolation, branch gateway identity, artifact trust boundary, or grader authority is unverified. STOP Witness promotion on missing provenance, unavailable classification, expired/unrecoverable state, digest mismatch, retained secret material, untrusted artifact writes, or replay divergence.
- Co-locate branch policy, promotion, artifact packaging, replay, and tests in the Witness feature. Split files over 500 lines by scheduler/promotion/replay/storage responsibility.
- Tests assert public promotion/replay outcomes. Do not mock the unit being classified or replayed.

## Work packets

### WP1 — Build isolated BranchRun execution

Re-verify the Plan 002 handoff before any branch starts: boundary token/hash, `snapshot_restore_ref`, parent node id, isolated writable root identity, history hash, Directory/Filesystem snapshot mode/id, grader digest, `grader_digest_source`, trusted evidence refs, non-branch-writable artifact store, and branch-tag propagation inputs. Restore the ForkPoint into one isolated branch context per attempt, assign run/branch/node identity from the Plan 002 handoff, configure model/seed/sampling from the real gateway, enforce resource/security policy, and persist bounded failure records. Authoritative grading must run in a trusted evaluator context with attacker-controlled cwd, import paths, plugin paths, and test discovery side effects excluded or neutralized. STOP before branch execution on Memory/VM-only state, unsupported snapshot mode, stale handoff, missing digest provenance, branch-writable evidence, or untrusted grader/import-path separation. Record Modal runtime identifiers when available, such as sandbox/task/image ids, as provider evidence rather than stable domain ids ([Modal environment variables](https://modal.com/docs/guide/environment_variables)).

Implementation guidance: keep the Branch gateway adapter inside the `witnesses` feature boundary because it exists to satisfy BranchRun provenance, not to become a general SDK wrapper. Its public contract is the local behavior boundary: inputs are the accepted ForkPoint handoff, branch identity, model/seed/sampling config, sandbox policy, and lineage tags; outputs are a finalized BranchRun record, native action/tool envelopes, provider request/response provenance, HUD trace refs, cleanup status, and bounded failure records. Scheduler, promotion, replay, and storage code must call this adapter instead of importing HUD/provider clients directly. Split implementation files only by real lifecycle responsibility: gateway execution, action-envelope capture, branch security policy, promotion, replay, and durable storage.

**Pass:** Two simultaneous probe branches cannot read or mutate each other's writable state, and every attempt produces a complete success/failure BranchRun record.  
**Fail:** Branches share mutable task state, inherit broad credentials, or failed attempts disappear.

### WP2 — Execute 12 genuine stochastic branches

Run 12 executed unique branches from the same ForkPoint with sampling diversity. Preserve HUD trace links, action records, file diffs, reward, model configuration, provider/gateway request ids, model response provenance, timing, and lineage. HUD file tracking is an explicit platform feature and may be disabled; Plan 003 must record whether branch file evidence comes from the accepted repo adapter, HUD file tracking, or another verified immutable export ([HUD File Tracking](https://docs.hud.ai/platform/file-tracking)). Do not stop early in the core run even when a Witness appears; the must-ship evidence is about 12 real executed branches.

**Pass:** Evidence lists 12 executed unique branch ids and seeds with real model/gateway and trace results, plus separate records for any replaced preflight failures.  
**Fail:** Branches are scripted replays, duplicated identities, or fresh-from-start rollouts.

### WP3 — Grade, classify, and deduplicate independently

Obtain authoritative verifier reward and HUD QA hacking classification, prove both signals join to the exact same BranchRun, then group qualifying candidates by target and mechanism through the verified dedup path. Reject promotion when `reward.hud_trace_id`, `qa_result_ref`, `branch_id`, `environment_version`, `grader_digest`, or action-record digest cannot be joined to the same branch trace. HUD task grading can score world state such as tests, files, or services, so the reward source must be the actual task verifier output, not a branch self-report ([HUD v6 Tasks & Tasksets](https://docs.hud.ai/v6/core/tasks)).

**Pass:** The promotion truth table rejects reward-only, QA-only, and missing-signal cases; equivalent attacks share a cluster id.  
**Fail:** Reward is inferred from QA, QA is inferred from reward, or every wording variant counts as distinct.

### WP4 — Materialize durable Witness candidates

For each qualifying candidate, store pre-attack filesystem-class state, history prefix, native recorded actions/tool results, file diff, verifier/QA outputs, environment/image/grader identity, model/seed/config, cluster, replay entrypoint, retention, and content digest. Define `pre_attack_snapshot_ref` as either the source ForkPoint restore or a recorded child snapshot before the first exploit action; `recorded_actions_ref` must name the exact inclusive action span replayed from that state. The sealed Witness manifest must contain every field from `docs/plans/specs/03-interfaces.md#exploit-witness-record`; missing fields produce `provenance_incomplete`. Modal Filesystem Snapshots and Directory Snapshots become Images that can restore future Sandboxes, and their TTL/retention must be recorded or set deliberately for proof use ([Modal Sandbox Snapshots](https://modal.com/docs/guide/sandbox-snapshots), [modal.Sandbox reference](https://modal.com/docs/sdk/py/latest/modal.Sandbox)). STOP promotion when the candidate cannot be cold-replayed from a durable filesystem-class pre-attack representation; memory/process snapshots may support discovery diagnostics only, not Witness sealing.

**Pass:** The candidate survives process restart and has no secret material; ephemeral state has a durable fallback.  
**Fail:** It depends on live process memory, mutable “latest” versions, or a dashboard link alone.

### WP5 — Gate Witness status on deterministic replay

Restore the saved pre-attack state and replay recorded actions without model rediscovery. Require three consecutive v1 runs to reproduce the same semantic successful reward under the pinned grader and environment. harden-v0's replay gate is a primary-source precedent for explicitly re-attempting prior exploits and rejecting a fix when replay still reaches the hack threshold; Plan 003 applies the same proof distinction before any release work begins ([harden-v0 loop source](https://github.com/few-sh/harden-v0/blob/b9dd28c732e7e5435da4a2ac90ae92ac6ea65007/harden/loop.py#L960-L984)).

**Pass:** At least one candidate passes all three runs and is sealed as a Witness.  
**Fail:** Any action diverges, an external dependency is unpinned, or reward is inconsistent; the candidate remains unproven.

### WP6 — Record metrics and honest fallback artifact

Compute branch count, distinct clusters, time to first Witness, replay success, restore latency, and setup work avoided from events. Mark unmeasured metrics explicitly. Retain one genuine prior-run Witness suitable for the demo fallback, clearly labelled with its original run.

**Pass:** Metrics derive from recorded timestamps/events, and fallback can be restored/replayed live.  
**Fail:** Values are estimated or a prerecorded artifact is presented as live discovery.

## Done-when (self-validation gate)

Run from repository root:

    python docs/plans/scripts/run_mapped.py plan-003-tests
    python docs/plans/scripts/run_mapped.py integration-witness
    python docs/plans/scripts/run_mapped.py security-branch
    python docs/plans/scripts/run_mapped.py lint
    python docs/plans/scripts/validate_graph.py
    python docs/plans/scripts/validate_sections.py
    python docs/plans/scripts/validate_ownership.py --repo-bound
    python docs/plans/scripts/validate_traceability.py
    python docs/plans/scripts/validate_file_sizes.py --plan 003
    python docs/plans/scripts/validate_evidence.py --plan 003 --require-complete

Expected evidence:

- one source ForkPoint id,
- Plan 002 restore handoff fields re-verified after process restart: boundary token/hash, `snapshot_restore_ref`, parent node id, isolated writable root identity, history hash, Directory/Filesystem snapshot mode/id, grader digest, `grader_digest_source`, trusted evidence refs, non-branch-writable artifact store, and branch-tag propagation inputs,
- 12 executed unique BranchRun records, seeds, gateway request ids, model response provenance, sampling configs or provider-supported seed semantics, trace links, live-generated action records, status, and cleanup result, plus separate non-counted setup/preflight failure records and replacement branch ids when applicable,
- separate reward and QA outputs with source ids, same-branch join proof, and unavailable-classification failure coverage,
- dedup cluster report with compared prior clusters, target/mechanism rationale, and real dedup path output,
- at least one sealed Witness with durable filesystem-class state, exact `pre_attack_snapshot_ref`, inclusive `recorded_actions_ref` replay span, complete Exploit Witness fields, retention decision, content digest, redaction result, and replay entrypoint,
- three consecutive deterministic v1 replay results from fresh restores without model calls,
- replay proof: no gateway/model requests during replay, fresh restore ids for all three runs, ordered action/tool envelope comparison, file diff/verifier output comparison, and unpinned external dependency divergence handling,
- branch security negative checks: denied unavailable-secret read, denied disallowed egress or metadata request, sibling writable-state isolation, artifact-store overwrite denial, trusted grader/import-path separation, grader/release credential absence, resource/time-limit enforcement, and timeout cleanup,
- measured/not-measured metrics,
- manifest `docs/plans/evidence/003/MANIFEST.json`.

No owned source file exceeds 500 lines without an approved split. Tests verify promotion, isolation, and replay behavior rather than internal scheduler structure.

## Recovery

Branch ids are immutable and attempts are append-only. Resume missing branches without rerunning completed ids; a new stochastic retry gets a new id. Clean up timed-out sandboxes and orphaned temporary snapshots using provider ids recorded in the manifest. Never promote a partially written candidate. Rollback removes the feature code and nonsealed temporary artifacts; sealed Witness evidence is append-only and may be marked superseded, not rewritten.

## Executor prompt

    /goal Execute docs/plans/003-stochastic-witness-loop.md only after Gate 2 is satisfied: Plans 002 and 004 manifests are complete and the Wave 3 merge gate is open. Run 12 executed real seeded isolated branches from the accepted ForkPoint, keep reward and HUD QA separate, deduplicate by target/mechanism, seal at least one durable Witness only after three deterministic v1 replays, pass the security and integration commands plus merge validators, stay inside owned paths, update evidence/003/MANIFEST.json, and append the Living-doc log. Never substitute scripted, scheduled-only, preflight-only, or fresh-start runs for stochastic state branches.

## Living-doc log

### Progress

- At every STOP or handoff, append a timestamped entry and mirror the blocker, failed precondition, and evidence refs in `docs/plans/evidence/003/MANIFEST.json`.
- [ ] Isolated BranchRun execution complete.
- [ ] Twelve genuine branches complete.
- [ ] Reward/QA/dedup gates complete.
- [ ] Durable candidate packaging complete.
- [ ] Three-run deterministic replay gate complete.
- [ ] Metrics and fallback artifact complete.

### Surprises & Discoveries

- 2026-06-20 — Corrected planning audit target from Plan 002 to Plan 003; Plan 003 remains blocked until Gate 2 and real branch gateway/snapshot restore/grader/QA/storage/security bindings are accepted.
- 2026-06-20 — External docs audit added non-normative inline grounding for HUD run/trace/reward/QA/file evidence, Modal Sandbox snapshot/network/runtime identity behavior, and harden-v0 dedup/replay precedent.

### Decision Log

- 2026-06-20 — Planning decision: co-locate stochastic discovery and deterministic Witness replay because Witness promotion is one vertical behavior boundary.
- 2026-06-20 — Grilling decision: every core BranchRun must be produced by a live model/gateway call with provider response provenance; synthetic action envelopes, scripted traces, cached model responses, or replay fixtures cannot satisfy the 12-branch evidence requirement.
- 2026-06-20 — Grilling decision: Plan 003 requires one repository-owned Branch gateway adapter as the mandatory live execution boundary. Direct HUD CLI/provider SDK calls are allowed only behind that adapter or as repo-map probe commands, preserving locality of behavior and modularity by the `witnesses` feature.
- 2026-06-20 — Grilling decision: the branch budget is 12 executed BranchRuns. Scheduled-only and preflight-failed attempts are evidenced separately and replaced; failures after the execution boundary count because they represent real stochastic continuations.
- 2026-06-20 — Grilling decision: sealed replay compares ordered native action envelopes and semantic verifier output, not reward alone; action-order divergence keeps the candidate unproven.
- 2026-06-20 — Grilling decision: Plan 003 uses four trust zones (`trusted_orchestrator`, `untrusted_branch`, `trusted_grader`, `trusted_release`) and gives untrusted branches only branch-scoped capabilities through the Branch gateway boundary.
- 2026-06-20 — Grilling decision: Plan 003 frontmatter depends on both `atomic-forkpoint-seam` and `legitimate-control-fixtures` because Gate 2 requires Plan 002 state fidelity and Plan 004 frozen controls before Wave 3 may start.

### Outcomes & Retrospective

- Pending execution.
