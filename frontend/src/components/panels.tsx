import { clsx } from 'clsx'
import {
  X,
  GitFork,
  FileText,
  FolderClosed,
  Clock,
  Copy,
  ExternalLink,
  Eye,
  Shuffle,
  Play,
  PlusCircle,
  ShieldCheck,
  CircleSlash,
} from 'lucide-react'
import type { ReactNode } from 'react'
import { Button, Chip, Divider } from './primitives'
import type { BranchRun, LegitimateControl, ProofSet } from '../domain/types'

/* ------------------------------------------------------------------ */
/* Shell + building blocks                                             */
/* ------------------------------------------------------------------ */

export function PanelShell({
  title,
  tag,
  tagStatus,
  tabs,
  onClose,
  children,
  footer,
}: {
  title: string
  tag?: string
  tagStatus?: string
  tabs?: string[]
  onClose?: () => void
  children: ReactNode
  footer?: ReactNode
}) {
  return (
    <aside className="flex w-80 shrink-0 flex-col border-l border-hairline bg-background">
      <div className="px-5 pt-5">
        <div className="flex items-center gap-2">
          <h2 className="font-display text-xl tracking-tight text-ink-primary">{title}</h2>
          {tag && <Chip status={tagStatus}>{tag}</Chip>}
          {onClose && (
            <button onClick={onClose} className="ml-auto text-ink-tertiary hover:text-ink-primary">
              <X size={18} />
            </button>
          )}
        </div>
        {tabs && (
          <div className="mt-4 flex gap-5 border-b border-hairline">
            {tabs.map((t, i) => (
              <button
                key={t}
                className={clsx(
                  '-mb-px border-b-2 pb-2 text-sm',
                  i === 0 ? 'border-ink-primary font-medium text-ink-primary' : 'border-transparent text-ink-secondary hover:text-ink-primary',
                )}
              >
                {t}
              </button>
            ))}
          </div>
        )}
      </div>
      <div className="scrollbar-thin flex-1 overflow-y-auto px-5 py-4">{children}</div>
      {footer && <div className="border-t border-hairline px-5 py-4">{footer}</div>}
    </aside>
  )
}

export function Section({ icon, title, children }: { icon: ReactNode; title: string; children: ReactNode }) {
  return (
    <div className="py-3">
      <div className="mb-1.5 flex items-center gap-2 text-sm font-medium text-ink-primary">
        <span className="text-ink-tertiary">{icon}</span>
        {title}
      </div>
      <div className="pl-6 text-sm text-ink-secondary-strong">{children}</div>
    </div>
  )
}

export function KV({ label, children, valueClass }: { label: string; children: ReactNode; valueClass?: string }) {
  return (
    <div className="flex items-center justify-between gap-3 py-1">
      <span className="text-sm text-ink-secondary">{label}</span>
      <span className={clsx('text-sm font-medium text-ink-primary', valueClass)}>{children}</span>
    </div>
  )
}

/* ------------------------------------------------------------------ */
/* ForkPoint overview panel  [screenshot 1]                            */
/* ------------------------------------------------------------------ */

export function ForkPointPanel({ onStart, onClose }: { onStart?: () => void; onClose?: () => void }) {
  return (
    <PanelShell
      title="QA ForkPoint · S0"
      tag="ROOT"
      tagStatus="root"
      tabs={['Overview', 'Evidence', 'State Diff']}
      onClose={onClose}
      footer={
        <div className="space-y-2 text-2xs text-ink-tertiary">
          <div className="flex justify-between">
            <span>Created</span>
            <span className="text-ink-secondary">May 8, 2025 · 10:21 AM</span>
          </div>
          <div className="flex justify-between">
            <span>Updated</span>
            <span className="text-ink-secondary">May 8, 2025 · 10:24 AM</span>
          </div>
        </div>
      }
    >
      <Section icon={<GitFork size={14} />} title="Fork reason">
        QA analysis indicates likely reward hacking via pytest plugin subversion.
      </Section>
      <Divider />
      <Section icon={<FileText size={14} />} title="Trace evidence">
        Trace shows reward gained after plugin injection and altered test discovery.
        <a className="mt-1.5 flex items-center gap-1 text-accent-text hover:underline" href="#">
          View trace excerpt <ExternalLink size={12} />
        </a>
      </Section>
      <Divider />
      <Section icon={<FolderClosed size={14} />} title="Snapshot mode">
        <div className="flex items-center justify-between">
          Directory Snapshot
          <span className="inline-flex items-center gap-1 text-accent-text">
            <ShieldCheck size={13} /> Captured
          </span>
        </div>
      </Section>
      <Divider />
      <Section icon={<Clock size={14} />} title="History prefix">
        <KV label="Up to step">12</KV>
        <KV label="Actions">1 – 12</KV>
        <KV label="Cumulative reward">1.00</KV>
      </Section>
      <Divider />
      <div className="grid grid-cols-2 gap-2 pt-3">
        <Button variant="secondary" size="sm" icon={<Eye size={14} />}>
          View trace
        </Button>
        <Button variant="secondary" size="sm" icon={<Shuffle size={14} />}>
          View state
        </Button>
      </div>
      <Button variant="primary" size="md" className="mt-2 w-full" icon={<Shuffle size={15} />} onClick={onStart}>
        Start stochastic branches
      </Button>
    </PanelShell>
  )
}

