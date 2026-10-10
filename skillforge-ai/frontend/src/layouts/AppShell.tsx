import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'
import { isAdminRole } from '@/utils/roles'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-accent text-white' : 'text-ink-muted hover:bg-white/70 hover:text-ink',
  ].join(' ')

export function AppShell() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const admin = isAdminRole(user?.role.code, user?.role.name)

  async function handleLogout() {
    await logout()
    navigate(admin ? '/admin/login' : '/login', { replace: true })
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-line/80 bg-panel/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div>
            <p className="font-display text-xl font-semibold tracking-tight text-ink sm:text-2xl">
              SkillForge AI
            </p>
            <p className="text-sm text-ink-muted">Skill intelligence for official statistics</p>
          </div>
          <nav className="flex flex-wrap items-center justify-end gap-2">
            {isAuthenticated && admin ? (
              <>
                <NavLink to="/admin" className={navLinkClass}>
                  Accounts
                </NavLink>
                <button
                  type="button"
                  onClick={() => void handleLogout()}
                  className="rounded-md border border-line bg-white px-3 py-2 text-sm font-medium text-ink transition hover:border-accent/40"
                >
                  Sign out
                </button>
              </>
            ) : isAuthenticated ? (
              <>
                <NavLink to="/home" className={navLinkClass}>
                  Home
                </NavLink>
                <NavLink to="/path" className={navLinkClass}>
                  My Learning
                </NavLink>
                <NavLink to="/assess" className={navLinkClass}>
                  Assessments
                </NavLink>
                <NavLink to="/gaps" className={navLinkClass}>
                  Skill Gaps
                </NavLink>
                <NavLink to="/account" className={navLinkClass}>
                  Profile
                </NavLink>
                <button
                  type="button"
                  onClick={() => void handleLogout()}
                  className="rounded-md border border-line bg-white px-3 py-2 text-sm font-medium text-ink transition hover:border-accent/40"
                >
                  Sign out
                </button>
              </>
            ) : (
              <>
                <NavLink to="/" className={navLinkClass} end>
                  Home
                </NavLink>
                <NavLink to="/login" className={navLinkClass}>
                  Sign in
                </NavLink>
                <NavLink to="/register" className={navLinkClass}>
                  Register
                </NavLink>
              </>
            )}
          </nav>
        </div>
        {user && (
          <div className="border-t border-line/60 bg-surface/60">
            <p className="mx-auto max-w-6xl px-4 py-2 text-xs text-ink-muted sm:px-6">
              Signed in as <span className="font-medium text-ink">{user.full_name}</span> (
              {user.role.code})
            </p>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}
