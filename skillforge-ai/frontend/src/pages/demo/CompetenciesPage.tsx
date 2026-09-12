import { PolarAngleAxis, PolarGrid, PolarRadiusAxis, Radar, RadarChart, ResponsiveContainer } from 'recharts'

import { ChartCard } from '@/components/demo/ChartCard'
import { CompetencyCard } from '@/components/demo/CompetencyCard'
import { demoCompetencies } from '@/data/demoData'

const categories = ['Statistical', 'Technical', 'Digital', 'Governance', 'Behavioural'] as const

export function CompetenciesPage() {
  const radarData = categories.map((category) => {
    const items = demoCompetencies.filter((item) => item.category === category)
    const avg = items.reduce((sum, item) => sum + item.currentPercent, 0) / (items.length || 1)
    return { category, score: Math.round(avg) }
  })

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Competencies</h1>
        <p className="mt-1 text-ink-muted">Current vs target proficiency across the configurable framework.</p>
      </header>

      <ChartCard title="Competency radar" subtitle="Category averages from the living profile">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" tick={{ fontSize: 12 }} />
            <PolarRadiusAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
            <Radar dataKey="score" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.28} />
          </RadarChart>
        </ResponsiveContainer>
      </ChartCard>

      {categories.map((category) => {
        const items = demoCompetencies.filter((item) => item.category === category)
        if (!items.length) return null
        return (
          <section key={category}>
            <h2 className="mb-3 font-semibold text-navy">{category}</h2>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {items.map((item) => (
                <CompetencyCard key={item.id} competency={item} />
              ))}
            </div>
          </section>
        )
      })}
    </div>
  )
}
