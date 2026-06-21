import type { ForkProofApi } from '../ForkProofApi'
import type {
  BranchRun,
  ExploitWitness,
  ForkPoint,
  GateMemberResult,
  LegitimateControl,
  Patch,
  ProofSet,
  ReleaseProof,
} from '../../domain/types'
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

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms))
}

function clone<T>(v: T): T {
  return JSON.parse(JSON.stringify(v))
}

/**
 * In-memory ForkProof backend. Holds mutable run state (proofset, fix
 * iteration, releaseproof) for the session. Swap for an HTTP-backed
 * implementation of the same interface to talk to the real services.
 */
export class MockForkProofApi implements ForkProofApi {
  private proofSet: ProofSet = clone(initialProofSet)

  async getForkPoint(): Promise<ForkPoint> {
    await delay(120)
    return clone(forkPoint)
  }

  async getControls(): Promise<LegitimateControl[]> {
    await delay(80)
    return clone(controls)
  }

  async getBranches(): Promise<BranchRun[]> {
    await delay(80)
    return clone(branches)
  }

  async runDiscovery(onBranch?: (b: BranchRun) => void): Promise<BranchRun[]> {
    const out: BranchRun[] = []
    // stream parents before children so the tree grows top-down
    const ordered = [...branches].sort((a, b) => (a.layout?.y ?? 0) - (b.layout?.y ?? 0))
    for (const b of ordered) {
      await delay(260)
      const rec = clone(b)
      out.push(rec)
      onBranch?.(rec)
    }
    return out
  }

  async getWitnesses(): Promise<ExploitWitness[]> {
    await delay(80)
    return branches
      .filter((b) => b.status === 'witness')
      .map((b) => ({
        schemaVersion: b.schemaVersion,
        witnessId: b.runId.replace('run-', 'wit-'),
        sourceBranchId: b.branchId,
        preAttackSnapshotRef: `${b.parentSnapshot ?? 'S0'}-pre`,
        durableSnapshotMode: b.snapshotMode,
        exploitTarget: 'verifier grader',
        exploitMechanism: b.clusterLabel ?? 'reward hacking',
        clusterId: b.clusterId ?? 'unknown',
        replayEntrypoint: `replay/${b.branchId}.json`,
        replayChecks: 'Deterministic pass',
        contentDigest: `${b.runId}-digest`,
        environmentVersion: b.environmentVersion,
        graderDigest: b.graderDigest,
        createdAt: b.completedAt ?? b.startedAt,
      }))
  }

  async getProofSet(): Promise<ProofSet> {
    await delay(60)
    return clone(this.proofSet)
  }

  async addToProofSet(witnessId: string): Promise<ProofSet> {
    await delay(120)
    if (!this.proofSet.exploitWitnessIds.includes(witnessId)) {
      this.proofSet = { ...this.proofSet, exploitWitnessIds: [...this.proofSet.exploitWitnessIds, witnessId] }
    }
    return clone(this.proofSet)
  }

  async removeFromProofSet(witnessId: string): Promise<ProofSet> {
    await delay(120)
    this.proofSet = {
      ...this.proofSet,
      exploitWitnessIds: this.proofSet.exploitWitnessIds.filter((id) => id !== witnessId),
    }
    return clone(this.proofSet)
  }

  async getPatch(iteration: number): Promise<Patch> {
    await delay(150)
    const p = patches[iteration] ?? patches[3]
    return clone(p)
  }

  async evaluateRelease(patch: Patch, onMember?: (r: GateMemberResult) => void): Promise<ReleaseProof> {
    const surviving = survivingWitnessByIteration[patch.iteration] ?? []
    const broken = brokenControlByIteration[patch.iteration] ?? []

    const witnessMembers: GateMemberResult[] = this.proofSet.exploitWitnessIds.map((id) => {
      const b = branches.find((x) => x.runId === `run-${id}`)
      const survived = surviving.includes(id)
      return {
        memberId: id,
        kind: 'witness' as const,
        name: b?.title ?? id,
        v1: 1,
        v2: survived ? 1 : 0,
        reward: survived ? 1.2 : (b?.reward ?? 1.0),
        status: 'pending' as const,
      }
    })

    const controlMembers: GateMemberResult[] = this.proofSet.legitimateControlIds.map((id) => {
      const c = controls.find((x) => x.controlId === id)
      const isBroken = broken.includes(id)
      return {
        memberId: id,
        kind: 'control' as const,
        name: c?.title ?? id,
        v1: 1,
        v2: isBroken ? 0 : 1,
        reward: isBroken ? 0 : 1,
        status: 'pending' as const,
      }
    })

    const results = [...witnessMembers, ...controlMembers]

    // stream each member as its deterministic replay "completes"
    for (const m of results) {
      await delay(320)
      m.status =
        m.kind === 'witness' ? (m.v2 === 0 ? 'killed' : 'survived') : m.v2 === 1 ? 'preserved' : 'broken'
      onMember?.({ ...m })
    }

    const witnessesKilled: [number, number] = [witnessMembers.filter((m) => m.v2 === 0).length, witnessMembers.length]
    const controlsPreserved: [number, number] = [controlMembers.filter((m) => m.v2 === 1).length, controlMembers.length]
    const allKilled = witnessesKilled[0] === witnessesKilled[1]
    const allPreserved = controlsPreserved[0] === controlsPreserved[1]
    const pass = allKilled && allPreserved

    return {
      schemaVersion: '1.0.0',
      releaseProofId: `rpf-${patch.iteration}`,
      proofSetId: this.proofSet.proofSetId,
      environmentV1: this.proofSet.environmentV1,
      graderV1Digest: this.proofSet.graderV1Digest,
      environmentV2: this.proofSet.environmentV1,
      graderV2Digest: GRADER_V2,
      patchRef: patch.patchRef,
      results,
      witnessesKilled,
      controlsPreserved,
      gateStatus: pass ? 'pass' : 'fail',
      failureKind: pass ? undefined : !allKilled ? 'witness_survived' : 'control_regression',
      reward: pass ? 1.0 : 0.0,
      similarity: pass ? 0.92 : 0.28,
      createdAt: new Date().toISOString(),
      status: pass ? 'evaluating' : 'failed',
    }
  }

  async publishRelease(releaseProofId: string): Promise<ReleaseProof> {
    await delay(200)
    // Recompute a passing proof and stamp it committed.
    const proof = await this.evaluateRelease(await this.getPatch(3))
    return {
      ...proof,
      releaseProofId,
      status: 'committed',
      gateStatus: 'pass',
      commitId: 'rpf-20250508-102431',
      publishedEnvironmentRef: `${this.proofSet.environmentV1} v2`,
    }
  }

  async replayWitness(witnessId: string): Promise<{ ok: boolean; detail: string }> {
    await delay(300)
    return { ok: true, detail: `Witness ${witnessId} replayed deterministically (v1).` }
  }
}
