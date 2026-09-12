import type { DemoSkillGap } from '@/data/demoData'

export function SkillGapCard({ gap }: { gap: DemoSkillGap }) {
  const styles = {
    High: 'border-red-200 bg-red-50/70',
    Medium: 'border-amber-200 bg-amber-50/60',
    Low: 'border-emerald-200 bg-emerald-50/50',
  }
  const badge = {
    High: 'bg-danger text-white',
    Medium: 'bg-amber text-white',
    Low: 'bg-success text-white',
  }

  return (
    <article className={`rounded-xl border p-5 shadow-sm ${styles[gap.priority]}`}>
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-ink">{gap.name}</h3>
        <span className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ${badge[gap.priority]}`}>
          {gap.priority}
        </span>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
        <div>
          <dt className="text-xs text-ink-muted">Current</dt>
          <dd className="font-semibold">{gap.current.toFixed(1)}</dd>
        </div>
        <div>
          <dt className="text-xs text-ink-muted">Required</dt>
          <dd className="font-semibold">{gap.required.toFixed(1)}</dd>
        </div>
        <div>
          <dt className="text-xs text-ink-muted">Gap</dt>
          <dd className="font-semibold text-danger">{gap.gap.toFixed(1)}</dd>
        </div>
      </dl>
      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{gap.explanation}</p>
    </article>
  )
}
