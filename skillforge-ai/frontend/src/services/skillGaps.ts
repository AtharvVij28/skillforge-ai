import api from '@/services/api'

export type SkillGapItem = {
  competency_id: string
  competency_code: string
  competency_name: string
  current_score: number | string
  required_score: number | string
  gap: number | string
  priority: 'HIGH' | 'MEDIUM' | 'LOW' | string
  confidence: number | string
  source: string
  status: 'GAP' | 'MET' | string
  explanation: string
}

export type SkillGapAnalysis = {
  analysis_id: string | null
  user_id: string
  job_role: string | null
  profile_completion_pct: number
  computed_at: string | null
  message: string | null
  open_gaps: number
  items: SkillGapItem[]
}

export async function fetchLatestSkillGaps(): Promise<SkillGapAnalysis> {
  const { data } = await api.get<SkillGapAnalysis>('/api/skills/gaps')
  return data
}

export async function analyzeSkillGaps(): Promise<SkillGapAnalysis> {
  const { data } = await api.post<SkillGapAnalysis>('/api/skills/gaps/analyze')
  return data
}

export function toScore(value: number | string): number {
  return typeof value === 'number' ? value : Number.parseFloat(value)
}
