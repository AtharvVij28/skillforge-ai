import { Navigate, Route, Routes } from 'react-router-dom'

import { AdminRoute } from '@/components/AdminRoute'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { AppShell } from '@/layouts/AppShell'
import { AccountPage } from '@/pages/AccountPage'
import { AdminAccountsPage } from '@/pages/AdminAccountsPage'
import { AdminLoginPage } from '@/pages/AdminLoginPage'
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage'
import { HomePage } from '@/pages/HomePage'
import { LearnerAssessmentsPage } from '@/pages/LearnerAssessmentsPage'
import { LearnerPathPage } from '@/pages/LearnerPathPage'
import { LearnerSkillGapsPage } from '@/pages/LearnerSkillGapsPage'
import { LearnHomePage } from '@/pages/LearnHomePage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ResetPasswordPage } from '@/pages/ResetPasswordPage'
import { StatusPage } from '@/pages/StatusPage'
import { VerifyEmailPage } from '@/pages/VerifyEmailPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/demo" element={<Navigate to="/" replace />} />
        <Route path="/status" element={<StatusPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-email" element={<VerifyEmailPage />} />
        <Route path="/admin/login" element={<AdminLoginPage />} />
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
        <Route
          path="/gaps"
          element={
            <ProtectedRoute>
              <LearnerSkillGapsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/assess"
          element={
            <ProtectedRoute>
              <LearnerAssessmentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/path"
          element={
            <ProtectedRoute>
              <LearnerPathPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <AdminRoute>
              <AdminAccountsPage />
            </AdminRoute>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
