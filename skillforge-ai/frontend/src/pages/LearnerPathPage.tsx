import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { getApiErrorMessage } from '@/services/apiErrors'
import {
  fetchLearningPath,
  generateLearningPath,
  type LearningPath,
} from '@/services/learningPath'

export function LearnerPathPage() {
  const [path, setPath] = useState<LearningPath | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function load(regenerate = false) {
    setLoading(true)
    setError(null)
    try {
      const data = regenerate ? await generateLearningPath() : await fetchLearningPath()
      setPath(data)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not load your learning path.'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-line bg-panel p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Study plan</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Your learning path</h1>
        <p className="mt-2 max-w-3xl text-sm text-ink-muted">
          Materials are ranked from your latest skill gaps. Complete an assessment first for a tighter match.
        </p>
        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => void load(true)}
            className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white"
          >
            Refresh path
          </button>
          <Link to="/assess" className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
            Take an assessment
          </Link>
        </div>
      </header>

      {error && <p className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-warn">{error}</p>}
      {loading && <p className="text-sm text-ink-muted">Loading your path…</p>}
      {path?.message && <p className="rounded-xl border border-line bg-panel p-5 text-sm text-ink-muted">{path.message}</p>}

      <div className="space-y-4">
        {path?.items.map((item) => (
          <article key={item.id} className="rounded-2xl border border-line bg-panel p-6 shadow-sm">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">Step {item.rank}</p>
            <h2 className="mt-2 font-display text-xl font-semibold text-navy">{item.title}</h2>
            <p className="mt-1 text-sm text-ink-muted">
              {item.competency_name}
              {item.estimated_effort_hours ? ` · ~${item.estimated_effort_hours} hours` : ''}
              {item.is_mock ? ' · catalog resource' : ''}
            </p>
            <p className="mt-3 text-sm leading-relaxed text-ink">{item.reason}</p>
            {item.url && (
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                className="mt-4 inline-flex rounded-md bg-navy px-4 py-2 text-sm font-semibold text-white"
              >
                Open study material
              </a>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}
