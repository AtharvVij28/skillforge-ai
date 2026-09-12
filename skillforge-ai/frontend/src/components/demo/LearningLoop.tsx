import { learningLoop } from '@/data/demoData'

export function LearningLoop({ variant = 'light' }: { variant?: 'light' | 'dark' }) {
  const isDark = variant === 'dark'
  return (
    <ol className="flex flex-wrap items-center gap-2">
      {learningLoop.map((step, index) => (
        <li key={step} className="flex items-center gap-2">
          <span
            className={`rounded-full px-3 py-1.5 text-xs font-semibold tracking-wide ${
              isDark ? 'bg-white/12 text-white' : 'bg-ai-soft text-navy'
            }`}
          >
            {step}
          </span>
          {index < learningLoop.length - 1 && (
            <span className={isDark ? 'text-white/50' : 'text-ink-muted'} aria-hidden>
              →
            </span>
          )}
        </li>
      ))}
    </ol>
  )
}
