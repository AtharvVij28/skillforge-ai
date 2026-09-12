import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'

export type DemoMode = 'learner' | 'admin' | null

const STORAGE_KEY = 'skillforge_demo_mode'

type DemoContextValue = {
  mode: DemoMode
  enterLearner: () => void
  enterAdmin: () => void
  exitDemo: () => void
}

const DemoContext = createContext<DemoContextValue | undefined>(undefined)

function readStoredMode(): DemoMode {
  const value = sessionStorage.getItem(STORAGE_KEY)
  if (value === 'learner' || value === 'admin') return value
  return null
}

export function DemoProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate()
  const [mode, setMode] = useState<DemoMode>(() => readStoredMode())

  const value = useMemo<DemoContextValue>(
    () => ({
      mode,
      enterLearner: () => {
        sessionStorage.setItem(STORAGE_KEY, 'learner')
        setMode('learner')
        navigate('/dashboard')
      },
      enterAdmin: () => {
        sessionStorage.setItem(STORAGE_KEY, 'admin')
        setMode('admin')
        navigate('/admin')
      },
      exitDemo: () => {
        sessionStorage.removeItem(STORAGE_KEY)
        setMode(null)
        navigate('/')
      },
    }),
    [mode, navigate],
  )

  return <DemoContext.Provider value={value}>{children}</DemoContext.Provider>
}

export function useDemo() {
  const context = useContext(DemoContext)
  if (!context) {
    throw new Error('useDemo must be used within DemoProvider')
  }
  return context
}
