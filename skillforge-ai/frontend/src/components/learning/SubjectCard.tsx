import type { LearningSubject } from '@/data/learningCatalog'

type SubjectCardProps = {
  subject: LearningSubject
  selected: boolean
  onToggle: (subjectId: string) => void
}

export function SubjectCard({ subject, selected, onToggle }: SubjectCardProps) {
  return (
    <button
      type="button"
      onClick={() => onToggle(subject.id)}
      aria-pressed={selected}
      className={[
        'group rounded-xl border p-4 text-left transition duration-200',
        selected
          ? 'border-ai bg-ai-soft shadow-sm ring-2 ring-ai/25'
          : 'border-line bg-panel hover:-translate-y-0.5 hover:border-ai/35 hover:shadow-sm',
      ].join(' ')}
    >
      <div className="flex items-start gap-3">
        <span
          className={[
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-lg text-xs font-bold tracking-wide',
            selected ? 'bg-ai text-white' : 'bg-surface text-navy group-hover:bg-ai-soft',
          ].join(' ')}
        >
          {subject.icon}
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-semibold text-navy">{subject.name}</h3>
            <span
              className={[
                'rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
                selected ? 'bg-ai text-white' : 'bg-surface text-ink-muted',
              ].join(' ')}
            >
              {selected ? 'Selected' : 'Select'}
            </span>
          </div>
          <p className="mt-1 text-sm leading-relaxed text-ink-muted">{subject.description}</p>
        </div>
      </div>
    </button>
  )
}
