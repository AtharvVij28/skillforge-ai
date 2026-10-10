import { type FormEvent, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/services/apiErrors'
import { isAdminRole } from '@/utils/roles'

export function LoginPage() {
  const { login } = useAuth()
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
      if (isAdminRole(user.role.code, user.role.name)) {
        navigate('/admin', { replace: true })
        return
      }
      navigate(from && from !== '/login' && from !== '/status' && !from.startsWith('/admin') ? from : '/home', {
        replace: true,
      })
    } catch (err) {
      setError(getApiErrorMessage(err, 'Login failed. Check your email and password.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">Sign in</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Sign in to your learner account after confirming your email.
      </p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">Password</span>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
        {error && <p className="text-sm text-warn">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-dark disabled:opacity-60"
        >
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p className="mt-4 text-sm text-ink-muted">
        <Link to="/forgot-password" className="font-medium text-accent hover:underline">
          Forgot password?
        </Link>
      </p>

      <p className="mt-4 text-sm text-ink-muted">
        New here?{' '}
        <Link to="/register" className="font-medium text-accent hover:underline">
          Create an account
        </Link>
      </p>
    </section>
  )
}
