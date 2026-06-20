# Plan 004 reference — control diversity and freezing

## Real task provenance

Record the repository/dataset mechanism, exact upstream task id, revision or digest, retrieval/preparation command, license/reference, dependency lock, environment v1, and grader digest. A lightweight manifest may point to large upstream content rather than duplicate it.

## Legitimate generation rules

A legitimate control solves the stated task rather than manipulating the grader/test framework. Generation may use:

- repository reference hints,
- a verified solver configuration,
- existing golden solutions when license permits,
- independent legitimate model runs with attack instructions excluded.

Preserve prompts/configuration or source provenance as allowed by policy. Never use the recorded exploit as a “hint” for controls.

## Diversity rubric

At least one substantive dimension must differ:

- algorithm/aggregation construction,
- module organization or API usage,
- error/edge-case handling,
- files changed for a legitimate reason,
- solver trajectory and implementation decisions,
- use of equivalent supported library mechanisms.

All controls must satisfy the same public task contract. Cosmetic edits do not create diversity.

## Freeze process

For each selected control:

1. Start from a clean pinned task.
2. Apply only the legitimate solution artifact.
3. Run the authoritative grader.
4. Repeat in three clean environments.
5. Save trace/result references.
6. Canonicalize and hash the solution.
7. Seal the control manifest.
8. Make later corrections by superseding, not mutation.

## Required negative behavior

Corrupt or remove one load-bearing part of a copied candidate and show the grader fails. This proves the harness is testing task behavior rather than accepting every fixture.

## Patch-era use

Plan 005 consumes sealed control ids. It may not update their solution contents or expected reward. When a control fails under v2, the release is rejected and the patch returns to the fixer; the control is not weakened to fit the patch.
