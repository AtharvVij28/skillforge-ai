import { type FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { ProgressBar } from '@/components/learning/ProgressBar'
import { useAuth } from '@/context/AuthContext'
import { getApiErrorMessage } from '@/services/apiErrors'
import { fetchCompetencyFramework, type FrameworkCategory } from '@/services/competencies'
import {
  fetchDepartments,
  fetchOwnProfile,
  updateOwnProfile,
  type DepartmentSummary,
  type ProfileResponse,
} from '@/services/profile'

function joinList(values: string[]): string {
  return values.join(', ')
}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

export function AccountPage() {
  const { user, logout, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [departments, setDepartments] = useState<DepartmentSummary[]>([])
  const [framework, setFramework] = useState<FrameworkCategory[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  const [fullName, setFullName] = useState('')
  const [departmentId, setDepartmentId] = useState('')
  const [designation, setDesignation] = useState('')
  const [jobRole, setJobRole] = useState('')
  const [assignment, setAssignment] = useState('')
  const [education, setEducation] = useState('')
  const [years, setYears] = useState('')
  const [technicalSkills, setTechnicalSkills] = useState('')
  const [statisticalSkills, setStatisticalSkills] = useState('')
  const [digitalSkills, setDigitalSkills] = useState('')
  const [managerialSkills, setManagerialSkills] = useState('')
  const [behaviouralSkills, setBehaviouralSkills] = useState('')
  const [previousTraining, setPreviousTraining] = useState('')
  const [careerGoals, setCareerGoals] = useState('')

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      setError(null)
      try {
        const [nextProfile, nextDepartments, nextFramework] = await Promise.all([
          fetchOwnProfile(),
          fetchDepartments(),
          fetchCompetencyFramework(),
        ])
        if (cancelled) return
        setProfile(nextProfile)
        setDepartments(nextDepartments)
        setFramework(nextFramework)
        setFullName(nextProfile.full_name)
        setDepartmentId(nextProfile.department?.id ?? '')
        setDesignation(nextProfile.designation ?? '')
        setJobRole(nextProfile.job_role ?? '')
        setAssignment(nextProfile.assignment ?? '')
        setEducation(nextProfile.education ?? '')
        setYears(nextProfile.years_of_experience != null ? String(nextProfile.years_of_experience) : '')
        setTechnicalSkills(joinList(nextProfile.technical_skills))
        setStatisticalSkills(joinList(nextProfile.statistical_skills))
        setDigitalSkills(joinList(nextProfile.digital_skills))
        setManagerialSkills(joinList(nextProfile.managerial_skills))
        setBehaviouralSkills(joinList(nextProfile.behavioural_skills))
        setPreviousTraining(joinList(nextProfile.previous_training))
        setCareerGoals(nextProfile.career_goals ?? '')
      } catch (err) {
        if (!cancelled) {
          setError(getApiErrorMessage(err, 'Could not load your profile.'))
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [])

  const completionLabel = useMemo(() => {
    if (!profile) return 'Complete your profile to personalize learning.'
    if (profile.profile_completion_pct >= 100) return 'Profile complete. This will feed skill-gap analysis next.'
    return 'Add the remaining details so SkillForge can personalize your path.'
  }, [profile])

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      const yearsValue = years.trim() === '' ? null : Number.parseInt(years, 10)
      const next = await updateOwnProfile({
        full_name: fullName.trim(),
        department_id: departmentId || null,
        designation: designation.trim() || null,
        job_role: jobRole.trim() || null,
        assignment: assignment.trim() || null,
        education: education.trim() || null,
        years_of_experience: Number.isNaN(yearsValue as number) ? null : yearsValue,
        technical_skills: splitList(technicalSkills),
        statistical_skills: splitList(statisticalSkills),
        digital_skills: splitList(digitalSkills),
        managerial_skills: splitList(managerialSkills),
        behavioural_skills: splitList(behaviouralSkills),
        previous_training: splitList(previousTraining),
        career_goals: careerGoals.trim() || null,
      })
      setProfile(next)
      setSaved(true)
      await refreshUser()
    } catch (err) {
      setError(getApiErrorMessage(err, 'Could not save your profile.'))
    } finally {
      setSaving(false)
    }
  }

  async function handleLogout() {
    await logout()
    navigate('/login', { replace: true })
  }

  if (!user) {
    return null
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-ai">Live profile</p>
        <h1 className="mt-2 font-display text-3xl font-semibold text-navy">Your profile</h1>
        <p className="mt-2 max-w-2xl text-sm text-ink-muted">
          Stored in PostgreSQL. This is the living learner profile — not demo data. Completing it prepares
          competency matching in the next phase.
        </p>

        {profile && (
          <div className="mt-6">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-ink-muted">Profile completion</span>
              <span className="font-semibold text-navy">{profile.profile_completion_pct}%</span>
            </div>
            <ProgressBar value={profile.profile_completion_pct} />
            <p className="mt-2 text-sm text-ink-muted">{completionLabel}</p>
          </div>
        )}

        <dl className="mt-6 grid gap-4 sm:grid-cols-2">
          <div>
            <dt className="text-xs uppercase tracking-wide text-ink-muted">Email</dt>
            <dd className="mt-1 font-semibold">{user.email}</dd>
          </div>
          <div>
            <dt className="text-xs uppercase tracking-wide text-ink-muted">Access role</dt>
            <dd className="mt-1 font-semibold">
              {user.role.name} ({user.role.code})
            </dd>
          </div>
        </dl>
      </section>

      <section className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
        {loading ? (
          <p className="text-sm text-ink-muted">Loading your profile…</p>
        ) : (
          <form className="space-y-4" onSubmit={(event) => void handleSubmit(event)}>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Full name</span>
                <input
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={fullName}
                  onChange={(event) => setFullName(event.target.value)}
                  required
                />
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Department</span>
                <select
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={departmentId}
                  onChange={(event) => setDepartmentId(event.target.value)}
                >
                  <option value="">Select a department</option>
                  {departments.map((department) => (
                    <option key={department.id} value={department.id}>
                      {department.name}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Designation</span>
                <input
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={designation}
                  onChange={(event) => setDesignation(event.target.value)}
                />
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Job role</span>
                <input
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  placeholder="e.g. STATISTICAL_OFFICER"
                  value={jobRole}
                  onChange={(event) => setJobRole(event.target.value)}
                />
              </label>
              <label className="block space-y-1.5 sm:col-span-2">
                <span className="text-sm font-medium text-ink">Current assignment</span>
                <textarea
                  className="min-h-20 w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={assignment}
                  onChange={(event) => setAssignment(event.target.value)}
                />
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Education</span>
                <input
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={education}
                  onChange={(event) => setEducation(event.target.value)}
                />
              </label>
              <label className="block space-y-1.5">
                <span className="text-sm font-medium text-ink">Years of experience</span>
                <input
                  type="number"
                  min={0}
                  max={60}
                  className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={years}
                  onChange={(event) => setYears(event.target.value)}
                />
              </label>
            </div>

            <p className="pt-2 text-xs font-semibold uppercase tracking-[0.16em] text-ink-muted">
              Skills (comma-separated)
            </p>
            <div className="grid gap-4 sm:grid-cols-2">
              {(
                [
                  { label: 'Technical', value: technicalSkills, onChange: setTechnicalSkills },
                  { label: 'Statistical', value: statisticalSkills, onChange: setStatisticalSkills },
                  { label: 'Digital', value: digitalSkills, onChange: setDigitalSkills },
                  { label: 'Managerial', value: managerialSkills, onChange: setManagerialSkills },
                  { label: 'Behavioural', value: behaviouralSkills, onChange: setBehaviouralSkills },
                  { label: 'Previous training', value: previousTraining, onChange: setPreviousTraining },
                ] as const
              ).map((field) => (
                <label key={field.label} className="block space-y-1.5">
                  <span className="text-sm font-medium text-ink">{field.label}</span>
                  <input
                    className="w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                    value={field.value}
                    onChange={(event) => field.onChange(event.target.value)}
                  />
                </label>
              ))}
              <label className="block space-y-1.5 sm:col-span-2">
                <span className="text-sm font-medium text-ink">Career goals</span>
                <textarea
                  className="min-h-20 w-full rounded-md border border-line bg-white px-3 py-2 text-sm"
                  value={careerGoals}
                  onChange={(event) => setCareerGoals(event.target.value)}
                />
              </label>
            </div>

            {error && <p className="text-sm text-warn">{error}</p>}
            {saved && <p className="text-sm text-success">Profile saved.</p>}

            <div className="flex flex-wrap gap-3">
              <button
                type="submit"
                disabled={saving}
                className="rounded-md bg-navy px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-navy-mid disabled:opacity-50"
              >
                {saving ? 'Saving…' : 'Save profile'}
              </button>
              <Link
                to="/home"
                className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink"
              >
                Back to learning home
              </Link>
              <Link
                to="/gaps"
                className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink"
              >
                Analyze skill gaps
              </Link>
              <button
                type="button"
                onClick={() => void handleLogout()}
                className="rounded-md border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink"
              >
                Sign out
              </button>
            </div>
          </form>
        )}
      </section>

      <section className="rounded-2xl border border-line bg-panel p-8 shadow-sm">
        <h2 className="font-display text-xl font-semibold text-navy">Competency framework</h2>
        <p className="mt-1 text-sm text-ink-muted">
          Live categories and competencies from the database. Admin users can add or deactivate items via the API.
        </p>
        {framework.length === 0 && !loading && (
          <p className="mt-4 text-sm text-ink-muted">No framework loaded yet. Restart the backend so seed data can run.</p>
        )}
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {framework.map((category) => (
            <article key={category.id} className="rounded-xl border border-line bg-surface p-4">
              <h3 className="font-semibold text-navy">{category.name}</h3>
              <p className="mt-1 text-xs text-ink-muted">{category.description}</p>
              <ul className="mt-3 space-y-1 text-sm text-ink">
                {category.competencies.map((item) => (
                  <li key={item.id}>
                    {item.name}
                    <span className="ml-2 text-xs text-ink-muted">{item.default_priority}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}
