<template>
  <div>
    <h2 class="page-header">流程定义管理</h2>
    <t-alert message="在这里配置所有的审批流程定义。每个流程包含多个审批节点，节点可按条件自动路由。修改后即时生效，无需重新部署。" theme="info" style="margin-bottom:20px" />

    <t-card :bordered="true">
      <t-table :data="defs" :columns="columns" row-key="workflowId" hover stripe @row-click="viewDef">
        <template #enabled="{ row }">
          <t-switch :value="row.enabled" size="small" @change="toggleDef(row)" />
        </template>
        <template #nodes="{ row }">{{ row.nodes.length }}个节点</template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click.stop="viewDef(row)">编辑</t-button>
            <t-button size="small" variant="text" @click.stop="cloneDef(row)">复制</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="drawerVisible" :header="`编辑流程：${editDef?.name}`" size="640px" :footer="false">
      <div v-if="editDef">
        <t-form layout="vertical">
          <t-form-item label="流程名称"><t-input v-model="editDef.name" /></t-form-item>
          <t-form-item label="说明"><t-textarea v-model="editDef.description" :maxlength="200" /></t-form-item>
          <t-form-item label="关联业务"><t-input :value="editDef.entityLabel" disabled /></t-form-item>
        </t-form>

        <t-divider />
        <div class="section-title">审批节点配置</div>

        <div v-for="(node, idx) in editDef.nodes" :key="node.nodeId" class="node-card">
          <t-card :bordered="true" class="node-card-inner">
            <div class="node-header">
              <t-tag variant="light">节点{{ idx + 1 }}</t-tag>
              <t-tag :theme="node.assignee === 'store_manager' ? 'primary' : node.assignee === 'finance' ? 'danger' : 'warning'" size="small" variant="light">{{ roleLabel(node.assignee) }}</t-tag>
              <t-button size="small" variant="text" v-if="editDef.nodes.length > 1" @click="removeNode(idx)" style="margin-left:auto;color:#D54941">删除</t-button>
            </div>
            <div class="node-form">
              <t-row :gutter="16">
                <t-col :span="8">
                  <t-form-item label="节点名称"><t-input v-model="node.name" /></t-form-item>
                </t-col>
                <t-col :span="8">
                  <t-form-item label="审批角色">
                    <t-select v-model="node.assignee">
                      <t-option value="store_manager" label="店长" />
                      <t-option value="finance" label="财务" />
                      <t-option value="head_office" label="总部运营" />
                    </t-select>
                  </t-form-item>
                </t-col>
                <t-col :span="4">
                  <t-form-item label="超时(小时)"><t-input v-model="node.timeoutHours" type="number" /></t-form-item>
                </t-col>
              </t-row>
              <div class="condition-section">
                <span class="condition-label">进入条件：</span>
                <span v-if="!node.conditions?.length" class="condition-empty">无条件（始终进入此节点）</span>
                <t-tag v-for="(c, ci) in node.conditions" :key="ci" closable @close="removeCondition(node, ci)" style="margin-right:4px">
                  {{ c.field }} {{ c.operator }} {{ c.value }}
                </t-tag>
                <t-button size="small" variant="text" theme="primary" @click="addCondition(node)">+ 添加条件</t-button>
              </div>
              <div class="node-actions">
                <span class="condition-label">通过 → <t-tag size="small" variant="light">{{ resolveLabel(node.actions.approve) }}</t-tag></span>
                <span class="condition-label" style="margin-left:16px">驳回 → <t-tag size="small" variant="light">{{ resolveLabel(node.actions.reject) }}</t-tag></span>
              </div>
            </div>
          </t-card>
          <div class="node-arrow" v-if="idx < editDef.nodes.length - 1">↓</div>
        </div>

        <t-button variant="outline" @click="addNode" style="width:100%;margin-top:8px">+ 添加审批节点</t-button>

        <div style="margin-top:24px;text-align:right">
          <t-button variant="outline" @click="drawerVisible = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="saveDef">保存流程定义</t-button>
        </div>
      </div>
    </t-drawer>

    <!-- Add Condition Dialog -->
    <t-dialog v-model:visible="conditionDialogVisible" header="添加条件" width="400px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="字段">
          <t-select v-model="newCond.field">
            <t-option value="totalAmount" label="总金额(totalAmount)" />
            <t-option value="amount" label="金额(amount)" />
            <t-option value="budget" label="预算(budget)" />
            <t-option value="amountChange" label="金额变动(amountChange)" />
          </t-select>
        </t-form-item>
        <t-form-item label="运算符">
          <t-select v-model="newCond.operator">
            <t-option value=">" label="大于" />
            <t-option value=">=" label="大于等于" />
            <t-option value="<" label="小于" />
            <t-option value="<=" label="小于等于" />
            <t-option value="==" label="等于" />
          </t-select>
        </t-form-item>
        <t-form-item label="阈值"><t-input v-model.number="newCond.value" type="number" /></t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="conditionDialogVisible = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="confirmAddCondition">确认</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getDefs as getDefData, workflow } from '@/utils/workflow-engine'

