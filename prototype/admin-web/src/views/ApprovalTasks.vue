<template>
  <div>
    <h2 class="page-header">审批中心</h2>
    <t-alert message="所有待审批事项统一在这里处理。支持按流程类型、优先级筛选。审批通过后自动进入下一节点或完成流程。" theme="info" style="margin-bottom:20px" />

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in stats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="2">
          <t-select v-model="filterType" placeholder="流程类型" clearable>
            <t-option v-for="d in defs" :key="d.workflowId" :value="d.workflowId" :label="d.name" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterPriority" placeholder="优先级" clearable>
            <t-option value="high" label="高优先级" />
            <t-option value="normal" label="普通" />
            <t-option value="low" label="低优先级" />
          </t-select>
        </t-col>
      </t-row>

      <t-tabs v-model="taskTab" :list="taskTabs" style="margin-bottom:16px" />
      <t-table :data="filteredTasks" :columns="taskColumns" row-key="taskId" hover stripe>
        <template #priority="{ row }">
          <t-tag :theme="row.priority === 'high' ? 'danger' : row.priority === 'low' ? 'default' : 'warning'" size="small" variant="light">
            {{ row.priority === 'high' ? '高' : row.priority === 'low' ? '低' : '普通' }}
          </t-tag>
        </template>
        <template #status="{ row }">
          <t-tag theme="warning" size="small" variant="light">待处理</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="hasPermission('BTN_APPROVE')" size="small" theme="success" @click="openApproveDialog(row)">通过</t-button>
            <t-button v-if="hasPermission('BTN_REJECT')" size="small" theme="danger" variant="outline" @click="openRejectDialog(row)">驳回</t-button>
            <t-button size="small" variant="text" theme="primary" @click="viewInstance(row)">流转</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- Approve Dialog -->
    <t-dialog v-model:visible="approveDialogVisible" header="审批确认" width="480px" :footer="false">
      <div v-if="currentTask" class="approve-task-info">
        <div class="approve-task-header">
          <t-tag variant="light">{{ getDefName(currentTask.workflowId) }}</t-tag>
          <t-tag :theme="currentTask.priority === 'high' ? 'danger' : 'warning'" size="small">{{ currentTask.priority === 'high' ? '高优先级' : '普通' }}</t-tag>
        </div>
        <div class="approve-task-title">{{ currentTask.entityName }}</div>
        <div class="approve-task-desc">{{ currentTask.summary }}</div>

        <t-divider />
        <div class="approve-section">
          <div class="approve-label">当前节点</div>
          <t-tag variant="light">{{ currentTask.nodeName }}</t-tag>
          <t-tag variant="light" style="margin-left:8px">{{ roleLabel(currentTask.assigneeRole) }}</t-tag>
        </div>

        <div class="approve-section">
          <div class="approve-label">审批意见</div>
          <t-textarea v-model="approveComment" placeholder="请填写审批意见（可选）" :maxlength="200" />
        </div>

        <!-- Next steps -->
        <div v-if="nextStep" class="approve-section next-step-info">
          <div class="approve-label">审批通过后</div>
          <t-alert v-if="nextStep.isFinal" theme="success" message="流程审批完成，将标记为已通过" />
          <t-alert v-else theme="primary" message="流转至下一节点：{{ nextStep.nodeName }}（{{ roleLabel(nextStep.assigneeRole) }}）" />
        </div>

        <div style="margin-top:20px;display:flex;gap:10px;justify-content:flex-end">
          <t-button variant="outline" @click="approveDialogVisible = false">取消</t-button>
          <t-button theme="success" @click="confirmApprove">确认通过</t-button>
        </div>
      </div>
    </t-dialog>

    <!-- Reject Dialog -->
    <t-dialog v-model:visible="rejectDialogVisible" header="驳回" width="480px" :footer="false">
      <div v-if="currentTask">
        <div class="approve-task-info">
          <div class="approve-task-title">{{ currentTask.entityName }}</div>
          <div class="approve-task-desc">{{ currentTask.summary }}</div>
        </div>
        <t-divider />
        <div class="approve-section">
          <div class="approve-label">驳回原因 <span style="color:#D54941">*</span></div>
          <t-textarea v-model="rejectReason" placeholder="请填写驳回原因" :maxlength="200" />
        </div>
        <div style="margin-top:20px;display:flex;gap:10px;justify-content:flex-end">
          <t-button variant="outline" @click="rejectDialogVisible = false">取消</t-button>
          <t-button theme="danger" @click="confirmReject" :disabled="!rejectReason.trim()">确认驳回</t-button>
        </div>
      </div>
    </t-dialog>

    <!-- Flow Instance Drawer -->
    <t-drawer v-model:visible="instanceDrawerVisible" header="流程流转图" size="400px" :footer="false">
      <div v-if="instanceView" class="flow-view">
        <div class="flow-status">
          <t-tag :theme="instanceView.status === 'running' ? 'warning' : 'success'" size="large">
            {{ instanceView.status === 'running' ? '进行中' : '已完成' }}
          </t-tag>
        </div>

        <div class="flow-timeline">
          <div v-for="(step, idx) in flowTimeline" :key="idx" class="flow-step" :class="{ active: step.active, done: step.done, rejected: step.rejected }">
            <div class="flow-dot" :style="{ background: step.active ? '#E37318' : step.rejected ? '#D54941' : step.done ? '#00A870' : '#ddd' }"></div>
            <div class="flow-content">
              <div class="flow-node-name">{{ step.name }}</div>
              <div class="flow-node-role">{{ step.role }}</div>
              <div class="flow-node-time" v-if="step.time">{{ step.time }}</div>
              <div class="flow-node-comment" v-if="step.comment">「{{ step.comment }}」</div>
            </div>
          </div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { hasPermission } from '@/utils/permission'
