<template>
  <div>
    <div class="page-top">
      <t-button variant="text" @click="router.push('/dashboard')">
        <t-icon name="chevron-left" /> 返回总览
      </t-button>
      <h2 class="page-header">告警中心</h2>
    </div>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in stats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card">
            <div class="stat-num" :style="{ color: s.color }">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="2">
          <t-select v-model="filterSeverity" placeholder="告警级别" clearable>
            <t-option value="Error" label="严重" />
            <t-option value="Warning" label="警告" />
            <t-option value="Info" label="信息" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterStatus" placeholder="处理状态" clearable>
            <t-option value="Unresolved" label="未处理" />
            <t-option value="Acknowledged" label="已确认" />
            <t-option value="Resolved" label="已解决" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterRoom" placeholder="按房间筛选" clearable>
            <t-option v-for="r in rooms.rooms" :key="r.roomId" :value="r.roomId" :label="r.name" />
          </t-select>
        </t-col>
      </t-row>

      <t-table :data="filteredAlerts" :columns="columns" row-key="alertId" hover stripe>
        <template #severity="{ row }">
          <t-tag :theme="severityTheme(row.severity)" size="small" variant="light">{{ severityLabel(row.severity) }}</t-tag>
        </template>
        <template #assignedRole="{ row }">
          <t-tag size="small" variant="light" :theme="row.assignedRole === '客服' ? 'success' : 'primary'">
            {{ row.assignedRole || '—' }}
          </t-tag>
        </template>
        <template #status="{ row }">
          <t-tag
            :theme="row.status === 'Unresolved' ? 'danger' : row.status === 'Acknowledged' ? 'warning' : 'success'"
            size="small" variant="light"
          >{{ statusLabel(row.status) }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status === 'Unresolved'" size="small" theme="warning" variant="text" @click="openHandleModal(row)">处理</t-button>
            <t-button v-if="row.status === 'Acknowledged'" size="small" theme="success" variant="text" @click="openResolveModal(row)">解决</t-button>
            <t-button v-if="row.status === 'Resolved'" size="small" variant="text" disabled style="color:#ccc">已处理</t-button>
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- Detail Drawer -->
    <t-drawer v-model:visible="drawerVisible" header="告警详情" size="400px" :footer="false">
      <div v-if="selectedAlert" class="detail-section">
        <div class="detail-row"><span>告警ID</span><span>{{ selectedAlert.alertId }}</span></div>
        <div class="detail-row"><span>设备编号</span><span>{{ selectedAlert.deviceCode }}</span></div>
        <div class="detail-row"><span>设备类型</span><span>{{ deviceTypeLabel(selectedAlert.deviceType) }}</span></div>
        <div class="detail-row"><span>房间</span><span>{{ selectedAlert.roomName }}</span></div>
        <div class="detail-row"><span>告警类型</span><t-tag size="small">{{ selectedAlert.type }}</t-tag></div>
        <div class="detail-row"><span>级别</span>
          <t-tag :theme="severityTheme(selectedAlert.severity)" size="small">{{ severityLabel(selectedAlert.severity) }}</t-tag>
        </div>
        <div class="detail-row"><span>状态</span>
          <t-tag :theme="selectedAlert.status === 'Unresolved' ? 'danger' : selectedAlert.status === 'Acknowledged' ? 'warning' : 'success'" size="small">
            {{ statusLabel(selectedAlert.status) }}
          </t-tag>
        </div>
        <div class="detail-row"><span>处理角色</span><span>{{ selectedAlert.assignedRole }}</span></div>
        <div class="detail-row"><span>负责人</span><span>{{ selectedAlert.assignedName }}</span></div>
        <div class="detail-row"><span>创建时间</span><span>{{ selectedAlert.createdAt }}</span></div>
        <t-divider />
        <h4>告警内容</h4>
        <p class="alert-message">{{ selectedAlert.message }}</p>
        <t-divider />
        <h4>详细说明</h4>
        <p class="alert-detail">{{ selectedAlert.detail }}</p>
        <t-divider v-if="selectedAlert.acknowledgedAt" />
        <div v-if="selectedAlert.acknowledgedAt" class="detail-row"><span>确认时间</span><span>{{ selectedAlert.acknowledgedAt }}</span></div>
        <div v-if="selectedAlert.handlingMethod" class="detail-row"><span>处理方式</span><span>{{ selectedAlert.handlingMethod }}</span></div>
        <div v-if="selectedAlert.handlingNote" class="detail-row"><span>处理备注</span><span>{{ selectedAlert.handlingNote }}</span></div>
        <div v-if="selectedAlert.escalatedTo" class="detail-row"><span>已转交</span><span>{{ selectedAlert.escalatedTo }}</span></div>
        <div v-if="selectedAlert.resolvedAt" class="detail-row"><span>解决时间</span><span>{{ selectedAlert.resolvedAt }}</span></div>
        <div v-if="selectedAlert.resolvedBy" class="detail-row"><span>处理人</span><span>{{ selectedAlert.resolvedBy }}</span></div>
        <t-divider />
        <t-space style="margin-top:12px">
          <t-button v-if="selectedAlert.status === 'Unresolved'" theme="warning" @click="drawerVisible=false; openHandleModal(selectedAlert)">处理告警</t-button>
          <t-button v-if="selectedAlert.status === 'Acknowledged'" theme="success" @click="drawerVisible=false; openResolveModal(selectedAlert)">标记已解决</t-button>
        </t-space>
      </div>
    </t-drawer>

    <!-- Handle Modal (确认 + 处理方式) -->
    <t-dialog v-model:visible="handleModalVisible" header="处理告警" width="480px" :footer="false">
      <div v-if="handlingAlert">
        <div class="handle-alert-info">
          <t-tag :theme="severityTheme(handlingAlert.severity)" size="small">{{ severityLabel(handlingAlert.severity) }}</t-tag>
          <span style="margin-left:8px;font-weight:600;">{{ handlingAlert.message }}</span>
        </div>
        <div class="handle-alert-meta">
          {{ handlingAlert.roomName }} · {{ handlingAlert.deviceCode }} · 指派: {{ handlingAlert.assignedName }}
        </div>

        <t-divider />

        <div class="handle-section">
          <div class="handle-label">处理角色</div>
          <t-tag :theme="handlingAlert.assignedRole === '客服' ? 'success' : 'primary'" size="medium">
            {{ handlingAlert.assignedRole === '客服' ? '客服人员' : '技术人员' }}
          </t-tag>
          <span class="handle-hint" v-if="handlingAlert.assignedRole === '客服'">
            此问题优先由客服人员处理（如更换电池、重启等简单操作）
          </span>
          <span class="handle-hint" v-else>
            此问题需技术人员处理（涉及硬件、线路或系统层面）
          </span>
        </div>

        <div class="handle-section">
          <div class="handle-label">处理方式</div>
          <t-radio-group v-model="handlingMethod" style="display:flex;flex-direction:column;gap:8px;">
            <t-radio v-for="m in availableMethods" :key="m" :value="m">{{ m }}</t-radio>
            <t-radio value="__other__">其他（请填写）</t-radio>
          </t-radio-group>
          <t-input v-if="handlingMethod === '__other__'" v-model="handlingMethodCustom" placeholder="请输入处理方式" style="margin-top:8px;" />
        </div>

        <div class="handle-section">
          <div class="handle-label">处理备注</div>
          <t-textarea v-model="handlingNote" placeholder="请填写处理说明或故障原因..." :maxlength="200" />
        </div>

        <div class="handle-section" v-if="handlingAlert.assignedRole === '客服'">
          <div class="handle-label">无法解决？</div>
          <t-button theme="warning" variant="outline" @click="escalateToTech">
            转交技术人员处理
          </t-button>
          <span class="handle-hint" style="margin-left:8px;">客服无法解决时，转交技术人员跟进</span>
        </div>

        <div style="margin-top:20px;display:flex;gap:10px;justify-content:flex-end;">
          <t-button variant="outline" @click="handleModalVisible = false">取消</t-button>
          <t-button theme="primary" @click="confirmHandle" :disabled="!canConfirmHandle">确认处理</t-button>
        </div>
      </div>
    </t-dialog>

    <!-- Resolve Modal -->
    <t-dialog v-model:visible="resolveModalVisible" header="标记已解决" width="480px" :footer="false">
      <div v-if="handlingAlert">
        <div class="handle-alert-info">
          <t-tag theme="success" size="small">处理中</t-tag>
          <span style="margin-left:8px;font-weight:600;">{{ handlingAlert.message }}</span>
        </div>
        <div class="handle-alert-meta">{{ handlingAlert.handlingMethod }} · {{ handlingAlert.assignedName }}</div>

        <t-divider />

        <div class="handle-section">
          <div class="handle-label">解决备注</div>
          <t-textarea v-model="resolveNote" placeholder="请描述解决方案和结果..." :maxlength="200" />
        </div>

        <div style="margin-top:20px;display:flex;gap:10px;justify-content:flex-end;">
          <t-button variant="outline" @click="resolveModalVisible = false">取消</t-button>
          <t-button theme="success" @click="confirmResolve">确认已解决</t-button>
        </div>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { alerts, rooms } from '@/mock/data'

const router = useRouter()

const filterSeverity = ref('')
const filterStatus = ref('')
const filterRoom = ref('')
const drawerVisible = ref(false)
const selectedAlert = ref<any>(null)

// Handle modal
const handleModalVisible = ref(false)
const resolveModalVisible = ref(false)
const handlingAlert = ref<any>(null)
const handlingMethod = ref('')
const handlingMethodCustom = ref('')
const handlingNote = ref('')
const resolveNote = ref('')

const methodsForCS = ['更换电池', '重启设备', '清洁维护', '检查连接线', '恢复出厂设置']
const methodsForTech = ['更换电池', '重启设备', '固件升级', '更换硬件模块', '检查RS485/Zigbee线路', '联系厂商维修']

const availableMethods = computed(() => {
  if (!handlingAlert.value) return []
  return handlingAlert.value.assignedRole === '客服' ? methodsForCS : methodsForTech
})

const canConfirmHandle = computed(() => {
  if (!handlingMethod.value) return false
  if (handlingMethod.value === '__other__' && !handlingMethodCustom.value.trim()) return false
  return true
})

const filteredAlerts = computed(() => {
  let list = alerts.alerts
  if (filterSeverity.value) list = list.filter(a => a.severity === filterSeverity.value)
  if (filterStatus.value) list = list.filter(a => a.status === filterStatus.value)
  if (filterRoom.value) list = list.filter(a => a.roomId === filterRoom.value)
  return list
})

const stats = computed(() => {
  const all = alerts.alerts
  return [
    { label: '告警总数', value: all.length, color: '#0052D9' },
    { label: '未处理', value: all.filter(a => a.status === 'Unresolved').length, color: '#D54941' },
    { label: '已确认', value: all.filter(a => a.status === 'Acknowledged').length, color: '#E37318' },
    { label: '已解决', value: all.filter(a => a.status === 'Resolved').length, color: '#00A870' },
  ]
})

function severityTheme(severity: string) {
  return severity === 'Error' ? 'danger' : severity === 'Warning' ? 'warning' : 'primary'
}

function severityLabel(severity: string) {
  return severity === 'Error' ? '严重' : severity === 'Warning' ? '警告' : '信息'
}

function statusLabel(status: string) {
  return status === 'Unresolved' ? '未处理' : status === 'Acknowledged' ? '已确认' : '已解决'
}

function deviceTypeLabel(type: string) {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响' }
  return map[type] || type
}

function viewDetail(alert: any) { selectedAlert.value = alert; drawerVisible.value = true }

function openHandleModal(alert: any) {
  handlingAlert.value = alert
  handlingMethod.value = ''
  handlingMethodCustom.value = ''
  handlingNote.value = ''
  handleModalVisible.value = true
}

function openResolveModal(alert: any) {
  handlingAlert.value = alert
  resolveNote.value = ''
  resolveModalVisible.value = true
}

function confirmHandle() {
  const alert = handlingAlert.value
  if (!alert) return
  const method = handlingMethod.value === '__other__' ? handlingMethodCustom.value : handlingMethod.value
  alert.status = 'Acknowledged'
  alert.acknowledgedAt = new Date().toLocaleString('zh-CN')
  alert.handlingMethod = method
  alert.handlingNote = handlingNote.value
  handleModalVisible.value = false
}

function confirmResolve() {
  const alert = handlingAlert.value
  if (!alert) return
  alert.status = 'Resolved'
  alert.resolvedAt = new Date().toLocaleString('zh-CN')
  alert.resolvedBy = alert.assignedName
  alert.resolveNote = resolveNote.value
  resolveModalVisible.value = false
}

function escalateToTech() {
  const alert = handlingAlert.value
  if (!alert) return
  const method = handlingMethod.value === '__other__' ? handlingMethodCustom.value : handlingMethod.value
  alert.status = 'Acknowledged'
  alert.acknowledgedAt = new Date().toLocaleString('zh-CN')
  alert.handlingMethod = method || '客服初步排查'
  alert.handlingNote = handlingNote.value || '客服无法解决，转交技术人员'
  alert.assignedRole = '技术'
  alert.assignedName = '阿强'
  alert.assignedTo = 'EMP003'
  alert.escalatedAt = new Date().toLocaleString('zh-CN')
  alert.escalatedFrom = '客服'
  handleModalVisible.value = false
}

const columns = [
  { colKey: 'createdAt', title: '时间', width: 160 },
  { colKey: 'roomName', title: '房间', width: 100 },
  { colKey: 'deviceCode', title: '设备', width: 130 },
  { colKey: 'message', title: '告警内容', ellipsis: true },
  { colKey: 'severity', title: '级别', width: 70 },
  { colKey: 'assignedRole', title: '处理角色', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 160 },
]
</script>

<style scoped>
.page-top { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.page-header { font-size: 20px; font-weight: 600; margin: 0; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
.detail-section { padding: 8px 0; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.alert-message { font-size: 14px; font-weight: 500; color: #333; margin-bottom: 8px; }
.alert-detail { font-size: 13px; color: #666; line-height: 1.6; }

.handle-alert-info { display: flex; align-items: center; }
.handle-alert-meta { font-size: 12px; color: #999; margin-top: 6px; }
.handle-section { margin-top: 16px; }
.handle-label { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 8px; }
.handle-hint { display: block; font-size: 12px; color: #999; margin-top: 4px; }
</style>
