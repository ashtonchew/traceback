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
