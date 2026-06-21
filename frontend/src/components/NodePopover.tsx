import { Activity, GitBranch, RefreshCw, ArrowUpRight, Camera, Sparkles, Play, Eye, PlusCircle, X } from 'lucide-react'
import type { ReactNode } from 'react'
import { Chip } from './primitives'
import type { BranchRun } from '../domain/types'

const POP_STATUS: Record<string, { label: string; class: string; chip: string }> = {
  witness: { label: 'Confirmed witness', class: 'text-accent-text', chip: 'witness' },
  promising: { label: 'Rewarded · awaiting QA', class: 'text-warn-text', chip: 'promising' },
  qa_review: { label: 'Rewarded · awaiting QA', class: 'text-warn-text', chip: 'qa-review' },
  control: { label: 'Legitimate control', class: 'text-ink-secondary-strong', chip: 'control' },
  snapshot: { label: 'Durable snapshot', class: 'text-ink-secondary-strong', chip: 'snapshot' },
}

function Row({ icon, label, children }: { icon: ReactNode; label: string; children: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5 text-sm">
      <span className="flex items-center gap-2 text-ink-secondary">
        <span className="text-ink-tertiary">{icon}</span>
        {label}
      </span>
      <span className="font-medium text-ink-primary">{children}</span>
    </div>
  )
}

export function NodePopover({
  branch,
  x,
  y,
  onClose,
  onAddToProofSet,
  onReplay,
}: {
  branch: BranchRun
  x: number
  y: number
  onClose: () => void
  onAddToProofSet?: () => void
  onReplay?: () => void
}) {
  const sd = POP_STATUS[branch.status] ?? POP_STATUS.promising
  return (
    <div
      style={{ left: x, top: y }}
      className="animate-dropdown-show absolute z-20 w-72 rounded-xl border border-hairline bg-surface-raised p-4 shadow-lg"
    >
      <div className="flex items-center gap-2">
        <span className="truncate text-sm font-semibold text-ink-primary">{branch.title}</span>
        <Chip status={sd.chip}>{branch.status === 'witness' ? 'WITNESS' : branch.status === 'control' ? 'CONTROL' : 'PROMISING'}</Chip>
        <button onClick={onClose} className="ml-auto text-ink-tertiary hover:text-ink-primary">
          <X size={15} />
        </button>
      </div>
      <div className="mt-2 divide-y divide-hairline">
        <Row icon={<Activity size={13} />} label="Status">
          <span className={sd.class}>{sd.label}</span>
        </Row>
        <Row icon={<GitBranch size={13} />} label="Cluster">
          {branch.clusterLabel ?? '—'}
        </Row>
        <Row icon={<RefreshCw size={13} />} label="Replay">
          {branch.status === 'witness' ? 'Deterministic pass' : 'Not run'}
        </Row>
        <Row icon={<ArrowUpRight size={13} />} label="Steps from fork">
          +{branch.stepsFromFork}
        </Row>
        <Row icon={<Camera size={13} />} label="Parent snapshot">
          {branch.parentSnapshot ?? 'S0'}
        </Row>
        <Row icon={<Sparkles size={13} />} label="Novelty">
          <span className="inline-flex items-center gap-1">
            {branch.novelty === 'new' ? 'new cluster' : 'existing cluster'} {branch.novelty === 'new' && <Chip status="witness">NEW</Chip>}
          </span>
        </Row>
      </div>
      <div className="mt-3 flex items-center gap-3 border-t border-hairline pt-3 text-sm">
        <button onClick={onReplay} className="inline-flex items-center gap-1.5 font-medium text-ink-primary hover:text-accent-text">
          <Play size={13} /> Replay
        </button>
        <button className="inline-flex items-center gap-1.5 font-medium text-ink-secondary hover:text-ink-primary">
          <Eye size={13} /> View state
        </button>
        <button onClick={onAddToProofSet} className="ml-auto inline-flex items-center gap-1.5 font-medium text-accent-text hover:underline">
          <PlusCircle size={13} /> Add to ProofSet
        </button>
      </div>
    </div>
  )
}
