import axios from 'axios'

function detailToMessage(detail: unknown): string | null {
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { loc?: unknown[]; msg?: string }
    if (first?.msg) {
      const field = Array.isArray(first.loc) ? String(first.loc[first.loc.length - 1]) : ''
      if (field === 'email') return 'Please enter a valid email address.'
      if (field === 'password') return first.msg
      if (field === 'full_name') return 'Please enter your full name.'
      return first.msg
    }
  }
  return null
}

export function getApiErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      if (error.code === 'ECONNABORTED') {
        return 'The server took too long to respond. Please try again.'
      }
      return 'Cannot reach the SkillForge API. Confirm the backend is running on http://127.0.0.1:8000.'
    }

    const status = error.response.status
    const message = detailToMessage(error.response.data?.detail)

    if (status === 409) {
      return message || 'An account with this email already exists.'
    }
    if (status === 401) {
      return message || 'Incorrect email or password.'
    }
    if (status === 403) {
      return message || 'This account is inactive.'
    }
    if (status === 422) {
      return message || 'Please check the form and try again.'
    }
    if (status >= 500) {
      return 'The server could not complete this request. Please try again.'
    }
    return message || fallback
  }

  return fallback
}
