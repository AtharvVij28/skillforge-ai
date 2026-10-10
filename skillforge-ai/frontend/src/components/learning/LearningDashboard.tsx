import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ProgressBar } from '@/components/learning/ProgressBar'
import { getSubjectById } from '@/data/learningCatalog'
import { getApiErrorMessage } from '@/services/apiErrors'
import { fetchLearningPath, generateLearningPath, type LearningPath } from '@/services/learningPath'
import { analyzeSkillGaps, fetchLatestSkillGaps, toScore, type SkillGapAnalysis } from '@/services/skillGaps'
import { getSelectedSubjectIds } from '@/services/subjectProgressService'

type LearningDashboardProps = {
  userId: string
  userFirstName: string
}

export function LearningDashboard({ userId, userFirstName }: LearningDashboardProps) {
  const subjectIds = getSelectedSubjectIds(userId)
  const [gaps, setGaps] = useState<SkillGapAnalysis | null>(null)
  const [path, setPath] = useState<LearningPath | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    async function load() {
      try {
        let gapData = await fetchLatestSkillGaps()
        if (!gapData.items.length) {
          gapData = await analyzeSkillGaps()
        }
        let pathData = await fetchLearningPath()
        if (!pathData.items.length) {
          pathData = await generateLearningPath()
        }
        if (cancelled) return
        setGaps(gapData)
        setPath(pathData)
      } catch (err) {
        if (!cancelled) setError(getApiErrorMessage(err, 'Could not load your competency dashboard.'))
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const items = gaps?.items ?? []
  const topGap = [...items].sort((a, b) => toScore(b.gap) - toScore(a.gap))[0]
  const nextResource = path?.items[0]

  return (
    <div className="demo-fade space-y-6">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Learning home</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy sm:text-4xl">
          Welcome back, {userFirstName} 👋
        </h1>
        <p className="mt-2 text-ink-muted">
          Your dashboard is based on your assessment results
          {gaps?.open_gaps ? ` · ${gaps.open_gaps} open gap${gaps.open_gaps === 1 ? '' : 's'}` : ''}.
        </p>
      </header>

      {error && <p className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-warn">{error}</p>}

      {topGap && (
        <section className="overflow-hidden rounded-2xl border border-line bg-panel shadow-sm">
          <div className="grid lg:grid-cols-[1.3fr_0.7fr]">
            <div className="space-y-4 p-6 sm:p-8">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">Priority gap</p>
              <h2 className="font-display text-2xl font-semibold text-navy">{topGap.competency_name}</h2>
              <p className="text-sm text-ink-muted">{topGap.explanation}</p>
              <div>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="text-ink-muted">
                    Current {toScore(topGap.current_score).toFixed(0)} / required{' '}
                    {toScore(topGap.required_score).toFixed(0)}
                  </span>
                  <span className="font-semibold text-navy">Gap {toScore(topGap.gap).toFixed(0)}</span>
                </div>
                <ProgressBar value={toScore(topGap.current_score)} />
              </div>
              <Link
                to="/gaps"
                className="inline-flex rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
              >
                View all skill gaps
              </Link>
            </div>
            <div className="border-t border-line bg-[linear-gradient(160deg,#0b1f3a_0%,#16325c_55%,#312e81_100%)] p-6 text-white sm:p-8 lg:border-l lg:border-t-0">
              <p className="text-xs uppercase tracking-[0.16em] text-white/60">Recommended next</p>
              <p className="mt-3 text-lg font-semibold">{nextResource?.title ?? 'Open your learning path'}</p>
              <p className="mt-2 text-sm text-white/70">
                {nextResource?.reason ?? 'Study material is ranked from the gaps in your latest assessment.'}
              </p>
              <Link
                to="/path"
                className="mt-6 inline-flex rounded-md bg-white/15 px-4 py-2 text-sm font-semibold text-white"
              >
                Continue learning
              </Link>
            </div>
          </div>
        </section>
      )}

      <section className="rounded-2xl border border-line bg-panel p-6 shadow-sm">
        <h2 className="font-display text-xl font-semibold text-navy">Your subjects</h2>
        <p className="mt-1 text-sm text-ink-muted">Live competency estimates from your assessment.</p>
        <div className="mt-5 space-y-4">
          {(items.length ? items : subjectIds.map((id) => ({ id }))).map((item) => {
            if ('competency_name' in item) {
              return (
                <div key={item.competency_id}>
                  <div className="mb-1.5 flex items-center justify-between gap-3 text-sm">
                    <span className="font-medium text-ink">{item.competency_name}</span>
                    <span className="text-ink-muted">{toScore(item.current_score).toFixed(0)}%</span>
                  </div>
                  <ProgressBar value={toScore(item.current_score)} />
                </div>
              )
            }
            const subject = getSubjectById(item.id)
            return (
              <div key={item.id}>
                <p className="text-sm font-medium text-ink">{subject?.name ?? item.id}</p>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
