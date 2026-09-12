import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { ChartCard } from '@/components/demo/ChartCard'
import { demoAdmin } from '@/data/demoData'

export function AdminAnalyticsPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Skill Analytics</h1>
        <p className="mt-1 text-ink-muted">Organisation-level gap concentration from demo data.</p>
      </header>
      <ChartCard title="Learners affected by top gaps">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={demoAdmin.topSkillGaps}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="learners" fill="#4f46e5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  )
}
