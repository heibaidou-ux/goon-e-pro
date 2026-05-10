<template>
  <div>
    <h2 class="page-header">权限配置</h2>
    <t-alert message="为每个角色分配可访问的资源（菜单和操作按钮）。勾选即表示授予该角色对应资源的访问权限。" theme="info" style="margin-bottom:20px" />

    <t-card :bordered="true">
      <t-radio-group v-model="selectedRole" variant="default" style="margin-bottom:16px">
        <t-radio-button v-for="r in roles" :key="r.roleId" :value="r.roleId">{{ r.name }}</t-radio-button>
      </t-radio-group>

      <t-divider />

      <t-form v-if="currentPermissions" layout="vertical">
        <div v-for="group in groupedResources" :key="group.label" class="perm-group">
          <div class="perm-group-header">{{ group.label }}</div>
          <div class="perm-items">
            <t-checkbox
              v-for="res in group.items"
              :key="res.resourceId"
              :value="res.resourceId"
              :checked="isChecked(res.resourceId)"
              @change="(checked: boolean) => togglePerm(res.resourceId, checked)"
            >
              <t-tag variant="light" size="small" :theme="res.type === 'menu' ? 'primary' : 'default'" style="margin-right:4px">
                {{ res.type === 'menu' ? '菜单' : '按钮' }}
              </t-tag>
              {{ res.label }}
            </t-checkbox>
          </div>
        </div>
      </t-form>

      <div v-if="!currentPermissions" style="padding:40px;text-align:center;color:#999">
        请先选择一个角色进行权限配置
      </div>

      <div v-if="currentPermissions" style="margin-top:20px;text-align:right">
        <t-button variant="outline" @click="resetPerms">重置</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="savePerms">保存权限配置</t-button>
      </div>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getAllRoles, getAllResources, getRolePermissions, permissions } from '@/utils/permission'

const roles = getAllRoles()
const allResources = getAllResources()
const selectedRole = ref('')
const localPerms = ref<Record<string, string[]>>({})

const groupedResources = computed(() => {
  const groups: { label: string; items: any[] }[] = []
  const menuMap: Record<string, any[]> = {}
  const buttonItems: any[] = []

  for (const res of allResources) {
    if (res.type === 'button') {
      buttonItems.push(res)
    } else {
      // Determine group from route
      let group = '其他'
      const route = res.route || ''
      if (route.startsWith('/dashboard') || route.startsWith('/rooms') || route.startsWith('/devices') || route.startsWith('/scenes') || route.startsWith('/alerts') || route.startsWith('/audit')) group = '门店运营'
      else if (route.startsWith('/product') || route.startsWith('/purchases') || route.startsWith('/inventory') || route.startsWith('/supplier')) group = '供应链'
      else if (route.startsWith('/revenue') || route.startsWith('/expense') || route.startsWith('/settlement') || route.startsWith('/reconciliation') || route.startsWith('/dividends') || route.startsWith('/reports') || route.startsWith('/assets')) group = '财务'
      else if (route.startsWith('/employee') || route.startsWith('/external') || route.startsWith('/scheduling') || route.startsWith('/attendance') || route.startsWith('/payroll') || route.startsWith('/performance') || route.startsWith('/cleaner')) group = '人力资源'
      else if (route.startsWith('/campaign') || route.startsWith('/coupon') || route.startsWith('/platform') || route.startsWith('/analysis')) group = '市场营销'
      else if (route.startsWith('/workflow') || route.startsWith('/approval') || route.startsWith('/role') || route.startsWith('/permission') || route.startsWith('/user-role')) group = '系统管理'

      if (!menuMap[group]) menuMap[group] = []
      menuMap[group].push(res)
    }
  }

  for (const [label, items] of Object.entries(menuMap)) {
    groups.push({ label, items })
  }
  groups.push({ label: '操作按钮', items: buttonItems })
  return groups
})

const currentPermissions = computed(() => {
  if (!selectedRole.value) return null
  if (!localPerms.value[selectedRole.value]) {
    localPerms.value[selectedRole.value] = [...getRolePermissions(selectedRole.value)]
  }
  return localPerms.value[selectedRole.value]
})

function isChecked(resourceId: string): boolean {
  const perms = currentPermissions.value
  if (!perms) return false
  if (perms.includes('*')) return true
  return perms.includes(resourceId)
}

function togglePerm(resourceId: string, checked: boolean) {
  const perms = localPerms.value[selectedRole.value]
  if (!perms) return
  if (checked) {
    if (!perms.includes(resourceId)) perms.push(resourceId)
  } else {
    const idx = perms.indexOf(resourceId)
    if (idx >= 0) perms.splice(idx, 1)
  }
}

function resetPerms() {
  localPerms.value[selectedRole.value] = [...getRolePermissions(selectedRole.value)]
}

function savePerms() {
  const perms = localPerms.value[selectedRole.value]
  if (!perms) return
  const rp = (permissions.rolePermissions as any[]).find((r: any) => r.roleId === selectedRole.value)
  if (rp) rp.permissions = perms
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.perm-group { margin-bottom: 20px; }
.perm-group-header { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 10px; padding: 6px 10px; background: #f5f7fa; border-radius: 4px; }
.perm-items { display: flex; flex-wrap: wrap; gap: 10px; padding: 0 10px; }
.perm-items .t-checkbox { margin-right: 16px; }
</style>
