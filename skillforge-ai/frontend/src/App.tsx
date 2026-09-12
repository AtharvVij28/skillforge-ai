import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppShell } from '@/layouts/AppShell'
import { DemoLayout } from '@/layouts/DemoLayout'
import { AccountPage } from '@/pages/AccountPage'
import { HomePage } from '@/pages/HomePage'
import { LearnHomePage } from '@/pages/LearnHomePage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { StatusPage } from '@/pages/StatusPage'
import { AdminAnalyticsPage } from '@/pages/demo/AdminAnalyticsPage'
import { AdminFrameworkPage } from '@/pages/demo/AdminFrameworkPage'
import { AdminLearnersPage } from '@/pages/demo/AdminLearnersPage'
import { AdminOverviewPage } from '@/pages/demo/AdminOverviewPage'
import { AssessmentsPage } from '@/pages/demo/AssessmentsPage'
import { CompetenciesPage } from '@/pages/demo/CompetenciesPage'
import { DashboardPage } from '@/pages/demo/DashboardPage'
import { DemoEntryPage } from '@/pages/demo/DemoEntryPage'
import { InsightsPage } from '@/pages/demo/InsightsPage'
import { LearningPathPage } from '@/pages/demo/LearningPathPage'
import { ProfilePage } from '@/pages/demo/ProfilePage'
import { SkillGapsPage } from '@/pages/demo/SkillGapsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/demo" element={<DemoEntryPage />} />
        {/* Status kept for diagnostics; removed from primary navigation */}
        <Route path="/status" element={<StatusPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/home"
          element={
            <ProtectedRoute>
              <LearnHomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/account"
          element={
            <ProtectedRoute>
              <AccountPage />
            </ProtectedRoute>
          }
        />
      </Route>

      <Route element={<DemoLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/competencies" element={<CompetenciesPage />} />
        <Route path="/skill-gaps" element={<SkillGapsPage />} />
        <Route path="/learning" element={<LearningPathPage />} />
        <Route path="/assessments" element={<AssessmentsPage />} />
        <Route path="/insights" element={<InsightsPage />} />
        <Route path="/admin" element={<AdminOverviewPage />} />
        <Route path="/admin/learners" element={<AdminLearnersPage />} />
        <Route path="/admin/framework" element={<AdminFrameworkPage />} />
        <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
