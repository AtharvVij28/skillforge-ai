import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { Link } from 'react-router-dom'

import { ChartCard } from '@/components/demo/ChartCard'
import { InsightCard } from '@/components/demo/InsightCard'
import { ProgressBar } from '@/components/demo/ProgressBar'
import { StatCard } from '@/components/demo/StatCard'
import { demoCompetencies, demoInsights, demoKpis, demoLearningPath, demoUser } from '@/data/demoData'

export function DashboardPage() {
  const chartData = demoCompetencies.slice(0, 6).map((item) => ({
    name: item.name.replace('Statistical Analysis', 'Stats').replace('Digital Governance', 'Gov'),
    score: item.currentPercent,
  }))

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Good morning, {demoUser.greetingName}</h1>
        <p className="mt-1 text-ink-muted">Here&apos;s your competency snapshot.</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Overall Competency" value={`${demoKpis.overallCompetency}%`} />
        <StatCard label="Competencies Assessed" value={String(demoKpis.competenciesAssessed)} />
        <StatCard label="Skill Gaps" value={String(demoKpis.skillGaps)} hint="1 high priority" />
        <StatCard label="Learning Progress" value={`${demoKpis.learningProgress}%`} />
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <ChartCard title="Competency Overview" subtitle="Current proficiency across core areas">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="score" fill="#4f46e5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <InsightCard title="AI Insight">
          <p>{demoInsights.headline}</p>
          <p className="mt-3">{demoInsights.items[0]}</p>
        </InsightCard>
      </div>

      <section className="rounded-xl border border-line bg-panel p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-ai">Recommended next step</p>
            <h2 className="mt-1 font-display text-xl font-semibold text-navy">{demoLearningPath[0].title}</h2>
            <p className="mt-1 text-sm text-ink-muted">{demoLearningPath[0].reason}</p>
          </div>
          <Link
            to="/learning"
            className="rounded-md bg-navy px-4 py-2 text-sm font-semibold text-white hover:bg-navy-mid"
          >
            Continue Learning
          </Link>
        </div>
        <div className="mt-4">
          <ProgressBar value={demoLearningPath[0].progress} />
        </div>
      </section>
    </div>
  )
}
