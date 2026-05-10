<template>
  <div>
    <h2 class="page-header">智能对账</h2>

    <t-alert message="系统自动将每笔订单与平台账单比对，发现差异生成工单。月结前必须处理完所有工单。" theme="info" style="margin-bottom:20px" />

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in recStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="2">
          <t-select v-model="filterPlatform" placeholder="平台" clearable>
            <t-option value="美团" label="美团" />
            <t-option value="抖音" label="抖音" />
            <t-option value="ERP" label="ERP内部" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterRecStatus" placeholder="状态" clearable>
            <t-option value="待处理" label="待处理" />
            <t-option value="已通过" label="已通过" />
          </t-select>
        </t-col>
      </t-row>

      <t-table :data="filteredTasks" :columns="taskColumns" row-key="taskId" hover stripe>
        <template #type="{ row }">
          <t-tag :theme="row.type === '金额一致' ? 'success' : 'danger'" size="small" variant="light">{{ row.type }}</t-tag>
        </template>
        <template #diffAmount="{ row }">
          <span v-if="row.diffAmount > 0" style="color:#D54941;font-weight:600">¥{{ row.diffAmount }}</span>
          <span v-else style="color:#00A870">—</span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '待处理' ? 'warning' : 'success'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status === '待处理'" size="small" theme="success" variant="text" @click="row.status='已通过';row.handler='店员';row.remark='已核实处理'">标记已处理</t-button>
            <t-button size="small" variant="text" theme="primary" @click="selectedTask=row;taskDetailVisible=true">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="taskDetailVisible" header="差异工单详情" width="480px" :footer="false">
      <div v-if="selectedTask" class="detail-sections">
        <div class="detail-row"><span>工单编号</span><span>{{ selectedTask.taskId }}</span></div>
        <div class="detail-row"><span>平台</span><t-tag variant="light">{{ selectedTask.platform }}</t-tag></div>
        <div class="detail-row"><span>订单号</span><span>{{ selectedTask.orderNo }}</span></div>
        <div class="detail-row"><span>系统金额</span><span>¥{{ selectedTask.systemAmount }}</span></div>
        <div class="detail-row"><span>平台金额</span><span>¥{{ selectedTask.platformAmount }}</span></div>
        <div class="detail-row" v-if="selectedTask.diffAmount"><span>差异金额</span><span class="diff-amount">¥{{ selectedTask.diffAmount }}</span></div>
        <div class="detail-row"><span>差异类型</span><t-tag :theme="selectedTask.type==='金额一致'?'success':'danger'" size="small">{{ selectedTask.type }}</t-tag></div>
        <div class="detail-row"><span>创建时间</span><span>{{ selectedTask.createdAt }}</span></div>
        <div class="detail-row"><span>处理人</span><span>{{ selectedTask.handler || '—' }}</span></div>
        <div class="detail-row"><span>备注</span><span>{{ selectedTask.remark || '—' }}</span></div>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import finance from '@mock/finance.json'

const filterPlatform = ref('')
const filterRecStatus = ref('')
const taskDetailVisible = ref(false)
const selectedTask = ref<any>(null)

const tasks = finance.reconciliationTasks

const recStats = computed(() => [
  { label: '工单总数', value: tasks.length, color: '#0052D9' },
  { label: '待处理', value: tasks.filter(t => t.status === '待处理').length, color: '#D54941' },
  { label: '已通过', value: tasks.filter(t => t.status === '已通过').length, color: '#00A870' },
  { label: '差异总金额', value: '¥' + tasks.filter(t => t.status === '待处理').reduce((s, t) => s + t.diffAmount, 0).toLocaleString(), color: '#E37318' },
])

const filteredTasks = computed(() => {
  let list = tasks
  if (filterPlatform.value) list = list.filter(t => t.platform === filterPlatform.value)
  if (filterRecStatus.value) list = list.filter(t => t.status === filterRecStatus.value)
  return list
})

const taskColumns = [
  { colKey: 'taskId', title: '工单编号', width: 100 },
  { colKey: 'platform', title: '平台', width: 70 },
  { colKey: 'orderNo', title: '订单号', width: 160 },
  { colKey: 'type', title: '差异类型', width: 170 },
  { colKey: 'diffAmount', title: '差异金额', width: 90 },
  { colKey: 'createdAt', title: '创建时间', width: 100 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 180 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
.detail-sections { padding: 8px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.diff-amount { color: #D54941; font-weight: 600; }
</style>
