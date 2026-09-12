import { NavLink, Outlet, useLocation } from 'react-router-dom'

import { DEMO_NOTICE, demoUser } from '@/data/demoData'
import { useDemo } from '@/context/DemoContext'

const learnerNav = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/profile', label: 'My Profile' },
  { to: '/competencies', label: 'Competencies' },
  { to: '/skill-gaps', label: 'Skill Gaps' },
  { to: '/assessments', label: 'Assessments' },
  { to: '/learning', label: 'Learning Path' },
  { to: '/insights', label: 'AI Insights' },
] as const

const adminNav = [
  { to: '/admin', label: 'Overview', end: true },
  { to: '/admin/learners', label: 'Learners' },
  { to: '/admin/framework', label: 'Competency Framework' },
  { to: '/admin/analytics', label: 'Skill Analytics' },
] as const

const navClass = ({ isActive }: { isActive: boolean }) =>
  [
    'block rounded-md px-3 py-2 text-sm font-medium transition',
    isActive ? 'bg-white/12 text-white' : 'text-white/70 hover:bg-white/8 hover:text-white',
  ].join(' ')

export function DemoLayout() {
  const { mode, exitDemo } = useDemo()
  const location = useLocation()
  const isAdmin = mode === 'admin' || location.pathname.startsWith('/admin')
  const nav = isAdmin ? adminNav : learnerNav

  return (
    <div className="min-h-screen bg-surface lg:grid lg:grid-cols-[260px_1fr]">
      <aside className="bg-navy text-white">
        <div className="border-b border-white/10 px-5 py-5">
          <p className="font-display text-lg font-semibold tracking-tight">SkillForge AI</p>
          <p className="mt-1 text-xs text-white/60">{isAdmin ? 'Administrator demo' : 'Learner demo'}</p>
        </div>
        <nav className="space-y-1 p-3">
          {nav.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === '/admin'} className={navClass}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 text-xs text-white/50">
          <p>Living competency profile</p>
          <p className="mt-1">Explainable skill gaps</p>
        </div>
      </aside>

      <div className="flex min-h-screen flex-col">
        <header className="flex items-center justify-between border-b border-line bg-panel px-4 py-3 sm:px-6">
          <div>
            <p className="text-sm font-semibold text-navy">SkillForge AI</p>
            <p className="text-xs text-ink-muted">Closed-loop learning intelligence</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              className="rounded-md border border-line px-3 py-1.5 text-xs font-medium text-ink-muted"
              title="Demo notifications"
            >
              Notifications
            </button>
            <div className="rounded-full bg-ai-soft px-3 py-1.5 text-xs font-semibold text-navy">
              {isAdmin ? 'Admin · Demo' : demoUser.fullName}
            </div>
            <button
              type="button"
              onClick={exitDemo}
              className="rounded-md border border-line px-3 py-1.5 text-xs font-medium text-ink hover:border-ai/40"
            >
              Exit demo
            </button>
          </div>
        </header>
        <p className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber sm:px-6">{DEMO_NOTICE}</p>
        <main className="demo-fade flex-1 px-4 py-6 sm:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
