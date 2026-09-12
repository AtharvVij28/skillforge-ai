import { Link } from 'react-router-dom'

import { LearningLoop } from '@/components/demo/LearningLoop'
import { useAuth } from '@/context/AuthContext'

export function HomePage() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="space-y-10">
      <section className="overflow-hidden rounded-2xl border border-line bg-panel shadow-sm">
        <div className="grid lg:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-6 p-8 sm:p-12">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-ai">SkillForge AI</p>
            <h1 className="font-display text-4xl font-semibold leading-tight text-navy sm:text-5xl">
              Turn skills into intelligence.
            </h1>
            <p className="max-w-xl text-base leading-relaxed text-ink-muted sm:text-lg">
              AI-powered competency intelligence and personalized learning for a future-ready workforce in
              India&apos;s Official Statistical System.
            </p>
            <div className="flex flex-wrap gap-3">
              {isAuthenticated ? (
                <Link
                  to="/home"
                  className="rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
                >
                  Continue learning
                </Link>
              ) : (
                <>
                  <Link
                    to="/register"
                    className="rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
                  >
                    Get started
                  </Link>
                  <Link
                    to="/login"
                    className="rounded-md border border-line bg-white px-5 py-2.5 text-sm font-semibold text-ink transition hover:border-ai/40"
                  >
                    Sign in
                  </Link>
                </>
              )}
              <Link
                to="/demo"
                className="rounded-md border border-line bg-white px-5 py-2.5 text-sm font-semibold text-ink transition hover:border-ai/40"
              >
                Explore demo
              </Link>
            </div>
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-[0.16em] text-ink-muted">The learning loop</p>
              <LearningLoop />
            </div>
          </div>
          <div className="bg-[linear-gradient(155deg,#0b1f3a_0%,#16325c_48%,#312e81_100%)] p-8 text-white sm:p-10">
            <p className="text-xs uppercase tracking-[0.18em] text-white/60">Why SkillForge</p>
            <ul className="mt-8 space-y-6">
              <li>
                <p className="text-xs font-bold tracking-[0.16em] text-indigo-200">Discover</p>
                <p className="mt-1 text-lg font-medium">Build a living competency profile.</p>
              </li>
              <li>
                <p className="text-xs font-bold tracking-[0.16em] text-indigo-200">Assess</p>
                <p className="mt-1 text-lg font-medium">Identify strengths and skill gaps.</p>
              </li>
              <li>
                <p className="text-xs font-bold tracking-[0.16em] text-indigo-200">Grow</p>
                <p className="mt-1 text-lg font-medium">Receive personalized learning pathways.</p>
              </li>
            </ul>
            <p className="mt-10 text-xs leading-relaxed text-white/55">
              Integration-ready for iGOT Karmayogi and NSSTA through API adapters. Demo resources are labelled and
              are not live government APIs.
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {[
          ['Living profile', 'Designation, role, learning history and assessments stay in one competency record.'],
          ['Explainable gaps', 'Every gap shows current vs required level, priority and a human-readable reason.'],
          ['Closed loop', 'Recommendations adapt after each assessment — not a one-time course list.'],
        ].map(([title, body]) => (
          <article key={title} className="rounded-xl border border-line bg-panel p-5 shadow-sm">
            <h2 className="font-semibold text-navy">{title}</h2>
            <p className="mt-2 text-sm leading-relaxed text-ink-muted">{body}</p>
          </article>
        ))}
      </section>
    </div>
  )
}
