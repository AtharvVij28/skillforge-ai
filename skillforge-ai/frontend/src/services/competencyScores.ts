import api from '@/services/api'

export type UserCompetencyScore = {
  competency_id: string
  competency_code: string
  competency_name: string
  current_score: number | string
  confidence: number | string
  source: string
}

export type UserCompetencyList = {
  items: UserCompetencyScore[]
  profile_completion_pct: number
  job_role: string | null
  has_assessment: boolean
}

export async function fetchMyCompetencyScores(): Promise<UserCompetencyList> {
  const { data } = await api.get<UserCompetencyList>('/api/skills/me')
  return data
}
