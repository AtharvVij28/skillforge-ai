import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate } from 'react-router-dom'

import { GetStartedAssessment } from '@/components/learning/GetStartedAssessment'
import { LearningDashboard } from '@/components/learning/LearningDashboard'
import { SubjectOnboarding } from '@/components/learning/SubjectOnboarding'
import { useAuth } from '@/context/AuthContext'
import { fetchMyCompetencyScores } from '@/services/competencyScores'
import { hasLearningOnboarding } from '@/services/subjectProgressService'
import { isAdminRole } from '@/utils/roles'
import { firstNameFromFullName } from '@/utils/userDisplay'

export function LearnHomePage() {
  const { user, isAuthenticated } = useAuth()
  const [refreshKey, setRefreshKey] = useState(0)
  const [hasAssessment, setHasAssessment] = useState<boolean | null>(null)

  const firstName = useMemo(
    () => firstNameFromFullName(user?.full_name ?? 'Learner'),
    [user?.full_name],
  )

  const handleOnboardingComplete = useCallback(() => {
    setRefreshKey((value) => value + 1)
  }, [])

  useEffect(() => {
    if (!user) return
    let cancelled = false
    async function load() {
      try {
        const scores = await fetchMyCompetencyScores()
        if (!cancelled) setHasAssessment(scores.has_assessment)
      } catch {
        if (!cancelled) setHasAssessment(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [user, refreshKey])

  if (user && isAdminRole(user.role.code, user.role.name)) {
    return <Navigate to="/admin" replace />
  }

  if (!isAuthenticated || !user) {
    return (
      <section className="rounded-2xl border border-line bg-panel p-8 text-center shadow-sm">
        <h1 className="font-display text-2xl font-semibold text-navy">Sign in required</h1>
        <p className="mt-2 text-sm text-ink-muted">Please sign in to access your learning home.</p>
        <Link
          to="/login"
          className="mt-6 inline-flex rounded-md bg-navy px-5 py-2.5 text-sm font-semibold text-white"
        >
          Sign in
        </Link>
      </section>
    )
  }

  if (!hasLearningOnboarding(user.id)) {
    return (
      <SubjectOnboarding
        userId={user.id}
        userFirstName={firstName}
        onComplete={handleOnboardingComplete}
      />
    )
  }

  if (hasAssessment === null) {
    return <p className="text-sm text-ink-muted">Loading your learning home…</p>
  }

  if (!hasAssessment) {
    return <GetStartedAssessment userId={user.id} userFirstName={firstName} />
  }

  return <LearningDashboard userId={user.id} userFirstName={firstName} />
}
