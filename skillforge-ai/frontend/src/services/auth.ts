import api from '@/services/api'
import { clearStoredToken, setStoredToken } from '@/services/tokenStorage'

export type RoleSummary = {
  code: string
  name: string
}

export type UserResponse = {
  id: string
  email: string
  full_name: string
  role: RoleSummary
  is_active: boolean
  last_login_at?: string | null
}

export type RegisterPayload = {
  email: string
  password: string
  full_name: string
}

export type LoginPayload = {
  email: string
  password: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export async function registerUser(payload: RegisterPayload): Promise<UserResponse> {
  const { data } = await api.post<UserResponse>('/api/auth/register', payload)
  return data
}

export async function loginUser(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/api/auth/login', payload)
  setStoredToken(data.access_token)
  return data
}

export async function fetchCurrentUser(): Promise<UserResponse> {
  const { data } = await api.get<UserResponse>('/api/auth/me')
  return data
}

export async function logoutUser(): Promise<void> {
  try {
    await api.post('/api/auth/logout')
  } finally {
    clearStoredToken()
  }
}
