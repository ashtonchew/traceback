import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import { Play, Bot, Wrench, Database, Settings, GitFork, ChevronDown } from 'lucide-react'
import type { ReactNode } from 'react'

const NAV = [
  { to: '/', label: 'Runs', icon: Play, end: true },
  { to: '/agents', label: 'Agents', icon: Bot },
  { to: '/tools', label: 'Tools', icon: Wrench },
  { to: '/memory', label: 'Memory', icon: Database },
  { to: '/settings', label: 'Settings', icon: Settings },
]

function Item({ to, label, icon: Icon, end }: { to: string; label: string; icon: typeof Play; end?: boolean }) {
  return (
    <NavLink to={to} end={end} className="group flex flex-col items-center gap-1 py-2">
      {({ isActive }) => (
        <>
          <span
            className={clsx(
              'flex h-9 w-9 items-center justify-center rounded-lg transition',
              isActive ? 'bg-surface text-ink-primary' : 'text-ink-tertiary group-hover:bg-surface group-hover:text-ink-secondary',
            )}
          >
            <Icon size={18} strokeWidth={1.75} />
          </span>
          <span className={clsx('text-2xs', isActive ? 'text-ink-secondary-strong' : 'text-ink-tertiary')}>{label}</span>
        </>
      )}
    </NavLink>
  )
}

export function Sidebar(): ReactNode {
  return (
    <aside className="flex w-18 shrink-0 flex-col items-center border-r border-hairline bg-background py-4">
      <div className="mb-6 flex h-10 w-10 items-center justify-center rounded-xl bg-fill-accent text-ink-inverse">
        <GitFork size={20} strokeWidth={2} />
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV.map((n) => (
          <Item key={n.to} {...n} />
        ))}
      </nav>
      <button className="mt-4 flex flex-col items-center gap-1 text-ink-tertiary transition hover:text-ink-secondary">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-fill-primary text-2xs font-semibold text-ink-inverse">AC</span>
        <ChevronDown size={14} />
      </button>
    </aside>
  )
}
