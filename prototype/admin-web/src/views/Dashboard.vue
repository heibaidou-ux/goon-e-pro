<template>
  <div>
    <h2 class="page-header">门店总览</h2>

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading />
      <span style="color:#999">加载中...</span>
    </t-space>

    <!-- Error -->
    <t-alert v-else-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

    <template v-else>
      <!-- 使用中/已预订订单列表 -->
      <t-card title="当前订单" :bordered="true" style="margin-bottom:20px">
        <t-table
          :data="activeOrders"
          :columns="orderColumns"
          row-key="appointmentId"
          size="small"
          hover
        >
          <template #roomName="{ row }">
            <span style="font-weight:500">{{ row.roomName }}</span>
          </template>
          <template #status="{ row }">
            <t-tag :theme="row.status === 'InUse' ? 'primary' : 'warning'" size="small" variant="light">
              {{ row.status === 'InUse' ? '使用中' : '已预订' }}
            </t-tag>
          </template>
          <template #timeSlot="{ row }">
            <span>{{ formatDateTime(row.startTime) }} - {{ formatDateTime(row.endTime) }}</span>
          </template>
        </t-table>
        <t-empty v-if="activeOrders.length === 0" description="当前无使用中或已预订的订单" style="padding:20px" />
      </t-card>

      <!-- 营收卡片 -->
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="3" v-for="card in revenueCards" :key="card.title">
          <t-card :bordered="true" hover-shadow @click="card.link ? router.push(card.link) : undefined" :style="{ cursor: card.link ? 'pointer' : 'default', height: '100%' }">
            <div class="stat-card">
              <div class="stat-label">{{ card.title }}</div>
              <div class="stat-value" :style="{ color: card.color }">{{ card.value }}</div>
              <div class="stat-sub">{{ card.sub }}</div>
            </div>
          </t-card>
        </t-col>
      </t-row>

      <!-- 今日概况 -->
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="6">
          <t-card title="今日营业概况" :bordered="true">
            <t-row :gutter="16">
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">总订单数</span>
                  <span class="info-num">{{ todayStats.totalOrders }}</span>
                </div>
              </t-col>
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">进行中</span>
                  <span class="info-num green">{{ todayStats.inUse }}</span>
                </div>
              </t-col>
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">待开始</span>
                  <span class="info-num purple">{{ todayStats.booked }}</span>
                </div>
              </t-col>
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">已结束</span>
                  <span class="info-num">{{ todayStats.completed }}</span>
                </div>
              </t-col>
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">今日营收</span>
                  <span class="info-num orange">¥{{ todayStats.revenue.toLocaleString() }}</span>
                </div>
              </t-col>
              <t-col :span="4">
                <div class="info-item">
                  <span class="info-label">今日应收</span>
                  <span class="info-num orange">¥{{ todayStats.expectedRevenue.toLocaleString() }}</span>
                </div>
              </t-col>
            </t-row>
          </t-card>
        </t-col>
        <t-col :span="6">
          <t-card title="包间报价标准" :bordered="true">
            <div v-for="room in bookableRooms" :key="room.roomId" class="price-row">
              <span class="price-room">{{ room.name }}</span>
              <span class="price-detail">¥{{ room.pricePerHour }}/时 · ¥{{ room.pricePerHalfHour }}/半小时</span>
              <span class="price-capacity">最大{{ room.capacity }}人</span>
            </div>
            <t-empty v-if="bookableRooms.length === 0" description="暂无包间数据" style="padding:20px" />
          </t-card>
        </t-col>
      </t-row>

      <!-- 实时房态 -->
      <t-card title="实时房态" :bordered="true" style="margin-bottom:20px">
        <div class="room-grid">
          <t-card
            v-for="room in roomList"
            :key="room.roomId"
            :bordered="true"
            class="room-card"
            :class="{ 'room-non-bookable': !isBookable(room) }"
            :style="{ borderTop: `3px solid ${getRoomColor(room.roomId)}` }"
            @click="goRoomDetail(room)"
          >
            <div class="room-card-header">
              <span class="room-name">{{ room.name }}</span>
              <t-tag size="small" :style="{ background: getRoomColor(room.roomId), color: '#fff', border: 'none' }">
                {{ getRoomStatusText(room.roomId) }}
              </t-tag>
            </div>
            <div class="room-card-body">
              <div class="room-info"><t-icon name="user" size="14px" /> 最大容纳 {{ room.capacity }} 人</div>

              <!-- Bookable rooms: show order list -->
              <div v-if="isBookable(room)" class="room-orders">
                <div v-if="getRoomOrders(room.roomId).length === 0" class="no-orders">暂无订单记录</div>
                <div v-for="order in getRoomOrders(room.roomId)" :key="order.orderId" class="order-mini">
                  <t-tag :theme="order.status === 'InUse' ? 'primary' : order.status === 'Booked' ? 'warning' : 'default'" size="small" variant="light">
                    {{ order.status === 'InUse' ? '使用中' : order.status === 'Booked' ? '待开始' : '已结束' }}
                  </t-tag>
                  <span class="order-customer">{{ order.customerName }}</span>
                  <span class="order-time">{{ order.date }} {{ order.startTime }}-{{ order.endTime }}</span>
                </div>
              </div>

              <!-- Non-bookable rooms: show device status summary -->
              <div v-else class="room-devices">
                <div v-for="dev in getRoomDevices(room.roomId)" :key="dev.deviceId" class="device-mini">
                  <t-icon :name="dev.status === 'Online' ? 'check-circle' : 'close-circle'" size="12px" :style="{ color: dev.status === 'Online' ? '#00A870' : '#D54941' }" />
                  <span>{{ deviceTypeLabel(dev.type) }}</span>
                  <span style="font-size:10px;color:#bbb;">{{ dev.deviceCode }}</span>
                  <t-tag :theme="dev.status === 'Online' ? 'success' : 'danger'" size="small" variant="light">
                    {{ dev.status === 'Online' ? '在线' : '离线' }}
                  </t-tag>
                </div>
              </div>
            </div>
          </t-card>
        </div>
      </t-card>

      <!-- 告警速览 -->
      <t-card :bordered="true">
        <template #title>
          <span>告警速览</span>
          <t-badge v-if="unresolvedAlerts.length" :count="unresolvedAlerts.length" style="margin-left:8px" />
        </template>
        <template #actions>
          <a href="javascript:;" @click="router.push('/alerts')">查看全部 →</a>
        </template>
        <t-table
          :data="recentAlerts"
          :columns="alertColumns"
          row-key="alertId"
          size="small"
          hover
        >
          <template #severity="{ row }">
            <t-tag :theme="severityTheme(row.severity)" size="small" variant="light">{{ severityLabel(row.severity) }}</t-tag>
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
import { ref, computed, onMounted, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { roomApi, orderApi, shopApi, iotApi } from '../services/api'

const router = useRouter()

// ── Reactive data ──
const loading = ref(false)
const loadError = ref('')
const dashboardError = ref<string | null>(null)

const roomArr = ref<any[]>([])
const orderArr = ref<any[]>([])
const shopOrders = ref<any[]>([])
const deviceArr = ref<any[]>([])
const alertArr = ref<any[]>([])

// Alias for template
const roomList = roomArr

// ── Normalization (API snake_case → template camelCase) ──

function normalizeRoom(r: any) {
  return {
    roomId: r.room_id,
    name: r.name,
    type: r.type,
    capacity: r.capacity,
    pricePerHour: r.price_per_hour,
    pricePerHalfHour: r.price_per_half_hour,
    facilities: r.facilities || [],
    bookable: true,
    status: r.is_active ? 'Active' : 'Inactive',
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
  }
}

function normalizeDevice(d: any) {
  return {
    deviceId: d.device_id,
    roomId: d.room_id,
    type: d.type,
    name: d.name,
    status: d.status,
    deviceCode: d.ha_entity_id || d.device_id,
  }
}

function normalizeAlert(a: any) {
  return {
    alertId: a.alert_id,
    roomId: a.room_id,
    roomName: a.room_name,
    deviceCode: a.device_code,
    severity: a.severity,
    type: a.type,
    message: a.message,
    status: a.status,
    createdAt: a.created_at,
  }
}

function normalizeShopOrder(o: any) {
  return {
    totalAmount: o.total_amount || 0,
    createdAt: o.created_at || '',
  }
}

// ── Computed ──

const bookableRooms = computed(() => roomArr.value.filter(r => r.bookable !== false))
const totalBookable = computed(() => bookableRooms.value.length)

const inUseRooms = computed(() => bookableRooms.value.filter(r => {
  const order = orderArr.value.find(o => o.roomId === r.roomId && o.status === 'InUse')
  return !!order
}).length)

const unresolvedAlerts = computed(() => alertArr.value.filter(a => a.status === 'Unresolved'))

const todayStr = new Date().toISOString().slice(0, 10)

const todayStats = computed(() => {
  const todayOrders = orderArr.value.filter(o => o.date === todayStr)
  const todayShop = shopOrders.value.filter((o: any) => {
    const d = (o.createdAt || '').slice(0, 10)
    return d === todayStr
  })
  const inUse = todayOrders.filter(o => o.status === 'InUse').length
  const booked = todayOrders.filter(o => o.status === 'Booked').length
  const completed = todayOrders.filter(o => o.status === 'Completed').length
  const roomRevenue = todayOrders.filter(o => o.status !== 'Booked').reduce((sum, o) => sum + o.totalAmount, 0)
  const shopRevenue = todayShop.reduce((sum: number, o: any) => sum + (o.totalAmount || 0), 0)
  const expectedRoomRev = todayOrders.reduce((sum, o) => sum + o.totalAmount, 0)
  const expectedShopRev = todayShop.reduce((sum: number, o: any) => sum + (o.totalAmount || 0), 0)
  return {
    totalOrders: todayOrders.length + todayShop.length,
    inUse, booked, completed,
    revenue: roomRevenue + shopRevenue,
    expectedRevenue: expectedRoomRev + expectedShopRev,
  }
})

const deviceTotalCount = computed(() => deviceArr.value.length)
const deviceOnlineCount = computed(() => deviceArr.value.filter(d => d.status === 'Online').length)
const deviceOnlineRate = computed(() => {
  if (deviceTotalCount.value === 0) return 0
  return Math.round(deviceOnlineCount.value / deviceTotalCount.value * 100)
})

const revenueCards = computed(() => [
  { title: '今日营收', value: `¥${todayStats.value.revenue.toLocaleString()}`, sub: '已结算金额', color: '#0052D9', link: '' },
  { title: '订单数', value: String(todayStats.value.totalOrders), sub: '今日全部订单', color: '#00A870', link: '' },
  { title: '活跃包间', value: `${inUseRooms.value}/${totalBookable.value}`, sub: `使用率 ${totalBookable.value > 0 ? Math.round(inUseRooms.value / totalBookable.value * 100) : 0}%`, color: '#E37318', link: '' },
  { title: '设备在线率', value: `${deviceOnlineRate.value}%`, sub: `${deviceOnlineCount.value}/${deviceTotalCount.value} 在线 · 告警 ${unresolvedAlerts.value.length} 条`, color: '#366EF4', link: '/alerts' },
])

const recentAlerts = computed(() => alertArr.value.slice(0, 5))

const roomStatusColorMap: Record<string, string> = { Active: '#00A870', Inactive: '#999', Maintenance: '#E37318' }
const roomStatusLabelMap: Record<string, string> = { Active: '正常', Inactive: '停用', Maintenance: '维护中' }

// ── Functions ──

function isBookable(room: any): boolean {
  return room ? room.bookable !== false : false
}

function getRoomColor(roomId: string): string {
  const room = roomArr.value.find(r => r.roomId === roomId)
  if (!room || !isBookable(room)) return '#999'
  if (room.status !== 'Active') return roomStatusColorMap[room.status] || '#999'
  const order = orderArr.value.find(o => o.roomId === roomId && o.status === 'InUse')
  if (order) return '#366EF4'
  const booked = orderArr.value.find(o => o.roomId === roomId && o.status === 'Booked')
  if (booked) return '#9C27B0'
  return '#00A870'
}

function getRoomStatusText(roomId: string): string {
  const room = roomArr.value.find(r => r.roomId === roomId)
  if (!room || !isBookable(room)) return '非包间'
  if (room.status !== 'Active') return roomStatusLabelMap[room.status] || room.status
  const order = orderArr.value.find(o => o.roomId === roomId && o.status === 'InUse')
  if (order) return '使用中'
  const booked = orderArr.value.find(o => o.roomId === roomId && o.status === 'Booked')
  if (booked) return '已预定'
  return '空闲'
}

function getRoomOrders(roomId: string) {
  return orderArr.value
    .filter(o => o.roomId === roomId)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 5)
}

