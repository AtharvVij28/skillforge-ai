import { useCallback, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { LearningDashboard } from '@/components/learning/LearningDashboard'
import { SubjectOnboarding } from '@/components/learning/SubjectOnboarding'
import { useAuth } from '@/context/AuthContext'
import { hasLearningOnboarding } from '@/services/subjectProgressService'
import { firstNameFromFullName } from '@/utils/userDisplay'

export function LearnHomePage() {
  const { user, isAuthenticated } = useAuth()
  const [refreshKey, setRefreshKey] = useState(0)

  const firstName = useMemo(
    () => firstNameFromFullName(user?.full_name ?? 'Learner'),
    [user?.full_name],
  )

  const handleOnboardingComplete = useCallback(() => {
    setRefreshKey((value) => value + 1)
  }, [])

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

  // refreshKey forces re-evaluation after subject selection is saved
  void refreshKey

  if (!hasLearningOnboarding(user.id)) {
    return (
      <SubjectOnboarding
        userId={user.id}
        userFirstName={firstName}
        onComplete={handleOnboardingComplete}
      />
    )
  }

  return <LearningDashboard userId={user.id} userFirstName={firstName} />
}
