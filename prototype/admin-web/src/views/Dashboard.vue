<template>
  <div>
    <h2 class="page-header">门店总览</h2>

    <!-- 营收卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="card in revenueCards" :key="card.title">
        <t-card :bordered="true" hover-shadow @click="card.link ? router.push(card.link) : undefined" :style="{ cursor: card.link ? 'pointer' : 'default' }">
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
      <t-col :span="3">
        <t-card title="员工状态" :bordered="true">
          <div v-for="emp in employees.employees" :key="emp.employeeId" class="emp-row">
            <t-avatar size="small">{{ emp.name.charAt(0) }}</t-avatar>
            <span class="emp-name">{{ emp.name }}</span>
            <span class="emp-role">{{ emp.roleLabel }}</span>
            <t-tag :theme="emp.status === 'OnDuty' ? 'success' : 'default'" size="small" variant="light">
              {{ emp.status === 'OnDuty' ? '在岗' : '休息' }}
            </t-tag>
          </div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="包间报价标准" :bordered="true">
          <div v-for="room in bookableRooms" :key="room.roomId" class="price-row">
            <span class="price-room">{{ room.name }}</span>
            <span class="price-detail">¥{{ room.pricePerHour }}/时 · ¥{{ room.pricePerHalfHour }}/半小时</span>
            <span class="price-capacity">最大{{ room.capacity }}人</span>
          </div>
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
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { rooms, orders, devices, alerts, employees, getRoomStatusColor, getRoomStatusLabel } from '@/mock/data'

const router = useRouter()

const bookableRooms = rooms.rooms.filter(r => r.bookable !== false)
const totalBookable = bookableRooms.length

const inUseRooms = computed(() => bookableRooms.filter(r => {
  const order = orders.orders.find(o => o.roomId === r.roomId && o.status === 'InUse')
  return !!order
}).length)

const unresolvedAlerts = computed(() => alerts.alerts.filter(a => a.status === 'Unresolved'))

const todayStats = computed(() => {
  const todayOrders = orders.orders.filter(o => o.date === '2026-05-08')
  const inUse = todayOrders.filter(o => o.status === 'InUse').length
  const booked = todayOrders.filter(o => o.status === 'Booked').length
  const completed = todayOrders.filter(o => o.status === 'Completed').length
  const revenue = todayOrders.filter(o => o.status !== 'Booked').reduce((sum, o) => sum + o.totalAmount, 0)
  const expectedRevenue = todayOrders.reduce((sum, o) => sum + o.totalAmount, 0)
  return { totalOrders: todayOrders.length, inUse, booked, completed, revenue, expectedRevenue }
})

const revenueCards = computed(() => [
  { title: '今日营收', value: `¥${todayStats.value.revenue.toLocaleString()}`, sub: '已结算金额', color: '#0052D9', link: '' },
  { title: '订单数', value: String(todayStats.value.totalOrders), sub: '今日全部订单', color: '#00A870', link: '' },
  { title: '活跃包间', value: `${inUseRooms.value}/${totalBookable}`, sub: `使用率 ${totalBookable > 0 ? Math.round(inUseRooms.value / totalBookable * 100) : 0}%`, color: '#E37318', link: '' },
  { title: '设备在线率', value: `${deviceOnlineRate.value}%`, sub: `${deviceOnlineCount.value}/${deviceTotalCount.value} 在线 · 告警 ${unresolvedAlerts.value.length} 条`, color: '#366EF4', link: '/alerts' },
])

const deviceTotalCount = computed(() => devices.devices.length)
const deviceOnlineCount = computed(() => devices.devices.filter(d => d.status === 'Online').length)
const deviceOnlineRate = computed(() => {
  if (deviceTotalCount.value === 0) return 0
  return Math.round(deviceOnlineCount.value / deviceTotalCount.value * 100)
})

const roomList = rooms.rooms

function isBookable(room: any): boolean {
  return room.bookable !== false
}

function getRoomColor(roomId: string): string {
  const room = rooms.rooms.find(r => r.roomId === roomId)
  if (!isBookable(room)) return '#999'
  if (room && room.status !== 'Active') return getRoomStatusColor(room.status)
  const order = orders.orders.find(o => o.roomId === roomId && o.status === 'InUse')
  if (order) return '#366EF4'
  const booked = orders.orders.find(o => o.roomId === roomId && o.status === 'Booked')
  if (booked) return '#9C27B0'
  return '#00A870'
}

function getRoomStatusText(roomId: string): string {
  const room = rooms.rooms.find(r => r.roomId === roomId)
  if (!isBookable(room)) return '非包间'
  if (room && room.status !== 'Active') return getRoomStatusLabel(room.status)
  const order = orders.orders.find(o => o.roomId === roomId && o.status === 'InUse')
  if (order) return '使用中'
  const booked = orders.orders.find(o => o.roomId === roomId && o.status === 'Booked')
  if (booked) return '已预定'
  return '空闲'
}

function getRoomOrders(roomId: string) {
  return orders.orders
    .filter(o => o.roomId === roomId)
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 5)
}

function getRoomDevices(roomId: string) {
  return devices.devices.filter(d => d.roomId === roomId)
}

function deviceTypeLabel(type: string): string {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响', Sensor: '传感器' }
  return map[type] || type
}

function goRoomDetail(room: any) {
  router.push('/room-detail/' + room.roomId)
}

const recentAlerts = alerts.alerts.slice(0, 5)

function severityTheme(severity: string) {
  return severity === 'Error' ? 'danger' : severity === 'Warning' ? 'warning' : 'primary'
}

function severityLabel(severity: string) {
  return severity === 'Error' ? '严重' : severity === 'Warning' ? '警告' : '信息'
}

const alertColumns = [
  { colKey: 'createdAt', title: '时间', width: 160 },
  { colKey: 'roomName', title: '房间', width: 100 },
  { colKey: 'deviceCode', title: '设备', width: 130 },
  { colKey: 'message', title: '告警内容', ellipsis: true },
  { colKey: 'severity', title: '级别', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }

.stat-card { text-align: center; padding: 8px 0; }
.stat-label { font-size: 13px; color: #999; margin-bottom: 8px; }
.stat-value { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.stat-sub { font-size: 12px; color: #bbb; }

.info-item { padding: 12px 0; text-align: center; }
.info-label { display: block; font-size: 13px; color: #999; margin-bottom: 6px; }
.info-num { font-size: 24px; font-weight: 700; color: #0052D9; }
.info-num.green { color: #00A870; }
.info-num.purple { color: #9C27B0; }
.info-num.orange { color: #E37318; }

.emp-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.emp-row:last-child { border-bottom: none; }
.emp-name { font-weight: 500; flex: 1; }
.emp-role { font-size: 12px; color: #999; margin-right: 8px; }

.price-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 13px; }
.price-row:last-child { border-bottom: none; }
.price-room { font-weight: 600; color: #333; min-width: 70px; }
.price-detail { color: #0052D9; flex: 1; }
.price-capacity { font-size: 11px; color: #999; }

.room-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
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
