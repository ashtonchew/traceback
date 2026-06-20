# Repository interface bindings

Status: **blocked**

This repository currently contains the ForkProof planning bundle and the source
handoff only. No product integration surface is checked in yet. Each missing
operation below is intentionally recorded as blocked rather than replaced with a
guessed SDK call or invented adapter.

| Semantic operation | Repository path | Symbol/entrypoint | Exercise/evidence | Status |
|---|---|---|---|---|
| HUD trace retrieval/export | Not present | Not present | `git ls-files` shows no product source or HUD adapter files. | blocked |
| HUD step/file evidence | Not present | Not present | No trace, file-evidence export, or HUD wrapper is checked in. | blocked |
| HUD Reward Hacking QA | Not present | Not present | No QA retrieval path or stored QA result is checked in. | blocked |
| HUD taskset/analytics | Not present | Not present | No taskset runner, analytics export, or HUD publication command is checked in. | blocked |
| HUD environment version publish/compare | Not present | Not present | No environment versioning or publishing boundary is checked in. | blocked |
| Modal sandbox create | Not present | Not present | No Modal dependency, configuration, or sandbox wrapper is checked in. | blocked |
| Modal core snapshot capture/restore | Not present | Not present | No Directory/Filesystem snapshot wrapper or capability probe is checked in. | blocked |
| Modal Memory/VM capability probe | Not present | Not present | No Alpha capability probe is checked in; do not assume access. | blocked |
| Agent/model gateway | Not present | Not present | No branch runner, model gateway, seed, or sampling configuration code is checked in. | blocked |
| Grader/verifier run and digest | Not present | Not present | No grader source, executable verifier, or digest mechanism is checked in. | blocked |
| harden-v0 fixer | Upstream located at `https://github.com/few-sh/harden-v0`; not linked in this repository | Not present | The public upstream exists, but no pinned fork, submodule, vendored copy, package dependency, or adapter is checked in. | blocked |
| harden-v0 replay/dedup/legitimate handling | Upstream located at `https://github.com/few-sh/harden-v0`; not linked in this repository | Not present | Upstream README exposes `--replay-enabled`, `.legitimate` handling, shared defense pool, and `dedup_hacks.py`; this repo still has no executable integration or pinned revision. | blocked |
| Persistence/artifact store | Not present | Not present | No database, object store, manifest store, or artifact retention implementation is checked in. | blocked |
| MongoDB task materialization | Not present | Not present | No `mongodb-sales-aggregation-engine` fixture, dataset, or fetch command is checked in. | blocked |
| Legitimate solver/reference hints | Not present | Not present | No solver, reference hints, or golden controls are checked in. | blocked |
| Secrets/network/resource isolation | Not present | Not present | No sandbox policy, egress control, secret scoping, or resource-limit configuration is checked in. | blocked |

## Verified local operations

| Operation | Repository path | Entry point | Exercise/evidence | Status |
|---|---|---|---|---|
| Plan graph validation | `docs/plans/scripts/validate_graph.py` | CLI | `python docs/plans/scripts/validate_graph.py` exits 0. | verified |
| Plan section validation | `docs/plans/scripts/validate_sections.py` | CLI | `python docs/plans/scripts/validate_sections.py` exits 0. | verified |
| Proposed ownership validation | `docs/plans/scripts/validate_ownership.py` | CLI | `python docs/plans/scripts/validate_ownership.py` exits 0. | verified |
| Repo-bound ownership validation | `docs/plans/scripts/validate_ownership.py` | CLI | Blocked until `STATUS.json` can become `accepted`; ownership bindings themselves are populated. | blocked |
| Mapped command runner | `docs/plans/scripts/run_mapped.py` | CLI | `python docs/plans/scripts/run_mapped.py baseline` exits 0 using `COMMANDS.json`. | verified |

## Required next inputs

Gate 1 can become accepted only after the repository gains or links real,
exercisable surfaces for the blocked rows above. Documentation, public SDK
knowledge, or an upstream URL alone is not enough under `AGENTS.md`; each row
needs a checked-in path plus command/output evidence.