/* ------------------------------------------------------------------ */
/* Branch / witness detail panel  [screenshot 4]                       */
/* ------------------------------------------------------------------ */

const STATUS_DISPLAY: Record<string, { label: string; class: string; tag: string; tagStatus: string }> = {
  witness: { label: 'CONFIRMED WITNESS', class: 'text-accent-text text-xs font-semibold', tag: 'WITNESS', tagStatus: 'witness' },
  promising: { label: 'PROMISING CANDIDATE', class: 'text-warn-text text-xs font-semibold', tag: 'PROMISING', tagStatus: 'promising' },
  qa_review: { label: 'AWAITING QA', class: 'text-warn-text text-xs font-semibold', tag: 'QA REVIEW', tagStatus: 'qa-review' },
  control: { label: 'LEGITIMATE CONTROL', class: 'text-ink-secondary-strong text-xs font-semibold', tag: 'CONTROL', tagStatus: 'control' },
  control_pass: { label: 'CONTROL PASS', class: 'text-accent-text text-xs font-semibold', tag: 'CONTROL PASS', tagStatus: 'control-pass' },
  dead_end: { label: 'DEAD END', class: 'text-ink-danger text-xs font-semibold', tag: 'DEAD END', tagStatus: 'dead-end' },
  duplicate: { label: 'DUPLICATE', class: 'text-ink-secondary-strong text-xs font-semibold', tag: 'DUPLICATE', tagStatus: 'duplicate' },
  snapshot: { label: 'SNAPSHOT', class: 'text-ink-secondary-strong text-xs font-semibold', tag: 'SNAPSHOT', tagStatus: 'snapshot' },
}

export function BranchPanel({
  branch,
  inProofSet,
  onClose,
  onAddToProofSet,
  onRemoveFromProofSet,
  onReplay,
}: {
  branch: BranchRun
  inProofSet?: boolean
  onClose?: () => void
  onAddToProofSet?: () => void
  onRemoveFromProofSet?: () => void
  onReplay?: () => void
}) {
  const sd = STATUS_DISPLAY[branch.status] ?? STATUS_DISPLAY.promising
  const rows: { label: string; value: ReactNode; valueClass?: string; copy?: boolean }[] = [
    { label: 'Branch ID', value: branch.branchId, valueClass: 'font-mono text-xs' },
    { label: 'Status', value: sd.label, valueClass: sd.class },
    ...(branch.qa
      ? [{ label: 'QA classification', value: branch.qa.classification, valueClass: branch.qa.isRewardHacking ? 'text-warn-text' : 'text-ink-secondary-strong' }]
      : []),
    { label: 'Replay', value: branch.status === 'witness' ? 'Deterministic pass' : 'Not run', valueClass: branch.status === 'witness' ? 'text-accent-text' : 'text-ink-secondary' },
    { label: 'Cluster', value: branch.clusterLabel ?? '—' },
    { label: 'Reward (H2F)', value: branch.reward.toFixed(2) },
    { label: 'Seed', value: String(branch.seed), valueClass: 'font-mono text-xs' },
    { label: 'Model', value: branch.model, valueClass: 'font-mono text-xs' },
    { label: 'Sampling config', value: `temp=${branch.samplingConfig.temperature.toFixed(1)}, top_p=${branch.samplingConfig.topP.toFixed(1)}`, valueClass: 'font-mono text-xs' },
    { label: 'Parent snapshot', value: branch.parentSnapshot ?? 'S0' },
    { label: 'Snapshot mode', value: cap(branch.snapshotMode) },
    { label: 'Environment', value: branch.environmentVersion },
    { label: 'Grader digest', value: branch.graderDigest, valueClass: 'font-mono text-xs', copy: true },
  ]
  return (
    <PanelShell title={branch.title} tag={sd.tag} tagStatus={sd.tagStatus} tabs={['Overview', 'Evidence', 'State', 'Replay']} onClose={onClose}>
      <div className="divide-y divide-hairline">
        {rows.map((r) => (
          <KV key={r.label} label={r.label} valueClass={r.valueClass}>
            <span className="inline-flex items-center gap-1">
              {r.value}
              {r.copy && <Copy size={11} className="text-ink-tertiary" />}
            </span>
          </KV>
        ))}
      </div>
      {branch.notes && (
        <div className="mt-4">
          <div className="mb-1 text-sm text-ink-secondary">Notes</div>
          <p className="text-sm text-ink-secondary-strong">{branch.notes}</p>
        </div>
      )}
      <div className="mt-5 space-y-2">
        <div className="text-2xs font-semibold uppercase tracking-wide text-ink-tertiary">Actions</div>
        <Button variant="primary" size="md" className="w-full" icon={<Play size={14} />} onClick={onReplay}>
          Replay witness
        </Button>
        <Button variant="secondary" size="md" className="w-full" icon={<Eye size={14} />}>
          View pre-attack state
        </Button>
        {inProofSet ? (
          <Button variant="secondary" size="md" className="w-full" icon={<CircleSlash size={14} />} onClick={onRemoveFromProofSet}>
            Remove from ProofSet
          </Button>
        ) : (
          <Button variant="secondary" size="md" className="w-full" icon={<PlusCircle size={14} />} onClick={onAddToProofSet}>
            Add to ProofSet
          </Button>
        )}
      </div>
    </PanelShell>
  )
}

