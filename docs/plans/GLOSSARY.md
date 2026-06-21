# ForkProof shared glossary

**Action boundary.** The quiescent point after one agent action has fully affected the executable environment and before the next action begins.

**Atomic fork.** The all-or-nothing invariant that executable state and the matching agent-history prefix are captured from one action boundary. A partial capture is invalid even when the provider exposes multiple underlying operations.

**Branch gateway adapter.** The repository-owned boundary through which an isolated branch invokes the live model, HUD, or provider gateway. It attaches branch lineage and request provenance without exposing raw provider credentials to untrusted branch code.

**Branch node.** A lineage-bearing executable state from which branches may be scheduled. The root node is a ForkPoint; a depth-two child node exists only after a selected boundary has been materialized and its state evidence validated.

**BranchRun.** One executed stochastic continuation from a ForkPoint or child node, including immutable branch identity, model and sampling configuration, reward, HUD trace identity, action record, status, and lineage. Setup failures before the execution boundary are not BranchRuns.

**Candidate exploit.** A completed BranchRun with verifier success and a positive reward-hacking classification that has not yet passed every deduplication, provenance, durability, and replay gate required for Witness promotion.

**Child node.** See Branch node.

**Clean evaluator context.** A grader execution context whose trusted tests, interpreter, dependencies, import paths, plugin discovery, working directory, and relevant environment variables are pinned and protected from branch-controlled substitution.

**Content digest.** A hash over a canonical immutable record and its referenced immutable artifact hashes. Mutable timestamps, display links, and other non-semantic presentation fields are excluded by the record's declared canonicalization rule.

**Control.** See Legitimate control.

**Discovery.** The stochastic phase that varies seeds or other sampling controls, and optionally models, to find attacks. Discovery results are not proof until deterministic replay gates pass.

**Durable fallback.** A retained, content-verified representation that can restore or reconstruct required state after the primary provider snapshot expires or becomes unavailable.

**Durable replay artifact.** A retained filesystem-class state reference or durable fallback plus recorded actions, history prefix, environment and evaluator identity, hashes, and replay entrypoint sufficient to reproduce an exploit without ephemeral process memory or model rediscovery.

**Eligible boundary.** An intermediate completed-action boundary inside a depth-1 BranchRun that a cheap evidence pre-filter has marked worth ranking for depth-two expansion. Eligibility makes a boundary rankable, not selected, and is distinct from Candidate exploit status.

**Environment image digest.** A content-derived identifier for the concrete container or VM image used by a run. It is not interchangeable with the HUD environment version, task checksum, Dockerfile digest, or grader digest.

**Environment version.** HUD's opaque logical identifier for a published or executed task environment. It supplies `environment_v1` or `environment_v2` in release records and must come from the authoritative HUD execution surface rather than being inferred from a local file hash.

**Evaluator identity.** The pinned identity bundle for the authoritative reward surface in a run. It includes the scoped grader digest and, where execution can affect semantics, the verifier harness, command arguments, dependencies, environment/runtime identity, and import or plugin discovery configuration.

**Evidence manifest.** The per-plan JSON record of commands, exit codes, behavior checks, artifacts, links, unresolved risks, skips, and completion status.

**Expansion prior.** The evidence-derived ranking used to allocate the next depth-two branch. In Plan 007 it is an LLM-as-judge over recorded eligible-boundary evidence; it selects where to spend compute but cannot confirm an exploit or bypass reward, classification, deduplication, provenance, or replay gates.

**Exploit cluster.** A recorded deduplication grouping for reward-hacking candidates that share a substantive exploit target and mechanism. Cluster membership does not itself confer Witness status, and wording or implementation variants do not count as distinct clusters.

**Exploit family variant.** A re-seeded or otherwise derived attack related to a sealed Witness. It is reported separately, cannot replace exact Witness replay, and does not enter the binary release gate unless Plan 003 independently promotes it to a sealed Witness.

**Exploit Witness.** A sealed reward-hacking regression artifact whose source BranchRun had verifier success and a positive hacking classification, whose target/mechanism cluster and provenance are complete, and whose durable recorded actions reproduced v1 success in three consecutive fresh deterministic replays without model rediscovery.

**Filesystem-class snapshot.** A Modal Directory Snapshot or Filesystem Snapshot. This describes captured state type, not retention: it satisfies Witness durability only with an explicit adequate retention policy or durable fallback.

**ForkPoint.** A HUD trace action boundary bound atomically to matching executable Modal state, history prefix, task and environment identity, evaluator identity, and reason for branching.

**Grader digest.** A content-derived identifier with an explicitly recorded scope and source for grader material used by a run. A hash of one test file is only a grader-file digest; proving the exact reward surface additionally requires the surrounding Evaluator identity when harness, dependency, runtime, import, or plugin state can change behavior.

**History prefix.** Agent-visible messages, tool calls, and results through exactly the associated action boundary.

