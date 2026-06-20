# Agent governance

## Source priority

Treat the checked-in repository, this bundle, and the supplied Hack2Fix2Hack handoff as the only project sources of truth. Do not infer an API signature, existing file path, runtime behavior, or command from familiarity with HUD, Modal, harden-v0, or another repository. Read `docs/plans/ASSUMPTIONS.md` before implementation. Anything tagged `verify-against-repo` remains unverified until Wave 1 records evidence.

## ExecPlans

For this project, an ExecPlan is one numbered file under `docs/plans/`. Execute only a plan whose `depends_on` plans have merged and whose wave merge gate is open. Follow `PLANS.md` and the selected plan from design through validation. Keep the selected plan's living-doc log and evidence manifest current at every stopping point.

## Engineering principles

**Locality of behavior.** A unit's behavior must be evident from reading that unit. Co-locate its contracts, orchestration, error handling, and behavioral tests. Avoid hidden global state and action at a distance.

**Modularity by feature.** Organize new work by vertical feature slice rather than by technical layer. The proposed `forkpoints`, `witnesses`, `controls`, `releases`, `demo`, and `research` folders are feature boundaries. Wave 1 may remap them to repository-native equivalents, but must preserve collision-free ownership.

**File size.** Target fewer than 500 lines of code per file. Split only along a real responsibility, lifecycle, or dependency seam. Do not create arbitrary `helpers` buckets.

**Tests verify functionality.** Tests assert observable outcomes through public behavior. They must fail when behavior breaks and survive internal refactors. Do not add change-detector tests, tautological schema restatements, or mocks of the unit being tested.

## Execution rules

1. Read the selected plan, its sibling `.REFERENCE.md`, the applicable specs, `GLOSSARY.md`, and the accepted repo map.
2. Confirm the plan owns every path it will write. Do not edit a sibling plan's paths.
3. Respect STOP conditions. Record a STOP in the evidence manifest; do not route around missing state fidelity, grader identity, security isolation, or real-system access.
4. Prefer the smallest behavior-complete change. No speculative abstraction, unused adapter, empty scaffold, or broad rewrite.
5. Use real acceptance fixtures. A fake HUD trace, fake grader, or fake snapshot cannot prove the core loop. Mocks are allowed only at narrow failure boundaries after a real integration path exists.
6. Keep discovery stochastic and proof deterministic. A rewarded branch is not a Witness until classification, deduplication, provenance, and replay gates pass.
7. Keep untrusted branch code isolated with minimum secrets and network access.
8. Run the plan's exact Done-when commands. Update `docs/plans/evidence/<NNN>/MANIFEST.json` with command, result, artifact path, and observed behavior.
9. Append decisions, surprises, progress, and outcomes to the plan's Living-doc log. Never rewrite history.
10. Do not call work complete based on code inspection. Completion is evidence-based.

## Merge discipline

Parallel plans run in isolated worktrees. Do not start a later wave until `docs/plans/000-index.md` says its merge gate is satisfied. Before merging a wave, run ownership, graph, section, traceability, and evidence validation. Resolve ownership changes by updating the affected plan frontmatter and repo map before source edits.

## Claims and reporting

Keep unmeasured values as `TBD`. Label prior-run demo artifacts honestly. Preserve the distinction between HUD reward and reward-hacking classification. Do not describe the search as full MCTS, complete exploit coverage, or general-purpose hardening.
