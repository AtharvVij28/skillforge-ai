import api from '@/services/api'

export type AdminUserSummary = {
  id: string
  email: string
  full_name: string
  role_code: string
  role_name: string
  is_active: boolean
  department_name: string | null
  job_role: string | null
  last_login_at: string | null
  created_at: string | null
}

export type AdminUserList = {
  items: AdminUserSummary[]
  total: number
  page: number
  page_size: number
}

export async function fetchRegisteredAccounts(page = 1): Promise<AdminUserList> {
  const { data } = await api.get<AdminUserList>('/api/admin/users', { params: { page, page_size: 50 } })
  return data
}
