import api from '@/services/api'

export type CompetencyItem = {
  id: string
  code: string
  name: string
  category_id: string
  category_code: string
  category_name: string
  description: string | null
  default_priority: string
  is_active: boolean
}

export type FrameworkCategory = {
  id: string
  code: string
  name: string
  description: string | null
  sort_order: number
  competencies: CompetencyItem[]
}

export async function fetchCompetencyFramework(): Promise<FrameworkCategory[]> {
  const { data } = await api.get<{ categories: FrameworkCategory[] }>('/api/competencies/framework')
  return data.categories
}
