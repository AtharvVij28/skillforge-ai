import api from '@/services/api'

export type DepartmentSummary = {
  id: string
  code: string
  name: string
}

export type ProfileResponse = {
  user_id: string
  email: string
  full_name: string
  role_code: string
  is_active: boolean
  department: DepartmentSummary | null
  designation: string | null
  job_role: string | null
  assignment: string | null
  education: string | null
  years_of_experience: number | null
  technical_skills: string[]
  statistical_skills: string[]
  digital_skills: string[]
  managerial_skills: string[]
  behavioural_skills: string[]
  previous_training: string[]
  career_goals: string | null
  profile_completion_pct: number
  updated_at: string | null
}

export type ProfileCompletionResponse = {
  profile_completion_pct: number
  filled_fields: number
  total_fields: number
  missing_fields: string[]
}

export type ProfileUpdatePayload = {
  full_name?: string
  department_id?: string | null
  designation?: string | null
  job_role?: string | null
  assignment?: string | null
  education?: string | null
  years_of_experience?: number | null
  technical_skills?: string[]
  statistical_skills?: string[]
  digital_skills?: string[]
  managerial_skills?: string[]
  behavioural_skills?: string[]
  previous_training?: string[]
  career_goals?: string | null
}

export async function fetchOwnProfile(): Promise<ProfileResponse> {
  const { data } = await api.get<ProfileResponse>('/api/profile')
  return data
}

export async function updateOwnProfile(payload: ProfileUpdatePayload): Promise<ProfileResponse> {
  const { data } = await api.put<ProfileResponse>('/api/profile', payload)
  return data
}

export async function fetchProfileCompletion(): Promise<ProfileCompletionResponse> {
  const { data } = await api.get<ProfileCompletionResponse>('/api/profile/completion')
  return data
}

export async function fetchDepartments(): Promise<DepartmentSummary[]> {
  const { data } = await api.get<{ items: DepartmentSummary[] }>('/api/profile/departments')
  return data.items
}
