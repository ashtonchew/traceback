# Repository orientation

Status: **blocked**

Verified on 2026-06-20 by Codex against commit
`99c53d2b3a27a682d67bc61a026cdc2bae16eb4e`.

## Identity

- Root: `/Users/ashtonchew/projects/hack2fix2hack`
- Remote: `https://github.com/ashtonchew/hack2fix2hack.git`
- Branch inspected: `main`
- Current branch for this update: `chore/plan-001-dev-bootstrap`

## Checked-in structure

The repository is a planning bundle. It does not yet contain product source,
package configuration, a source package, a test package, a CI workflow, or a
runtime lockfile.

Tracked top-level files:

- `.gitignore`
- `AGENTS.md`
- `CLAUDE.md`
- `PLANS.md`
- `README.md`
- `docs/plans/**`
- `docs/spec/hack2fix2hack-handoff (4).html`

## Toolchain

The only executable checked-in workflow today is the Python standard-library
validator suite in `docs/plans/scripts/`.

Observed local interpreter:

- `python --version` -> `Python 3.12.13`

No third-party dependencies are required for the current planning validators.
Do not add `uv`, Node, pytest, or application dependencies until product source
or a real integration surface is checked in and mapped here.

## Agent instructions

The applicable repository instruction file is `AGENTS.md`. It requires:

- `docs/plans/ASSUMPTIONS.md` before implementation,
- one selected numbered ExecPlan under `docs/plans/`,
- evidence-backed completion,
- no source implementation until Gate 1 is accepted,
- no fabricated HUD, Modal, grader, trace, task, or harden-v0 interface claims.

## Baseline command

The smallest passing checked-in health command is:

```sh
python docs/plans/scripts/validate_graph.py
```

This is recorded as `baseline` in `COMMANDS.json`.

Additional useful local checks while the repo remains planning-only:

```sh
python docs/plans/scripts/validate_sections.py
python docs/plans/scripts/validate_ownership.py
python docs/plans/scripts/validate_traceability.py
python docs/plans/scripts/validate_evidence.py
python docs/plans/scripts/validate_file_sizes.py --plan 001
```

`python docs/plans/scripts/run_all.py` is not the baseline because the global
file-size check scans `docs/spec/hack2fix2hack-handoff (4).html`, a checked-in
1359-line source artifact. Plan-scoped file-size validation avoids treating that
source handoff as implementation code.

## Development state

The future source, test, fixture, script, and artifact boundaries are accepted
as new repository-native paths in `OWNERSHIP-BINDINGS.json` because no existing
package layout is available to remap into.

Gate 1 remains blocked. Developers should not start Plans 002-007 until the
missing real surfaces in `STATUS.json` and `INTERFACES.md` are supplied and
verified.
