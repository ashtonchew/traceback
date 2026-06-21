import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { clsx } from 'clsx'
import { ShieldCheck, Check, ArrowRight, Database, ExternalLink, Copy, FileDiff, Download } from 'lucide-react'
import { RunHeader } from '../components/RunHeader'
import { RunSummaryFooter } from '../components/RunSummaryFooter'
import { MiniThumb } from '../components/MiniThumb'
import { KV } from '../components/panels'
import { Button, Chip } from '../components/primitives'
import { useRun } from '../store/RunProvider'

function Confetti() {
  const bits = [
    { x: '8%', y: '14%', c: 'bg-fill-accent', r: '12deg' },
    { x: '22%', y: '40%', c: 'bg-accent', r: '-20deg' },
    { x: '70%', y: '12%', c: 'bg-warn', r: '30deg' },
    { x: '86%', y: '34%', c: 'bg-fill-accent', r: '-12deg' },
    { x: '15%', y: '70%', c: 'bg-green-300', r: '40deg' },
    { x: '90%', y: '64%', c: 'bg-accent', r: '18deg' },
    { x: '50%', y: '8%', c: 'bg-green-300', r: '-30deg' },
    { x: '40%', y: '76%', c: 'bg-warn', r: '22deg' },
  ]
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {bits.map((b, i) => (
        <span key={i} className={clsx('absolute h-2 w-1.5 rounded-sm opacity-70', b.c)} style={{ left: b.x, top: b.y, transform: `rotate(${b.r})` }} />
      ))}
    </div>
  )
}

function BigStat({ value, label }: { value: string; label: string }) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-state-green-border bg-state-green-soft py-6">
      <div className="font-display text-5xl tracking-tight text-ink-primary">{value}</div>
      <div className="mt-1 text-sm text-ink-secondary-strong">{label}</div>
      <div className="mt-1 flex items-center gap-1 text-sm font-medium text-accent-text">
        100% <Check size={13} />
      </div>
    </div>
  )
}

