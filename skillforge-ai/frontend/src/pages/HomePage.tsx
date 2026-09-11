import { Link } from 'react-router-dom'

export function HomePage() {
  return (
    <section className="overflow-hidden rounded-2xl border border-line bg-panel shadow-sm">
      <div className="grid gap-0 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-5 p-8 sm:p-10">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-accent">Phase 1 scaffold</p>
          <h1 className="font-display text-3xl font-semibold leading-tight text-ink sm:text-4xl">
            Personalized skill intelligence for India&apos;s Official Statistical System
          </h1>
          <p className="max-w-2xl text-base leading-relaxed text-ink-muted sm:text-lg">
            Development environment is ready. Authentication, competency engines, assessments, and
            dashboards will be added in later phases.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              to="/status"
              className="rounded-md bg-accent px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-accent-dark"
            >
              Check API status
            </Link>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink transition hover:border-accent/40"
            >
              Open API docs
            </a>
          </div>
        </div>
        <div className="border-t border-line bg-[linear-gradient(145deg,#0f2744_0%,#14532d_55%,#0b6e4f_100%)] p-8 text-white lg:border-l lg:border-t-0">
          <p className="text-sm uppercase tracking-[0.16em] text-white/70">Learning loop</p>
          <ol className="mt-6 space-y-3 text-sm leading-relaxed text-white/90">
            <li>1. Profile</li>
            <li>2. Assess</li>
            <li>3. Recommend</li>
            <li>4. Learn</li>
            <li>5. Assess again</li>
          </ol>
        </div>
      </div>
    </section>
  )
}
