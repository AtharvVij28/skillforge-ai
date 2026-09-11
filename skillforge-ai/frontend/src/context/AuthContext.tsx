import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
  type LoginPayload,
  type RegisterPayload,
  type UserResponse,
} from '@/services/auth'
import { clearStoredToken, getStoredToken } from '@/services/tokenStorage'

type AuthContextValue = {
  user: UserResponse | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  register: (payload: RegisterPayload) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refreshUser = useCallback(async () => {
    const token = getStoredToken()
    if (!token) {
      setUser(null)
      return
    }
    const current = await fetchCurrentUser()
    setUser(current)
  }, [])

  useEffect(() => {
    let cancelled = false
    async function load() {
      setIsLoading(true)
      try {
        if (!getStoredToken()) {
          if (!cancelled) setUser(null)
          return
        }
        const current = await fetchCurrentUser()
        if (!cancelled) setUser(current)
      } catch {
        clearStoredToken()
        if (!cancelled) setUser(null)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    void load()
    return () => {
      cancelled = true
    }
  }, [refreshUser])

  const login = useCallback(async (payload: LoginPayload) => {
    await loginUser(payload)
    const current = await fetchCurrentUser()
    setUser(current)
  }, [])

  const register = useCallback(async (payload: RegisterPayload) => {
    await registerUser(payload)
    await loginUser({ email: payload.email, password: payload.password })
    const current = await fetchCurrentUser()
    setUser(current)
  }, [])

  const logout = useCallback(async () => {
    await logoutUser()
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isLoading,
      login,
      register,
      logout,
      refreshUser,
    }),
    [user, isLoading, login, register, logout, refreshUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
