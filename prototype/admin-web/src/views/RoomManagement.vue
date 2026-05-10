<template>
  <div>
    <h2 class="page-header">房间管理</h2>
    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="3">
          <t-input v-model="searchText" placeholder="搜索房间名称..." clearable>
            <template #prefix-icon><t-icon name="search" /></template>
          </t-input>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterType" placeholder="房间类型" clearable>
            <t-option value="MeetingRoom" label="会议室" />
            <t-option value="TeaRoom" label="茶室" />
            <t-option value="Exhibition" label="展厅" />
            <t-option value="Workspace" label="工作间" />
          </t-select>
        </t-col>
      </t-row>

      <t-table
        :data="filteredRooms"
        :columns="columns"
        row-key="roomId"
        hover
        stripe
      >
        <template #type="{ row }">
          <t-tag variant="light">{{ roomTypeLabel(row.type) }}</t-tag>
        </template>
        <template #status="{ row }">
          <t-tag
            :style="{ background: getStatusColor(row.roomId), color: '#fff', border: 'none' }"
            size="small"
          >{{ getStatusLabel(row.roomId) }}</t-tag>
        </template>
        <template #pricing="{ row }">
          <span v-if="row.pricePerHour > 0">¥{{ row.pricePerHour }}/时 · ¥{{ row.pricePerHalfHour }}/半小时</span>
          <span v-else style="color:#999">免费</span>
        </template>
        <template #currentOrder="{ row }">
          <t-tag v-if="getRoomOrder(row.roomId)" theme="primary" variant="light" size="small">
            {{ getRoomOrder(row.roomId)?.customerName }} {{ getRoomOrder(row.roomId)?.startTime }}-{{ getRoomOrder(row.roomId)?.endTime }}
          </t-tag>
          <span v-else style="color:#999">—</span>
        </template>
        <template #facilities="{ row }">
          <t-space size="small">
            <t-tag v-for="f in row.facilities" :key="f" size="small" variant="light">{{ f }}</t-tag>
          </t-space>
        </template>
        <template #actions="{ row }">
          <t-space>
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" theme="primary" @click="editRoom(row)">编辑</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 房间详情抽屉 -->
    <t-drawer v-model:visible="drawerVisible" :header="`${selectedRoom?.name} 详情`" size="400px" :footer="false">
      <div v-if="selectedRoom" class="room-detail">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-row"><span>房间编号</span><span>{{ selectedRoom.roomCode }}</span></div>
          <div class="detail-row"><span>房间类型</span><span>{{ roomTypeLabel(selectedRoom.type) }}</span></div>
          <div class="detail-row"><span>容纳人数</span><span>{{ selectedRoom.capacity }}人</span></div>
          <div class="detail-row"><span>面积</span><span>{{ selectedRoom.area }}㎡</span></div>
          <div class="detail-row"><span>当前状态</span><t-tag size="small" :style="{ background: getStatusColor(selectedRoom.roomId), color: '#fff', border: 'none' }">{{ getStatusLabel(selectedRoom.roomId) }}</t-tag></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>设备列表</h4>
          <div v-for="dev in roomDevices" :key="dev.deviceId" class="device-item">
            <span>{{ deviceTypeLabel(dev.type) }}</span>
            <span style="color:#bbb;font-size:11px;margin-left:4px">{{ dev.deviceCode }}</span>
            <t-tag :theme="dev.status === 'Online' ? 'success' : 'danger'" size="small" variant="light">
              {{ dev.status === 'Online' ? '在线' : '离线' }}
            </t-tag>
          </div>
          <div v-if="!roomDevices.length" style="color:#999;font-size:13px">暂未绑定设备</div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { rooms, orders, devices, getRoomStatusColor, getRoomStatusLabel } from '@/mock/data'

const searchText = ref('')
const filterType = ref('')
const drawerVisible = ref(false)
const selectedRoom = ref<any>(null)

const filteredRooms = computed(() => {
  let list = rooms.rooms
  if (searchText.value) {
    list = list.filter(r => r.name.includes(searchText.value))
  }
  if (filterType.value) {
    list = list.filter(r => r.type === filterType.value)
  }
  return list
})

const roomDevices = computed(() => {
  if (!selectedRoom.value) return []
  return devices.devices.filter(d => d.roomId === selectedRoom.value.roomId)
})

function getStatusColor(roomId: string): string {
  const room = rooms.rooms.find(r => r.roomId === roomId)
  if (room && room.status !== 'Active') return getRoomStatusColor(room.status)
  const order = orders.orders.find(o => o.roomId === roomId && (o.status === 'InUse' || o.status === 'Booked'))
  if (order) {
    return order.status === 'InUse' ? '#366EF4' : '#9C27B0'
  }
  return '#00A870'
}

function getStatusLabel(roomId: string): string {
  const room = rooms.rooms.find(r => r.roomId === roomId)
  if (room && room.status !== 'Active') return getRoomStatusLabel(room.status)
  const order = orders.orders.find(o => o.roomId === roomId && (o.status === 'InUse' || o.status === 'Booked'))
  if (order) return order.status === 'InUse' ? '使用中' : '已预定'
  return '空闲'
}

function getRoomOrder(roomId: string) {
  return orders.orders.find(o => o.roomId === roomId && (o.status === 'InUse' || o.status === 'Booked'))
}

function roomTypeLabel(type: string): string {
  const map: Record<string, string> = { MeetingRoom: '会议室', TeaRoom: '茶室', Exhibition: '展厅', Workspace: '工作间' }
  return map[type] || type
}

function deviceTypeLabel(type: string): string {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响' }
  return map[type] || type
}

function viewDetail(room: any) {
  selectedRoom.value = room
  drawerVisible.value = true
}

function editRoom(room: any) {
  selectedRoom.value = room
  drawerVisible.value = true
}

const columns = [
  { colKey: 'roomCode', title: '编号', width: 80 },
  { colKey: 'name', title: '房间名称', width: 120 },
  { colKey: 'type', title: '类型', width: 80 },
  { colKey: 'capacity', title: '容纳', width: 60 },
  { colKey: 'area', title: '面积', width: 60 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'pricing', title: '定价', width: 180 },
  { colKey: 'currentOrder', title: '当前订单', width: 180 },
  { colKey: 'facilities', title: '设施', ellipsis: true },
  { colKey: 'actions', title: '操作', width: 140 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }

.room-detail { padding: 8px 0; }
.detail-section { margin-bottom: 12px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.device-item { display: flex; align-items: center; gap: 8px; padding: 6px 0; border-bottom: 1px solid #f5f5f5; font-size: 13px; }
.device-item:last-child { border-bottom: none; }
</style>
