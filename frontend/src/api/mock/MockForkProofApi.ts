import { DatasetForkProofApi, type RunDataset } from '../dataset'
import {
  branches,
  brokenControlByIteration,
  controls,
  forkPoint,
  initialProofSet,
  patches,
  survivingWitnessByIteration,
} from './fixtures'

const GRADER_V2 = 'd71be0c9f3a24e8b6c0a1d2e3f405162738495a0b1c2d3e4f5061728394a5b6c'

/** The in-memory demo dataset (fabricated fixtures). */
const mockDataset: RunDataset = {
  forkPoint,
  controls,
  branches,
  initialProofSet,
  patches,
  survivingWitnessByIteration,
  brokenControlByIteration,
  graderV2: GRADER_V2,
}

/**
 * In-memory Traceback backend. Holds mutable run state (proofset, fix
 * iteration, releaseproof) for the session. The real backend
 * (`HttpForkProofApi`) reuses the same {@link DatasetForkProofApi} engine over a
 * dataset fetched from static JSON, so both modes behave identically.
 */
export class MockForkProofApi extends DatasetForkProofApi {
  constructor() {
    super(() => Promise.resolve(mockDataset))
  }
}
