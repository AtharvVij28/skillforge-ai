import { Link } from 'react-router-dom'

import { ProgressBar } from '@/components/learning/ProgressBar'
import { getRecommendationForSubjects, getSubjectById } from '@/data/learningCatalog'
import {
  getContinueLearning,
  getSelectedSubjectIds,
  getSubjectProgress,
} from '@/services/subjectProgressService'

type LearningDashboardProps = {
  userId: string
  userFirstName: string
}

export function LearningDashboard({ userId, userFirstName }: LearningDashboardProps) {
  const subjectIds = getSelectedSubjectIds(userId)
  const progress = getSubjectProgress(userId)
  const continueItem = getContinueLearning(userId)
  const continueSubject = continueItem ? getSubjectById(continueItem.subjectId) : undefined
  const recommendation = getRecommendationForSubjects(subjectIds)

  return (
    <div className="demo-fade space-y-6">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Learning home</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy sm:text-4xl">
          Welcome back, {userFirstName} 👋
        </h1>
        <p className="mt-2 text-ink-muted">Pick up where you left off.</p>
      </header>

      {continueItem && (
        <section className="overflow-hidden rounded-2xl border border-line bg-panel shadow-sm">
          <div className="grid lg:grid-cols-[1.3fr_0.7fr]">
            <div className="space-y-4 p-6 sm:p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">Continue learning</p>
              <h2 className="font-display text-2xl font-semibold text-navy">{continueItem.courseTitle}</h2>
              <p className="text-sm text-ink-muted">
                Chapter {continueItem.currentChapter} of {continueItem.totalChapters}
                {continueSubject ? ` · ${continueSubject.name}` : ''}
              </p>
              <div>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-ink-muted">Progress</span>
                  <span className="font-semibold text-navy">{continueItem.progressPercent}%</span>
                </div>
                <ProgressBar value={continueItem.progressPercent} />
              </div>
              <p className="text-sm text-ink-muted">
                Last activity: <span className="font-medium text-ink">{continueItem.lastActivity}</span>
              </p>
              <Link
                to="/learning"
                className="inline-flex rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
              >
                Continue Learning
              </Link>
            </div>
            <div className="border-t border-line bg-[linear-gradient(160deg,#0b1f3a_0%,#16325c_55%,#312e81_100%)] p-6 text-white sm:p-8 lg:border-l lg:border-t-0">
              <p className="text-xs uppercase tracking-[0.16em] text-white/60">Next up</p>
              <p className="mt-3 text-lg font-semibold">{continueItem.lastActivity}</p>
              <p className="mt-2 text-sm text-white/70">
                You&apos;re {continueItem.progressPercent}% through this course. Keep the learning loop moving.
              </p>
            </div>
          </div>
        </section>
      )}

      <section className="rounded-2xl border border-line bg-panel p-6 shadow-sm">
        <h2 className="font-display text-xl font-semibold text-navy">Your subjects</h2>
        <p className="mt-1 text-sm text-ink-muted">Progress across the subjects you selected.</p>
        <div className="mt-5 space-y-4">
          {progress.map((item) => {
            const subject = getSubjectById(item.subjectId)
            return (
              <div key={item.subjectId}>
                <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                  <span className="font-medium text-ink">{subject?.name ?? item.subjectId}</span>
                  <span className="text-ink-muted">{item.progressPercent}%</span>
                </div>
                <ProgressBar value={item.progressPercent} />
              </div>
            )
          })}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-2xl border border-line bg-panel p-6 shadow-sm">
          <h2 className="font-display text-lg font-semibold text-navy">Recent activity</h2>
          <ul className="mt-4 space-y-3 text-sm">
            {progress.slice(0, 3).map((item) => {
              const subject = getSubjectById(item.subjectId)
              return (
                <li key={item.subjectId} className="rounded-lg border border-line bg-surface px-3 py-3">
                  <p className="font-medium text-ink">{item.lastActivity}</p>
                  <p className="mt-0.5 text-ink-muted">
                    {subject?.name ?? item.subjectId} · Chapter {item.currentChapter}
                  </p>
                </li>
              )
            })}
          </ul>
        </section>

        <section className="rounded-2xl border border-ai/20 bg-ai-soft/60 p-6 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">Recommended for you</p>
          <h2 className="mt-2 font-display text-xl font-semibold text-navy">{recommendation.title}</h2>
          <p className="mt-2 text-sm leading-relaxed text-ink-muted">{recommendation.reason}</p>
          <Link
            to="/learning"
            className="mt-5 inline-flex rounded-md border border-ai/30 bg-white px-4 py-2 text-sm font-semibold text-navy transition hover:border-ai"
          >
            View learning path
          </Link>
        </section>
      </div>
    </div>
  )
}
