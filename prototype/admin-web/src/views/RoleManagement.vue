<template>
  <div>
    <h2 class="page-header">角色管理</h2>
    <t-alert message="管理系统中的所有角色。系统角色不可删除，自定义角色可自由配置权限集。" theme="info" style="margin-bottom:20px" />

    <t-card :bordered="true">
      <t-table :data="roles" :columns="columns" row-key="roleId" hover stripe>
        <template #color="{ row }">
          <div style="display:flex;align-items:center;gap:6px">
            <span :style="{ display:'inline-block', width:12, height:12, borderRadius:'50%', background:row.color }"></span>
            <span>{{ row.name }}</span>
          </div>
        </template>
        <template #isSystem="{ row }">
          <t-tag v-if="row.isSystem" theme="primary" size="small" variant="light">系统</t-tag>
          <t-tag v-else theme="default" size="small" variant="light">自定义</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="editRole(row)">编辑</t-button>
            <t-button size="small" variant="text" theme="danger" :disabled="row.isSystem" @click="deleteRole(row)">删除</t-button>
          </t-space>
        </template>
      </t-table>
      <div style="margin-top:16px">
        <t-button theme="primary" @click="addRole">+ 新建角色</t-button>
      </div>
    </t-card>

    <t-dialog v-model:visible="dialogVisible" :header="isEditing ? '编辑角色' : '新建角色'" width="480px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="角色名称"><t-input v-model="form.name" placeholder="请输入角色名称" /></t-form-item>
        <t-form-item label="角色标识"><t-input v-model="form.roleId" :disabled="isEditing" placeholder="英文标识，如 senior_manager" /></t-form-item>
        <t-form-item label="角色描述"><t-textarea v-model="form.description" :maxlength="200" /></t-form-item>
        <t-form-item label="颜色">
          <t-select v-model="form.color">
            <t-option value="#0052D9" label="蓝色" />
            <t-option value="#00A870" label="绿色" />
            <t-option value="#E37318" label="橙色" />
            <t-option value="#D54941" label="红色" />
            <t-option value="#9C27B0" label="紫色" />
            <t-option value="#333333" label="黑色" />
          </t-select>
        </t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="dialogVisible = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="saveRole">保存</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getAllRoles, permissions } from '@/utils/permission'

const roles = ref(getAllRoles())
const dialogVisible = ref(false)
const isEditing = ref(false)
const form = ref({ roleId: '', name: '', description: '', color: '#0052D9' })
const editingRoleId = ref('')

function editRole(role: any) {
  isEditing.value = true
  editingRoleId.value = role.roleId
  form.value = { roleId: role.roleId, name: role.name, description: role.description, color: role.color }
  dialogVisible.value = true
}

function addRole() {
  isEditing.value = false
  editingRoleId.value = ''
  form.value = { roleId: '', name: '', description: '', color: '#0052D9' }
  dialogVisible.value = true
}

function saveRole() {
  if (!form.value.name || !form.value.roleId) return
  if (isEditing.value) {
    const idx = roles.value.findIndex((r: any) => r.roleId === editingRoleId.value)
    if (idx >= 0) {
      roles.value[idx] = { ...roles.value[idx], ...form.value }
    }
  } else {
    roles.value.push({
      roleId: form.value.roleId,
      name: form.value.name,
      description: form.value.description,
      isSystem: false,
      color: form.value.color,
    })
    // Also add empty permission entry for the new role
    ;(permissions.rolePermissions as any[]).push({ roleId: form.value.roleId, permissions: [] })
  }
  dialogVisible.value = false
}

function deleteRole(role: any) {
  const idx = roles.value.findIndex((r: any) => r.roleId === role.roleId)
  if (idx >= 0) roles.value.splice(idx, 1)
  // Also remove permission entry
  const rpIdx = (permissions.rolePermissions as any[]).findIndex((rp: any) => rp.roleId === role.roleId)
  if (rpIdx >= 0) (permissions.rolePermissions as any[]).splice(rpIdx, 1)
  // Remove user-role assignments
  const userRoles = permissions.userRoles as any[]
  for (const ur of userRoles) {
    const ridx = ur.roles.indexOf(role.roleId)
    if (ridx >= 0) ur.roles.splice(ridx, 1)
  }
}

const columns = [
  { colKey: 'roleId', title: '标识', width: 160 },
  { colKey: 'color', title: '角色', width: 100 },
  { colKey: 'description', title: '描述', ellipsis: true },
  { colKey: 'isSystem', title: '类型', width: 80 },
  { colKey: 'actions', title: '操作', width: 140 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
</style>
