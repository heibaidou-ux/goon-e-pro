<template>
  <div>
    <h2 class="page-header">订单管理</h2>

    <t-card :bordered="true">
      <t-tabs v-model="activeTab" @change="onTabChange">
        <t-tab-panel value="shop" :label="'茶品订单 (' + shopOrderList.length + ')'"></t-tab-panel>
        <t-tab-panel value="room" :label="'包间订单 (' + roomOrderList.length + ')'"></t-tab-panel>
      </t-tabs>

      <!-- 茶品订单 -->
      <div v-if="activeTab === 'shop'" class="tab-content">
        <t-table
          :data="shopOrderList"
          :columns="shopColumns"
          row-key="orderId"
          hover
          stripe
          size="small"
          :pagination="{ pageSize: 20, total: shopOrderList.length }"
        >
          <template #items="{ row }">
            <span class="cell-ellipsis" :title="formatItems(row.items)">{{ formatItems(row.items) }}</span>
          </template>
          <template #totalAmount="{ row }">
            <span class="cell-amount">¥{{ row.totalAmount }}</span>
          </template>
          <template #createdAt="{ row }">
            {{ (row.createdAt || '').slice(0, 16).replace('T', ' ') }}
          </template>
          <template #_logistics="{ row }">
            <t-tag :theme="lgStatusTheme(row._logistics?.status)" size="small" variant="light">
              {{ lgStatusLabel(row._logistics?.status) }}
            </t-tag>
          </template>
          <template #actions="{ row }">
            <t-space size="small">
              <t-button size="small" variant="text" theme="primary" @click="openLogistics(row)">物流管理</t-button>
              <t-button size="small" variant="text" theme="default" @click="viewTimeline(row)">详情</t-button>
            </t-space>
          </template>
        </t-table>
      </div>

      <!-- 包间订单 -->
      <div v-if="activeTab === 'room'" class="tab-content">
        <t-table
          :data="roomOrderList"
          :columns="roomColumns"
          row-key="orderId"
          hover
          stripe
          size="small"
          :pagination="{ pageSize: 20, total: roomOrderList.length }"
        >
          <template #totalAmount="{ row }">
            <span class="cell-amount">¥{{ row.totalAmount }}</span>
          </template>
          <template #status="{ row }">
            <t-tag :theme="row.status === 'InUse' ? 'primary' : row.status === 'Booked' ? 'warning' : row.status === 'Completed' ? 'success' : 'default'" size="small" variant="light">
              {{ row.status === 'InUse' ? '使用中' : row.status === 'Booked' ? '已预定' : row.status === 'Completed' ? '已结束' : row.status }}
            </t-tag>
          </template>
        </t-table>
      </div>
    </t-card>

    <!-- Logistics Management Dialog -->
    <t-dialog v-model:visible="lgVisible" header="物流管理" width="520px" :footer="false">
      <div v-if="lgOrder" class="lg-wrap">
        <div class="lg-order-info">
          <span class="lg-order-id">订单：{{ lgOrder.orderId }}</span>
          <span class="lg-customer">{{ lgOrder.customerName || lgOrder.name || '用户' }}</span>
          <span class="lg-amount">¥{{ lgOrder.totalAmount }}</span>
        </div>

        <t-form layout="vertical" style="margin-top:16px">
          <t-form-item label="物流状态">
            <t-radio-group v-model="lgForm.status">
              <t-radio value="pending">待发货</t-radio>
              <t-radio value="transit">运输中</t-radio>
              <t-radio value="delivered">已签收</t-radio>
            </t-radio-group>
          </t-form-item>
          <t-form-item label="快递公司">
            <t-select v-model="lgForm.carrier" placeholder="选择快递公司" filterable>
              <t-option value="顺丰速运" label="顺丰速运" />
              <t-option value="圆通速递" label="圆通速递" />
              <t-option value="中通快递" label="中通快递" />
              <t-option value="韵达快递" label="韵达快递" />
              <t-option value="申通快递" label="申通快递" />
              <t-option value="京东快递" label="京东快递" />
              <t-option value="EMS" label="EMS" />
            </t-select>
          </t-form-item>
          <t-form-item label="快递单号">
            <t-input v-model="lgForm.trackingNo" placeholder="输入快递单号" />
          </t-form-item>
          <t-form-item label="备注">
            <t-textarea v-model="lgForm.remark" placeholder="物流备注（选填）" :rows="2" />
          </t-form-item>
        </t-form>

        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="lgVisible = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="saveLogistics">保存物流信息</t-button>
        </div>
      </div>
    </t-dialog>

    <!-- Logistics Timeline Dialog -->
    <t-dialog v-model:visible="tlVisible" header="物流详情" width="480px" :footer="false">
      <div v-if="tlOrder" class="tl-wrap">
        <div class="tl-header">
          <div class="tl-status" :class="'tl-' + (tlOrder._logistics?.status || 'pending')">
            {{ lgStatusLabel(tlOrder._logistics?.status) }}
          </div>
          <div class="tl-carrier" v-if="tlOrder._logistics?.carrier">
            {{ tlOrder._logistics.carrier }} · {{ tlOrder._logistics.trackingNo }}
          </div>
        </div>
        <div class="tl-timeline">
          <div class="tl-item" v-for="(evt, i) in tlEvents" :key="i" :class="{ active: i === 0 }">
            <div class="tl-dot" :class="{ filled: i === 0 }"></div>
            <div class="tl-content">
              <div class="tl-event">{{ evt.event }}</div>
              <div class="tl-time">{{ evt.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { orders, shopOrders } from '@/mock/data'

type TabValue = 'shop' | 'room'

const activeTab = ref<TabValue>('shop')

// ── Shop orders ──
const shopOrderList = computed(() => {
  const raw = shopOrders as any[]
  return raw.map(o => {
    const log = getOrderLogistics(o.orderId)
    if (log) o._logistics = log
    return o
  }).sort((a, b) => (b.createdAt || '').localeCompare(a.createdAt || ''))
})

function getOrderLogistics(orderId: string): any {
  try {
    const data = localStorage.getItem('shop_logistics_' + orderId)
    if (data) return JSON.parse(data)
  } catch (e) { /* ignore */ }
  return null
}

function lgStatusLabel(status?: string): string {
  const map: Record<string, string> = { pending: '待发货', transit: '运输中', delivered: '已签收' }
  return map[status || 'pending'] || '待发货'
}

function lgStatusTheme(status?: string) {
  const map: Record<string, string> = { pending: 'warning', transit: 'primary', delivered: 'success' }
  return map[status || 'pending'] as any
}

const shopColumns = [
  { colKey: 'orderId', title: '订单号', width: 130 },
  { colKey: 'customerName', title: '客户', width: 80 },
  { colKey: 'items', title: '商品', width: 200, ellipsis: true },
  { colKey: 'totalAmount', title: '金额', width: 80 },
  { colKey: 'createdAt', title: '下单时间', width: 150 },
  { colKey: '_logistics', title: '物流状态', width: 100 },
  { colKey: 'actions', title: '操作', width: 160 },
]

// ── Room orders ──
const roomOrderList = computed(() => {
  const arr = (orders?.orders || []) as any[]
  return arr.sort((a, b) => (b.date || '').localeCompare(a.date || ''))
})

const roomColumns = [
  { colKey: 'orderId', title: '订单号', width: 120 },
  { colKey: 'customerName', title: '客户', width: 80 },
  { colKey: 'roomName', title: '包间', width: 80 },
  { colKey: 'date', title: '日期', width: 100 },
  { colKey: 'startTime', title: '时段', width: 120 },
  { colKey: 'totalAmount', title: '金额', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
]

function onTabChange(val: string | number) {
  activeTab.value = val as TabValue
}

// ── Logistics modal ──
const lgVisible = ref(false)
const lgOrder = ref<any>(null)
const lgForm = reactive({ status: 'pending', carrier: '', trackingNo: '', remark: '' })

function openLogistics(order: any) {
  lgOrder.value = order
  const log = getOrderLogistics(order.orderId)
  lgForm.status = log?.status || 'pending'
  lgForm.carrier = log?.carrier || ''
  lgForm.trackingNo = log?.trackingNo || ''
  lgForm.remark = log?.remark || ''
  lgVisible.value = true
}

function saveLogistics() {
  if (!lgOrder.value) return
  const data = {
    status: lgForm.status,
    carrier: lgForm.carrier,
    trackingNo: lgForm.trackingNo,
    remark: lgForm.remark,
    updatedAt: new Date().toISOString(),
  }
  localStorage.setItem('shop_logistics_' + lgOrder.value.orderId, JSON.stringify(data))
  // Update in-memory copy
  lgOrder.value._logistics = data
  lgVisible.value = false
}

// ── Timeline modal ──
const tlVisible = ref(false)
const tlOrder = ref<any>(null)
const tlEvents = computed(() => {
  const o = tlOrder.value
  if (!o) return []
  const log = o._logistics
  const events: { event: string; time: string }[] = []
  const created = o.createdAt || new Date().toISOString()
  events.push({ event: '订单已提交', time: created })
  if (!log || log.status === 'pending') {
    events.push({ event: '等待卖家发货', time: '—' })
    return events
  }
  events.push({ event: '商品已发货' + (log.carrier ? ' （' + log.carrier + '）' : ''), time: log.updatedAt || '—' })
  if (log.trackingNo) {
    events.push({ event: '快递已揽收 · 单号：' + log.trackingNo, time: log.updatedAt || '—' })
  }
  if (log.status === 'delivered') {
    events.push({ event: '已签收' + (log.remark ? ' （' + log.remark + '）' : ''), time: log.updatedAt || '—' })
  }
  return events
})

function viewTimeline(order: any) {
  tlOrder.value = order
  tlVisible.value = true
}

function formatItems(items: any[] | undefined): string {
  if (!items || !items.length) return '—'
  return items.map((i: any) => i.name || i.productName || '').join('、')
}
</script>

<style scoped>
.tab-content { margin-top: 16px; }
.cell-ellipsis { display: inline-block; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.cell-amount { font-weight: 600; color: #0052D9; }
.lg-wrap .lg-order-info { display: flex; gap: 16px; font-size: 13px; color: #333; padding: 12px; background: #f5f7fa; border-radius: 8px; }
.lg-order-id { font-weight: 600; }
.lg-customer { color: #666; }
.lg-amount { margin-left: auto; font-weight: 700; color: #0052D9; }
.tl-wrap { padding: 4px 0; }
.tl-header { text-align: center; margin-bottom: 20px; }
.tl-status { font-size: 20px; font-weight: 700; }
.tl-status.tl-pending { color: #E37318; }
.tl-status.tl-transit { color: #0052D9; }
.tl-status.tl-delivered { color: #00A870; }
.tl-carrier { font-size: 13px; color: #999; margin-top: 4px; }
.tl-timeline { position: relative; padding-left: 20px; }
.tl-item { position: relative; padding-bottom: 20px; padding-left: 16px; border-left: 2px solid #e0e0e0; }
.tl-item:last-child { border-left-color: transparent; padding-bottom: 0; }
.tl-item.active .tl-event { color: #333; font-weight: 600; }
.tl-dot { position: absolute; left: -6px; top: 0; width: 10px; height: 10px; border-radius: 50%; background: #e0e0e0; }
.tl-dot.filled { background: #0052D9; }
.tl-event { font-size: 13px; color: #999; }
.tl-time { font-size: 11px; color: #ccc; margin-top: 2px; }
</style>
