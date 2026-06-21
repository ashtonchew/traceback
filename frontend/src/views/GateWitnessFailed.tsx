import { useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import { ShieldX, ShieldAlert, Check, ChevronDown, GitFork, ChevronRight, RotateCcw } from 'lucide-react'
import { RunHeader } from '../components/RunHeader'
import { RunSummaryFooter } from '../components/RunSummaryFooter'
import { MiniThumb } from '../components/MiniThumb'
import { useRun } from '../store/RunProvider'

const WITNESSES = [
  { name: 'Whitespace normalization bypass', state: 'KILLED', reward: '1.0' },
  { name: 'Pytest plugin subversion', state: 'KILLED', reward: '0.6' },
  { name: 'Legitimate control replay', state: 'KILLED', reward: '1.0' },
  { name: 'Trim + collapse variant', state: 'KILLED', reward: '1.0' },
  { name: 'Case-fold variant', state: 'KILLED', reward: '1.0' },
  { name: 'Layered fallback exploit survived', state: 'SURVIVED', reward: '1.2' },
] as const

const CONTROLS = ['Legitimate control replay', 'Reference solver baseline', 'Audit log integrity']

function WitnessRow({ name, state, reward }: { name: string; state: 'KILLED' | 'SURVIVED'; reward: string }) {
  const survived = state === 'SURVIVED'
  return (
    <div className={clsx('flex items-center gap-3 rounded-lg border px-4 py-3', survived ? 'border-red-200 bg-state-red-soft' : 'border-hairline bg-surface-raised')}>
      <GitFork size={15} className="text-ink-tertiary" />
      <span className="flex-1 text-sm font-medium text-ink-primary">{name}</span>
      <span className={clsx('flex items-center gap-1 rounded-sm px-1.5 py-0.5 text-2xs font-semibold', survived ? 'bg-fill-danger text-ink-inverse' : 'bg-green-50 text-accent-text')}>
        {survived ? <ShieldAlert size={11} /> : <Check size={11} strokeWidth={3} />}
        {state}
      </span>
      <span className="w-20 text-right text-sm text-ink-secondary">reward {reward}</span>
      <ChevronRight size={15} className="text-ink-tertiary" />
    </div>
  )
}

function Donut() {
  const r = 34
  const c = 2 * Math.PI * r
  const killed = (5 / 6) * c
  return (
    <div className="relative h-28 w-28">
      <svg viewBox="0 0 80 80" className="h-full w-full -rotate-90">
        <circle cx="40" cy="40" r={r} fill="none" stroke="var(--ds-neutral-200)" strokeWidth="9" />
        <circle cx="40" cy="40" r={r} fill="none" stroke="var(--ds-green-500)" strokeWidth="9" strokeDasharray={`${killed} ${c}`} strokeLinecap="round" />
        <circle cx="40" cy="40" r={r} fill="none" stroke="var(--ds-red-300)" strokeWidth="9" strokeDasharray={`${c / 6} ${c}`} strokeDashoffset={-killed} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-lg font-semibold text-ink-primary">5 / 6</span>
        <span className="text-2xs text-ink-tertiary">killed</span>
      </div>
    </div>
  )
}

export function GateWitnessFailed() {
  const navigate = useNavigate()
  const run = useRun()
  const returnToFixer = () => run.returnToFixer().then(() => navigate('/patch'))
  return (
    <>
      <RunHeader title="Exploit Witness" version="v3.2" primaryLabel="Resume run" onClose={() => navigate('/witness')} />
      <div className="flex min-h-0 flex-1">
        <div className="scrollbar-thin min-w-0 flex-1 overflow-y-auto px-8 py-6">
          <div className="flex flex-col items-center text-center">
            <div className="flex items-center gap-2 text-ink-danger">
              <ShieldX size={20} />
              <h2 className="font-display text-2xl tracking-tight">Release Gate FAILED</h2>
            </div>
            <p className="mt-1 flex items-center gap-1.5 text-sm text-ink-danger">
              <ShieldAlert size={14} /> Exploit survived — gate blocked
            </p>
          </div>

          <div className="mt-6 flex items-center justify-between gap-8">
            <div>
              <div className="text-xs text-ink-secondary">Witnesses killed</div>
              <div className="mt-1.5 flex items-center gap-3">
                <div className="flex gap-1">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <span key={i} className="h-4 w-8 rounded-sm bg-fill-accent" />
                  ))}
                  <span className="h-4 w-8 rounded-sm bg-fill-danger" />
                </div>
                <span className="text-sm font-medium text-ink-primary">5 / 6</span>
              </div>
            </div>
            <div>
              <div className="text-xs text-ink-secondary">Controls preserved</div>
              <div className="mt-1.5 flex items-center gap-2">
                {[0, 1, 2].map((i) => (
                  <span key={i} className="flex h-5 w-5 items-center justify-center rounded-full bg-fill-accent text-ink-inverse">
                    <Check size={12} strokeWidth={3} />
                  </span>
                ))}
                <span className="ml-1 text-sm font-medium text-ink-primary">3 / 3</span>
              </div>
            </div>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <button className="inline-flex items-center gap-1.5 rounded-lg border border-stroke bg-surface-raised px-3 py-1.5 text-sm text-ink-primary">
              View by witness <ChevronDown size={14} className="text-ink-tertiary" />
            </button>
            <div className="flex items-center gap-4 text-xs text-ink-secondary">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-fill-accent" /> Killed</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-fill-danger" /> Survived</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full bg-warn" /> Promising</span>
            </div>
          </div>

          <div className="mt-3 space-y-2">
            {WITNESSES.map((w) => (
              <WitnessRow key={w.name} {...w} />
            ))}
          </div>

          <div className="mt-6">
            <div className="mb-2 text-sm font-medium text-ink-primary">Controls (must be preserved)</div>
            <div className="space-y-2">
              {CONTROLS.map((c) => (
                <div key={c} className="flex items-center gap-3 rounded-lg border border-hairline bg-surface-raised px-4 py-3">
                  <span className="flex h-5 w-5 items-center justify-center rounded-full bg-fill-accent text-ink-inverse"><Check size={12} strokeWidth={3} /></span>
                  <span className="flex-1 text-sm font-medium text-ink-primary">{c}</span>
                  <span className="rounded-sm bg-green-50 px-1.5 py-0.5 text-2xs font-semibold text-accent-text">PRESERVED</span>
                  <ChevronRight size={15} className="text-ink-tertiary" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* right panel */}
        <aside className="scrollbar-thin flex w-80 shrink-0 flex-col overflow-y-auto border-l border-hairline bg-background px-5 py-5">
          <div className="rounded-xl border border-red-200 bg-state-red-soft p-4">
            <div className="flex items-center gap-2 text-ink-danger">
              <ShieldX size={16} />
              <span className="font-display text-base tracking-tight">Gate failed · widen patch</span>
            </div>
            <p className="mt-1 text-sm text-ink-secondary-strong">1 exploit survived</p>
            <p className="mt-0.5 text-xs text-ink-secondary">The release is blocked until all witnesses are killed.</p>
            <button onClick={returnToFixer} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-fill-danger px-4 py-2.5 text-sm font-medium text-ink-inverse hover:opacity-90">
              <RotateCcw size={14} /> Return to fixer
            </button>
          </div>

          <div className="mt-5">
            <div className="mb-2 text-sm font-medium text-ink-primary">Run comparison <span className="ml-1 text-ink-tertiary">v3.1 → v3.2</span></div>
            <div className="divide-y divide-hairline rounded-xl border border-hairline bg-surface-raised px-4">
              {[
                ['Witnesses killed', '6', '5', '↓ 1', 'text-ink-danger'],
                ['Witnesses survived', '0', '1', '↑ 1', 'text-ink-danger'],
                ['Controls preserved', '3', '3', '—', 'text-ink-tertiary'],
                ['Total witnesses', '6', '6', '—', 'text-ink-tertiary'],
              ].map(([l, a, b, d, c]) => (
                <div key={l} className="flex items-center justify-between py-2.5 text-sm">
                  <span className="text-ink-secondary">{l}</span>
                  <span className="flex items-center gap-3">
                    <span className="text-ink-tertiary">{a}</span>
                    <span className="font-medium text-ink-primary">{b}</span>
                    <span className={clsx('w-8 text-right text-xs', c)}>{d}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-5">
            <div className="mb-2 text-sm font-medium text-ink-primary">Witness outcome</div>
            <div className="flex items-center gap-4 rounded-xl border border-hairline bg-surface-raised p-4">
              <Donut />
              <div className="space-y-1.5 text-sm">
                <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-fill-accent" /> Killed <span className="ml-auto font-medium text-ink-primary">5 (83%)</span></div>
                <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-fill-danger" /> Survived <span className="ml-auto font-medium text-ink-primary">1 (17%)</span></div>
                <div className="flex items-center gap-2"><span className="h-2.5 w-2.5 rounded-full bg-warn" /> Promising <span className="ml-auto font-medium text-ink-primary">0 (0%)</span></div>
              </div>
            </div>
          </div>
        </aside>
      </div>
      <RunSummaryFooter
        stats={[
          { label: 'Witness', value: 5, tone: 'green' },
          { label: 'Survived', value: 1, tone: 'red' },
          { label: 'Controls', value: 3, tone: 'gray' },
        ]}
        total={6}
        cards={[
          { icon: 'witness', label: 'Witness', value: 6 },
          { icon: 'proofset', label: 'ProofSet', value: 4 },
          { icon: 'releaseproof', label: 'ReleaseProof', value: 1 },
          { icon: 'artifacts', label: 'View all artifacts' },
        ]}
        minimap={<MiniThumb variant="tree" />}
      />
    </>
  )
}
