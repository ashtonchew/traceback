# Traceback UI

React + React Flow implementation of the Traceback / Exploit Witness run-graph designs.

Built with Vite + React + TypeScript + Tailwind, consuming the repo's Granola-style
design system (`../design-system/tailwind-preset.js` + `tokens.css`, self-hosted fonts).
The branch/fork graphs are rendered with [`@xyflow/react`](https://reactflow.dev) using
custom node and edge types.

## Run

```bash
cd frontend
npm install
npm run dev        # http://localhost:5174
```

`npm run build` produces a static bundle in `dist/`.

## Data source: real vs mock

The UI talks to a `ForkProofApi`. Which implementation it uses is chosen by one
env var (`frontend/.env.example`):

| `VITE_FORKPROOF_API` | Source |
| --- | --- |
| `http` (default) | Real build-time data fetched from `public/api/*.json` |
| `mock` | In-memory demo dataset (`src/api/mock/`) |

```bash
npm run dev                          # real data (default)
VITE_FORKPROOF_API=mock npm run dev  # in-memory demo
```

The real JSON is generated from committed repo artifacts (the Plan 002 ForkPoint
evidence record, the frozen Legitimate controls, the sealed Witness replay
roundtrip, and the Plan 005 ReleaseProof) by a small Python mapper. Regenerate
it whenever those artifacts change:

```bash
# from the repo root
uv run python -m forkproof.api.export   # writes frontend/public/api/*.json
```

What is real vs. placeholder is documented in `src/forkproof/api/mapping.py`:
ForkPoint identity/snapshot/grader digests, the controls + baseline runs, the
sealed Witness, replay digests, v2 grader/environment digests, and ReleaseProof
verdict are **real**. The remaining branch-tree sibling nodes preserve the UI
geometry and are marked illustrative in their notes.

## Deploy to Vercel

Static SPA — no server. In the Vercel project settings set **Root Directory** to
`frontend`; `vercel.json` already pins the build (`npm run build` → `dist`) and the
SPA rewrite so deep links like `/witness` resolve. The committed
`public/api/*.json` ships as static files, so the build needs no Python at deploy
time.

## Screens

The primary buttons walk the discover → witness → fix → gate → release narrative.
Use the dropdown next to **Resume run** (top-right) to jump directly to any screen:

| Route | Screen |
| --- | --- |
| `/` | QA ForkPoint root (horizontal) |
| `/tree` | Traceback Run — expanded branch tree |
| `/witness` | Exploit Witness tree + branch detail panel |
| `/proofset` | Exploit Witness + proof set panel |
| `/patch` | Verifier Patch v2 (code diff) |
| `/gate` | Release Gate — running |
| `/gate/witness-failed` | Release Gate — exploit survived |
| `/gate/control-failed` | Release Gate — control broken |
| `/releaseproof` | Release proof committed |

## Structure

- `src/nodes/` — React Flow custom node types (`forkpoint`, `branch`, `leaf`, `trace`,
  `qa`, `snapshot`, `stopped`) and the cluster-colored edge.
- `src/data/graphs.ts` — node/edge fixtures for the three graph scenes.
- `src/components/` — app shell (sidebar, header, footer), detail panels, primitives.
- `src/views/` — one component per screen.

All colors/spacing/type come from design-system tokens; a small set of semantic
state tokens (`warn`, soft tints) is added in `tailwind.config.js`. `bash
../design-system/lint-design.sh src` reports 0 violations.
