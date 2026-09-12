import { demoAdmin } from '@/data/demoData'

export function AdminLearnersPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Learners</h1>
        <p className="mt-1 text-ink-muted">Sample cohort for the administrator demo.</p>
      </header>
      <div className="overflow-x-auto rounded-xl border border-line bg-panel shadow-sm">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="bg-surface text-xs uppercase tracking-wide text-ink-muted">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Competency</th>
              <th className="px-4 py-3">Open gaps</th>
            </tr>
          </thead>
          <tbody>
            {demoAdmin.learners.map((learner) => (
              <tr key={learner.name} className="border-t border-line">
                <td className="px-4 py-3 font-medium">{learner.name}</td>
                <td className="px-4 py-3">{learner.department}</td>
                <td className="px-4 py-3">{learner.competency}%</td>
                <td className="px-4 py-3">{learner.gaps}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
