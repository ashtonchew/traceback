# Repository interface bindings

Status: **blocked**

This repository currently contains the ForkProof planning bundle, dependency
bootstrap, and the source handoff. SDK/source dependencies are installed or
fetchable, but product integration surfaces are still missing. Each missing
operation below is intentionally recorded as blocked rather than replaced with a
guessed adapter.

| Semantic operation | Repository path | Symbol/entrypoint | Exercise/evidence | Status |
|---|---|---|---|---|
| HUD trace retrieval/export | SDK installed through `hud-python[modal]==0.6.4`; adapter not present | Not present | `uv run hud --help` works, but no repository trace retrieval/export wrapper exists. | blocked |
| HUD step/file evidence | Not present | Not present | No trace, file-evidence export, or HUD wrapper is checked in. | blocked |
| HUD Reward Hacking QA | Not present | Not present | No QA retrieval path or stored QA result is checked in. | blocked |
| HUD taskset/analytics | Not present | Not present | No taskset runner, analytics export, or HUD publication command is checked in. | blocked |
| HUD environment version publish/compare | Not present | Not present | No environment versioning or publishing boundary is checked in. | blocked |
| Modal sandbox create | SDK installed through `modal==1.5.0`; adapter not present | Not present | `uv run python -m modal --version` reports 1.5.0, but no sandbox wrapper exists. | blocked |
| Modal core snapshot capture/restore | SDK installed; adapter not present | Not present | No Directory/Filesystem snapshot wrapper or capability probe is checked in. | blocked |
| Modal Memory/VM capability probe | Not present | Not present | No Alpha capability probe is checked in; do not assume access. | blocked |
| Agent/model gateway | Not present | Not present | No branch runner, model gateway, seed, or sampling configuration code is checked in. | blocked |
| Grader/verifier run and digest | Not present | Not present | No grader source, executable verifier, or digest mechanism is checked in. | blocked |
| harden-v0 fixer | `.external/harden-v0` via `scripts/bootstrap_external_deps.sh` | `python -m harden` | Pinned revision `b9dd28c...`; `env PYTHONPATH=.external/harden-v0 uv run python -m harden --help` exits 0. No repository adapter exists yet. | partial |
| harden-v0 replay/dedup/legitimate handling | `.external/harden-v0` via `scripts/bootstrap_external_deps.sh` | `python -m harden`, `dedup_hacks.py` | Help output exposes `--replay-enabled`, `.legitimate` behavior, and pool flags. No adapter or task binding exists yet. | partial |
| Persistence/artifact store | Not present | Not present | No database, object store, manifest store, or artifact retention implementation is checked in. | blocked |
| MongoDB task materialization | `.external/terminal-wrench/tasks/mongodb-sales-aggregation-engine` via `scripts/bootstrap_external_deps.sh` | Dataset task directory | Pinned revision `d8a2961...`; task source exists for `claude-opus-4.6` and `gemini-3.1-pro`. No repository-native fixture materialization command exists yet. | partial |
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
| Dependency sync | `pyproject.toml`, `uv.lock` | CLI | `uv sync --all-extras --all-groups` exits 0. | verified |
| External dependency checkout | `scripts/bootstrap_external_deps.sh` | CLI | Fetches harden-v0 and a sparse Terminal Wrench MongoDB-task checkout pinned under `.external/`. | verified |
| Local environment config | `.env.example`, root `.env` | dotenv-compatible env file | `.env.example` is committed; `.env` is ignored and loaded by `scripts/bootstrap_external_deps.sh` when present. | verified |

## Required next inputs

Gate 1 can become accepted only after the repository gains real, exercisable
product surfaces for the blocked rows above. Dependency installation and source
checkouts are necessary, but not sufficient: each adapter needs a checked-in
path plus command/output evidence.

These inputs arrive as structured evidence packets. `EVIDENCE-PACKETS.md`
defines the runtime packet (Ashton) and the proof/control packet (Katherine),
maps every packet field to the prerequisite, interface row, and command it
unblocks, and states the integration procedure Akhil follows to flip each
`STATUS.json` prerequisite. The Akhil-owned HUD-facing inputs are listed there
too.
