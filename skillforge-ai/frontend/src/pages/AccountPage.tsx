import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'

export function AccountPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  if (!user) {
    return null
  }

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  return (
    <section className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">Your account</h1>
      <p className="mt-2 text-sm text-ink-muted">
        Live user from PostgreSQL via GET /api/auth/me. This is not the Atharv Vij demo profile.
      </p>

      <dl className="mt-6 grid gap-4 sm:grid-cols-2">
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-muted">Name</dt>
          <dd className="mt-1 font-semibold">{user.full_name}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-muted">Email</dt>
          <dd className="mt-1 font-semibold">{user.email}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-muted">Role</dt>
          <dd className="mt-1 font-semibold">
            {user.role.name} ({user.role.code})
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-muted">Status</dt>
          <dd className="mt-1 font-semibold">{user.is_active ? 'Active' : 'Inactive'}</dd>
        </div>
      </dl>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          to="/home"
          className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
        >
          Go to learning home
        </Link>
        <button
          type="button"
          onClick={() => void handleLogout()}
          className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink transition hover:border-accent/40"
        >
          Sign out
        </button>
      </div>
    </section>
  )
}