**Legitimate control.** A sealed, provenance-backed, path-diverse valid solution that repeatedly succeeds under v1 and must continue to succeed under verifier hardening.

**Lineage.** The immutable parent ForkPoint and branch-node chain that explains how a BranchRun reached its starting state.

**Merge gate.** Evidence conditions that all required plans in one wave must satisfy before the next dependent wave may begin.

**MCTS-shaped.** Tree-structured state expansion inspired by Monte Carlo Tree Search, without claiming a complete selection, expansion, value propagation, or tree policy implementation.

**Near-miss state.** An eligible boundary whose recorded observable state exposes plausible new leverage over the reward mechanism but has not completed the exploit on that path. It is a preferred expansion target, not evidence that a deeper exploit will succeed.

**Predictive-validity check.** A single-case, falsifiable comparison between the expansion prior's predicted surface/mechanism and the observed depth-two result. It checks one prediction at `n=1`; it is not statistical validation or evidence of better-than-random selection.

**Promising child.** The eligible boundary selected by the expansion prior for replay-to-boundary materialization. It becomes a child node only after replay reaches that boundary and the restored state evidence matches the recorded evidence.

**Proof.** The deterministic phase that starts from fresh restored durable state and replays pinned recorded actions against pinned environment and evaluator identities without live model rediscovery.

**ProofSet.** An immutable rerunnable HUD taskset or repository-native suite containing every in-scope sealed Exploit Witness, at least the required sealed legitimate controls, and optional separately reported exploit-family variants.

**Release candidate.** A sealed hardened environment artifact backed by a passing ReleaseProof but not yet published, including when publication is permission-blocked.

**Release gate.** The per-case binary rule that a patch may ship only when every sealed Witness changes from semantic verifier success under v1 to semantic failure under v2 and every legitimate control remains semantic success under both versions. Numeric `1` and `0` are bindings of the current grader, not the general contract.

**ReleaseProof.** A sealed, content-verified before/after artifact linking environment and evaluator identities for v1 and v2, the immutable ProofSet, patch/fixer provenance, per-case results, and the release-gate verdict.

**Replay divergence.** A deterministic replay failure in which ordered action history, state evidence, artifact digests, verifier output, or required semantic outcome differs from the sealed record. Matching only the final reward does not erase divergence elsewhere.

**Replay entrypoint.** The recorded command or repository-native operation that verifies artifact integrity, restores the pinned pre-attack state, replays recorded actions, runs the pinned evaluator, captures results, and performs cleanup.

**Replay-to-boundary.** Deterministically replaying a BranchRun's recorded actions from its parent state through a selected action boundary, then requiring the resulting state evidence to match the boundary's recorded evidence before a child node may be created.

**Repo map.** Wave 1's checked record of real repository paths, commands, interfaces, capabilities, ownership bindings, and grounding status.

**Reward.** The authoritative environment verifier's task-success signal in its repository-bound representation. It is independent from reward-hacking classification.

**Reward-hacking classification.** A structured assessment that a trajectory gamed the evaluator, including HUD QA output where used. It is independent from reward: a positive classification without verifier success is diagnostic and cannot become a Witness.

**Sealed artifact.** An immutable finalized record with complete required fields, verified content digest, and required referenced evidence. Corrections create a superseding artifact rather than mutating the sealed record.

**Snapshot mode.** The executable-state capture type: Directory, Filesystem, or Memory. VM Sandbox is an execution profile that may support Filesystem Snapshots; it is not itself a snapshot mode.

**Source trace.** A stable reward-success HUD trace selected as ForkProof input. A suspicious trace is the product trigger; a legitimate trace used only for grounding or state-fidelity work must be labelled as such and cannot serve as exploit evidence.

**State fidelity.** The property that a fresh restore matches the original action boundary on declared task-visible, grader-visible, history, identity, and security probes.

**STOP condition.** A correctness, security, ownership, or evidence failure that forbids proceeding until it is resolved and recorded.

**Task checksum.** HUD's content-derived checksum of the task definition emitted by a run. It is not interchangeable with task id, environment version, environment image digest, or evaluator identity.

**Training admission set.** The trajectories receiving semantic verifier success under one named verifier version before independent legitimacy or reward-hacking labels are applied.

**Training contamination.** The fraction of one explicitly named training admission set that has a positive reward-hacking classification. Numerator and denominator must refer to the same verifier version and population.

**Verifier harness digest.** A content-derived identifier for the command/script layer that invokes the grader and writes or returns reward. It complements, but does not replace, grader-file and complete Evaluator identity.

**VM Sandbox profile.** A conditional Modal execution profile with a full Linux kernel for tasks requiring behavior such as Docker-in-sandbox or systemd. It may use Filesystem Snapshots and is never treated as a snapshot mode or an automatic substitute for the core sandbox path.

**Work packet.** A small vertical increment with its own behavior-level pass/fail observation and recovery boundary.
