import { type FormEvent, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { getApiErrorMessage } from '@/services/apiErrors'
import { resetPassword } from '@/services/auth'

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const result = await resetPassword(token, password)
      setMessage(result.message)
    } catch (err) {
      setError(getApiErrorMessage(err, 'This reset link is invalid or has expired.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">Choose a new password</h1>
      <p className="mt-2 text-sm text-ink-muted">
        This form never shows your previous password. The reset link can be used only once.
      </p>
      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">New password</span>
          <input
            type="password"
            required
            minLength={8}
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
        {error && <p className="text-sm text-warn">{error}</p>}
        {message && <p className="text-sm text-success">{message}</p>}
        <button
          type="submit"
          disabled={submitting || !token}
          className="w-full rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
        >
          {submitting ? 'Updating…' : 'Update password'}
        </button>
      </form>
      <p className="mt-4 text-sm text-ink-muted">
        <Link to="/login" className="font-medium text-accent hover:underline">
          Sign in
        </Link>
      </p>
    </section>
  )
}