const defs = getDefData()
const drawerVisible = ref(false)
const editDef = ref<any>(null)
const conditionDialogVisible = ref(false)
const conditionTargetNode = ref<any>(null)
const newCond = ref({ field: 'totalAmount', operator: '>', value: 0 })

function roleLabel(role: string): string {
  const map: Record<string, string> = { store_manager: '店长', finance: '财务', head_office: '总部运营' }
  return map[role] || role
}

function resolveLabel(target: string): string {
  if (target === '__approved__') return '审批通过'
  if (target === '__rejected__') return '审批驳回'
  const def = editDef.value
  if (!def) return target
  const node = def.nodes.find((n: any) => n.nodeId === target)
  return node ? node.name : target
}

function viewDef(def: any) {
  editDef.value = JSON.parse(JSON.stringify(def))
  drawerVisible.value = true
}

function toggleDef(def: any) { def.enabled = !def.enabled }

function cloneDef(def: any) {
  const clone = JSON.parse(JSON.stringify(def))
  clone.workflowId = def.workflowId + '_COPY'
  clone.name = def.name + '（副本）'
  defs.push(clone)
}

function addNode() {
  if (!editDef.value) return
  const lastNode = editDef.value.nodes[editDef.value.nodes.length - 1]
  const newId = 'n' + (editDef.value.nodes.length + 1)
  const newNode = {
    nodeId: newId,
    name: '新审批节点',
    type: 'approval',
    assigneeType: 'role',
    assignee: 'store_manager',
    timeoutHours: 48,
    conditions: [],
    actions: { approve: '__approved__', reject: '__rejected__' },
  }
  if (lastNode) lastNode.actions.approve = newId
  editDef.value.nodes.push(newNode)
}

function removeNode(idx: number) {
  if (!editDef.value) return
  editDef.value.nodes.splice(idx, 1)
}

function addCondition(node: any) {
  conditionTargetNode.value = node
  newCond.value = { field: 'totalAmount', operator: '>', value: 0 }
  conditionDialogVisible.value = true
}

function removeCondition(node: any, idx: number) {
  node.conditions.splice(idx, 1)
}

function confirmAddCondition() {
  if (conditionTargetNode.value) {
    conditionTargetNode.value.conditions.push({ ...newCond.value })
  }
  conditionDialogVisible.value = false
}

function saveDef() {
  const idx = defs.findIndex((d: any) => d.workflowId === editDef.value.workflowId)
  if (idx >= 0) defs[idx] = editDef.value
  drawerVisible.value = false
}

const columns = [
  { colKey: 'workflowId', title: '流程ID', width: 150 },
  { colKey: 'name', title: '流程名称', width: 160 },
  { colKey: 'entityLabel', title: '关联业务', width: 100 },
  { colKey: 'nodes', title: '节点数', width: 80 },
  { colKey: 'description', title: '说明', ellipsis: true },
  { colKey: 'version', title: '版本', width: 60 },
  { colKey: 'enabled', title: '启用', width: 70 },
  { colKey: 'actions', title: '操作', width: 120 },
]
</script>

<style scoped>
.section-title { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 14px; }
.node-card { margin-bottom: 0; }
.node-card-inner { margin-bottom: 0; }
.node-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.node-form { padding-left: 8px; }
.condition-section { display: flex; align-items: center; flex-wrap: wrap; gap: 6px; padding: 8px 0; margin-top: 4px; background: #f9f9f9; border-radius: 4px; padding: 8px; }
.condition-label { font-size: 12px; color: #666; font-weight: 500; }
.condition-empty { font-size: 12px; color: #ccc; }
.node-actions { margin-top: 8px; padding: 6px 8px; background: #f5f7fa; border-radius: 4px; }
.node-arrow { text-align: center; color: #bbb; font-size: 20px; padding: 2px 0; line-height: 1; }
</style>
