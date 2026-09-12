export function firstNameFromFullName(fullName: string): string {
  const trimmed = fullName.trim()
  if (!trimmed) return 'Learner'
  return trimmed.split(/\s+/)[0] ?? 'Learner'
}
