import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { ProgressBar } from '@/components/learning/ProgressBar'
import { getApiErrorMessage } from '@/services/apiErrors'
import {
  analyzeSkillGaps,
  fetchLatestSkillGaps,
  toScore,
  type SkillGapAnalysis,
  type SkillGapItem,
} from '@/services/skillGaps'

const priorityStyles: Record<string, string> = {
  HIGH: 'border-red-200 bg-red-50/70',
  MEDIUM: 'border-amber-200 bg-amber-50/60',
  LOW: 'border-emerald-200 bg-emerald-50/50',
}

const priorityBadge: Record<string, string> = {
  HIGH: 'bg-danger text-white',
  MEDIUM: 'bg-amber text-white',
  LOW: 'bg-success text-white',
}

function GapCard({ item }: { item: SkillGapItem }) {
  const current = toScore(item.current_score)
  const required = toScore(item.required_score)
  const gap = toScore(item.gap)
  return (
    <article className={`rounded-xl border p-5 shadow-sm ${priorityStyles[item.priority] ?? 'border-line bg-panel'}`}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="font-semibold text-ink">{item.competency_name}</h3>
          <p className="mt-0.5 text-xs uppercase tracking-wide text-ink-muted">
            {item.status === 'MET' ? 'Requirement met' : 'Open gap'} · {item.source}
          </p>
        </div>
        <span
          className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide ${priorityBadge[item.priority] ?? 'bg-navy text-white'}`}
        >
          {item.priority}
        </span>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
        <div>
          <dt className="text-xs text-ink-muted">Current</dt>
          <dd className="font-semibold">{current.toFixed(1)}</dd>
        </div>
        <div>
          <dt className="text-xs text-ink-muted">Required</dt>
          <dd className="font-semibold">{required.toFixed(1)}</dd>
        </div>
        <div>
          <dt className="text-xs text-ink-muted">Gap</dt>
          <dd className="font-semibold text-danger">{gap.toFixed(1)}</dd>
        </div>
      </dl>
      <p className="mt-3 text-sm leading-relaxed text-ink-muted">{item.explanation}</p>
    </article>
  )
}

export function LearnerSkillGapsPage() {
  const [analysis, setAnalysis] = useState<SkillGapAnalysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function loadLatest() {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchLatestSkillGaps()
      setAnalysis(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not load skill gaps.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLatest()
  }, [])

  async function handleAnalyze() {
    setAnalyzing(true)
    setError(null)
    try {
      const data = await analyzeSkillGaps()
      setAnalysis(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not analyze skill gaps.'))
    } finally {
      setAnalyzing(false)
    }
  }

  const chartData = useMemo(
    () =>
      (analysis?.items ?? []).map((item) => ({
        name: item.competency_name,
        gap: toScore(item.gap),
      })),
    [analysis],
  )

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-line bg-panel p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Live analysis</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Skill gaps</h1>
        <p className="mt-2 max-w-3xl text-sm text-ink-muted">
          Gaps are calculated by comparing your current competency estimate with the requirements of your job
          role. Every card shows the numbers and a written explanation — not an unexplained AI score.
        </p>
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => void handleAnalyze()}
            disabled={analyzing}
            className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid disabled:opacity-50"
          >
            {analyzing ? 'Analyzing…' : 'Analyze skill gaps'}
          </button>
          <Link to="/account" className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
            Edit profile
          </Link>
        </div>
        {analysis && (
          <div className="mt-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-ink-muted">
                Job role: <span className="font-medium text-ink">{analysis.job_role ?? 'Not set'}</span>
                {analysis.open_gaps > 0 ? ` · ${analysis.open_gaps} open gap${analysis.open_gaps === 1 ? '' : 's'}` : ''}
              </span>
              <span className="font-semibold text-navy">{analysis.profile_completion_pct}% profile</span>
            </div>
            <ProgressBar value={analysis.profile_completion_pct} />
          </div>
        )}
      </header>

      {error && (
        <p className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-warn">{error}</p>
      )}

      {loading && <p className="text-sm text-ink-muted">Loading saved analysis…</p>}

      {analysis?.message && (
        <section className="rounded-2xl border border-line bg-panel p-6 text-sm text-ink-muted shadow-sm">
          {analysis.message}{' '}
          {!analysis.job_role && (
            <Link to="/account" className="font-semibold text-navy">
              Add a job role
            </Link>
          )}
        </section>
      )}

      {chartData.length > 0 && (
        <section className="rounded-2xl border border-line bg-panel p-6 shadow-sm">
          <h2 className="font-display text-lg font-semibold text-navy">Required minus current</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical" margin={{ left: 16, right: 16 }}>
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="gap" fill="#b91c1c" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      )}

      {analysis && analysis.items.length > 0 && (
        <div className="grid gap-4 lg:grid-cols-2">
          {analysis.items.map((item) => (
            <GapCard key={item.competency_id} item={item} />
          ))}
        </div>
      )}
    </div>
  )
}
