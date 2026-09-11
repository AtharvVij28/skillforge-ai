import { NavLink, Outlet } from 'react-router-dom'

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  [
    'rounded-md px-3 py-2 text-sm font-medium transition-colors',
    isActive ? 'bg-accent text-white' : 'text-ink-muted hover:bg-white/70 hover:text-ink',
  ].join(' ')

export function AppShell() {
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
          <nav className="flex items-center gap-2">
            <NavLink to="/" className={navLinkClass} end>
              Home
            </NavLink>
            <NavLink to="/status" className={navLinkClass}>
              System status
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <Outlet />
      </main>
    </div>
  )
}
