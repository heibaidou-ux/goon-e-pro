<template>
  <div>
    <div class="detail-header">
      <t-button variant="text" @click="router.push('/dashboard')">
        <t-icon name="chevron-left" /> 返回总览
      </t-button>
      <h2 class="page-title">{{ room?.name || '房间详情' }}</h2>
    </div>

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading />
      <span style="color:#999">加载中...</span>
    </t-space>

    <template v-else>
      <!-- Error -->
      <t-alert v-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="4">
          <t-card :bordered="true">
            <div class="info-section">
              <h3>基本信息</h3>
              <div class="info-grid">
                <div class="info-item"><span class="info-label">房间编号</span><span class="info-val">{{ room?.roomId }}</span></div>
                <div class="info-item"><span class="info-label">类型</span><t-tag size="small">{{ roomTypeLabel(room?.type) }}</t-tag></div>
                <div class="info-item"><span class="info-label">容纳人数</span><span class="info-val">{{ room?.capacity }}人</span></div>
                <div class="info-item"><span class="info-label">面积</span><span class="info-val">{{ room?.area || '—' }}㎡</span></div>
                <div class="info-item"><span class="info-label">设施</span><span class="info-val">{{ room?.facilities?.join('、') || '—' }}</span></div>
                <div class="info-item"><span class="info-label">状态</span>
                  <t-tag :theme="room?.status === 'Active' ? 'success' : 'danger'" size="small">{{ roomStatusLabel(room?.status) }}</t-tag>
                </div>
              </div>
            </div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card :bordered="true" v-if="isBookable">
            <h3>当前订单</h3>
            <div v-if="currentOrder" class="current-order">
              <div class="order-status">
                <t-tag :theme="currentOrder.status === 'InUse' ? 'primary' : 'warning'" size="medium">
                  {{ currentOrder.status === 'InUse' ? '使用中' : '已预定' }}
                </t-tag>
              </div>
              <div class="info-grid" style="margin-top:12px">
                <div class="info-item"><span class="info-label">客户</span><span class="info-val">{{ currentOrder.customerName }}</span></div>
                <div class="info-item"><span class="info-label">电话</span><span class="info-val">{{ currentOrder.customerPhone }}</span></div>
                <div class="info-item"><span class="info-label">日期</span><span class="info-val">{{ currentOrder.date }}</span></div>
                <div class="info-item"><span class="info-label">时段</span><span class="info-val">{{ currentOrder.startTime }} - {{ currentOrder.endTime }}</span></div>
                <div class="info-item"><span class="info-label">时长</span><span class="info-val">{{ currentOrder.duration }}小时</span></div>
                <div class="info-item"><span class="info-label">金额</span><span class="info-val" style="color:#e37318;font-weight:700">¥{{ currentOrder.totalAmount }}</span></div>
                <div class="info-item"><span class="info-label">门锁密码</span><span class="info-val" style="font-weight:600">{{ currentOrder.doorCode || '未分配' }}</span></div>
                <div class="info-item"><span class="info-label">支付状态</span>
                  <t-tag :theme="currentOrder.paymentStatus === 'Paid' ? 'success' : 'warning'" size="small">{{ currentOrder.paymentStatus === 'Paid' ? '已支付' : '未支付' }}</t-tag>
                </div>
              </div>
            </div>
            <div v-else class="empty-state">当前无订单</div>
          </t-card>
        </t-col>
        <t-col :span="4">
          <t-card :bordered="true">
            <h3>设备状态</h3>
            <div v-if="roomDevices.length > 0">
              <div v-for="dev in roomDevices" :key="dev.deviceId" class="device-row">
                <t-icon :name="dev.status === 'Online' ? 'check-circle' : 'close-circle'" :style="{ color: dev.status === 'Online' ? '#00A870' : '#D54941' }" />
                <span class="device-code">{{ deviceTypeLabel(dev.type) }}</span>
                <span style="font-size:11px;color:#bbb;">{{ dev.deviceCode }}</span>
                <t-tag :theme="dev.status === 'Online' ? 'success' : 'danger'" size="small" variant="light">
                  {{ dev.status === 'Online' ? '在线' : dev.status === 'Offline' ? '离线' : dev.status === 'Fault' ? '故障' : '维护中' }}
                </t-tag>
              </div>
            </div>
            <div v-else class="empty-state">无设备</div>
          </t-card>
        </t-col>
      </t-row>

      <!-- Order history -->
      <t-card :bordered="true" style="margin-bottom:20px" v-if="isBookable">
        <template #title><span>订单记录</span></template>
        <t-table :data="roomOrders" :columns="orderColumns" row-key="orderId" size="small" hover>
          <template #status="{ row }">
            <t-tag :theme="row.status === 'InUse' ? 'primary' : row.status === 'Booked' ? 'warning' : 'success'" size="small" variant="light">
              {{ row.status === 'InUse' ? '使用中' : row.status === 'Booked' ? '已预定' : '已结束' }}
            </t-tag>
          </template>
          <template #paymentStatus="{ row }">
            <t-tag :theme="row.paymentStatus === 'Paid' ? 'success' : 'warning'" size="small" variant="light">
              {{ row.paymentStatus === 'Paid' ? '已支付' : '未支付' }}
            </t-tag>
          </template>
        </t-table>
      </t-card>

      <!-- Alerts for this room -->
      <t-card :bordered="true">
        <template #title><span>相关告警</span></template>
        <t-table :data="roomAlerts" :columns="alertColumns" row-key="alertId" size="small" hover>
          <template #severity="{ row }">
            <t-tag :theme="row.severity === 'Error' ? 'danger' : row.severity === 'Warning' ? 'warning' : 'primary'" size="small" variant="light">
              {{ row.severity === 'Error' ? '严重' : row.severity === 'Warning' ? '警告' : '信息' }}
            </t-tag>
          </template>
          <template #status="{ row }">
            <t-tag :theme="row.status === 'Unresolved' ? 'danger' : row.status === 'Acknowledged' ? 'warning' : 'success'" size="small" variant="light">
              {{ row.status === 'Unresolved' ? '未处理' : row.status === 'Acknowledged' ? '已确认' : '已解决' }}
            </t-tag>
          </template>
        </t-table>
      </t-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { roomApi, orderApi, iotApi } from '../services/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const loadError = ref('')

