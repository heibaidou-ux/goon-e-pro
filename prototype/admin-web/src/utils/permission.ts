import permissions from '@mock/permissions.json'

export interface Resource {
  resourceId: string
  type: string
  label: string
  route?: string
  action?: string
}

export interface Role {
  roleId: string
  name: string
  description: string
  isSystem: boolean
  color: string
}

export interface RolePermission {
  roleId: string
  permissions: string[]
}

export interface UserRole {
  userId: string
  name: string
  roles: string[]
  store: string
}

// Get the current user's role from localStorage
export function getCurrentUserRoles(): string[] {
  const userJson = localStorage.getItem('erp_user')
  if (!userJson) return []

  const userRoles = (permissions.userRoles as UserRole[])
  const found = userRoles.find(u => u.name === userJson)
  return found?.roles || []
}

// Check if current user has a specific permission (resourceId)
export function hasPermission(resourceId: string): boolean {
  const roles = getCurrentUserRoles()
  if (roles.length === 0) return false

  const rolePerms = permissions.rolePermissions as RolePermission[]
  for (const rp of rolePerms) {
    if (roles.includes(rp.roleId)) {
      if (rp.permissions.includes('*')) return true
      if (rp.permissions.includes(resourceId)) return true
    }
  }
  return false
}

// Check if user has any of the given permissions
export function hasAnyPermission(resourceIds: string[]): boolean {
  return resourceIds.some(id => hasPermission(id))
}

// Get all menu resources visible to the current user
export function getAccessibleMenus(): Resource[] {
  const roles = getCurrentUserRoles()
  if (roles.length === 0) return []

  const rolePerms = (permissions.rolePermissions as RolePermission[])
  let allowedResources: string[] = []

  for (const rp of rolePerms) {
    if (roles.includes(rp.roleId)) {
      if (rp.permissions.includes('*')) {
        return (permissions.resources as Resource[]).filter(r => r.type === 'menu')
      }
      allowedResources = [...allowedResources, ...rp.permissions]
    }
  }

  const allMenus = (permissions.resources as Resource[]).filter(r => r.type === 'menu')
  return allMenus.filter(m => allowedResources.includes(m.resourceId))
}

// Get all roles
export function getAllRoles(): Role[] {
  return permissions.roles as Role[]
}

// Get role permissions
export function getRolePermissions(roleId: string): string[] {
  const rp = (permissions.rolePermissions as RolePermission[]).find(r => r.roleId === roleId)
  return rp?.permissions || []
}

// Get all resources
export function getAllResources(): Resource[] {
  return permissions.resources as Resource[]
}

// Get user-role assignments
export function getUserRolesList(): UserRole[] {
  return permissions.userRoles as UserRole[]
}

// Export for admin configuration pages
export {
  permissions,
}
