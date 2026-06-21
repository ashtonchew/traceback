import { useNavigate } from 'react-router-dom'
import { RunHeader } from '../components/RunHeader'
import { RunSummaryFooter } from '../components/RunSummaryFooter'
import { RunCanvas } from '../components/RunCanvas'
import { MiniThumb } from '../components/MiniThumb'
import { forkproofTree } from '../data/graphs'

export function RunTree() {
  const navigate = useNavigate()
  return (
    <>
      <RunHeader title="ForkProof Run" version="v3.2" subtitle="mongodb-sales-aggregation-engine" primaryLabel="Resume run" />
      <div className="min-h-0 flex-1">
        <RunCanvas nodes={forkproofTree.nodes} edges={forkproofTree.edges} onNodeClick={() => navigate('/witness')} fitPadding={0.15} />
      </div>
      <RunSummaryFooter
        stats={[
          { label: 'Witness', value: 2, tone: 'green' },
          { label: 'Promising', value: 2, tone: 'warn' },
          { label: 'QA Review', value: 1, tone: 'warn' },
          { label: 'Controls', value: 1, tone: 'gray' },
          { label: 'Dead End', value: 1, tone: 'red' },
        ]}
        total={8}
        cards={[
          { icon: 'witness', label: 'Witness', value: 2 },
          { icon: 'proofset', label: 'ProofSet', value: 4 },
          { icon: 'releaseproof', label: 'ReleaseProof', value: 1 },
          { icon: 'artifacts', label: 'View all artifacts' },
        ]}
        minimap={<MiniThumb variant="tree" />}
      />
    </>
  )
}
