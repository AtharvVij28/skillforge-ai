import type { DemoQuestion } from '@/data/demoData'

export function AssessmentQuestion({
  question,
  index,
  total,
  selected,
  revealed,
  onSelect,
  onNext,
}: {
  question: DemoQuestion
  index: number
  total: number
  selected: number | null
  revealed: boolean
  onSelect: (optionIndex: number) => void
  onNext: () => void
}) {
  return (
    <section className="rounded-xl border border-line bg-panel p-6 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">
        Question {index + 1} of {total}
      </p>
      <h2 className="mt-3 font-display text-xl font-semibold leading-snug text-navy">{question.stem}</h2>
      <div className="mt-6 space-y-2">
        {question.options.map((option, optionIndex) => {
          const isSelected = selected === optionIndex
          const isCorrect = optionIndex === question.correctIndex
          let styles = 'border-line bg-white hover:border-ai/40'
          if (revealed && isCorrect) styles = 'border-success bg-emerald-50'
          else if (revealed && isSelected && !isCorrect) styles = 'border-danger bg-red-50'
          else if (isSelected) styles = 'border-ai bg-ai-soft'

          return (
            <button
              key={option}
              type="button"
              disabled={revealed}
              onClick={() => onSelect(optionIndex)}
              className={`w-full rounded-lg border px-4 py-3 text-left text-sm transition ${styles}`}
            >
              <span className="mr-2 font-semibold text-ink-muted">{String.fromCharCode(65 + optionIndex)}.</span>
              {option}
            </button>
          )
        })}
      </div>
      {revealed && (
        <div className="mt-5 rounded-lg border border-line bg-surface p-4 text-sm">
          <p className={`font-semibold ${selected === question.correctIndex ? 'text-success' : 'text-danger'}`}>
            {selected === question.correctIndex ? 'Correct!' : 'Not quite.'}
          </p>
          <p className="mt-2 text-ink-muted">{question.explanation}</p>
        </div>
      )}
      <button
        type="button"
        disabled={selected === null}
        onClick={onNext}
        className="mt-6 rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid disabled:opacity-50"
      >
        {revealed ? (index + 1 === total ? 'Finish assessment' : 'Next question') : 'Check answer'}
      </button>
    </section>
  )
}
