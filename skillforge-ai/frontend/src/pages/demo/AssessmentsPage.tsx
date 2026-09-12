import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { AssessmentQuestion } from '@/components/demo/AssessmentQuestion'
import { ProgressBar } from '@/components/demo/ProgressBar'
import { demoAssessment } from '@/data/demoData'

export function AssessmentsPage() {
  const questions = demoAssessment.questions
  const [index, setIndex] = useState(3)
  const [selected, setSelected] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)
  const [pythonScore, setPythonScore] = useState(3.2)
  const [complete, setComplete] = useState(false)

  const question = questions[index]
  const progress = useMemo(() => ((index + (revealed ? 1 : 0)) / questions.length) * 100, [index, revealed, questions.length])

  function handleNext() {
    if (!revealed) {
      setRevealed(true)
      if (selected === question.correctIndex) {
        setPythonScore((value) => Math.min(4.5, Number((value + 0.2).toFixed(1))))
      }
      return
    }
    if (index + 1 >= questions.length) {
      setComplete(true)
      return
    }
    setIndex((value) => value + 1)
    setSelected(null)
    setRevealed(false)
  }

  if (complete) {
    return (
      <section className="rounded-xl border border-line bg-panel p-8 shadow-sm">
        <h1 className="font-display text-2xl font-semibold text-navy">Assessment complete</h1>
        <p className="mt-2 text-ink-muted">
          Competency scores updated in demo state. Recommendations would re-rank next — Profile → Assess → Recommend.
        </p>
        <p className="mt-4 text-sm font-semibold">
          Python {pythonScore.toFixed(1)} (simulated)
        </p>
        <Link to="/insights" className="mt-6 inline-block rounded-md bg-navy px-4 py-2 text-sm font-semibold text-white">
          View AI insights
        </Link>
      </section>
    )
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">{demoAssessment.title}</h1>
        <p className="mt-1 text-ink-muted">Simulated in the browser. Backend assessment APIs are unchanged.</p>
      </header>
      <ProgressBar value={progress} tone="navy" />
      <AssessmentQuestion
        question={question}
        index={index}
        total={questions.length}
        selected={selected}
        revealed={revealed}
        onSelect={setSelected}
        onNext={handleNext}
      />
      {revealed && (
        <p className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-success">
          Competency update: Python 3.2 → {pythonScore.toFixed(1)}
        </p>
      )}
    </div>
  )
}
