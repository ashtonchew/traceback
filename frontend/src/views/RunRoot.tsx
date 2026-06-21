import { useNavigate } from 'react-router-dom'
import { RunHeader } from '../components/RunHeader'
import { RunSummaryFooter } from '../components/RunSummaryFooter'
import { RunCanvas } from '../components/RunCanvas'
import { ForkPointPanel } from '../components/panels'
import { MiniThumb } from '../components/MiniThumb'
import { rootGraph } from '../data/graphs'
import { useRun } from '../store/RunProvider'

export function RunRoot() {
  const navigate = useNavigate()
  const run = useRun()
  const onStart = () => {
    run.startDiscovery()
    navigate('/witness')
  }
  return (
    <>
      <RunHeader title="ForkProof Run" version="v3.2" subtitle="mongodb-sales-aggregation-engine" primaryLabel="Resume run" />
      <div className="flex min-h-0 flex-1">
        <div className="min-w-0 flex-1">
          <RunCanvas nodes={rootGraph.nodes} edges={rootGraph.edges} fitPadding={0.35} />
        </div>
        <ForkPointPanel onStart={onStart} />
      </div>
      <RunSummaryFooter
        stats={[
          { label: 'Witness', value: 0, tone: 'green' },
          { label: 'Promising', value: 0, tone: 'warn' },
          { label: 'Controls', value: 0, tone: 'gray' },
        ]}
        total={0}
        cards={[
          { icon: 'witness', label: 'Witness', value: 0 },
          { icon: 'proofset', label: 'ProofSet', value: 0 },
          { icon: 'releaseproof', label: 'ReleaseProof', value: 0 },
        ]}
        minimap={<MiniThumb variant="row" />}
      />
    </>
  )
}
