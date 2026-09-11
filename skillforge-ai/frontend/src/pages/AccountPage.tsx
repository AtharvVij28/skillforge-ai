import { useAuth } from '@/context/AuthContext'

export function AccountPage() {
  const { user, logout } = useAuth()

  if (!user) {
    return null
  }

  return (
    <section className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
      <h1 className="font-display text-2xl font-semibold text-ink">Your account</h1>
      <p className="mt-2 text-sm text-ink-muted">Authenticated session (Phase 3 verification).</p>

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
          <dd className="mt-1 font-semibold">{user.role.name} ({user.role.code})</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-ink-muted">Status</dt>
          <dd className="mt-1 font-semibold">{user.is_active ? 'Active' : 'Inactive'}</dd>
        </div>
      </dl>

      <button
        type="button"
        onClick={() => void logout()}
        className="mt-6 rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink transition hover:border-accent/40"
      >
        Sign out
      </button>
    </section>
  )
}
