export function isAdminRole(code?: string | null, name?: string | null): boolean {
  const roleCode = (code || '').toUpperCase()
  const roleName = (name || '').toUpperCase()
  return roleCode === 'ADMIN' || roleName.includes('ADMIN')
}
