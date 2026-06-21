import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import { FileCheck2, FolderOpen, GitFork, Play, Settings, ShieldCheck, Tree02 } from './icons'
import type { ComponentType, ReactNode } from 'react'
import type { IconProps } from './icons'

const NAV = [
  { to: '/', label: 'Runs', icon: Play, end: true },
  { to: '/witness?focus=confirmed', label: 'Witness', icon: GitFork },
  { to: '/proofset', label: 'Proof set', icon: FileCheck2 },
  { to: '/releaseproof', label: 'Release', icon: ShieldCheck },
  { to: '/artifacts', label: 'Artifacts', icon: FolderOpen },
]

const UTILITY_NAV = [
  { to: '/settings', label: 'Settings', icon: Settings },
]

function Item({ to, label, icon: Icon, end }: { to: string; label: string; icon: ComponentType<IconProps>; end?: boolean }) {
  return (
    <NavLink to={to} end={end} aria-label={label} className="group flex flex-col items-center gap-1 rounded-lg py-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring">
      {({ isActive }) => (
        <>
          <span
            className={clsx(
              'flex h-9 w-9 items-center justify-center rounded-lg transition-[background-color,color,transform] duration-150 ease-out group-active:scale-[0.96]',
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
      <NavLink
        to="/"
        aria-label="Traceback home"
        className="mb-6 flex h-10 w-10 items-center justify-center rounded-xl bg-fill-accent text-ink-inverse transition-[background-color,transform] duration-150 ease-out hover:bg-fill-accent-hover active:scale-[0.96] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <Tree02 size={20} strokeWidth={2} />
      </NavLink>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV.map((n) => (
          <Item key={n.to} {...n} />
        ))}
      </nav>
      <nav className="flex flex-col gap-1">
        {UTILITY_NAV.map((n) => (
          <Item key={n.to} {...n} />
        ))}
      </nav>
    </aside>
  )
}
