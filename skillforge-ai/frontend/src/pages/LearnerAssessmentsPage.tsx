import { useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import { ProgressBar } from '@/components/learning/ProgressBar'
import { useAuth } from '@/context/AuthContext'
import { competencyCodesForSubjects } from '@/data/learningCatalog'
import { getApiErrorMessage } from '@/services/apiErrors'
import {
  generateAssessment,
  startAssessment,
  submitAttempt,
  type AttemptResult,
  type AssessmentQuestion,
} from '@/services/assessments'
import { getSelectedSubjectIds } from '@/services/subjectProgressService'

function score(value: number | string | null | undefined): number {
  if (value == null) return 0
  return typeof value === 'number' ? value : Number.parseFloat(value)
}

export function LearnerAssessmentsPage() {
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const fromOnboarding = searchParams.get('from') === 'onboarding'
  const autoStarted = useRef(false)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [attemptId, setAttemptId] = useState<string | null>(null)
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([])
  const [index, setIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [result, setResult] = useState<AttemptResult | null>(null)

  const competencyCodes = useMemo(() => {
    if (!user) return []
    return competencyCodesForSubjects(getSelectedSubjectIds(user.id))
  }, [user])

  const question = questions[index]
  const progress = useMemo(() => {
    if (!questions.length) return 0
    return ((index + (question && answers[question.id] ? 0.35 : 0)) / questions.length) * 100
  }, [answers, index, question, questions.length])

  async function handleGenerate() {
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const questionCount = Math.min(12, Math.max(5, competencyCodes.length * 2 || 5))
      const assessment = await generateAssessment(questionCount, competencyCodes)
      const started = await startAssessment(assessment.id)
      setAttemptId(started.attempt_id)
      setQuestions(started.questions)
      setAnswers({})
      setIndex(0)
    } catch (err) {
      setError(
        getApiErrorMessage(
          err,
          'Could not generate an assessment for your selected interests. Please try again.',
        ),
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!fromOnboarding || autoStarted.current || !user) return
    autoStarted.current = true
    void handleGenerate()
    // Intentionally start once when arriving from interest selection.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fromOnboarding, user?.id])

  async function handleSubmit() {
    if (!attemptId) return
    const payload = questions.map((item) => ({
      question_id: item.id,
      selected_option: answers[item.id] || '—',
    }))
    setLoading(true)
    setError(null)
    try {
      const next = await submitAttempt(attemptId, payload)
      setResult(next)
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not submit the assessment.'))
    } finally {
      setLoading(false)
    }
  }

  if (result) {
    return (
      <section className="space-y-6">
        <div className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Results</p>
          <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Assessment complete</h1>
          <p className="mt-2 text-sm text-ink-muted">{result.feedback_summary}</p>
          <p className="mt-4 font-display text-4xl font-semibold text-navy">{score(result.percentage).toFixed(0)}%</p>
          <p className="mt-2 text-sm text-ink-muted">
            Your competency gaps have been calculated from this attempt. Open the dashboard to see them.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/home" className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white">
              View my dashboard
            </Link>
            <Link to="/gaps" className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
              Review skill gaps
            </Link>
            <Link to="/path" className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink">
              Open learning path
            </Link>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2">
          {result.competency_breakdown.map((item) => (
            <article key={item.competency_name} className="rounded-xl border border-line bg-panel p-5 shadow-sm">
              <h2 className="font-semibold text-navy">{item.competency_name}</h2>
              <p className="mt-2 text-sm text-ink-muted">
                {score(item.percent_correct).toFixed(0)}% correct · score {score(item.previous_score).toFixed(1)} →{' '}
                {score(item.updated_score).toFixed(1)}
              </p>
            </article>
          ))}
        </div>
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-line bg-panel p-6 shadow-sm sm:p-8">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Live assessment</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">
          {fromOnboarding ? 'Get started with assessment' : 'Assess your competencies'}
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-ink-muted">
          {fromOnboarding
            ? 'We are generating questions from the interests you selected. Complete this quiz so your dashboard can show real competency gaps calculated from your scores.'
            : 'SkillForge builds a quiz from your selected interests, scores it, updates competency estimates, then recommends study material. If an OpenAI key is configured on the server, new questions can be model-written; otherwise a curated question bank is used.'}
        </p>
        <button
          type="button"
          onClick={() => void handleGenerate()}
          disabled={loading}
          className="mt-5 rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
        >
          {loading
            ? fromOnboarding && !questions.length
              ? 'Generating your assessment…'
              : 'Preparing…'
            : questions.length
              ? 'Generate a new assessment'
              : 'Generate assessment'}
        </button>
      </header>

      {error && <p className="rounded-xl border border-line bg-panel px-4 py-3 text-sm text-warn">{error}</p>}

      {question && (
        <section className="rounded-xl border border-line bg-panel p-6 shadow-sm">
          <ProgressBar value={progress} />
          <p className="mt-4 text-xs font-semibold uppercase tracking-[0.16em] text-ai">
            Question {index + 1} of {questions.length} · {question.competency_name}
          </p>
          <h2 className="mt-3 font-display text-xl font-semibold leading-snug text-navy">{question.stem}</h2>
          <div className="mt-6 space-y-2">
            {question.options.map((option) => {
              const selected = answers[question.id] === option.key
              return (
                <button
                  key={option.key}
                  type="button"
                  onClick={() => setAnswers((current) => ({ ...current, [question.id]: option.key }))}
                  className={`w-full rounded-lg border px-4 py-3 text-left text-sm transition ${
                    selected ? 'border-ai bg-ai-soft' : 'border-line bg-white hover:border-ai/40'
                  }`}
                >
                  <span className="mr-2 font-semibold text-ink-muted">{option.key}.</span>
                  {option.text}
                </button>
              )
            })}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            {index + 1 < questions.length ? (
              <button
                type="button"
                disabled={!answers[question.id]}
                onClick={() => setIndex((value) => value + 1)}
                className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
              >
                Next question
              </button>
            ) : (
              <button
                type="button"
                disabled={!answers[question.id] || loading}
                onClick={() => void handleSubmit()}
                className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-50"
              >
                {loading ? 'Scoring…' : 'Submit and score'}
              </button>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
