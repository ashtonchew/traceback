import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'
import { Play, ChevronDown, X, Database, Check } from './icons'
import { Button, IconButton, LiveDot, VersionPill } from './primitives'
import { SCENES } from '../lib/scenes'

function SceneMenu({ tone }: { tone: 'primary' | 'dark' }) {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const { pathname } = useLocation()

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false) }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open])
  const variant = tone === 'primary' ? 'bg-fill-accent text-ink-inverse hover:bg-fill-accent-hover' : 'bg-fill-primary text-ink-inverse hover:bg-fill-primary-hover'
  return (
    <div className="relative flex items-stretch">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={clsx(
          'inline-flex h-full origin-left items-center justify-center rounded-lg rounded-l-none border-l border-black/10 px-2 text-sm transition-[background-color,color,transform] duration-150 ease-out active:scale-[0.96] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          variant,
        )}
        aria-label="Open screen menu"
        aria-expanded={open}
      >
        <ChevronDown size={14} />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-[100]" onClick={() => setOpen(false)} />
          <div className="animate-dropdown-show origin-top-right absolute right-0 z-[101] mt-2 w-72 rounded-lg border border-hairline bg-surface-raised p-1.5 shadow-lg">
            <div className="px-2.5 py-1.5 text-2xs font-semibold uppercase tracking-wide text-ink-tertiary">Jump to screen</div>
            {SCENES.map((s) => (
              <button
                key={s.path}
                onClick={() => {
                  navigate(s.path)
                  setOpen(false)
                }}
                className={clsx(
                  'flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-left text-sm text-ink-primary transition-[background-color,color,transform] duration-150 ease-out hover:bg-surface active:scale-[0.98] focus:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  pathname === s.path && 'bg-surface',
                )}
              >
                <span className="w-12 shrink-0 text-2xs text-ink-tertiary">{s.group}</span>
                <span className="min-w-0 flex-1 truncate">{s.label}</span>
                {pathname === s.path && <Check size={14} className="text-accent-text" />}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

interface RunHeaderProps {
  title: string
  version?: string
  status?: { tone: 'green' | 'red'; label: string }
  subtitle?: string
  primaryLabel?: string
  primaryTone?: 'primary' | 'dark'
  onPrimary?: () => void
  onClose?: () => void
}

export function RunHeader({
  title,
  version,
  status = { tone: 'green', label: 'Live' },
  subtitle,
  primaryLabel = 'Resume run',
  primaryTone = 'primary',
  onPrimary,
  onClose,
}: RunHeaderProps) {
  return (
    <header className="flex items-start justify-between border-b border-hairline bg-background px-8 py-4">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="m-0 font-display text-3xl leading-none tracking-tight text-ink-primary">{title}</h1>
          <div className="flex translate-y-0.5 items-center gap-2.5">
            {version && <VersionPill>{version}</VersionPill>}
            <LiveDot tone={status.tone} label={status.label} />
          </div>
        </div>
        {subtitle && (
          <p className="mt-1 flex items-center gap-1.5 text-sm text-ink-secondary">
            <Database size={13} className="text-ink-tertiary" />
            {subtitle}
          </p>
        )}
      </div>
      <div className="flex items-center gap-2">
        <div className="inline-flex items-stretch">
          <Button variant={primaryTone} size="sm" icon={<Play size={14} />} className="rounded-r-none" onClick={onPrimary}>
            {primaryLabel}
          </Button>
          <SceneMenu tone={primaryTone} />
        </div>
        {onClose && (
          <IconButton label="Close" onClick={onClose} className="ml-1">
            <X size={18} />
          </IconButton>
        )}
      </div>
    </header>
  )
}
