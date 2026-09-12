import { InsightCard } from '@/components/demo/InsightCard'
import { demoInsights, demoLearningPath, demoUser } from '@/data/demoData'

export function InsightsPage() {
  return (
    <div className="space-y-6">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">SkillForge AI</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-navy">AI Insights</h1>
        <p className="mt-2 max-w-3xl text-ink-muted">
          Insights are grounded in the demo profile, role requirements, gaps and learning history. Claims stay
          explainable — nothing is presented as a live external model score.
        </p>
      </header>

      <InsightCard title="Profile reading">
        <p>{demoInsights.headline}</p>
      </InsightCard>

      <div className="grid gap-4 md:grid-cols-2">
        {demoInsights.items.map((item) => (
          <InsightCard key={item} title="Explainable finding">
            {item}
          </InsightCard>
        ))}
      </div>

      <section className="rounded-xl border border-line bg-panel p-6 shadow-sm">
        <h2 className="font-display text-xl font-semibold text-navy">Why this recommendation?</h2>
        <p className="mt-1 text-sm text-ink-muted">
          {demoLearningPath[0].title} for {demoUser.targetRole}
        </p>
        <ol className="mt-4 list-decimal space-y-2 pl-5 text-sm leading-relaxed text-ink">
          {demoInsights.whyThisRecommendation.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ol>
      </section>
    </div>
  )
}
