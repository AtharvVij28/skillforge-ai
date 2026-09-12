import { frameworkCategories } from '@/data/demoData'

export function AdminFrameworkPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="font-display text-3xl font-semibold text-navy">Competency Framework</h1>
        <p className="mt-1 max-w-3xl text-ink-muted">
          Framework categories are data, not hardcoded product logic. Future admin tools will edit these records
          without changing application code.
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {frameworkCategories.map((category) => (
          <section key={category.name} className="rounded-xl border border-line bg-panel p-5 shadow-sm">
            <h2 className="font-semibold text-navy">{category.name}</h2>
            <ul className="mt-3 space-y-2 text-sm text-ink-muted">
              {category.items.map((item) => (
                <li key={item} className="border-b border-line/70 pb-2 last:border-0">
                  {item}
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  )
}
