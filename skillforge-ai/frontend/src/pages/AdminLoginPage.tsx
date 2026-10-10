import { type FormEvent, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/services/apiErrors'
import { isAdminRole } from '@/utils/roles'

export function AdminLoginPage() {
  const { login, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      const user = await login({ email: email.trim(), password })
      if (!isAdminRole(user.role.code, user.role.name)) {
        await logout()
        setError('This portal is for administrators only. Use learner sign-in instead.')
        return
      }
      const next = from && from.startsWith('/admin') ? from : '/admin'
      navigate(next, { replace: true })
    } catch (err) {
      setError(getApiErrorMessage(err, 'Admin sign-in failed. Check your email and password.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Administration</p>
      <h1 className="mt-2 font-display text-2xl font-semibold text-ink">Admin sign in</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Separate from learner registration. Only accounts with the ADMIN role can enter this portal.
      </p>

      <form className="mt-6 space-y-4" onSubmit={(event) => void handleSubmit(event)}>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">Admin email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
        {error && <p className="text-sm text-warn">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid disabled:opacity-60"
        >
          {submitting ? 'Signing in…' : 'Sign in as admin'}
        </button>
      </form>

      <p className="mt-4 text-sm text-ink-muted">
        Learner?{' '}
        <Link to="/login" className="font-medium text-accent hover:underline">
          Go to learner sign-in
        </Link>
      </p>
    </section>
  )
}
