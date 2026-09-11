import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 8000,
})

export type HealthResponse = {
  status: string
  service: string
  environment: string
  phase: number
  ai_provider: string
  course_provider_mode: string
}

export async function fetchHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/api/health')
  return data
}

export default api
