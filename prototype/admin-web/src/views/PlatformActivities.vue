<template>
  <div>
    <h2 class="page-header">第三方平台活动管理</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="2"><t-select v-model="filterPlatformName" placeholder="选择平台" clearable>
        <t-option value="美团" label="美团" /><t-option value="抖音" label="抖音" /><t-option value="线下" label="线下" />
      </t-select></t-col>
      <t-col :span="2"><t-select v-model="filterPlatformStatus" placeholder="状态" clearable>
        <t-option value="进行中" label="进行中" /><t-option value="已结束" label="已结束" /><t-option value="计划中" label="计划中" />
      </t-select></t-col>
    </t-row>

    <t-card :bordered="true" style="margin-bottom:20px">
      <t-table :data="filteredPlatformActivities" :columns="columns" row-key="paId" hover stripe>
        <template #platform="{ row }">
          <t-tag :theme="row.platform === '美团' ? 'warning' : row.platform === '抖音' ? 'primary' : 'default'" variant="light" size="small">{{ row.platform }}</t-tag>
        </template>
        <template #cost="{ row }">¥{{ row.cost.toLocaleString() }}</template>
        <template #transactionAmount="{ row }">¥{{ row.transactionAmount.toLocaleString() }}</template>
        <template #actualAmount="{ row }">¥{{ row.actualAmount.toLocaleString() }}</template>
        <template #roi="{ row }">
          <t-tag v-if="row.roi > 0" :theme="row.roi > 1 ? 'success' : 'warning'" size="small" variant="light">{{ row.roi.toFixed(1) }}</t-tag>
          <span v-else style="color:#999">—</span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '进行中' ? 'success' : row.status === '已结束' ? 'default' : 'primary'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-button size="small" variant="text" theme="primary" @click="selectedPA=row;paDetailVisible=true">详情</t-button>
        </template>
      </t-table>
    </t-card>

    <!-- Cross-platform comparison -->
    <t-card title="跨平台效果对比" :bordered="true">
      <t-table :data="platformComparison" :columns="compareColumns" row-key="platform" hover stripe>
        <template #cost="{ row }">¥{{ row.totalCost.toLocaleString() }}</template>
        <template #revenue="{ row }">¥{{ row.totalRevenue.toLocaleString() }}</template>
        <template #roi="{ row }">
          <t-tag :theme="row.roi > 1 ? 'success' : 'danger'" size="small" variant="light">{{ row.roi.toFixed(1) }}</t-tag>
        </template>
        <template #customerCost="{ row }">¥{{ row.customerCost.toFixed(1) }}</template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="paDetailVisible" :header="selectedPA?.name" size="400px" :footer="false">
      <div v-if="selectedPA" class="detail-sections">
        <div class="detail-row"><span>平台</span><t-tag variant="light">{{ selectedPA.platform }}</t-tag></div>
        <div class="detail-row"><span>活动形式</span><span>{{ selectedPA.type }}</span></div>
        <div class="detail-row"><span>时间</span><span>{{ selectedPA.startDate }} ~ {{ selectedPA.endDate }}</span></div>
        <div class="detail-row"><span>投入成本</span><span class="price">¥{{ selectedPA.cost.toLocaleString() }}</span></div>
        <div class="detail-row"><span>曝光量</span><span>{{ selectedPA.impressions.toLocaleString() }}</span></div>
        <div class="detail-row"><span>订单量</span><span>{{ selectedPA.orders }}</span></div>
        <div class="detail-row"><span>核销量</span><span>{{ selectedPA.redemptions }}</span></div>
        <div class="detail-row"><span>交易额</span><span class="price">¥{{ selectedPA.transactionAmount.toLocaleString() }}</span></div>
        <div class="detail-row"><span>平台补贴</span><span>¥{{ selectedPA.subsidy.toLocaleString() }}</span></div>
        <div class="detail-row"><span>平台佣金</span><span>¥{{ selectedPA.commission.toLocaleString() }}</span></div>
        <div class="detail-row"><span>实际到账</span><span class="price">¥{{ selectedPA.actualAmount.toLocaleString() }}</span></div>
        <div class="detail-row"><span>ROI</span><span :style="{color:selectedPA.roi>1?'#00A870':'#D54941',fontWeight:600}">{{ selectedPA.roi.toFixed(1) }}</span></div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import marketing from '@mock/marketing.json'

const filterPlatformName = ref('')
const filterPlatformStatus = ref('')
const paDetailVisible = ref(false)
const selectedPA = ref<any>(null)

const platformActivities = marketing.platformActivities

const filteredPlatformActivities = computed(() => {
  let list = platformActivities
  if (filterPlatformName.value) list = list.filter(a => a.platform === filterPlatformName.value)
  if (filterPlatformStatus.value) list = list.filter(a => a.status === filterPlatformStatus.value)
  return list
})

const platformComparison = computed(() => {
  const grouped: Record<string, any[]> = {}
  platformActivities.forEach(a => {
    if (!grouped[a.platform]) grouped[a.platform] = []
    grouped[a.platform].push(a)
  })
  return Object.entries(grouped).map(([platform, acts]) => {
    const totalCost = acts.reduce((s, a) => s + a.cost, 0)
    const totalRevenue = acts.reduce((s, a) => s + a.actualAmount, 0)
    const totalOrders = acts.reduce((s, a) => s + a.orders, 0)
    return { platform, totalCost, totalRevenue, roi: totalCost > 0 ? totalRevenue / totalCost : 0, customerCost: totalOrders > 0 ? totalCost / totalOrders : 0 }
  })
})

const columns = [
  { colKey: 'platform', title: '平台', width: 70 },
  { colKey: 'name', title: '活动名称', width: 180, ellipsis: true },
  { colKey: 'type', title: '形式', width: 80 },
  { colKey: 'cost', title: '投入', width: 80 },
  { colKey: 'impressions', title: '曝光', width: 80 },
  { colKey: 'orders', title: '订单', width: 60 },
  { colKey: 'redemptions', title: '核销', width: 60 },
  { colKey: 'actualAmount', title: '实际到账', width: 100 },
  { colKey: 'roi', title: 'ROI', width: 70 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 70 },
]

const compareColumns = [
  { colKey: 'platform', title: '平台', width: 80 },
  { colKey: 'cost', title: '总投入', width: 100 },
  { colKey: 'revenue', title: '总收入', width: 100 },
  { colKey: 'roi', title: 'ROI', width: 80 },
  { colKey: 'customerCost', title: '单客获取成本', width: 120 },
]
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
