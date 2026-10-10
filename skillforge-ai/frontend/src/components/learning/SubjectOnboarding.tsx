import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { SubjectCard } from '@/components/learning/SubjectCard'
import { LEARNING_SUBJECTS } from '@/data/learningCatalog'
import { saveSubjectSelection } from '@/services/subjectProgressService'

type SubjectOnboardingProps = {
  userId: string
  userFirstName: string
  onComplete: () => void
}

type Phase = 'select' | 'ready'

export function SubjectOnboarding({ userId, userFirstName, onComplete }: SubjectOnboardingProps) {
  const navigate = useNavigate()
  const [selected, setSelected] = useState<string[]>([])
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>('select')

  const canContinue = selected.length > 0

  const selectedCountLabel = useMemo(() => {
    if (selected.length === 0) return 'Select at least one subject to continue'
    if (selected.length === 1) return '1 subject selected'
    return `${selected.length} subjects selected`
  }, [selected.length])

  useEffect(() => {
    if (phase !== 'ready') return
    const timer = window.setTimeout(() => navigate('/assess?from=onboarding'), 1200)
    return () => window.clearTimeout(timer)
  }, [phase, navigate])

  function toggleSubject(subjectId: string) {
    setSelected((current) =>
      current.includes(subjectId) ? current.filter((id) => id !== subjectId) : [...current, subjectId],
    )
  }

  function handleContinue() {
    if (!canContinue) return
    setSaving(true)
    setError(null)
    try {
      saveSubjectSelection(userId, selected)
      onComplete()
      setPhase('ready')
    } catch {
      setError('Could not save your subject preferences. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  if (phase === 'ready') {
    return (
      <div className="demo-fade mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-line bg-panel px-8 py-16 text-center shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">All set</p>
        <h1 className="mt-3 font-display text-3xl font-semibold text-navy">Interests saved</h1>
        <p className="mt-3 text-ink-muted">
          Great choices, {userFirstName}. Next we&apos;ll assess those subjects so your dashboard shows real competency
          gaps.
        </p>
        <button
          type="button"
          onClick={() => navigate('/assess?from=onboarding')}
          className="mt-8 rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid"
        >
          Get started with assessment
        </button>
      </div>
    )
  }

  return (
    <div className="demo-fade space-y-8">
      <header className="max-w-2xl">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Welcome</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy sm:text-4xl">
          Welcome to SkillForge AI 👋
        </h1>
        <p className="mt-2 text-base text-ink-muted">Let&apos;s personalize your learning journey.</p>
      </header>

      <section className="rounded-2xl border border-line bg-panel p-6 shadow-sm sm:p-8">
        <h2 className="font-display text-2xl font-semibold text-navy">What do you want to learn?</h2>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-ink-muted">
          Choose the subjects that match your interests and goals. We&apos;ll use your choices to personalize your
          learning experience.
        </p>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {LEARNING_SUBJECTS.map((subject) => (
            <SubjectCard
              key={subject.id}
              subject={subject}
              selected={selected.includes(subject.id)}
              onToggle={toggleSubject}
            />
          ))}
        </div>

        <div className="mt-8 flex flex-col gap-3 border-t border-line pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-ink-muted">{selectedCountLabel}</p>
          <button
            type="button"
            disabled={!canContinue || saving}
            onClick={handleContinue}
            className="rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid disabled:cursor-not-allowed disabled:opacity-50"
          >
            {saving ? 'Saving…' : 'Continue'}
          </button>
        </div>
        {error && <p className="mt-3 text-sm text-warn">{error}</p>}
      </section>
    </div>
  )
}
