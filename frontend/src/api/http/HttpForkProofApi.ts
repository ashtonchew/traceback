import { apiBase } from '../config'
import { DatasetForkProofApi, type ReleaseBlock, type ReplayEvidence, type RunDataset } from '../dataset'
import type { BranchRun, ExploitWitness, ForkPoint, LegitimateControl, Patch, ProofSet } from '../../domain/types'

/** Shape of the exported `release.json` (patches + gate-outcome maps + verdict). */
interface ReleaseBundle {
  graderV2Digest: string
  patches: Record<string, Patch>
  survivingWitnessByIteration: Record<string, string[]>
  brokenControlByIteration: Record<string, string[]>
  release?: ReleaseBlock
}

async function fetchJson<T>(route: string): Promise<T> {
  const res = await fetch(`${apiBase}/${route}.json`, { headers: { accept: 'application/json' } })
  if (!res.ok) throw new Error(`Traceback API: GET ${route}.json -> ${res.status} ${res.statusText}`)
  return (await res.json()) as T
}

/**
 * Load the real {@link RunDataset} from the static JSON exported by
 * `forkproof.api.export`. These are plain files (no server), so the real-data
 * mode deploys as a static site. Records are mapped from committed repo
 * artifacts; see `src/forkproof/api/mapping.py` for what is real vs. TBD.
 */
async function loadDataset(): Promise<RunDataset> {
  const [forkPoint, controls, branches, witnessOverlay, initialProofSet, release, replay] = await Promise.all([
    fetchJson<ForkPoint>('forkpoint'),
    fetchJson<LegitimateControl[]>('controls'),
    fetchJson<BranchRun[]>('branches'),
    fetchJson<Record<string, Partial<ExploitWitness>>>('witnesses'),
    fetchJson<ProofSet>('proofset'),
    fetchJson<ReleaseBundle>('release'),
    fetchJson<ReplayEvidence>('replay'),
  ])
  return {
    forkPoint,
    controls,
    branches,
    witnessOverlay,
    initialProofSet,
    // JSON object keys are strings; numeric indexing coerces, so this is safe.
    patches: release.patches as unknown as RunDataset['patches'],
    survivingWitnessByIteration: release.survivingWitnessByIteration as unknown as RunDataset['survivingWitnessByIteration'],
    brokenControlByIteration: release.brokenControlByIteration as unknown as RunDataset['brokenControlByIteration'],
    graderV2: release.graderV2Digest,
    release: release.release,
    replay,
  }
}

/** Real Traceback backend: the {@link DatasetForkProofApi} engine over fetched static JSON. */
export class HttpForkProofApi extends DatasetForkProofApi {
  constructor() {
    super(loadDataset)
  }
}
