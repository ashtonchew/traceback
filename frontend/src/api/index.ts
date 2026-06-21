import type { ForkProofApi } from './ForkProofApi'
import { MockForkProofApi } from './mock/MockForkProofApi'

/**
 * Single app-wide API instance. Today this is the in-memory mock; to integrate
 * a real backend, implement `ForkProofApi` (e.g. `HttpForkProofApi`) and swap
 * the line below — no store or view changes required.
 */
export const api: ForkProofApi = new MockForkProofApi()

export type { ForkProofApi }
