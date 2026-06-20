# Development bootstrap

Status: **planning-only**

This repository currently needs only Python to validate the checked-in planning
bundle. There is no application package, source tree, lockfile, or test runner
yet.

## Required local dependency

- Python 3.x with the standard library.
- Verified locally with `Python 3.12.13`.

The plan validators use standard-library modules only, including `argparse`,
`json`, `pathlib`, `glob`, and `subprocess`.

## First command

Run the mapped baseline from the repository root:

```sh
python docs/plans/scripts/run_mapped.py baseline
```

Expected result:

```text
RUN: baseline: cwd=. argv=['python', 'docs/plans/scripts/validate_graph.py']
PASS: 7 plans, 7 dependencies, waves [1, 2, 3, 4, 5], acyclic
```

## Useful planning checks

```sh
python docs/plans/scripts/validate_graph.py
python docs/plans/scripts/validate_sections.py
python docs/plans/scripts/validate_ownership.py
python docs/plans/scripts/validate_traceability.py
python docs/plans/scripts/validate_evidence.py
python docs/plans/scripts/validate_file_sizes.py --plan 001
```

## Do not install yet

Do not add `uv`, `pytest`, Node, Modal, HUD, or harden-v0 dependencies until a
plan owns the path and a real repository surface requires the dependency. The
current minimal development contract is a verified repo map, not a guessed app
stack.

## Before source work

Plans 002-007 must wait until `STATUS.json` is `accepted`. The current state is
`blocked` because the real HUD trace, MongoDB task, adapters, grader,
harden-v0 integration, artifact store, and sandbox controls are not checked in
or linked by repository configuration.
