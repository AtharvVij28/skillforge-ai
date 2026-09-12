import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '@/context/AuthContext'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-accent text-white' : 'text-ink-muted hover:bg-white/70 hover:text-ink',
  ].join(' ')

export function AppShell() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
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
            {isAuthenticated ? (
              <>
                <NavLink to="/home" className={navLinkClass}>
                  Home
                </NavLink>
                <NavLink to="/learning" className={navLinkClass}>
                  My Learning
                </NavLink>
                <NavLink to="/competencies" className={navLinkClass}>
                  Subjects
                </NavLink>
                <NavLink to="/assessments" className={navLinkClass}>
                  Assessments
                </NavLink>
                <NavLink to="/insights" className={navLinkClass}>
                  AI Insights
                </NavLink>
                <NavLink to="/account" className={navLinkClass}>
                  Profile
                </NavLink>
                {(user?.role.code === 'ADMIN' || user?.role.name?.toUpperCase().includes('ADMIN')) && (
                  <NavLink to="/admin" className={navLinkClass}>
                    Admin
                  </NavLink>
                )}
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
                <NavLink to="/demo" className={navLinkClass}>
                  Explore demo
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
