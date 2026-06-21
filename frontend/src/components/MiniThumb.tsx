import { Maximize2 } from 'lucide-react'

/** Decorative minimap thumbnail shown in the run-summary footer. */
export function MiniThumb({ variant = 'tree' }: { variant?: 'row' | 'tree' }) {
  return (
    <div className="relative h-14 w-44 rounded-lg border border-hairline bg-surface-raised">
      <svg viewBox="0 0 176 56" className="h-full w-full p-2">
        {variant === 'row' ? (
          <>
            <rect x="6" y="20" width="34" height="16" rx="3" className="fill-surface-sunken stroke-stroke" />
            <rect x="62" y="20" width="34" height="16" rx="3" className="fill-surface-sunken stroke-stroke" />
            <rect x="118" y="18" width="36" height="20" rx="3" className="fill-none" stroke="var(--ds-green-500)" />
            <line x1="40" y1="28" x2="62" y2="28" stroke="var(--ds-green-500)" />
            <line x1="96" y1="28" x2="118" y2="28" stroke="var(--ds-green-500)" />
          </>
        ) : (
          <>
            <rect x="74" y="4" width="28" height="9" rx="2" className="fill-none" stroke="var(--ds-green-500)" />
            <line x1="88" y1="13" x2="36" y2="24" stroke="var(--ds-green-500)" />
            <line x1="88" y1="13" x2="88" y2="24" stroke="var(--fp-edge-promising)" />
            <line x1="88" y1="13" x2="140" y2="24" stroke="var(--ds-neutral-700)" />
            <rect x="22" y="24" width="28" height="8" rx="2" className="fill-surface-sunken stroke-stroke" />
            <rect x="74" y="24" width="28" height="8" rx="2" className="fill-surface-sunken stroke-stroke" />
            <rect x="126" y="24" width="28" height="8" rx="2" className="fill-surface-sunken stroke-stroke" />
            <rect x="8" y="42" width="24" height="7" rx="2" className="fill-surface-sunken stroke-stroke" />
            <rect x="40" y="42" width="24" height="7" rx="2" className="fill-surface-sunken stroke-stroke" />
            <rect x="74" y="42" width="24" height="7" rx="2" className="fill-surface-sunken stroke-stroke" />
          </>
        )}
      </svg>
      <button className="absolute bottom-1 right-1 text-ink-tertiary">
        <Maximize2 size={11} />
      </button>
    </div>
  )
}
