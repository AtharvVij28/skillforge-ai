import api from '@/services/api'

export type LearningPathItem = {
  id: string
  rank: number
  title: string
  provider: string
  url: string | null
  competency_name: string
  gap_at_generation: number | string | null
  estimated_effort_hours: number | string | null
  reason: string
  expected_benefit: string | null
  is_mock: boolean
}

export type LearningPath = {
  job_role: string | null
  message: string | null
  items: LearningPathItem[]
}

export async function fetchLearningPath(): Promise<LearningPath> {
  const { data } = await api.get<LearningPath>('/api/learning/path')
  return data
}

export async function generateLearningPath(): Promise<LearningPath> {
  const { data } = await api.post<LearningPath>('/api/learning/path/generate')
  return data
}
