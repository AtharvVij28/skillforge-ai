import { Navigate, useLocation } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { isAdminRole } from '@/utils/roles'

export function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="rounded-xl border border-line bg-panel p-6 text-ink-muted">Checking administrator access…</div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />
  }

  if (!isAdminRole(user?.role.code, user?.role.name)) {
    return <Navigate to="/home" replace />
  }

  return <>{children}</>
}
