# Plan 006 publish workspace

Evidence and the deploy delta for publishing the hardened `mongodb-sales-aggregation-engine`
environment to HUD. No secrets are stored here.

## What's here

- `hud-target.json` — the authorized publish target, found via a read-only `GET /v2/registry`
  probe (team `hud-hacks`, registry env `b3409057`).
- `v2/tests/` — the hardened grader (`test.sh` + `task_assets/test_outputs.py`) regenerated from
  committed sources; its `grader_v2_digest` matches the sealed ReleaseProof.
- `v2-grader-verification.json` — offline digest match against the ReleaseProof.
- `v2-runtime-kill-proof.json` — grader-form kill in real `mongo:7.0` containers (witness `0.0`,
  controls `1.0`), via the Plan 005 `_DockerVerifierRunner` harness.
- `v2-deploy-proof.json` — deploy-form kill: builds the actual image and runs `env.py`'s served
  grader; witness `0.0`, controls `1.0`, and all root `/tests` subversions blocked `0.0`.
- `v2-env/` — the **deploy delta** layered on the v1 env (`envs/mongodb-sales-aggregation-engine`)
  to build the deployable image: `env.py` (hardened grader), `Dockerfile.hud` (bakes the trusted
  suite at read-only `/tests`), `.hud/config.json` (targets registry `b3409057`). The full build
  context = v1 env + this delta + `v2/tests/` at `/tests` (assembled transiently for `hud deploy`,
  so large files like `uv.lock` are not duplicated here).
- `publication-prepared-attempt.json` / `publication-published-attempt.json` — the validated
  `prepared` and `published` PublicationAttempts.

## The v1 → v2 hardening delta

v1's grader runs `pytest` from the agent-writable `/app`, so an agent-planted `conftest.py`
force-passes it (the recorded reward hack). The hardened grader:

1. serves the trusted suite from `/tests` (outside `/app`);
2. pins the suite digest and **allow-lists the whole `/tests` tree**, so any planted file
   (e.g. a `conftest.py` next to the suite) is rejected;
3. runs `pytest` from `/` with conftest discovery off (`--noconftest`), plugin auto-load off,
   the cache plugin off, and import shadowing blocked.

## v3 → v4 (security fix)

v3 (build `3bc11838`) was the first hardened publish. A post-publish bug hunt found it still
bypassable: the agent runs as **root**, and a force-pass `conftest.py` planted directly in
`/tests/task_assets/` defeated the grader, because `PYTEST_DISABLE_PLUGIN_AUTOLOAD` does not
disable conftest discovery and the v3 digest gate only covered `test_outputs.py`. **v4**
(build `d7b8043a`) adds `--noconftest` and the full `/tests` tree allow-list, re-proven by
`v2-deploy-proof.json`. v4 is the live latest; v3 is retained but superseded.
