<template>
  <div>
    <h2 class="page-header">用户角色分配</h2>
    <t-alert message="为每个用户分配一个或多个角色。用户的最终权限为其所有角色权限的并集。勾选即表示授予该用户对应角色。" theme="info" style="margin-bottom:20px" />

    <t-card :bordered="true">
      <t-table :data="userRolesList" :columns="columns" row-key="userId" hover stripe>
        <template #name="{ row }">
          <div style="display:flex;align-items:center;gap:6px">
            <t-icon name="user-circle" size="18px" />
            <span>{{ row.name }}</span>
          </div>
        </template>
        <template #store="{ row }">
          <t-tag variant="light" size="small">{{ row.store }}</t-tag>
        </template>
        <template #roles="{ row }">
          <t-space size="3">
            <t-tag
              v-for="roleId in row.roles"
              :key="roleId"
              size="small"
              :style="getRoleStyle(roleId)"
              closable
              @close="removeRole(row, roleId)"
            >
              {{ getRoleName(roleId) }}
            </t-tag>
            <t-button size="small" variant="text" theme="primary" @click="openAddRole(row)">+</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="dialogVisible" header="添加角色" width="360px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="选择角色">
          <t-select v-model="selectedRoleToAdd" placeholder="请选择角色">
            <t-option v-for="r in availableRoles" :key="r.roleId" :value="r.roleId" :label="r.name" />
          </t-select>
        </t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="dialogVisible = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" :disabled="!selectedRoleToAdd" @click="confirmAddRole">确认</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getUserRolesList, getAllRoles, permissions } from '@/utils/permission'

const userRolesList = ref(getUserRolesList())
const allRoles = getAllRoles()
const dialogVisible = ref(false)
const selectedRoleToAdd = ref('')
const currentUser = ref<any>(null)

function getRoleName(roleId: string): string {
  return allRoles.find(r => r.roleId === roleId)?.name || roleId
}

function getRoleStyle(roleId: string): Record<string, string> {
  const role = allRoles.find(r => r.roleId === roleId)
  return role ? { background: role.color + '22', color: role.color, borderColor: role.color + '44' } : {}
}

function openAddRole(user: any) {
  currentUser.value = user
  selectedRoleToAdd.value = ''
  dialogVisible.value = true
}

function confirmAddRole() {
  if (!currentUser.value || !selectedRoleToAdd.value) return
  if (!currentUser.value.roles.includes(selectedRoleToAdd.value)) {
    currentUser.value.roles.push(selectedRoleToAdd.value)
  }
  dialogVisible.value = false
}

function removeRole(user: any, roleId: string) {
  const idx = user.roles.indexOf(roleId)
  if (idx >= 0) user.roles.splice(idx, 1)
}

const availableRoles = computed(() => {
  if (!currentUser.value) return allRoles
  return allRoles.filter(r => !currentUser.value.roles.includes(r.roleId))
})

const columns = [
  { colKey: 'name', title: '用户', width: 140 },
  { colKey: 'store', title: '所属门店', width: 120 },
  { colKey: 'roles', title: '角色', ellipsis: true },
]
</script>

<style scoped>
</style>