import { getDefs, getTasksForRole, getNextNode, getInstance, getFirstNode, workflow } from '@/utils/workflow-engine'

const taskTab = ref('pending')
const filterType = ref('')
const filterPriority = ref('')
const approveDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const instanceDrawerVisible = ref(false)
const currentTask = ref<any>(null)
const approveComment = ref('')
const rejectReason = ref('')
const instanceView = ref<any>(null)
const nextStep = ref<any>(null)
const flowTimeline = ref<any[]>([])

const defs = getDefs()

// Simulate: current user's role from localStorage
const currentRole = computed(() => {
  const user = localStorage.getItem('erp_user')
  const roleMap: Record<string, string> = { '张店长': 'store_manager', '李财务': 'finance', '王运营': 'head_office' }
  return user ? (roleMap[user] || 'store_manager') : 'store_manager'
})

const allTasks = computed(() => getTasksForRole(currentRole.value))
const taskTabs = [
  { value: 'pending', label: `待处理（${allTasks.value.length}）` },
  { value: 'history', label: '已处理' },
]

const stats = computed(() => {
  const high = allTasks.value.filter(t => t.priority === 'high').length
  return [
    { label: '待审批', value: allTasks.value.length, color: '#E37318' },
    { label: '高优先级', value: high, color: '#D54941' },
    { label: '流程数', value: defs.length, color: '#0052D9' },
    { label: '本月已完成', value: '12', color: '#00A870' },
  ]
})

const filteredTasks = computed(() => {
  let list = allTasks.value
  if (filterType.value) list = list.filter(t => t.workflowId === filterType.value)
  if (filterPriority.value) list = list.filter(t => t.priority === filterPriority.value)
  return list
})

function getDefName(wfId: string): string {
  return defs.find(d => d.workflowId === wfId)?.name || wfId
}

function roleLabel(role: string): string {
  const map: Record<string, string> = { store_manager: '店长', finance: '财务', head_office: '总部运营' }
  return map[role] || role
}

function openApproveDialog(task: any) {
  currentTask.value = task
  approveComment.value = ''
  // Calculate next step
  const result = getNextNode(task.workflowId, task.nodeId, 'approve')
  if (result.isFinal) {
    nextStep.value = { isFinal: true }
  } else {
    const def = defs.find(d => d.workflowId === task.workflowId)
    const node = def?.nodes.find(n => n.nodeId === result.targetNodeId)
    if (node) {
      nextStep.value = { isFinal: false, nodeName: node.name, assigneeRole: node.assignee }
    }
  }
  approveDialogVisible.value = true
}

function openRejectDialog(task: any) {
  currentTask.value = task
  rejectReason.value = ''
  rejectDialogVisible.value = true
}

function confirmApprove() {
  if (!currentTask.value) return
  const task = currentTask.value
  task.status = 'approved'
  // In production: call API to advance workflow
  approveDialogVisible.value = false
}

function confirmReject() {
  if (!currentTask.value) return
  currentTask.value.status = 'rejected'
  rejectDialogVisible.value = false
}

function viewInstance(task: any) {
  const inst = getInstance(task.instanceId)
  instanceView.value = inst || task

  // Build timeline
  const def = defs.find(d => d.workflowId === task.workflowId)
  const steps = def?.nodes || []
  flowTimeline.value = steps.map((n, i) => ({
    name: n.name,
    role: roleLabel(n.assignee),
    active: n.nodeId === task.nodeId,
    done: false,
    rejected: false,
    time: i === 0 ? task.createdAt : undefined,
    comment: undefined,
  }))
  instanceDrawerVisible.value = true
}

const taskColumns = [
  { colKey: 'taskId', title: '任务编号', width: 120 },
  { colKey: 'entityName', title: '审批事项', width: 170 },
  { colKey: 'summary', title: '摘要', ellipsis: true },
  { colKey: 'priority', title: '优先级', width: 80 },
  { colKey: 'nodeName', title: '当前节点', width: 100 },
  { colKey: 'createdAt', title: '创建时间', width: 100 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 200 },
]
</script>

<style scoped>
/* .page-header, .stat-card, .stat-num, .stat-label from global */

.approve-task-info { padding: 4px 0; }
.approve-task-header { display: flex; gap: 8px; margin-bottom: 8px; }
.approve-task-title { font-size: 16px; font-weight: 600; color: #333; }
.approve-task-desc { font-size: 13px; color: #999; margin-top: 4px; }
.approve-section { margin-top: 16px; }
.approve-label { font-size: 13px; font-weight: 600; color: #333; margin-bottom: 6px; }
.next-step-info { background: #f5f7fa; padding: 12px; border-radius: 6px; }

.flow-view { padding: 8px 0; }
.flow-status { text-align: center; margin-bottom: 24px; }
.flow-timeline { position: relative; padding-left: 20px; }
.flow-step { display: flex; gap: 12px; padding-bottom: 24px; position: relative; }
.flow-step:last-child { padding-bottom: 0; }
.flow-step::before { content: ''; position: absolute; left: 6px; top: 16px; bottom: 0; width: 2px; background: #eee; }
.flow-step:last-child::before { display: none; }
.flow-dot { width: 14px; height: 14px; border-radius: 50%; flex-shrink: 0; margin-top: 2px; }
.flow-content { flex: 1; }
.flow-node-name { font-weight: 600; font-size: 14px; color: #333; }
.flow-node-role { font-size: 12px; color: #999; }
.flow-node-time { font-size: 11px; color: #bbb; margin-top: 2px; }
.flow-node-comment { font-size: 12px; color: #666; font-style: italic; margin-top: 2px; }
</style>
