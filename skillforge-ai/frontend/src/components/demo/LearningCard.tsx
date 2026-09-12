import { ProgressBar } from '@/components/demo/ProgressBar'
import type { DemoLearningResource } from '@/data/demoData'

export function LearningCard({
  resource,
  onAction,
}: {
  resource: DemoLearningResource
  onAction: () => void
}) {
  const priorityClass =
    resource.priority === 'High'
      ? 'bg-red-50 text-danger'
      : resource.priority === 'Medium'
        ? 'bg-amber-50 text-amber'
        : 'bg-emerald-50 text-success'

  return (
    <article className="flex h-full flex-col rounded-xl border border-line bg-panel p-5 shadow-sm transition hover:border-ai/30 hover:shadow-md">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-ai">{resource.providerLabel}</p>
      <h3 className="mt-2 font-display text-xl font-semibold text-navy">{resource.title}</h3>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className={`rounded-full px-2.5 py-0.5 font-semibold ${priorityClass}`}>Priority: {resource.priority}</span>
        <span className="rounded-full bg-surface px-2.5 py-0.5 text-ink-muted">{resource.difficulty}</span>
        <span className="rounded-full bg-surface px-2.5 py-0.5 text-ink-muted">{resource.durationHours} hours</span>
      </div>
      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{resource.reason}</p>
      <div className="mt-4">
        <div className="mb-1 flex justify-between text-xs text-ink-muted">
          <span>Progress</span>
          <span>{resource.progress}%</span>
        </div>
        <ProgressBar value={resource.progress} tone="ai" />
      </div>
      <button
        type="button"
        onClick={onAction}
        className="mt-auto w-full rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
      >
        {resource.action}
      </button>
    </article>
  )
}
