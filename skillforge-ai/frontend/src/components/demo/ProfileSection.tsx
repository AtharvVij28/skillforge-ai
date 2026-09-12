export function ProfileSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-line bg-panel p-6 shadow-sm">
      <h2 className="font-display text-lg font-semibold text-navy">{title}</h2>
      <div className="mt-4">{children}</div>
    </section>
  )
}
