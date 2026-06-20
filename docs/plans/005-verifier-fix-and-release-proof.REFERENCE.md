# Plan 005 reference — patch loop and proof matrix

## Fixer adapter boundary

The adapter should expose only repository-needed inputs/outputs around the verified harden-v0 integration:

- Witness/trajectory evidence in its accepted format,
- exact grader source/version,
- legitimate controls or legitimate marker handling,
- fixer configuration,
- patch/diff output,
- replay/autopatch result,
- logs and run identity.

Do not normalize away harden-v0 behavior merely to fit a new abstraction. Keep adapter code local to releases unless another shipped feature genuinely consumes it.

## ProofSet membership

Core membership is closed over all sealed core Witnesses available at gate start and at least three sealed controls. Record selection query/time so a late-arriving Witness cannot be silently ignored. Optional family variants are labelled as stochastic/derived and do not replace exact Witness replay.

## Gate matrix

| Case | v1 expected | v2 expected | Failure response |
|---|---|---|---|
| Exact Witness | success | failure | Survives: reject and widen patch |
| Legitimate control | success | success | Breaks: reject and relax patch |
| Family variant | recorded baseline | preferably failure | Report separately unless promoted/sealed |
| Corrupt control negative | failure | failure | Harness sanity check |

The repository's reward representation is authoritative. Store raw outputs and normalized semantic status.

## Grader identity check

Before every case:

1. Resolve intended environment/grader version.
2. Load the runtime path used by evaluation.
3. Compute/read the canonical digest.
4. Compare to the ReleaseProof candidate.
5. Abort on mismatch.

Do not accept a source-file diff as proof that deployed/runtime code changed.

## Iteration limits

Use the existing fixer loop's configured bounds. Record each candidate patch and rejection reason. Do not keep broadening a patch indefinitely; a bounded failure is an honest result. A patch that cannot preserve controls does not ship.

## ReleaseProof evidence

At minimum link:

- ProofSet digest,
- v1/v2 environment and grader identities,
- fixer run and patch,
- exact per-case trace/result,
- normalized gate decision,
- killed/preserved counts,
- rejection history,
- release candidate artifact,
- timestamps and content digest.

## Behavioral tests

Include:

- all-pass gate,
- one surviving Witness rejects,
- one broken control rejects,
- missing case rejects,
- mixed grader digest rejects,
- immutable artifact round-trip,
- adapter integration against real harden-v0 path.
