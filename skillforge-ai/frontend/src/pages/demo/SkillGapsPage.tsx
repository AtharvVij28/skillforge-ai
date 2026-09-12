import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { ChartCard } from '@/components/demo/ChartCard'
import { SkillGapCard } from '@/components/demo/SkillGapCard'
import { demoSkillGaps } from '@/data/demoData'

export function SkillGapsPage() {
  const chartData = demoSkillGaps.map((gap) => ({ name: gap.name.replace(' & Database Management', ''), gap: gap.gap }))

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">AI-Identified Skill Gaps</h1>
        <p className="mt-2 max-w-3xl text-ink-muted">
          Skill gaps are calculated by comparing your current competency level with the requirements of your target
          role. Every card includes the numbers and an explanation — not an unexplained AI score.
        </p>
      </header>

      <ChartCard title="Gap analysis" subtitle="Required minus current proficiency">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
            <XAxis type="number" domain={[0, 1.6]} tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="gap" fill="#b91c1c" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid gap-4 lg:grid-cols-2">
        {demoSkillGaps.map((gap) => (
          <SkillGapCard key={gap.id} gap={gap} />
        ))}
      </div>
    </div>
  )
}