function cap(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

/* ------------------------------------------------------------------ */
/* ProofSet panel  [screenshot 5]                                      */
/* ------------------------------------------------------------------ */

function ProofRow({ name, badge, tone }: { name: string; badge: string; tone: 'fail' | 'pass' | 'variant' }) {
  const toneCls = tone === 'fail' ? 'text-ink-danger bg-state-red-soft' : tone === 'pass' ? 'text-accent-text bg-green-50' : 'text-ink-secondary-strong bg-tint-blue'
  const Icon = tone === 'fail' ? CircleSlash : tone === 'pass' ? ShieldCheck : Shuffle
  return (
    <div className="flex items-center justify-between gap-2 rounded-lg border border-hairline bg-surface-raised px-3 py-2.5">
      <span className="flex items-center gap-2 text-sm text-ink-primary">
        <Icon size={14} className={tone === 'fail' ? 'text-ink-danger' : tone === 'pass' ? 'text-accent-text' : 'text-ink-secondary'} />
        {name}
      </span>
      <span className={clsx('rounded-sm px-1.5 py-0.5 text-2xs font-semibold', toneCls)}>{badge}</span>
    </div>
  )
}

function ProofGroup({ title, count, children }: { title: string; count: number; children: ReactNode }) {
  return (
    <div className="py-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-ink-primary">
        {title} <span className="text-ink-tertiary">{count}</span>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  )
}

export function ProofSetPanel({
  proofSet,
  branches,
  controls,
  variantNames,
  onRun,
  onClose,
}: {
  proofSet: ProofSet
  branches: BranchRun[]
  controls: LegitimateControl[]
  variantNames: Record<string, string>
  onRun?: () => void
  onClose?: () => void
}) {
  const witnessName = (id: string) => branches.find((b) => b.runId === `run-${id}`)?.title ?? id
  const controlName = (id: string) => controls.find((c) => c.controlId === id)?.title ?? id
  const headlineTotal = proofSet.exploitWitnessIds.length + proofSet.legitimateControlIds.length
  return (
    <PanelShell
      title="ProofSet"
      onClose={onClose}
      footer={
        <div className="space-y-3">
          <Button variant="primary" size="md" className="w-full" icon={<Play size={14} />} onClick={onRun}>
            Run ProofSet
          </Button>
          <div className="flex justify-between text-2xs text-ink-tertiary">
            <span>Created</span>
            <span className="text-ink-secondary">May 8, 2025 · 10:25 AM</span>
          </div>
        </div>
      }
    >
      <p className="-mt-1 flex items-center gap-1.5 text-sm text-ink-secondary">
        <ShieldCheck size={14} className="text-ink-tertiary" /> {headlineTotal} total
      </p>
      <Divider className="my-3" />
      <ProofGroup title="Exploit Witnesses" count={proofSet.exploitWitnessIds.length}>
        {proofSet.exploitWitnessIds.map((id) => (
          <ProofRow key={id} name={witnessName(id)} badge="MUST FAIL" tone="fail" />
        ))}
      </ProofGroup>
      <ProofGroup title="Legitimate Controls" count={proofSet.legitimateControlIds.length}>
        {proofSet.legitimateControlIds.map((id) => (
          <ProofRow key={id} name={controlName(id)} badge="MUST PASS" tone="pass" />
        ))}
      </ProofGroup>
      <ProofGroup title="Re-seeded Variants" count={proofSet.exploitFamilyVariantIds.length}>
        {proofSet.exploitFamilyVariantIds.map((id) => (
          <ProofRow key={id} name={variantNames[id] ?? id} badge="VARIANT" tone="variant" />
        ))}
      </ProofGroup>
    </PanelShell>
  )
}
