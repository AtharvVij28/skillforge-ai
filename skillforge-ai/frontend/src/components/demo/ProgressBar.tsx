export function ProgressBar({
  value,
  tone = 'ai',
}: {
  value: number
  tone?: 'ai' | 'success' | 'amber' | 'danger' | 'navy'
}) {
  const colors = {
    ai: 'bg-ai',
    success: 'bg-success',
    amber: 'bg-amber',
    danger: 'bg-danger',
    navy: 'bg-navy-mid',
  }

  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-line/80">
      <div
        className={`h-full rounded-full transition-all duration-500 ${colors[tone]}`}
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  )
}
