import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Link } from 'react-router-dom'

import { ChartCard } from '@/components/demo/ChartCard'
import { StatCard } from '@/components/demo/StatCard'
import { demoAdmin, frameworkCategories } from '@/data/demoData'

export function AdminOverviewPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Administrator overview</h1>
        <p className="mt-1 text-ink-muted">
          Mock cohort analytics for the Round 1 demo. No admin backend writes are performed.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Learners" value={demoAdmin.kpis.totalLearners.toLocaleString('en-IN')} />
        <StatCard label="Average Competency" value={`${demoAdmin.kpis.averageCompetency}%`} />
        <StatCard label="Critical Skill Gaps" value={String(demoAdmin.kpis.criticalSkillGaps)} />
        <StatCard label="Assessments Completed" value={demoAdmin.kpis.assessmentsCompleted.toLocaleString('en-IN')} />
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <ChartCard title="Competency distribution" subtitle="Average score by framework category">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={demoAdmin.competencyDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#16325c" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Top skill gaps" subtitle="Learners with a high-priority gap">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={demoAdmin.topSkillGaps} layout="vertical" margin={{ left: 16 }}>
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Bar dataKey="learners" fill="#b91c1c" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Learning engagement" subtitle="Demo hours recorded (not live LMS data)">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={demoAdmin.engagement}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="hours" stroke="#4f46e5" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <section className="rounded-xl border border-line bg-panel p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg font-semibold text-navy">Department overview</h2>
          <Link to="/admin/learners" className="text-sm font-medium text-ai hover:underline">
            View learners
          </Link>
        </div>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-ink-muted">
              <tr>
                <th className="pb-2">Department</th>
                <th className="pb-2">Learners</th>
                <th className="pb-2">Avg competency</th>
              </tr>
            </thead>
            <tbody>
              {demoAdmin.departments.map((row) => (
                <tr key={row.name} className="border-t border-line">
                  <td className="py-2.5 font-medium">{row.name}</td>
                  <td>{row.learners}</td>
                  <td>{row.competency}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-xl border border-line bg-panel p-5 shadow-sm">
        <h2 className="font-display text-lg font-semibold text-navy">Competency Framework</h2>
        <p className="mt-1 text-sm text-ink-muted">Configurable categories — not hardcoded into business rules.</p>
        <div className="mt-4 grid gap-3 md:grid-cols-5">
          {frameworkCategories.map((category) => (
            <div key={category.name} className="rounded-lg border border-line bg-surface p-3">
              <p className="text-sm font-semibold text-navy">{category.name}</p>
              <p className="mt-1 text-xs text-ink-muted">{category.items.length} competencies</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
