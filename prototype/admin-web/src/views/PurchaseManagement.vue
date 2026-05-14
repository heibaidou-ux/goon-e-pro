<template>
  <div>
    <h2 class="page-header">采购与配货管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in stats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-tabs v-model="activeTab" :list="tabs" @change="activeTab = $event" style="margin-bottom:16px" />
      <t-table :data="filteredOrders" :columns="orderColumns" row-key="poId" hover stripe>
        <template #type="{ row }">
          <t-tag :theme="row.type === '统一配货' ? 'primary' : 'warning'" variant="light" size="small">{{ row.type }}</t-tag>
        </template>
        <template #totalAmount="{ row }">¥{{ row.totalAmount.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="statusTheme(row.status)" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #items="{ row }">
          <t-popup trigger="hover" :content="row.items.map((i:any) => `${i.productName}×${i.qty}`).join('、')">
            <span style="color:#0052D9;cursor:pointer">{{ row.items.length }}项</span>
          </t-popup>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="(row.status === '待审核' || row.status === '待审批') && hasPermission('BTN_APPROVE')" size="small" theme="success" variant="text" @click="approveOrder(row)">审批</t-button>
            <t-button v-if="(row.status === '待审核' || row.status === '待审批') && hasPermission('BTN_REJECT')" size="small" theme="danger" variant="text" @click="rejectOrder(row)">驳回</t-button>
            <t-button v-if="row.status === '审批中' && hasPermission('BTN_REJECT')" size="small" theme="warning" variant="text" @click="rejectOrder(row)">驳回</t-button>
            <t-button size="small" variant="text" theme="primary" @click="viewOrder(row)">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- Detail Drawer -->
    <t-drawer v-model:visible="drawerVisible" :header="`采购单 ${selectedOrder?.poId}`" size="420px" :footer="false">
      <div v-if="selectedOrder" class="detail-sections">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-row"><span>采购类型</span><t-tag :theme="selectedOrder.type==='统一配货'?'primary':'warning'" variant="light" size="small">{{ selectedOrder.type }}</t-tag></div>
          <div class="detail-row"><span>供应商</span><span>{{ selectedOrder.supplierName || '内部调拨' }}</span></div>
          <div class="detail-row"><span>提报人</span><span>{{ selectedOrder.submitter }}</span></div>
          <div class="detail-row"><span>创建时间</span><span>{{ selectedOrder.createdAt }}</span></div>
          <div class="detail-row"><span>状态</span><t-tag :theme="statusTheme(selectedOrder.status)" size="small" variant="light">{{ selectedOrder.status }}</t-tag></div>
          <div class="detail-row"><span>备注</span><span>{{ selectedOrder.remark || '—' }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section"><h4>商品明细</h4>
          <t-table :data="selectedOrder.items" :columns="itemColumns" row-key="productId" size="small" />
        </div>
        <t-divider />
        <div class="detail-section">
          <div class="detail-row" style="font-weight:600;font-size:15px"><span>合计金额</span><span class="price">¥{{ selectedOrder.totalAmount.toLocaleString() }}</span></div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { hasPermission } from '@/utils/permission'
import supplyChain from '@mock/supply-chain.json'

const activeTab = ref('all')
const drawerVisible = ref(false)
const selectedOrder = ref<any>(null)

const tabs = [
  { value: 'all', label: '全部' },
  { value: '待审核', label: '待审核' },
  { value: '待审批', label: '待审批' },
  { value: '审批中', label: '审批中' },
  { value: '已收货', label: '已收货' },
  { value: '已完成', label: '已完成' },
]

const orders = supplyChain.purchaseOrders

const stats = computed(() => {
  const all = orders
  return [
    { label: '采购单总数', value: all.length, color: '#0052D9' },
    { label: '待处理', value: all.filter(o => o.status === '待审核' || o.status === '待审批').length, color: '#E37318' },
    { label: '已收货', value: all.filter(o => o.status === '已收货').length, color: '#00A870' },
    { label: '本月采购额', value: '¥' + all.filter(o => o.createdAt.startsWith('2026-05')).reduce((s, o) => s + o.totalAmount, 0).toLocaleString(), color: '#D54941' },
  ]
})

const filteredOrders = computed(() => {
  if (activeTab.value === 'all') return orders
  return orders.filter(o => o.status === activeTab.value)
})

function statusTheme(s: string): string {
  const map: Record<string, string> = { '待审核': 'warning', '待审批': 'warning', '审批中': 'primary', '已收货': 'success', '已完成': 'default' }
  return map[s] || 'default'
}

function approveOrder(order: any) { order.status = '已收货'; order.receivedAt = new Date().toISOString().slice(0, 10) }
function rejectOrder(order: any) { /* simulated rejection */ }
function viewOrder(order: any) { selectedOrder.value = order; drawerVisible.value = true }

const orderColumns = [
  { colKey: 'poId', title: '采购单号', width: 150 },
  { colKey: 'type', title: '类型', width: 90 },
  { colKey: 'supplierName', title: '供应商/门店', width: 130, ellipsis: true },
  { colKey: 'items', title: '商品', width: 70 },
  { colKey: 'totalAmount', title: '金额', width: 100 },
  { colKey: 'submitter', title: '提报人', width: 90 },
  { colKey: 'createdAt', title: '提报日期', width: 100 },
  { colKey: 'status', title: '状态', width: 90 },
  { colKey: 'actions', title: '操作', width: 160 },
]

const itemColumns = [
  { colKey: 'productName', title: '商品名称', width: 120 },
  { colKey: 'qty', title: '数量', width: 60 },
  { colKey: 'unit', title: '单位', width: 50 },
  { colKey: 'price', title: '单价', width: 80 },
  { colKey: 'amount', title: '小计', width: 80 },
]
</script>

<style scoped>
/* .page-header, .stat-card, .stat-num, .stat-label from global */
/* .detail-sections, .detail-row from global */
</style>
