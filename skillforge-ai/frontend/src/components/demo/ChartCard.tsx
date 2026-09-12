export function ChartCard({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-panel p-5 shadow-sm">
      <h2 className="font-display text-lg font-semibold text-navy">{title}</h2>
      {subtitle && <p className="mt-1 text-sm text-ink-muted">{subtitle}</p>}
      <div className="mt-4 h-64 w-full">{children}</div>
    </section>
  )
}