function getRoomDevices(roomId: string) {
  return deviceArr.value.filter(d => d.roomId === roomId)
}

function deviceTypeLabel(type: string): string {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响', Sensor: '传感器' }
  return map[type] || type
}

function goRoomDetail(room: any) {
  router.push('/room-detail/' + room.roomId)
}

function severityTheme(severity: string) {
  return severity === 'Error' ? 'danger' : severity === 'Warning' ? 'warning' : 'primary'
}

function severityLabel(severity: string) {
  return severity === 'Error' ? '严重' : severity === 'Warning' ? '警告' : '信息'
}

onErrorCaptured((err) => {
  dashboardError.value = (err as Error)?.message || String(err)
  return false
})

const alertColumns = [
  { colKey: 'createdAt', title: '时间', width: 160 },
  { colKey: 'roomName', title: '房间', width: 100 },
  { colKey: 'deviceCode', title: '设备', width: 130 },
  { colKey: 'message', title: '告警内容', ellipsis: true },
  { colKey: 'severity', title: '级别', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
]

// ── Load ──

async function loadActiveOrders() {
  try {
    const res = await fetch(localStorage.getItem('erp_api_base') || 'http://localhost:8000' + '/api/operations/active-orders', {
      headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('erp_api_token') || '') }
    })
    if (res.ok) {
      const data = await res.json()
      activeOrders.value = data || []
    }
  } catch(e) { /* silent */ }
}

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  try {
    const [rooms, ords, devs, alrts, shops] = await Promise.all([
      roomApi.list().catch(() => []),
      orderApi.list().catch(() => []),
      iotApi.devices().catch(() => []),
      iotApi.alerts().catch(() => []),
      shopApi.list().catch(() => []),
    ])
    roomArr.value = (rooms || []).map(normalizeRoom)
    orderArr.value = (ords || []).map(normalizeOrder)
    deviceArr.value = (devs || []).map(normalizeDevice)
    alertArr.value = (alrts || []).map(normalizeAlert)
    shopOrders.value = (shops || []).map(normalizeShopOrder)
  } catch (e: any) {
    loadError.value = '加载总览数据失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadDashboard(); loadActiveOrders() })
</script>

<style scoped>
/* Revenue cards */
.stat-card { text-align: center; padding: 8px 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.stat-label { font-size: 13px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.stat-sub { font-size: 12px; color: #bbb; }

.info-item { padding: 12px 0; text-align: center; }
.info-label { display: block; font-size: 13px; color: #999; margin-bottom: 6px; }
.info-num { font-size: 24px; font-weight: 700; color: #0052D9; }
.info-num.green { color: #00A870; }
.info-num.purple { color: #9C27B0; }
.info-num.orange { color: #E37318; }

.price-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.price-row:last-child { border-bottom: none; }
.price-room { font-weight: 600; color: #333; min-width: 70px; }
.price-detail { color: #0052D9; flex: 1; }
.price-capacity { font-size: 11px; color: #999; }

.room-card { cursor: pointer; transition: box-shadow 0.2s; }
.room-card:hover { box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
.room-card.room-non-bookable { opacity: 0.85; }
.room-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.room-name { font-weight: 600; font-size: 14px; }
.room-card-body { font-size: 13px; color: #666; }
.room-info { display: flex; align-items: center; gap: 4px; margin-bottom: 8px; }

.room-orders { border-top: 1px solid #f0f0f0; padding-top: 8px; }
.no-orders { color: #ccc; font-size: 12px; text-align: center; padding: 8px 0; }
.order-mini { display: flex; align-items: center; gap: 6px; padding: 4px 0; font-size: 12px; }
.order-mini:not(:last-child) { border-bottom: 1px solid #fafafa; }
.order-customer { font-weight: 500; color: #333; min-width: 40px; }
.order-time { color: #999; font-size: 11px; }

.room-devices { border-top: 1px solid #f0f0f0; padding-top: 8px; }
.device-mini { display: flex; align-items: center; gap: 4px; padding: 2px 0; font-size: 11px; }
</style>
