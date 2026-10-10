import { useEffect, useState } from 'react'

import { getApiErrorMessage } from '@/services/apiErrors'
import { fetchRegisteredAccounts, type AdminUserList } from '@/services/admin'

function formatDate(value: string | null): string {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return '—'
  return parsed.toLocaleString()
}

export function AdminAccountsPage() {
  const [data, setData] = useState<AdminUserList | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const next = await fetchRegisteredAccounts()
        if (!cancelled) setData(next)
      } catch (err) {
        if (!cancelled) setError(getApiErrorMessage(err, 'Could not load registered accounts.'))
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-line bg-panel p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Admin portal</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Registered accounts</h1>
        <p className="mt-2 max-w-3xl text-sm text-ink-muted">
          Live directory from PostgreSQL. Passwords are never shown. Public registration creates LEARNER accounts
          only.
        </p>
        {data && (
          <p className="mt-4 text-sm font-medium text-ink">
            {data.total} account{data.total === 1 ? '' : 's'} registered
          </p>
        )}
      </header>

      {error && <p className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-warn">{error}</p>}
      {loading && <p className="text-sm text-ink-muted">Loading accounts…</p>}

      {data && (
        <div className="overflow-x-auto rounded-2xl border border-line bg-panel shadow-sm">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b border-line bg-surface text-xs uppercase tracking-wide text-ink-muted">
              <tr>
                <th className="px-4 py-3 font-semibold">Name</th>
                <th className="px-4 py-3 font-semibold">Email</th>
                <th className="px-4 py-3 font-semibold">Role</th>
                <th className="px-4 py-3 font-semibold">Department</th>
                <th className="px-4 py-3 font-semibold">Job role</th>
                <th className="px-4 py-3 font-semibold">Status</th>
                <th className="px-4 py-3 font-semibold">Last login</th>
                <th className="px-4 py-3 font-semibold">Created</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((account) => (
                <tr key={account.id} className="border-b border-line/70 last:border-0">
                  <td className="px-4 py-3 font-medium text-ink">{account.full_name}</td>
                  <td className="px-4 py-3">{account.email}</td>
                  <td className="px-4 py-3">{account.role_code}</td>
                  <td className="px-4 py-3">{account.department_name ?? '—'}</td>
                  <td className="px-4 py-3">{account.job_role ?? '—'}</td>
                  <td className="px-4 py-3">{account.is_active ? 'Active' : 'Inactive'}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{formatDate(account.last_login_at)}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{formatDate(account.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
