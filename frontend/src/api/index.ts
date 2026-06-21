import type { ForkProofApi } from './ForkProofApi'
import { apiMode } from './config'
import { HttpForkProofApi } from './http/HttpForkProofApi'
import { MockForkProofApi } from './mock/MockForkProofApi'

/**
 * Single app-wide API instance, selected by `VITE_FORKPROOF_API` (see
 * `./config`). Default `http` reads the real build-time data exported from repo
 * artifacts; `mock` uses the in-memory demo dataset. Both implement the same
 * `ForkProofApi` over the shared `DatasetForkProofApi` engine, so the store and
 * views are identical in either mode.
 */
export const api: ForkProofApi = apiMode === 'mock' ? new MockForkProofApi() : new HttpForkProofApi()

export type { ForkProofApi }