const roomId = route.params.roomId as string
const roomDetail = ref<any>(null)
const orderList = ref<any[]>([])
const deviceList = ref<any[]>([])
const alertList = ref<any[]>([])

const room = computed(() => roomDetail.value)
const isBookable = computed(() => room.value?.bookable !== false)

const roomOrders = computed(() =>
  orderList.value
    .filter((o: any) => o.roomId === roomId)
    .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime())
)

const currentOrder = computed(() =>
  orderList.value.find((o: any) => o.roomId === roomId && (o.status === 'InUse' || o.status === 'Booked'))
)

const roomDevices = computed(() => deviceList.value.filter((d: any) => d.roomId === roomId))
const roomAlerts = computed(() => alertList.value.filter((a: any) => a.roomId === roomId))

function roomTypeLabel(type: string | undefined) {
  const map: Record<string, string> = { MeetingRoom: '会议室', TeaRoom: '茶室', Exhibition: '展厅', Workspace: '工作间' }
  return map[type || ''] || type || ''
}

function roomStatusLabel(status: string | undefined) {
  const map: Record<string, string> = { Active: '正常', Inactive: '停用', Maintenance: '维修中', Cleaning: '打扫中' }
  return map[status || ''] || status || ''
}

function deviceTypeLabel(type: string): string {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响', Sensor: '传感器' }
  return map[type] || type
}

function normalizeRoom(r: any) {
  return {
    roomId: r.room_id,
    name: r.name,
    type: r.type,
    capacity: r.capacity,
    area: r.area || 0,
    facilities: r.facilities || [],
    status: r.is_active ? 'Active' : 'Inactive',
    bookable: true,
  }
}

function normalizeOrder(o: any) {
  return {
    orderId: o.order_id,
    roomId: o.room_id,
    customerName: o.customer_name || '',
    customerPhone: o.customer_phone || '',
    date: o.date || '',
    startTime: o.start_time || '',
    endTime: o.end_time || '',
    duration: o.duration || 0,
    totalAmount: o.total_amount || 0,
    status: o.status,
    paymentStatus: o.payment_status || '',
    doorCode: o.door_code || '',
  }
}

function normalizeDevice(d: any) {
  return {
    deviceId: d.device_id,
    roomId: d.room_id,
    type: d.type,
    deviceCode: d.ha_entity_id || d.device_id,
    status: d.status,
  }
}

function normalizeAlert(a: any) {
  return {
    alertId: a.alert_id,
    roomId: a.room_id,
    deviceCode: a.device_code,
    severity: a.severity,
    message: a.message,
    status: a.status,
    createdAt: a.created_at,
  }
}

const orderColumns = [
  { colKey: 'orderId', title: '订单号', width: 140 },
  { colKey: 'customerName', title: '客户', width: 80 },
  { colKey: 'date', title: '日期', width: 100 },
  { colKey: 'startTime', title: '开始', width: 60 },
  { colKey: 'endTime', title: '结束', width: 60 },
  { colKey: 'totalAmount', title: '金额', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'paymentStatus', title: '支付', width: 80 },
]

const alertColumns = [
  { colKey: 'createdAt', title: '时间', width: 160 },
  { colKey: 'deviceCode', title: '设备', width: 130 },
  { colKey: 'message', title: '内容', ellipsis: true },
  { colKey: 'severity', title: '级别', width: 70 },
  { colKey: 'status', title: '状态', width: 80 },
]

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const [r, ords, devs, alrts] = await Promise.all([
      roomApi.get(roomId).catch(() => null),
      orderApi.list().catch(() => []),
      iotApi.devices({ room_id: roomId }).catch(() => []),
      iotApi.alerts({ room_id: roomId }).catch(() => []),
    ])
    if (r) roomDetail.value = normalizeRoom(r)
    orderList.value = (ords || []).map(normalizeOrder)
    deviceList.value = (devs || []).map(normalizeDevice)
    alertList.value = (alrts || []).map(normalizeAlert)
  } catch (e: any) {
    loadError.value = '加载房间详情失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
/* .detail-header, .page-title, .empty-state from global */
h3 { font-size: 15px; font-weight: 600; margin-bottom: 12px; color: #333; }
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.info-item { display: flex; flex-direction: column; gap: 2px; }
.info-label { font-size: 12px; color: #999; }
.info-val { font-size: 13px; color: #333; }
.device-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.device-row:last-child { border-bottom: none; }
.device-code { font-weight: 500; }
</style>
