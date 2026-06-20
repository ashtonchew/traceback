# Hack2Fix2Hack implementation-plan bundle

This bundle converts the supplied Hack2Fix2Hack / ForkProof handoff into repository-executable plans without claiming access to the repository.

Start with `docs/plans/000-index.md`. Wave 1 is mandatory: it grounds real paths, interfaces, commands, and baseline behavior in `docs/plans/repo-map/`. No implementation plan may edit source code until that gate is accepted.

Planning-bundle validation:

    python docs/plans/scripts/run_all.py

Repository-connected execution additionally uses:

    python docs/plans/scripts/validate_ownership.py --repo-bound
    python docs/plans/scripts/run_mapped.py <command-name>

The proposed `src/forkproof/**` and `tests/forkproof/**` paths are collision boundaries for planning, not claims about the unseen repository. Assumption A-001 records the decision and the conditions for changing it.
