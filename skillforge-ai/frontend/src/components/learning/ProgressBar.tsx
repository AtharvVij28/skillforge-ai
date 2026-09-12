type ProgressBarProps = {
  value: number
  className?: string
}

export function ProgressBar({ value, className = '' }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(100, value))
  return (
    <div className={`h-2.5 w-full overflow-hidden rounded-full bg-line ${className}`}>
      <div
        className="h-full rounded-full bg-gradient-to-r from-navy-mid to-ai transition-all duration-500"
        style={{ width: `${clamped}%` }}
      />
    </div>
  )
}
