import { ProgressBar } from '@/components/demo/ProgressBar'
import type { DemoCompetency } from '@/data/demoData'

export function CompetencyCard({ competency }: { competency: DemoCompetency }) {
  const tone =
    competency.status === 'Priority gap' ? 'danger' : competency.status === 'Developing' ? 'amber' : 'success'

  return (
    <article className="rounded-xl border border-line bg-panel p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-ink">{competency.name}</p>
          <p className="text-xs text-ink-muted">{competency.category}</p>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-[11px] font-semibold ${
            tone === 'danger'
              ? 'bg-red-50 text-danger'
              : tone === 'amber'
                ? 'bg-amber-50 text-amber'
                : 'bg-emerald-50 text-success'
          }`}
        >
          {competency.status}
        </span>
      </div>
      <div className="mt-3 flex justify-between text-xs text-ink-muted">
        <span>Current {competency.currentLevel.toFixed(1)}</span>
        <span>Target {competency.targetLevel.toFixed(1)}</span>
      </div>
      <div className="mt-2">
        <ProgressBar value={(competency.currentLevel / competency.targetLevel) * 100} tone={tone} />
      </div>
      <p className="mt-2 text-sm font-medium text-navy">{competency.currentPercent}%</p>
    </article>
  )
}
