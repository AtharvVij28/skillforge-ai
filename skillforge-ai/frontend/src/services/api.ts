import axios from 'axios'

import { clearStoredToken, getStoredToken } from '@/services/tokenStorage'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 8000,
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = String(error.config?.url || '')
    const isCredentialAttempt = url.includes('/api/auth/login') || url.includes('/api/auth/register')
    if (status === 401 && !isCredentialAttempt) {
      clearStoredToken()
    }
    return Promise.reject(error)
  },
)

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
