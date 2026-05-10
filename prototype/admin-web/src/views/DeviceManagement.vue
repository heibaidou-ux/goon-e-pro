<template>
  <div>
    <h2 class="page-header">IoT设备管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3">
        <t-select v-model="filterRoom" placeholder="按房间筛选" clearable>
          <t-option v-for="r in rooms.rooms" :key="r.roomId" :value="r.roomId" :label="r.name" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterType" placeholder="按类型筛选" clearable>
          <t-option value="Lock" label="门锁" />
          <t-option value="AC" label="空调" />
          <t-option value="Light" label="灯光" />
          <t-option value="Curtain" label="窗帘" />
          <t-option value="Speaker" label="音响" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterStatus" placeholder="按状态筛选" clearable>
          <t-option value="Online" label="在线" />
          <t-option value="Offline" label="离线" />
          <t-option value="Fault" label="故障" />
        </t-select>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="stat in stats" :key="stat.label">
        <t-card :bordered="true">
          <div class="stat-card">
            <div class="stat-num" :style="{ color: stat.color }">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-card v-for="group in groupedDevices" :key="group.roomId" :title="group.roomName" :bordered="true" style="margin-bottom:16px">
      <template #subtitle>
        <t-tag size="small" variant="light">{{ group.devices.length }}台设备</t-tag>
      </template>
      <t-table :data="group.devices" :columns="columns" row-key="deviceId" size="small" hover stripe>
        <template #status="{ row }">
          <t-tag :theme="deviceStatusTheme(row.status)" size="small" variant="light">
            {{ deviceStatusLabel(row.status) }}
          </t-tag>
        </template>
        <template #type="{ row }">
          <t-tag variant="outline" size="small">{{ deviceTypeLabel(row.type) }}</t-tag>
        </template>
        <template #info="{ row }">
          <span v-if="row.type === 'Lock'">电量 {{ row.batteryLevel }}%</span>
          <span v-else-if="row.type === 'AC'">{{ row.temperature }}°C · {{ modeLabel(row.mode) }}</span>
          <span v-else-if="row.type === 'Light'">亮度 {{ row.brightness }}% · {{ row.colorTemp }}K</span>
          <span v-else-if="row.type === 'Curtain'">{{ row.position === 'open' ? '打开' : row.position === 'closed' ? '关闭' : row.position }}</span>
          <span v-else-if="row.type === 'Speaker'">音量 {{ row.volume }}% · {{ row.playing ? '播放中' : '已停止' }}</span>
        </template>
        <template #protocol="{ row }">
          <t-tag size="small" variant="light">{{ row.protocol }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" theme="warning" v-if="row.status !== 'Online'" @click="troubleshoot(row)">排障</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="drawerVisible" :header="`${deviceTypeLabel(selectedDevice?.type)} 详情`" size="400px" :footer="false">
      <div v-if="selectedDevice" class="detail-section">
        <div class="detail-row"><span>设备类型</span><span>{{ deviceTypeLabel(selectedDevice.type) }}</span></div>
        <div class="detail-row"><span>设备编号</span><span>{{ selectedDevice.deviceCode }}</span></div>
        <div class="detail-row"><span>所属房间</span><span>{{ getRoomName(selectedDevice.roomId) }}</span></div>
        <div class="detail-row"><span>通信协议</span><span>{{ selectedDevice.protocol }}</span></div>
        <div class="detail-row"><span>当前状态</span>
          <t-tag :theme="deviceStatusTheme(selectedDevice.status)" size="small">
            {{ deviceStatusLabel(selectedDevice.status) }}
          </t-tag>
        </div>
        <div class="detail-row" v-if="queueLength > 0">
          <span>指令队列</span>
          <t-tag variant="light" theme="warning">⏳ {{ queueLength }} 条待执行</t-tag>
        </div>
        <t-divider />
        <div v-if="selectedDevice.type === 'Lock'" class="control-panel">
          <h4>门锁控制</h4>
          <div class="detail-row"><span>电量</span><span>{{ selectedDevice.batteryLevel }}%</span></div>
          <t-button block theme="primary" style="margin-top:12px" :disabled="sending" @click="sendCmd('unlock')">
            {{ sending ? '执行中...' : '远程开门' }}
          </t-button>
        </div>
        <div v-else-if="selectedDevice.type === 'AC'" class="control-panel">
          <h4>空调控制</h4>
          <div class="detail-row"><span>当前温度</span><span>{{ selectedDevice.temperature }}°C</span></div>
          <div class="detail-row"><span>运行模式</span><span>{{ modeLabel(selectedDevice.mode) }}</span></div>
          <t-space style="margin-top:12px">
            <t-button size="small" :disabled="sending" @click="sendCmd('cool')">制冷</t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('heat')">制热</t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('off')">关闭</t-button>
          </t-space>
        </div>
        <div v-else-if="selectedDevice.type === 'Light'" class="control-panel">
          <h4>灯光控制</h4>
          <div class="detail-row"><span>亮度</span><span>{{ selectedDevice.brightness }}%</span></div>
          <div class="detail-row"><span>色温</span><span>{{ selectedDevice.colorTemp }}K</span></div>
          <t-space style="margin-top:12px">
            <t-button size="small" :disabled="sending" @click="sendCmd('on')">开灯</t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('off')">关灯</t-button>
          </t-space>
        </div>
        <div v-else-if="selectedDevice.type === 'Curtain'" class="control-panel">
          <h4>窗帘控制</h4>
          <div class="detail-row"><span>位置</span><span>{{ selectedDevice.position }}</span></div>
          <t-space style="margin-top:12px">
            <t-button size="small" :disabled="sending" @click="sendCmd('open')">打开</t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('close')">关闭</t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('stop')">停止</t-button>
          </t-space>
        </div>
        <div v-else-if="selectedDevice.type === 'Speaker'" class="control-panel">
          <h4>音响控制</h4>
          <div class="detail-row"><span>音量</span><span>{{ selectedDevice.volume }}%</span></div>
          <div class="detail-row"><span>状态</span><span>{{ selectedDevice.playing ? '播放中' : '已停止' }}</span></div>
          <div class="detail-row"><span>音源</span><span>{{ selectedDevice.source }}</span></div>
          <t-space style="margin-top:12px">
            <t-button size="small" :disabled="sending" @click="sendCmd(selectedDevice.playing ? 'pause' : 'play')">
              {{ selectedDevice.playing ? '暂停' : '播放' }}
            </t-button>
            <t-button size="small" :disabled="sending" @click="sendCmd('mute')">静音</t-button>
          </t-space>
        </div>
        <div v-if="lastCmdStatus" style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:13px;text-align:center"
          :style="{ background: lastCmdStatus === 'success' ? '#e8f5e9' : lastCmdStatus === 'failed' ? '#fef0ef' : '#fff3e0', color: lastCmdStatus === 'success' ? '#2e7d32' : lastCmdStatus === 'failed' ? '#d54941' : '#e37318' }">
          {{ lastCmdStatus === 'success' ? '✅ 指令执行成功' : lastCmdStatus === 'sending' ? '⏳ 指令发送中...' : '❌ 指令执行失败' }}
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { devices, rooms } from '@/mock/data'
import commandQueue from '@/utils/command-queue'

const filterRoom = ref('')
const filterType = ref('')
const filterStatus = ref('')
const drawerVisible = ref(false)
const selectedDevice = ref<any>(null)
const sending = ref(false)
const lastCmdStatus = ref<'success' | 'failed' | 'sending' | ''>('')
const queueLength = ref(0)

const filteredDevices = computed(() => {
  let list = devices.devices
  if (filterRoom.value) list = list.filter(d => d.roomId === filterRoom.value)
  if (filterType.value) list = list.filter(d => d.type === filterType.value)
  if (filterStatus.value) list = list.filter(d => d.status === filterStatus.value)
  return list
})

const groupedDevices = computed(() => {
  const sorted = [...rooms.rooms]
  return sorted.map(room => {
    const roomDevices = filteredDevices.value.filter(d => d.roomId === room.roomId)
    return {
      roomId: room.roomId,
      roomName: room.name,
      devices: roomDevices,
    }
  }).filter(g => g.devices.length > 0)
})

const stats = computed(() => {
  const all = filteredDevices.value
  return [
    { label: '设备总数', value: all.length, color: '#0052D9' },
    { label: '在线', value: all.filter(d => d.status === 'Online').length, color: '#00A870' },
    { label: '离线', value: all.filter(d => d.status === 'Offline').length, color: '#D54941' },
    { label: '故障', value: all.filter(d => d.status === 'Fault').length, color: '#E37318' },
  ]
})

function deviceTypeLabel(type: string) {
  const map: Record<string, string> = { Lock: '门锁', AC: '空调', Light: '灯光', Curtain: '窗帘', Speaker: '音响', Sensor: '传感器' }
  return map[type] || type
}

function deviceStatusLabel(status: string) {
  const map: Record<string, string> = { Online: '在线', Offline: '离线', Fault: '故障', Maintenance: '维修中' }
  return map[status] || status
}

function deviceStatusTheme(status: string) {
  const map: Record<string, string> = { Online: 'success', Offline: 'danger', Fault: 'warning', Maintenance: 'primary' }
  return map[status] || 'default'
}

function modeLabel(mode: string) {
  const map: Record<string, string> = { cool: '制冷', heat: '制热', off: '关闭', fan: '送风', dry: '除湿', auto: '自动' }
  return map[mode] || mode
}

function getRoomName(roomId: string) {
  return rooms.rooms.find(r => r.roomId === roomId)?.name || roomId
}

function viewDetail(device: any) {
  selectedDevice.value = device
  drawerVisible.value = true
}

function troubleshoot(device: any) {
  selectedDevice.value = device
  drawerVisible.value = true
}

function sendCmd(action: string) {
  if (!selectedDevice.value) return
  sending.value = true
  lastCmdStatus.value = 'sending'
  const cmd = {
    deviceId: selectedDevice.value.deviceId,
    deviceName: selectedDevice.value.deviceCode,
    roomName: getRoomName(selectedDevice.value.roomId),
    type: selectedDevice.value.type as any,
    action,
    operator: localStorage.getItem('erp_user') || '店员',
    sourceIp: window.location.hostname,
  }
  commandQueue.onEach((c) => {
    queueLength.value = commandQueue.length
    if (c.deviceId === cmd.deviceId) {
      lastCmdStatus.value = c.status
      if (c.status === 'success' || c.status === 'failed') {
        setTimeout(() => { sending.value = false }, 500)
      }
    }
  })
  commandQueue.enqueue(cmd)
  queueLength.value = commandQueue.length
}

const columns = [
  { colKey: 'type', title: '设备类型', width: 80 },
  { colKey: 'deviceCode', title: '编号', width: 130 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'info', title: '运行信息', ellipsis: true },
  { colKey: 'protocol', title: '协议', width: 70 },
  { colKey: 'actions', title: '操作', width: 120 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 24px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
.detail-section { padding: 8px 0; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 12px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.control-panel { background: #f9f9f9; padding: 12px; border-radius: 6px; margin-top: 8px; }
</style>
