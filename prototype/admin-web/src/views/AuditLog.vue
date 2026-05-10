<template>
  <div>
    <h2 class="page-header">操作审计 · 防抵赖日志</h2>

    <t-alert message="所有远程操作（开锁、场景覆盖、手动改状态）自动记录操作人、来源IP、执行结果。异常操作强制标注。" theme="info" style="margin-bottom:20px" />

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2">
        <t-select v-model="filterAction" placeholder="操作类型" clearable>
          <t-option value="ManualStatusChange" label="手动改状态" />
          <t-option value="RemoteUnlock" label="远程开门" />
          <t-option value="SceneOverride" label="场景覆盖" />
          <t-option value="RoomSetup" label="房间设置" />
          <t-option value="DeviceControl" label="设备控制" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterAuditStatus" placeholder="抽查状态" clearable>
          <t-option value="Pending" label="待抽查" />
          <t-option value="Reviewed" label="已抽查" />
          <t-option value="Flagged" label="异常标记" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterResult" placeholder="执行结果" clearable>
          <t-option value="success" label="成功" />
          <t-option value="failed" label="失败" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterRemote" placeholder="操作来源" clearable>
          <t-option value="remote" label="远程操作" />
          <t-option value="local" label="本地操作" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-date-picker v-model="filterDate" placeholder="操作日期" clearable />
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in auditStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <template #title>
        <t-space>
          <span>操作记录</span>
          <t-badge :count="pendingCount" v-if="pendingCount" />
        </t-space>
      </template>
      <template #actions>
        <t-button size="small" variant="outline" theme="primary">导出审计日志</t-button>
      </template>

      <t-table :data="filteredAuditLogs" :columns="columns" row-key="id" hover stripe>
        <template #action="{ row }">
          <t-tag :theme="actionTheme(row.action)" size="small" variant="light">{{ actionLabel(row.action) }}</t-tag>
        </template>
        <template #roomInfo="{ row }">
          <span>{{ row.roomName }}</span>
        </template>
        <template #operator="{ row }">
          <div class="operator-cell">
            <span class="operator-name">{{ row.operatorName }}</span>
            <span class="operator-role">{{ row.operatorRole }}<span v-if="row.remote" class="remote-badge">远程</span></span>
          </div>
        </template>
        <template #result="{ row }">
          <t-tag :theme="row.status === 'success' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'" size="small">
            {{ row.status === 'success' ? '✅ 成功' : row.status === 'failed' ? '❌ 失败' : '—' }}
          </t-tag>
        </template>
        <template #auditStatus="{ row }">
          <t-tag
            :theme="row.auditStatus === 'Pending' ? 'warning' : row.auditStatus === 'Reviewed' ? 'success' : 'danger'"
            size="small" variant="light"
          >{{ auditStatusLabel(row.auditStatus) }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button v-if="row.auditStatus === 'Pending'" size="small" variant="text" theme="success" @click="approve(row)">通过</t-button>
            <t-button v-if="row.auditStatus === 'Pending'" size="small" variant="text" theme="danger" @click="flag(row)">标记</t-button>
          </t-space>
        </template>
      </t-table>

      <t-pagination
        v-model="currentPage"
        :total="totalLogs"
        :page-size="pageSize"
        style="margin-top:16px"
        show-jumper
      />
    </t-card>

    <t-drawer v-model:visible="drawerVisible" header="操作审计详情" size="450px" :footer="false">
      <div v-if="selectedLog" class="detail-section">
        <div class="log-header">
          <t-tag :theme="actionTheme(selectedLog.action)" size="medium">{{ actionLabel(selectedLog.action) }}</t-tag>
          <span class="log-time">{{ selectedLog.createdAt }}</span>
        </div>
        <t-divider />
        <div class="detail-row"><span>操作人</span><span>{{ selectedLog.operatorName }} · {{ selectedLog.operatorRole }}</span></div>
        <div class="detail-row"><span>房间</span><span>{{ selectedLog.roomName }}</span></div>
        <div class="detail-row"><span>操作原因</span><span>{{ selectedLog.reason }}</span></div>
        <div class="detail-row"><span>目标状态</span><span>{{ selectedLog.targetStatus }}</span></div>
        <div class="detail-row"><span>原状态</span><span style="color:#999">{{ selectedLog.previousStatus }}</span></div>
        <t-divider />
        <div class="detail-row">
          <span>执行结果</span>
          <t-tag :theme="selectedLog.status === 'success' ? 'success' : selectedLog.status === 'failed' ? 'danger' : 'warning'" size="small">
            {{ selectedLog.status === 'success' ? '成功' : selectedLog.status === 'failed' ? '失败' : '待确认' }}
          </t-tag>
        </div>
        <div class="detail-row" v-if="selectedLog.sourceIp"><span>来源IP</span><code class="ip-code">{{ selectedLog.sourceIp }}</code></div>
        <div class="detail-row" v-if="selectedLog.remote !== undefined"><span>操作来源</span><span>{{ selectedLog.remote ? '远程(Web/API)' : '本地(门店)' }}</span></div>
        <t-divider />
        <div class="detail-row"><span>抽查状态</span>
          <t-tag :theme="selectedLog.auditStatus === 'Pending' ? 'warning' : selectedLog.auditStatus === 'Reviewed' ? 'success' : 'danger'" size="small">
            {{ auditStatusLabel(selectedLog.auditStatus) }}
          </t-tag>
        </div>
        <div v-if="selectedLog.reviewedBy" class="detail-row"><span>审核人</span><span>{{ selectedLog.reviewedBy }}</span></div>
        <div v-if="selectedLog.reviewNote" class="detail-row"><span>审核备注</span><span>{{ selectedLog.reviewNote }}</span></div>
        <t-divider v-if="selectedLog.auditStatus === 'Pending'" />
        <t-space v-if="selectedLog.auditStatus === 'Pending'" style="margin-top:12px">
          <t-button theme="success" @click="approve(selectedLog)">审核通过</t-button>
          <t-button theme="danger" variant="outline" @click="flag(selectedLog)">标记异常</t-button>
        </t-space>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { rooms } from '@/mock/data'

const currentPage = ref(1)
const pageSize = ref(10)
const filterAction = ref('')
const filterAuditStatus = ref('')
const filterResult = ref('')
const filterRemote = ref('')
const filterDate = ref('')
const drawerVisible = ref(false)
const selectedLog = ref<any>(null)

const auditLogs = ref([
  { id: 'AUD001', action: 'ForceCheckout', roomId: 'RM001', roomName: '大会议室', operatorId: 'EMP001', operatorName: '小林', operatorRole: '店长', reason: '客人超时15分钟未离开，经电话确认后操作', previousStatus: 'InUse', targetStatus: 'Cleaning', auditStatus: 'Pending', status: 'success', sourceIp: '192.168.1.100', remote: false, createdAt: '2026-05-08 11:45:00' },
  { id: 'AUD002', action: 'RemoteUnlock', roomId: 'RM002', roomName: '中茶室A', operatorId: 'EMP002', operatorName: '小陈', operatorRole: '服务员', reason: '门锁离线，客人手机没电无法开门，物理钥匙在后备箱', previousStatus: 'InUse', targetStatus: 'InUse', auditStatus: 'Reviewed', status: 'success', sourceIp: '192.168.1.103', remote: false, reviewedBy: 'EMP001', reviewedAt: '2026-05-08 11:00:00', createdAt: '2026-05-08 10:45:00' },
  { id: 'AUD003', action: 'ManualStatusChange', roomId: 'RM004', roomName: '大茶室C', operatorId: 'EMP001', operatorName: '小林', operatorRole: '店长', reason: '客人电话预约，系统显示时段被锁定，手动释放', previousStatus: 'Booked', targetStatus: 'Active', auditStatus: 'Pending', status: 'success', sourceIp: '192.168.1.100', remote: false, createdAt: '2026-05-08 09:30:00' },
  { id: 'AUD004', action: 'RemoteUnlock', roomId: 'RM004', roomName: '大茶室C', operatorId: 'E008', operatorName: '赵总', operatorRole: '总经理', reason: '远程开门：VIP客人已到店，系统自动门禁异常', previousStatus: 'Booked', targetStatus: 'InUse', auditStatus: 'Pending', status: 'success', sourceIp: '183.6.122.45', remote: true, createdAt: '2026-05-09 20:15:00' },
  { id: 'AUD005', action: 'SceneOverride', roomId: 'RM001', roomName: '大会议室', operatorId: 'EMP001', operatorName: '小林', operatorRole: '店长', reason: '客人反馈品茶场景灯太暗，手动切换至会议场景', previousStatus: 'TeaSession', targetStatus: 'Meeting', auditStatus: 'Reviewed', status: 'success', sourceIp: '192.168.1.100', remote: false, reviewedBy: 'EMP001', reviewedAt: '2026-05-07 16:30:00', createdAt: '2026-05-07 16:20:00' },
  { id: 'AUD006', action: 'RoomSetMaintenance', roomId: 'RM002', roomName: '中茶室A', operatorId: 'EMP003', operatorName: '阿强', operatorRole: '技术员', reason: '门锁更换电池中，暂时标记为维修状态', previousStatus: 'Active', targetStatus: 'Maintenance', auditStatus: 'Flagged', status: 'success', sourceIp: '192.168.1.101', remote: false, reviewedBy: 'EMP001', reviewedAt: '2026-05-07 14:00:00', reviewNote: '维修时长超预期：标记30分钟实际3小时', createdAt: '2026-05-07 11:00:00' },
  { id: 'AUD007', action: 'ForceCheckout', roomId: 'RM004', roomName: '大茶室C', operatorId: 'EMP002', operatorName: '小陈', operatorRole: '服务员', reason: '包间使用超时，下一位客人已到店等待', previousStatus: 'InUse', targetStatus: 'Cleaning', auditStatus: 'Pending', status: 'failed', sourceIp: '192.168.1.103', remote: false, createdAt: '2026-05-07 17:45:00' },
  { id: 'AUD008', action: 'RemoteUnlock', roomId: 'RM003', roomName: '中茶室B', operatorId: 'E008', operatorName: '赵总', operatorRole: '总经理', reason: '远程开门：客人报修门锁故障，远程应急开门', previousStatus: 'InUse', targetStatus: 'InUse', auditStatus: 'Pending', status: 'success', sourceIp: '183.6.122.45', remote: true, createdAt: '2026-05-06 22:30:00' },
  { id: 'AUD009', action: 'ManualStatusChange', roomId: 'RM001', roomName: '大会议室', operatorId: 'EMP001', operatorName: '小林', operatorRole: '店长', reason: '散客到店直接安排包间，未经过小程序预约', previousStatus: 'Active', targetStatus: 'InUse', auditStatus: 'Reviewed', status: 'success', sourceIp: '192.168.1.100', remote: false, reviewedBy: 'EMP001', reviewedAt: '2026-05-06 10:00:00', createdAt: '2026-05-06 09:55:00' },
  { id: 'AUD010', action: 'DeviceControl', roomId: 'RM002', roomName: '中茶室A', operatorId: 'E009', operatorName: '钱副总', operatorRole: '副总经理', reason: '远程控制空调：客人反馈温度过低', previousStatus: '24°C', targetStatus: '26°C', auditStatus: 'Pending', status: 'success', sourceIp: '47.96.233.18', remote: true, createdAt: '2026-05-09 14:20:00' },
])

const filteredAuditLogs = computed(() => {
  let list = auditLogs.value
  if (filterAction.value) list = list.filter(l => l.action === filterAction.value)
  if (filterAuditStatus.value) list = list.filter(l => l.auditStatus === filterAuditStatus.value)
  if (filterResult.value) list = list.filter(l => l.status === filterResult.value)
  if (filterRemote.value === 'remote') list = list.filter(l => l.remote)
  if (filterRemote.value === 'local') list = list.filter(l => !l.remote)
  return list
})

const auditStats = computed(() => [
  { label: '总记录', value: auditLogs.value.length, color: '#0052D9' },
  { label: '远程操作', value: auditLogs.value.filter(l => l.remote).length, color: '#E37318' },
  { label: '待抽查', value: auditLogs.value.filter(l => l.auditStatus === 'Pending').length, color: '#D54941' },
  { label: '异常标记', value: auditLogs.value.filter(l => l.auditStatus === 'Flagged').length, color: '#D54941' },
])

const pendingCount = computed(() => auditLogs.value.filter(l => l.auditStatus === 'Pending').length)
const totalLogs = computed(() => filteredAuditLogs.value.length)

function actionLabel(action: string) {
  const map: Record<string, string> = {
    ForceCheckout: '强制退房', RemoteUnlock: '远程开门', ManualStatusChange: '手动改状态',
    SceneOverride: '场景覆盖', RoomSetMaintenance: '设为维修', DeviceControl: '设备控制',
  }
  return map[action] || action
}

function actionTheme(action: string) {
  const map: Record<string, string> = {
    ForceCheckout: 'danger', RemoteUnlock: 'warning', ManualStatusChange: 'primary',
    SceneOverride: 'success', RoomSetMaintenance: 'default', DeviceControl: 'default',
  }
  return map[action] || 'default'
}

function auditStatusLabel(status: string) {
  return status === 'Pending' ? '待抽查' : status === 'Reviewed' ? '已通过' : '异常'
}

function viewDetail(log: any) { selectedLog.value = log; drawerVisible.value = true }

function approve(log: any) { log.auditStatus = 'Reviewed'; log.reviewedBy = `店长-${localStorage.getItem('erp_user') || '系统'}`; log.reviewedAt = new Date().toISOString() }

function flag(log: any) { log.auditStatus = 'Flagged'; log.reviewedBy = `店长-${localStorage.getItem('erp_user') || '系统'}`; log.reviewNote = '需进一步核实' }

const columns = [
  { colKey: 'createdAt', title: '操作时间', width: 160 },
  { colKey: 'action', title: '操作类型', width: 100 },
  { colKey: 'roomName', title: '房间', width: 100 },
  { colKey: 'operator', title: '操作人', width: 130 },
  { colKey: 'reason', title: '操作原因', ellipsis: true },
  { colKey: 'result', title: '结果', width: 80 },
  { colKey: 'auditStatus', title: '抽查', width: 80 },
  { colKey: 'actions', title: '操作', width: 150 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
.operator-cell { display: flex; flex-direction: column; gap: 2px; }
.operator-name { font-weight: 500; }
.operator-role { font-size: 11px; color: #999; display: flex; align-items: center; gap: 4px; }
.remote-badge { font-size: 9px; background:#fff3e0; color:#e37318; padding:1px 5px; border-radius:4px; }
.detail-section { padding: 8px 0; }
.log-header { display: flex; align-items: center; justify-content: space-between; }
.log-time { font-size: 13px; color: #999; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.ip-code { font-family: 'Courier New', monospace; background: #f5f5f5; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
</style>
