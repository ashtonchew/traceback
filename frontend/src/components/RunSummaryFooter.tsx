import { clsx } from 'clsx'
import { ChevronDown, Maximize2, Lock, GitFork, FileCheck2, ShieldCheck, FolderOpen } from 'lucide-react'
import type { ReactNode } from 'react'

export interface SummaryStat {
  label: string
  value: number | string
  tone?: 'green' | 'warn' | 'red' | 'gray'
}

const DOT: Record<string, string> = {
  green: 'bg-fill-accent',
  warn: 'bg-warn',
  red: 'bg-fill-danger',
  gray: 'bg-ink-tertiary',
}

function Stat({ label, value, tone = 'gray' }: SummaryStat) {
  return (
    <span className="inline-flex items-center gap-1.5 text-sm text-ink-secondary-strong">
      <span className={clsx('h-1.5 w-1.5 rounded-full', DOT[tone])} />
      {label} <span className="font-medium text-ink-primary">{value}</span>
    </span>
  )
}

export interface FooterCard {
  icon: 'witness' | 'proofset' | 'releaseproof' | 'artifacts'
  label: string
  value?: number | string
}

const CARD_ICON = {
  witness: GitFork,
  proofset: FileCheck2,
  releaseproof: ShieldCheck,
  artifacts: FolderOpen,
}

function Card({ icon, label, value }: FooterCard) {
  const Icon = CARD_ICON[icon]
  return (
    <div className="flex items-center gap-2 rounded-lg border border-hairline bg-surface-raised px-4 py-2.5">
      <Icon size={15} className="text-ink-tertiary" />
      <span className="text-sm text-ink-secondary-strong">{label}</span>
      {value !== undefined && <span className="text-sm font-medium text-ink-primary">{value}</span>}
    </div>
  )
}

export function RunSummaryFooter({
  stats,
  total,
  cards,
  minimap,
}: {
  stats: SummaryStat[]
  total?: number | string
  cards: FooterCard[]
  minimap?: ReactNode
}) {
  return (
    <div className="flex items-center justify-between gap-6 border-t border-hairline bg-background px-8 py-4">
      <div className="flex items-center gap-4">
        <button className="inline-flex items-center gap-1 text-sm font-medium text-ink-primary">
          Run summary <ChevronDown size={14} className="text-ink-tertiary" />
        </button>
        <div className="flex items-center gap-4">
          {stats.map((s) => (
            <Stat key={s.label} {...s} />
          ))}
          {total !== undefined && (
            <span className="text-sm text-ink-secondary-strong">
              Total <span className="font-medium text-ink-primary">{total}</span>
            </span>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        {cards.map((c) => (
          <Card key={c.label} {...c} />
        ))}
      </div>

      <div className="flex items-center gap-2">
        {minimap}
        <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-hairline text-ink-tertiary hover:bg-surface">
          <Maximize2 size={14} />
        </button>
        <button className="flex h-8 w-8 items-center justify-center rounded-lg border border-hairline text-ink-tertiary hover:bg-surface">
          <Lock size={13} />
        </button>
      </div>
    </div>
  )
}
