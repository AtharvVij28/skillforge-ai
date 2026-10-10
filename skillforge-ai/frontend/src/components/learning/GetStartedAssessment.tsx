import { Link } from 'react-router-dom'

import { getSubjectById } from '@/data/learningCatalog'
import { getSelectedSubjectIds } from '@/services/subjectProgressService'

type GetStartedAssessmentProps = {
  userId: string
  userFirstName: string
}

export function GetStartedAssessment({ userId, userFirstName }: GetStartedAssessmentProps) {
  const subjectIds = getSelectedSubjectIds(userId)
  const names = subjectIds.map((id) => getSubjectById(id)?.name ?? id)

  return (
    <div className="demo-fade mx-auto max-w-2xl space-y-6">
      <header className="rounded-2xl border border-line bg-panel px-8 py-12 text-center shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Next step</p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-navy">Get started with assessment</h1>
        <p className="mt-3 text-ink-muted">
          Welcome, {userFirstName}. Before we can show your dashboard, we need to assess the subjects you chose.
          Your competency gaps will be calculated from this attempt — not from mock data.
        </p>
        {names.length > 0 && (
          <p className="mt-4 text-sm font-medium text-ink">{names.join(' · ')}</p>
        )}
        <Link
          to="/assess?from=onboarding"
          className="mt-8 inline-flex rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
        >
          Start assessment
        </Link>
      </header>
    </div>
  )
}
