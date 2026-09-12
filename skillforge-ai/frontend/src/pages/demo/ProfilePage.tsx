import { ProgressBar } from '@/components/demo/ProgressBar'
import { ProfileSection } from '@/components/demo/ProfileSection'
import { demoCompetencies, demoKpis, demoTrainingHistory, demoUser } from '@/data/demoData'

export function ProfilePage() {
  return (
    <div className="space-y-6">
      <header className="rounded-xl border border-line bg-[linear-gradient(120deg,#0b1f3a,#16325c)] p-6 text-white">
        <p className="text-xs uppercase tracking-[0.16em] text-white/60">Living competency profile</p>
        <h1 className="mt-2 font-display text-3xl font-semibold">{demoUser.fullName}</h1>
        <p className="mt-1 text-white/80">
          {demoUser.designation} · {demoUser.department}
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-4">
        {[
          ['Experience', `${demoUser.experienceYears} years`],
          ['Education', demoUser.education],
          ['Training completed', String(demoUser.trainingCompleted)],
          ['Profile completion', `${demoUser.profileCompletion}%`],
        ].map(([label, value]) => (
          <div key={label} className="rounded-xl border border-line bg-panel p-4">
            <p className="text-xs text-ink-muted">{label}</p>
            <p className="mt-1 font-semibold text-navy">{value}</p>
          </div>
        ))}
      </div>

      <ProfileSection title="Professional Information">
        <dl className="grid gap-4 sm:grid-cols-2 text-sm">
          <div>
            <dt className="text-ink-muted">Role</dt>
            <dd className="font-medium">{demoUser.role}</dd>
          </div>
          <div>
            <dt className="text-ink-muted">Location</dt>
            <dd className="font-medium">{demoUser.location}</dd>
          </div>
          <div>
            <dt className="text-ink-muted">Email</dt>
            <dd className="font-medium">{demoUser.email}</dd>
          </div>
          <div>
            <dt className="text-ink-muted">Overall competency</dt>
            <dd className="font-medium">{demoKpis.overallCompetency}%</dd>
          </div>
        </dl>
      </ProfileSection>

      <ProfileSection title="Education & Experience">
        <p className="text-sm leading-relaxed text-ink-muted">
          {demoUser.education}. {demoUser.experienceYears} years supporting official statistics workflows in{' '}
          {demoUser.department}, with growing responsibility in statistical computing.
        </p>
      </ProfileSection>

      <ProfileSection title="Training History">
        <ul className="space-y-3">
          {demoTrainingHistory.map((item) => (
            <li key={item.title} className="flex justify-between gap-3 border-b border-line/80 pb-3 text-sm last:border-0">
              <span className="font-medium text-ink">{item.title}</span>
              <span className="text-ink-muted">
                {item.year} · {item.provider}
              </span>
            </li>
          ))}
        </ul>
      </ProfileSection>

      <ProfileSection title="Target Role">
        <p className="text-sm font-semibold text-navy">{demoUser.targetRole}</p>
        <p className="mt-2 text-sm text-ink-muted">
          Role-aware requirements drive skill-gap priority. Competency targets are configurable in the framework —
          not hardcoded in the product logic.
        </p>
      </ProfileSection>

      <ProfileSection title="Competency Summary">
        <div className="space-y-3">
          {demoCompetencies.slice(0, 6).map((item) => (
            <div key={item.id}>
              <div className="mb-1 flex justify-between text-sm">
                <span>{item.name}</span>
                <span className="text-ink-muted">{item.currentPercent}%</span>
              </div>
              <ProgressBar
                value={item.currentPercent}
                tone={item.status === 'Priority gap' ? 'danger' : item.status === 'Developing' ? 'amber' : 'success'}
              />
            </div>
          ))}
        </div>
      </ProfileSection>
    </div>
  )
}