function EnvCard({ when, version, status, rows, published }: { when: string; version: string; status: string; rows: [string, string, boolean | null][]; published?: boolean }) {
  return (
    <div className={clsx('rounded-xl border p-4', published ? 'border-state-green-border bg-state-green-soft' : 'border-hairline bg-surface-raised')}>
      <div className="flex items-center justify-between">
        <span className="font-display text-base tracking-tight text-ink-primary">Environment {version}</span>
        <span className="text-2xs font-semibold uppercase tracking-wide text-ink-tertiary">{when}</span>
      </div>
      <div className="mt-3 space-y-1.5 text-sm">
        <div className="flex justify-between"><span className="text-ink-secondary">{published ? 'Published version' : 'Active version'}</span><span className="font-medium text-ink-primary">{version}</span></div>
        <div className="flex justify-between"><span className="text-ink-secondary">Status</span><span className={clsx('text-2xs font-semibold uppercase', published ? 'text-accent-text' : 'text-ink-secondary-strong')}>{status}</span></div>
        {rows.map(([l, v, ok]) => (
          <div key={l} className="flex justify-between">
            <span className="text-ink-secondary">{l}</span>
            <span className={clsx('flex items-center gap-1 font-medium', ok === null ? 'text-ink-tertiary' : 'text-ink-primary')}>
              {v} {ok === true && <Check size={12} className="text-accent-text" />}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function ReleaseProof() {
  const navigate = useNavigate()
  const run = useRun()
  const rp = run.releaseProof

  useEffect(() => {
    if (!rp || rp.status !== 'committed') run.publish()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const wk = rp?.witnessesKilled ?? [run.proofSet?.exploitWitnessIds.length ?? 6, run.proofSet?.exploitWitnessIds.length ?? 6]
  const cp = rp?.controlsPreserved ?? [run.proofSet?.legitimateControlIds.length ?? 3, run.proofSet?.legitimateControlIds.length ?? 3]
  const env = rp?.environmentV1 ?? 'mongodb-sales-aggregation-engine'
  const publishedRef = rp?.publishedEnvironmentRef ?? `${env} v2`
  const commitId = rp?.commitId ?? 'rpf-20250508-102431'
  const reward = (rp?.reward ?? 1.0).toFixed(2)
  const similarity = (rp?.similarity ?? 0.92).toFixed(2)
  return (
    <>
      <RunHeader title="Exploit Witness" version="v3.2" primaryLabel="Resume run" onClose={() => navigate('/witness')} />
      <div className="flex min-h-0 flex-1">
        <div className="scrollbar-thin relative min-w-0 flex-1 overflow-y-auto px-8 py-8">
          <Confetti />
          <div className="relative mx-auto max-w-3xl">
            <div className="flex flex-col items-center text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-full bg-green-50 text-accent-text">
                <ShieldCheck size={24} />
              </span>
              <h2 className="mt-3 font-display text-3xl tracking-tight text-ink-primary">ReleaseProof committed</h2>
              <p className="mt-1 text-base text-accent-text">Published {publishedRef}</p>
              <p className="mt-1 text-sm text-ink-secondary">All witnesses were successfully killed and controls were preserved.</p>
            </div>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <BigStat value={`${wk[0]} / ${wk[1]}`} label="witnesses killed" />
              <BigStat value={`${cp[0]} / ${cp[1]}`} label="controls preserved" />
            </div>

            <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
              <EnvCard
                when="Before"
                version="v1"
                status="Live"
                rows={[
                  ['Witnesses rewarded', `${wk[1]} / ${wk[1]}`, null],
                  ['Controls rewarded', `${cp[1]} / ${cp[1]}`, null],
                  ['ReleaseProof', 'Not committed', null],
                ]}
              />
              <ArrowRight size={20} className="text-ink-tertiary" />
              <EnvCard
                when="After (published)"
                version="v2"
                status="Published"
                published
                rows={[
                  ['Witnesses blocked', `${wk[0]} / ${wk[1]}`, true],
                  ['Controls preserved', `${cp[0]} / ${cp[1]}`, true],
                  ['ReleaseProof', 'Committed', true],
                ]}
              />
            </div>

            <div className="mt-5 flex items-center gap-3 rounded-xl border border-state-green-border bg-state-green-soft p-4">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-fill-accent text-ink-inverse"><Database size={18} /></span>
              <div className="flex-1">
                <div className="text-2xs uppercase tracking-wide text-ink-tertiary">Published</div>
                <div className="text-sm font-medium text-ink-primary">{publishedRef}</div>
                <div className="text-xs text-ink-secondary">Environment successfully published and live.</div>
              </div>
              <Button variant="secondary" size="sm" icon={<ExternalLink size={14} />}>View in HUD</Button>
            </div>
          </div>
        </div>

        {/* right panel */}
        <aside className="flex w-80 shrink-0 flex-col border-l border-hairline bg-background">
          <div className="flex items-center gap-2 px-5 pt-5">
            <ShieldCheck size={16} className="text-accent-text" />
            <h2 className="font-display text-xl tracking-tight text-ink-primary">ReleaseProof</h2>
            <Chip status="witness">COMMITTED</Chip>
          </div>
          <div className="flex-1 px-5 py-4">
            <div className="divide-y divide-hairline">
              <KV label="Environment" valueClass="text-xs">{env}</KV>
              <KV label="Published version">v2</KV>
              <KV label="Commit ID" valueClass="font-mono text-xs">
                <span className="inline-flex items-center gap-1">{commitId} <Copy size={11} className="text-ink-tertiary" /></span>
              </KV>
              <KV label="Status" valueClass="text-accent-text text-xs font-semibold">COMMITTED</KV>
              <KV label="Reward (H2F)">{reward}</KV>
              <KV label="Similarity">{similarity}</KV>
            </div>
            <div className="mt-4">
              <div className="mb-1 text-sm text-ink-secondary">Notes</div>
              <p className="text-sm text-ink-secondary-strong">All witnesses killed. All controls preserved.</p>
            </div>
            <div className="mt-5 space-y-2">
              <div className="text-2xs font-semibold uppercase tracking-wide text-ink-tertiary">Actions</div>
              <Button variant="primary" size="md" className="w-full" icon={<ExternalLink size={14} />}>View ReleaseProof</Button>
              <Button variant="secondary" size="md" className="w-full" icon={<FileDiff size={14} />}>View state diff</Button>
              <Button variant="secondary" size="md" className="w-full" icon={<Download size={14} />}>Download evidence</Button>
            </div>
          </div>
        </aside>
      </div>
      <RunSummaryFooter
        stats={[
          { label: 'Witnesses', value: 6, tone: 'green' },
          { label: 'Controls', value: 3, tone: 'gray' },
        ]}
        total={9}
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
