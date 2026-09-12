import { useDemo } from '@/context/DemoContext'

export function DemoEntryPage() {
  const { enterLearner, enterAdmin } = useDemo()

  return (
    <section className="mx-auto max-w-3xl space-y-8">
      <div className="text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Hackathon demo</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Enter SkillForge AI</h1>
        <p className="mt-2 text-ink-muted">
          Mock demo state only — does not change backend authentication or live user records.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <button
          type="button"
          onClick={enterLearner}
          className="rounded-2xl border border-line bg-panel p-8 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-ai/40 hover:shadow-md"
        >
          <p className="text-xs font-semibold uppercase tracking-wide text-ai">Learner</p>
          <p className="mt-3 font-display text-2xl font-semibold text-navy">Enter Learner Demo</p>
          <p className="mt-2 text-sm text-ink-muted">
            Profile, skill gaps, personalized path, assessment loop and explainable AI insights.
          </p>
        </button>
        <button
          type="button"
          onClick={enterAdmin}
          className="rounded-2xl border border-line bg-panel p-8 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-navy/30 hover:shadow-md"
        >
          <p className="text-xs font-semibold uppercase tracking-wide text-navy">Administrator</p>
          <p className="mt-3 font-display text-2xl font-semibold text-navy">Enter Admin Demo</p>
          <p className="mt-2 text-sm text-ink-muted">
            Cohort competency, critical gaps, engagement and a configurable competency framework.
          </p>
        </button>
      </div>
    </section>
  )
}
