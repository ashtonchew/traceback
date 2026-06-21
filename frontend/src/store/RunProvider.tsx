import { createContext, useCallback, useContext, useEffect, useMemo, useReducer, type ReactNode } from 'react'
import { api } from '../api'
import type {
  BranchRun,
  ForkPoint,
  GateMemberResult,
  LegitimateControl,
  Patch,
  ProofSet,
  ReleaseProof,
  RunPhase,
} from '../domain/types'

interface RunState {
  phase: RunPhase
  loading: boolean
  forkPoint?: ForkPoint
  branches: BranchRun[]
  controls: LegitimateControl[]
  proofSet?: ProofSet
  selectedBranchId?: string
  fixIteration: number
  patch?: Patch
  gate: { status: 'idle' | 'running' | 'done'; results: GateMemberResult[] }
  releaseProof?: ReleaseProof
}

type Action =
  | { type: 'LOADED'; forkPoint: ForkPoint; controls: LegitimateControl[]; proofSet: ProofSet; branches: BranchRun[] }
  | { type: 'PHASE'; phase: RunPhase }
  | { type: 'RESET_BRANCHES' }
  | { type: 'ADD_BRANCH'; branch: BranchRun }
  | { type: 'SELECT'; id?: string }
  | { type: 'PROOFSET'; proofSet: ProofSet }
  | { type: 'PATCH'; patch: Patch; iteration: number }
  | { type: 'GATE_START' }
  | { type: 'GATE_MEMBER'; result: GateMemberResult }
  | { type: 'GATE_DONE'; releaseProof: ReleaseProof }
  | { type: 'RELEASEPROOF'; releaseProof: ReleaseProof }

const initial: RunState = {
  phase: 'forked',
  loading: true,
  branches: [],
  controls: [],
  fixIteration: 1,
  gate: { status: 'idle', results: [] },
}

function reducer(state: RunState, action: Action): RunState {
  switch (action.type) {
    case 'LOADED':
      return {
        ...state,
        loading: false,
        forkPoint: action.forkPoint,
        controls: action.controls,
        proofSet: action.proofSet,
        branches: action.branches,
        phase: action.branches.length ? 'discovered' : 'forked',
        selectedBranchId: state.selectedBranchId ?? 'layeredFallback',
      }
    case 'PHASE':
      return { ...state, phase: action.phase }
    case 'RESET_BRANCHES':
      return { ...state, branches: [], phase: 'discovering' }
    case 'ADD_BRANCH':
      return { ...state, branches: [...state.branches, action.branch] }
    case 'SELECT':
      return { ...state, selectedBranchId: action.id }
    case 'PROOFSET':
      return { ...state, proofSet: action.proofSet }
    case 'PATCH':
      return { ...state, patch: action.patch, fixIteration: action.iteration, phase: 'fixing' }
    case 'GATE_START':
      return { ...state, gate: { status: 'running', results: [] }, phase: 'gating' }
    case 'GATE_MEMBER':
      return { ...state, gate: { status: 'running', results: [...state.gate.results, action.result] } }
    case 'GATE_DONE':
      return {
        ...state,
        gate: { status: 'done', results: action.releaseProof.results },
        releaseProof: action.releaseProof,
        phase: action.releaseProof.gateStatus === 'pass' ? 'released' : 'gate_failed',
      }
    case 'RELEASEPROOF':
      return { ...state, releaseProof: action.releaseProof, phase: 'released' }
    default:
      return state
  }
}

interface RunActions {
  startDiscovery: () => Promise<void>
  select: (id?: string) => void
  selectedBranch: () => BranchRun | undefined
  addToProofSet: (branchId: string) => Promise<void>
  removeFromProofSet: (branchId: string) => Promise<void>
  loadPatch: (iteration?: number) => Promise<Patch>
  runGate: () => Promise<ReleaseProof | undefined>
  returnToFixer: () => Promise<void>
  publish: () => Promise<void>
  replayWitness: (branchId: string) => Promise<void>
}

const RunContext = createContext<(RunState & RunActions) | null>(null)

export function RunProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initial)

  useEffect(() => {
    let alive = true
    Promise.all([api.getForkPoint(), api.getControls(), api.getProofSet(), api.getBranches()]).then(
      ([forkPoint, controls, proofSet, branches]) => {
        if (alive) dispatch({ type: 'LOADED', forkPoint, controls, proofSet, branches })
      },
    )
    return () => {
      alive = false
    }
  }, [])

  const startDiscovery = useCallback(async () => {
    dispatch({ type: 'RESET_BRANCHES' })
    await api.runDiscovery((branch) => dispatch({ type: 'ADD_BRANCH', branch }))
    dispatch({ type: 'PHASE', phase: 'discovered' })
  }, [])

  const select = useCallback((id?: string) => dispatch({ type: 'SELECT', id }), [])

  const selectedBranch = useCallback(
    () => state.branches.find((b) => b.runId === `run-${state.selectedBranchId}`),
    [state.branches, state.selectedBranchId],
  )

  const addToProofSet = useCallback(async (branchId: string) => {
    const proofSet = await api.addToProofSet(branchId)
    dispatch({ type: 'PROOFSET', proofSet })
  }, [])

  const removeFromProofSet = useCallback(async (branchId: string) => {
    const proofSet = await api.removeFromProofSet(branchId)
    dispatch({ type: 'PROOFSET', proofSet })
  }, [])

  const loadPatch = useCallback(
    async (iteration?: number) => {
      const it = iteration ?? state.fixIteration
      const patch = await api.getPatch(it)
      dispatch({ type: 'PATCH', patch, iteration: it })
      return patch
    },
    [state.fixIteration],
  )

  const runGate = useCallback(async () => {
    let patch = state.patch
    if (!patch) patch = await api.getPatch(state.fixIteration)
    dispatch({ type: 'GATE_START' })
    const releaseProof = await api.evaluateRelease(patch, (result) => dispatch({ type: 'GATE_MEMBER', result }))
    dispatch({ type: 'GATE_DONE', releaseProof })
    return releaseProof
  }, [state.patch, state.fixIteration])

  const returnToFixer = useCallback(async () => {
    const next = Math.min(state.fixIteration + 1, 3)
    const patch = await api.getPatch(next)
    dispatch({ type: 'PATCH', patch, iteration: next })
  }, [state.fixIteration])

  const publish = useCallback(async () => {
    const releaseProof = await api.publishRelease('rpf-final')
    dispatch({ type: 'RELEASEPROOF', releaseProof })
  }, [])

  const replayWitness = useCallback(async (branchId: string) => {
    await api.replayWitness(branchId)
  }, [])

  const value = useMemo(
    () => ({
      ...state,
      startDiscovery,
      select,
      selectedBranch,
      addToProofSet,
      removeFromProofSet,
      loadPatch,
      runGate,
      returnToFixer,
      publish,
      replayWitness,
    }),
    [state, startDiscovery, select, selectedBranch, addToProofSet, removeFromProofSet, loadPatch, runGate, returnToFixer, publish, replayWitness],
  )

  return <RunContext.Provider value={value}>{children}</RunContext.Provider>
}

export function useRun() {
  const ctx = useContext(RunContext)
  if (!ctx) throw new Error('useRun must be used within RunProvider')
  return ctx
}
