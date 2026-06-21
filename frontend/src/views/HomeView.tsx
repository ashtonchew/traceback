import { useNavigate } from 'react-router-dom'
import { RunCanvas } from '../components/RunCanvas'
import { Button } from '../components/primitives'
import { rootGraph } from '../data/graphs'
import { FileCheck2, GitFork, Play, ShieldCheck } from '../components/icons'

export function HomeView() {
  const navigate = useNavigate()

  return (
    <div className="relative min-h-0 flex-1 overflow-hidden bg-background">
      <div className="absolute inset-0 opacity-35">
        <RunCanvas nodes={rootGraph.nodes} edges={rootGraph.edges} fitPadding={0.22} fitMaxZoom={0.72} showZoomBar={false} interactive={false} />
      </div>
      <div className="relative z-10 flex h-full items-center justify-center px-8">
        <section className="max-w-2xl text-center">
          <div className="mb-4 inline-flex items-center gap-2 rounded-lg border border-hairline bg-surface-raised px-3 py-1.5 text-xs font-medium text-ink-secondary shadow-sm">
            <ShieldCheck size={14} className="text-accent-text" />
            Real execution evidence, replayed into a release proof
          </div>
          <h1 className="font-display text-5xl leading-tight tracking-tight text-ink-primary">Traceback turns reward-hacking traces into release evidence.</h1>
          <p className="mx-auto mt-5 max-w-xl text-base leading-relaxed text-ink-secondary-strong">
            Start with the suspicious HUD trace, open its QA ForkPoint, inspect candidate branches, then seal a ProofSet that must kill the exploit witness while preserving legitimate controls. The visible IDs, digests, replay results, and ReleaseProof are sourced from committed artifacts rather than placeholder demo state.
          </p>
          <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
            <Button variant="primary" size="md" icon={<Play size={15} />} onClick={() => navigate('/runs')}>
              Open runs
            </Button>
            <Button variant="secondary" size="md" icon={<GitFork size={15} />} onClick={() => navigate('/witness?focus=confirmed')}>
              View witness
            </Button>
            <Button variant="secondary" size="md" icon={<FileCheck2 size={15} />} onClick={() => navigate('/proofset')}>
              Check proofset
            </Button>
          </div>
        </section>
      </div>
    </div>
  )
}
