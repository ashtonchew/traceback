import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { NodeMouseHandler } from '@xyflow/react'
import { RunHeader } from '../components/RunHeader'
import { RunSummaryFooter } from '../components/RunSummaryFooter'
import { RunCanvas } from '../components/RunCanvas'
import { BranchPanel, ProofSetPanel } from '../components/panels'
import { NodePopover } from '../components/NodePopover'
import { MiniThumb } from '../components/MiniThumb'
import { buildRunGraph } from '../data/buildGraph'
import { variantNames } from '../api/mock/fixtures'
import { useRun } from '../store/RunProvider'

export function RunWitness({ mode = 'branch' }: { mode?: 'branch' | 'proofset' }) {
  const navigate = useNavigate()
  const run = useRun()
  const [pop, setPop] = useState<{ id: string; x: number; y: number } | null>(null)

  const { nodes, edges } = useMemo(
    () => buildRunGraph(run.forkPoint, run.branches, run.selectedBranchId),
    [run.forkPoint, run.branches, run.selectedBranchId],
  )

  const selected = run.selectedBranch()
  const popBranch = pop ? run.branches.find((b) => b.runId === `run-${pop.id}`) : undefined
  const inProofSet = selected ? run.proofSet?.exploitWitnessIds.includes(run.selectedBranchId ?? '') : false

  const witnessCount = run.branches.filter((b) => b.status === 'witness').length
  const promisingCount = run.branches.filter((b) => b.status === 'promising' || b.status === 'qa_review').length
  const controlCount = run.branches.filter((b) => b.status === 'control' || b.status === 'control_pass').length

  const onNodeClick: NodeMouseHandler = (e, node) => {
    if (node.id === 'fork') return
    run.select(node.id)
    const branch = run.branches.find((b) => b.runId === `run-${node.id}`)
    if (branch && node.type === 'branch') setPop({ id: node.id, x: e.clientX - 120, y: e.clientY + 12 })
    else setPop(null)
  }

  return (
    <>
      <RunHeader title="Exploit Witness" version="v3.2" primaryLabel="Resume run" />
      <div className="flex min-h-0 flex-1">
        <div className="relative min-w-0 flex-1">
          <RunCanvas nodes={nodes} edges={edges} onNodeClick={onNodeClick} fitPadding={0.18} />
          {pop && popBranch && (
            <div className="pointer-events-none fixed inset-0 z-20">
              <div className="pointer-events-auto">
                <NodePopover
                  branch={popBranch}
                  x={pop.x}
                  y={pop.y}
                  onClose={() => setPop(null)}
                  onReplay={() => run.replayWitness(pop.id)}
                  onAddToProofSet={() => {
                    run.addToProofSet(pop.id)
                    setPop(null)
                    navigate('/proofset')
                  }}
                />
              </div>
            </div>
          )}
        </div>
        {mode === 'proofset' && run.proofSet ? (
          <ProofSetPanel
            proofSet={run.proofSet}
            branches={run.branches}
            controls={run.controls}
            variantNames={variantNames}
            onRun={async () => {
              await run.loadPatch(run.fixIteration)
              navigate('/patch')
            }}
            onClose={() => navigate('/witness')}
          />
        ) : selected ? (
          <BranchPanel
            branch={selected}
            inProofSet={inProofSet}
            onClose={() => run.select(undefined)}
            onAddToProofSet={() => {
              run.addToProofSet(run.selectedBranchId ?? '')
              navigate('/proofset')
            }}
            onRemoveFromProofSet={() => run.removeFromProofSet(run.selectedBranchId ?? '')}
          />
        ) : null}
      </div>
      <RunSummaryFooter
        stats={[
          { label: 'Witness', value: witnessCount, tone: 'green' },
          { label: 'Promising', value: promisingCount, tone: 'warn' },
          { label: 'Controls', value: controlCount, tone: 'gray' },
        ]}
        total={run.branches.length}
        cards={[
          { icon: 'witness', label: 'Witness', value: witnessCount },
          { icon: 'proofset', label: 'ProofSet', value: (run.proofSet?.exploitWitnessIds.length ?? 0) + (run.proofSet?.legitimateControlIds.length ?? 0) },
          { icon: 'releaseproof', label: 'ReleaseProof', value: run.releaseProof?.status === 'committed' ? 1 : 0 },
          { icon: 'artifacts', label: 'View all artifacts' },
        ]}
        minimap={<MiniThumb variant="tree" />}
      />
    </>
  )
}
