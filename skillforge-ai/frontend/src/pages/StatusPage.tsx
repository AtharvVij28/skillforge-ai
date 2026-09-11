import { useEffect, useState } from 'react'

import { fetchHealth, type HealthResponse } from '@/services/api'

type LoadState = 'idle' | 'loading' | 'ok' | 'error'

export function StatusPage() {
  const [state, setState] = useState<LoadState>('idle')
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      setState('loading')
      setError(null)
      try {
        const data = await fetchHealth()
        if (!cancelled) {
          setHealth(data)
          setState('ok')
        }
      } catch (err) {
        if (!cancelled) {
          setHealth(null)
          setState('error')
          setError(err instanceof Error ? err.message : 'Unable to reach backend')
        }
      }
    }

    void load()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="space-y-4">
      <div>
        <h1 className="font-display text-3xl font-semibold text-ink">System status</h1>
        <p className="mt-2 text-ink-muted">
          Verifies frontend-to-backend connectivity for the Phase 1 environment.
        </p>
      </div>

      <div className="rounded-xl border border-line bg-panel p-6 shadow-sm">
        {state === 'loading' && <p className="text-ink-muted">Checking `/api/health`…</p>}

        {state === 'ok' && health && (
          <dl className="grid gap-3 sm:grid-cols-2">
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">Status</dt>
              <dd className="mt-1 font-semibold text-accent">{health.status}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">Service</dt>
              <dd className="mt-1 font-semibold">{health.service}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">Environment</dt>
              <dd className="mt-1 font-semibold">{health.environment}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">Phase</dt>
              <dd className="mt-1 font-semibold">{health.phase}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">AI provider</dt>
              <dd className="mt-1 font-semibold">{health.ai_provider}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-ink-muted">Course providers</dt>
              <dd className="mt-1 font-semibold">{health.course_provider_mode}</dd>
            </div>
          </dl>
        )}

        {state === 'error' && (
          <div className="space-y-2">
            <p className="font-semibold text-warn">Backend unreachable</p>
            <p className="text-sm text-ink-muted">{error}</p>
            <p className="text-sm text-ink-muted">
              Start the API with <code className="rounded bg-surface px-1.5 py-0.5">uvicorn app.main:app --reload</code>{' '}
              from the <code className="rounded bg-surface px-1.5 py-0.5">backend</code> folder.
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
