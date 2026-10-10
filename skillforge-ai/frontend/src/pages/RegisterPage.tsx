import { type FormEvent, useState } from 'react'
import { Link } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/services/apiErrors'
import { resendVerification } from '@/services/auth'

export function RegisterPage() {
  const { register } = useAuth()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submittedEmail, setSubmittedEmail] = useState<string | null>(null)
  const [resendMessage, setResendMessage] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [resending, setResending] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    setResendMessage(null)
    try {
      const trimmed = email.trim()
      await register({ email: trimmed, password, full_name: fullName.trim() })
      setSubmittedEmail(trimmed)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Registration failed. Please try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleResend() {
    if (!submittedEmail) return
    setResending(true)
    setError(null)
    try {
      const result = await resendVerification(submittedEmail)
      setResendMessage(result.message)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not resend the confirmation email.'))
    } finally {
      setResending(false)
    }
  }

  if (submittedEmail) {
    return (
      <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 shadow-sm">
        <h1 className="font-display text-2xl font-semibold text-ink">Check your email</h1>
        <p className="mt-3 text-sm text-ink-muted">
          We sent a confirmation link to <strong className="text-ink">{submittedEmail}</strong>. Open that message
          and confirm your address before signing in. The dashboard will not be available until this step is done.
        </p>
        {resendMessage && <p className="mt-4 text-sm text-success">{resendMessage}</p>}
        {error && <p className="mt-4 text-sm text-warn">{error}</p>}
        <button
          type="button"
          onClick={() => void handleResend()}
          disabled={resending}
          className="mt-6 w-full rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        >
          {resending ? 'Sending…' : 'Resend confirmation email'}
        </button>
        <p className="mt-4 text-sm text-ink-muted">
          Confirmed already?{' '}
          <Link to="/login" className="font-medium text-accent hover:underline">
            Sign in
          </Link>
        </p>
      </section>
    )
  }

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">Create account</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Use an email inbox you can access. We will send a confirmation link before you can sign in. Public
        registration creates a <strong>LEARNER</strong> account. You cannot register as ADMIN.
      </p>

      <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
        <label className="block space-y-1.5">
          <span className="text-sm font-medium text-ink">Full name</span>
          <input
            type="text"
            required
            maxLength={255}
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm outline-none focus:border-accent"
          />
        </label>
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
            minLength={8}
            maxLength={128}
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
          {submitting ? 'Sending confirmation…' : 'Register'}
        </button>
      </form>

      <p className="mt-4 text-sm text-ink-muted">
        Already registered?{' '}
        <Link to="/login" className="font-medium text-accent hover:underline">
          Sign in
        </Link>
      </p>
    </section>
  )
}
