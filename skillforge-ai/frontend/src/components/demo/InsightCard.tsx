export function InsightCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <article className="rounded-xl border border-ai/20 bg-ai-soft/70 p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-ai">{title}</p>
      <div className="mt-3 text-sm leading-relaxed text-ink">{children}</div>
    </article>
  )
}
