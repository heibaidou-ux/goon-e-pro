<template>
  <div>
    <h2 class="page-header">智能对账 · 核销中心</h2>

    <t-alert message="系统自动比对每笔订单与平台结算价，差额>0.1元自动标红。月结前必须处理完所有异常项。" theme="info" style="margin-bottom:20px" />

    <!-- 核销状态漏斗 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in recStats" :key="s.label">
        <t-card :bordered="true" :class="['stat-card-wrap', { 'stat-active': activeFunnel === s.key }]" @click="activeFunnel = s.key">
          <div class="stat-card">
            <div class="stat-num" :style="{ color: s.color }">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
            <div class="stat-sub" v-if="s.sub">{{ s.sub }}</div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 待确认流水池 -->
    <t-card :bordered="true" title="⏳ 待确认流水" style="margin-bottom:20px">
      <template #subtitle>
        <t-tag variant="light" theme="danger">{{ unmatchedTxs.length }}笔待核销</t-tag>
      </template>
      <t-table :data="unmatchedTxs" :columns="unmatchedColumns" row-key="txId" hover stripe>
        <template #risk="{ row }">
          <t-tag :theme="row.risk === 'high' ? 'danger' : row.risk === 'medium' ? 'warning' : 'success'" size="small">
            {{ row.risk === 'high' ? '高风险' : row.risk === 'medium' ? '中风险' : '低风险' }}
          </t-tag>
        </template>
        <template #diffAmount="{ row }">
          <span :style="{ color: row.diffAmount > 10 ? '#D54941' : '#E37318', fontWeight: 600 }">
            ¥{{ row.diffAmount }} ({{ row.diffRate }})
          </span>
        </template>
        <template #reason="{ row }">
          <t-tag variant="light" theme="warning" size="small">{{ row.reason }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" theme="primary" variant="text" @click="confirmTx(row)">确认</t-button>
            <t-button size="small" variant="text" @click="showTxDetail(row)">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 差异工单列表 -->
    <t-card :bordered="true" title="📋 对账差异工单">
      <template #subtitle>
        <t-space>
          <t-tag variant="light">已匹配 {{ tasks.filter(t => t.diffAmount === 0).length }}</t-tag>
          <t-tag variant="light" theme="danger">异常 {{ tasks.filter(t => t.diffAmount > 0).length }}</t-tag>
        </t-space>
      </template>
      <template #actions>
        <t-button size="small" variant="outline" theme="primary" @click="showToast('导出对账报表')">导出报表</t-button>
      </template>

      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="2">
          <t-select v-model="filterPlatform" placeholder="平台" clearable>
            <t-option value="美团" label="美团" />
            <t-option value="抖音" label="抖音" />
            <t-option value="ERP" label="ERP内部" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterMatchStatus" placeholder="核销状态" clearable>
            <t-option value="matched" label="已匹配" />
            <t-option value="abnormal" label="异常" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterRecStatus" placeholder="处理状态" clearable>
            <t-option value="待处理" label="待处理" />
            <t-option value="已通过" label="已通过" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterChannel" placeholder="渠道" clearable>
            <t-option value="包间预订" label="包间预订" />
            <t-option value="到店餐饮" label="到店餐饮" />
            <t-option value="团购套餐" label="团购套餐" />
            <t-option value="会员充值" label="会员充值" />
            <t-option value="线下收款" label="线下收款" />
          </t-select>
        </t-col>
      </t-row>

      <t-table :data="filteredTasks" :columns="taskColumns" row-key="taskId" hover stripe>
        <template #type="{ row }">
          <t-tag :theme="row.type === '金额一致' ? 'success' : 'danger'" size="small" variant="light">{{ row.type }}</t-tag>
        </template>
        <template #matchStatus="{ row }">
          <t-tag :theme="row.diffAmount === 0 ? 'success' : 'danger'" size="small" variant="light">
            {{ row.diffAmount === 0 ? '✅ 已匹配' : '❌ 异常' }}
          </t-tag>
        </template>
        <template #diffAmount="{ row }">
          <span v-if="row.diffAmount > 0" style="color:#D54941;font-weight:600">¥{{ row.diffAmount }}</span>
          <span v-else style="color:#00A870">—</span>
        </template>
        <template #diffReason="{ row }">
          <t-tag v-if="row.diffReason" variant="light" theme="warning" size="small">{{ row.diffReason }}</t-tag>
          <span v-else style="color:#999">—</span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '待处理' ? 'warning' : 'success'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status === '待处理' && row.diffAmount === 0" size="small" theme="success" variant="text" @click="markResolved(row)">标记已处理</t-button>
            <t-button v-if="row.status === '待处理' && row.diffAmount > 0" size="small" theme="warning" variant="text" @click="openManualAlign(row)">手动对齐</t-button>
            <t-button size="small" variant="text" theme="primary" @click="selectedTask=row;taskDetailVisible=true">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 手动对齐对话框 -->
    <t-dialog v-model:visible="alignDialogVisible" header="手动对齐" width="420px" :footer="false">
      <div v-if="alignTask" class="detail-sections">
        <t-alert message="差额较小或已知原因时，可手动强行对齐。操作将记录为'人工调账'审计日志。" theme="warning" style="margin-bottom:14px" />
        <div class="detail-row"><span>工单</span><span>{{ alignTask.taskId }} · {{ alignTask.orderNo }}</span></div>
        <div class="detail-row"><span>差额</span><span class="diff-amount">¥{{ alignTask.diffAmount }}</span></div>
        <div class="detail-row"><span>差异原因</span><span>{{ alignTask.diffReason || '—' }}</span></div>
        <t-form style="margin-top:14px">
          <t-form-item label="调账备注">
            <t-textarea v-model="alignRemark" placeholder="请输入调账原因（必填），如：美团满减活动差额、抖音平台服务费差异等" :rows="3" />
          </t-form-item>
          <t-space style="margin-top:12px">
            <t-button theme="warning" @click="confirmManualAlign">确认强行对齐</t-button>
            <t-button variant="outline" @click="alignDialogVisible=false">取消</t-button>
          </t-space>
        </t-form>
      </div>
    </t-dialog>

    <t-dialog v-model:visible="taskDetailVisible" header="差异工单详情" width="480px" :footer="false">
      <div v-if="selectedTask" class="detail-sections">
        <div class="detail-row"><span>工单编号</span><span>{{ selectedTask.taskId }}</span></div>
        <div class="detail-row"><span>平台</span><t-tag variant="light">{{ selectedTask.platform }}</t-tag></div>
        <div class="detail-row"><span>订单号</span><span>{{ selectedTask.orderNo }}</span></div>
        <div class="detail-row"><span>渠道</span><t-tag variant="light">{{ selectedTask.channel }}</t-tag></div>
        <div class="detail-row"><span>系统金额</span><span>¥{{ selectedTask.systemAmount }}</span></div>
        <div class="detail-row"><span>平台结算金额</span><span>¥{{ selectedTask.platformAmount }}</span></div>
        <div class="detail-row" v-if="selectedTask.diffAmount"><span>差异金额</span><span class="diff-amount">¥{{ selectedTask.diffAmount }}</span></div>
        <div class="detail-row"><span>差异原因</span><t-tag v-if="selectedTask.diffReason" theme="warning" variant="light" size="small">{{ selectedTask.diffReason }}</t-tag><span v-else>—</span></div>
        <div class="detail-row"><span>核销状态</span>
          <t-tag :theme="selectedTask.diffAmount === 0 ? 'success' : 'danger'" size="small">
            {{ selectedTask.diffAmount === 0 ? '已匹配' : '异常' }}
          </t-tag>
        </div>
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
const filterMatchStatus = ref('')
const filterRecStatus = ref('')
const filterChannel = ref('')
const activeFunnel = ref('all')
const taskDetailVisible = ref(false)
const selectedTask = ref<any>(null)
const alignDialogVisible = ref(false)
const alignTask = ref<any>(null)
const alignRemark = ref('')

const tasks = finance.reconciliationTasks
const unmatchedTxs = finance.unmatchedTransactions

const recStats = computed(() => {
  const total = tasks.length
  const matched = tasks.filter(t => t.diffAmount === 0).length
  const abnormal = tasks.filter(t => t.diffAmount > 0 && t.status === '待处理').length
  const resolved = tasks.filter(t => t.status === '已通过').length
  const totalDiff = tasks.filter(t => t.status === '待处理').reduce((s, t) => s + t.diffAmount, 0)
  return [
    { key: 'all', label: '工单总数', value: total, color: '#0052D9', sub: `${matched}已匹配 · ${abnormal}异常` },
    { key: 'matched', label: '已匹配', value: matched, color: '#00A870', sub: '自动核销通过' },
    { key: 'abnormal', label: '异常待处理', value: abnormal, color: '#D54941', sub: `待确认 ¥${totalDiff}` },
    { key: 'resolved', label: '已处理', value: resolved, color: '#999', sub: '已完成核销' },
  ]
})

const filteredTasks = computed(() => {
  let list = tasks
  if (filterPlatform.value) list = list.filter(t => t.platform === filterPlatform.value)
  if (filterMatchStatus.value === 'matched') list = list.filter(t => t.diffAmount === 0)
  if (filterMatchStatus.value === 'abnormal') list = list.filter(t => t.diffAmount > 0)
  if (filterRecStatus.value) list = list.filter(t => t.status === filterRecStatus.value)
  if (filterChannel.value) list = list.filter(t => t.channel === filterChannel.value)
  if (activeFunnel.value === 'matched') list = list.filter(t => t.diffAmount === 0)
  if (activeFunnel.value === 'abnormal') list = list.filter(t => t.diffAmount > 0 && t.status === '待处理')
  if (activeFunnel.value === 'resolved') list = list.filter(t => t.status === '已通过')
  return list
})

const taskColumns = [
  { colKey: 'taskId', title: '工单编号', width: 100 },
  { colKey: 'platform', title: '平台', width: 70 },
  { colKey: 'channel', title: '渠道', width: 80 },
  { colKey: 'orderNo', title: '订单号', width: 160 },
  { colKey: 'matchStatus', title: '核销', width: 90 },
  { colKey: 'type', title: '差异类型', width: 170 },
  { colKey: 'diffAmount', title: '差异金额', width: 90 },
  { colKey: 'diffReason', title: '差异原因', width: 150 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 160 },
]

const unmatchedColumns = [
  { colKey: 'orderNo', title: '订单号', width: 160 },
  { colKey: 'platform', title: '平台', width: 60 },
  { colKey: 'channel', title: '渠道', width: 80 },
  { colKey: 'diffAmount', title: '差异', width: 120 },
  { colKey: 'reason', title: '差异原因', width: 150 },
  { colKey: 'risk', title: '风险等级', width: 80 },
  { colKey: 'detectedAt', title: '检测时间', width: 90 },
  { colKey: 'actions', title: '操作', width: 120 },
]

function markResolved(row: any) {
  row.status = '已通过'
  row.handler = localStorage.getItem('erp_user') || '店员'
  row.remark = '已核实处理'
}

function openManualAlign(row: any) {
  alignTask.value = row
  alignRemark.value = ''
  alignDialogVisible.value = true
}

function confirmManualAlign() {
  if (!alignRemark.value.trim()) { showToast('请填写调账备注理由'); return }
  const user = localStorage.getItem('erp_user') || '店员'
  alignTask.value.status = '已通过'
  alignTask.value.handler = user
  alignTask.value.remark = `人工调账: ${alignRemark.value}`
  alignDialogVisible.value = false
  // 生成审计日志
  const auditLogs = JSON.parse(localStorage.getItem('erp_audit_logs') || '[]')
  auditLogs.push({
    id: `ADJ${Date.now()}`,
    type: 'ManualAdjustment',
    taskId: alignTask.value.taskId,
    orderNo: alignTask.value.orderNo,
    platform: alignTask.value.platform,
    diffAmount: alignTask.value.diffAmount,
    reason: alignRemark.value,
    operator: user,
    createdAt: new Date().toLocaleString('zh-CN'),
    source: 'Reconciliation',
  })
  localStorage.setItem('erp_audit_logs', JSON.stringify(auditLogs))
  showToast(`✅ 人工调账完成，已记入审计日志`)
}

function confirmTx(row: any) {
  const idx = unmatchedTxs.indexOf(row)
  if (idx > -1) unmatchedTxs.splice(idx, 1)
  showToast('已确认，转入正常流水')
}

function showTxDetail(row: any) {
  showToast(`订单 ${row.orderNo}: 系统价 ¥${row.systemAmount} / 平台结算 ¥${row.platformSettlement}`)
}

function showToast(msg: string) {
  const el = document.createElement('div')
  el.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.8);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;z-index:9999'
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2000)
}
</script>

<style scoped>
.stat-card-wrap { cursor: pointer; transition: transform .15s; }
.stat-card-wrap:hover { transform: translateY(-2px); }
.stat-active { box-shadow: 0 0 0 2px #0052D9; border-radius: 8px; }
/* .stat-card, .stat-num, .stat-label, .detail-sections, .detail-row from global */
.stat-sub { font-size: 11px; color: #bbb; margin-top: 2px; }
.diff-amount { color: #D54941; font-weight: 600; }
</style>
