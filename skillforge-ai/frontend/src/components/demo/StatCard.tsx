export function StatCard({
  label,
  value,
  hint,
}: {
  label: string
  value: string
  hint?: string
}) {
  return (
    <article className="rounded-xl border border-line bg-panel p-5 shadow-sm transition hover:border-ai/30 hover:shadow-md">
      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-ink-muted">{label}</p>
      <p className="mt-2 font-display text-3xl font-semibold text-navy">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-muted">{hint}</p>}
    </article>
  )
}
