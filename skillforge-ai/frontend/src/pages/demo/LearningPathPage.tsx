import { useState } from 'react'
import { Link } from 'react-router-dom'

import { LearningCard } from '@/components/demo/LearningCard'
import { demoLearningPath } from '@/data/demoData'

export function LearningPathPage() {
  const [message, setMessage] = useState<string | null>(null)

  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Your Personalized Learning Path</h1>
        <p className="mt-2 max-w-3xl text-ink-muted">
          Recommendations are prioritized using your role, competency gaps, learning history and assessment
          performance. Catalog items below are demo learning resources — integration-ready for iGOT Karmayogi and
          NSSTA, not live APIs.
        </p>
      </header>

      {message && (
        <p className="rounded-lg border border-ai/20 bg-ai-soft px-4 py-3 text-sm text-navy">{message}</p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        {demoLearningPath.map((resource) => (
          <LearningCard
            key={resource.id}
            resource={resource}
            onAction={() =>
              setMessage(
                `${resource.action} opened for “${resource.title}”. In production this would launch the provider course via an API adapter.`,
              )
            }
          />
        ))}
      </div>

      <p className="text-sm text-ink-muted">
        After learning, close the loop with an{' '}
        <Link to="/assessments" className="font-medium text-ai hover:underline">
          assessment
        </Link>
        .
      </p>
    </div>
  )
}
