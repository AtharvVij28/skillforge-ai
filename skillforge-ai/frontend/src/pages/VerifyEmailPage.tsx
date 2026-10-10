import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { getApiErrorMessage } from '@/services/apiErrors'
import { verifyEmail } from '@/services/auth'

export function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const [status, setStatus] = useState<'working' | 'ok' | 'error'>('working')
  const [message, setMessage] = useState('Confirming your email…')

  useEffect(() => {
    let cancelled = false
    async function confirm() {
      if (!token) {
        setStatus('error')
        setMessage('This confirmation link is missing a token.')
        return
      }
      try {
        const result = await verifyEmail(token)
        if (!cancelled) {
          setStatus('ok')
          setMessage(result.message)
        }
      } catch (err) {
        if (!cancelled) {
          setStatus('error')
          setMessage(getApiErrorMessage(err, 'This confirmation link is invalid or has expired.'))
        }
      }
    }
    void confirm()
    return () => {
      cancelled = true
    }
  }, [token])

  return (
    <section className="mx-auto max-w-md rounded-2xl border border-line bg-panel p-8 text-center shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">
        {status === 'ok' ? 'Email confirmed' : status === 'error' ? 'Confirmation failed' : 'Confirming email'}
      </h1>
      <p className={`mt-3 text-sm ${status === 'error' ? 'text-warn' : 'text-ink-muted'}`}>{message}</p>
      {status === 'ok' && (
        <Link
          to="/login"
          className="mt-6 inline-flex rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white"
        >
          Sign in
        </Link>
      )}
      {status === 'error' && (
        <Link to="/register" className="mt-6 inline-flex text-sm font-medium text-accent hover:underline">
          Back to registration
        </Link>
      )}
    </section>
  )
}
