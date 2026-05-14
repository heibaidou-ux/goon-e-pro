<template>
  <div>
    <h2 class="page-header">营销效果分析</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in analysisStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-card title="月度营销投入趋势" :bordered="true">
          <div class="trend-chart">
            <div v-for="(m, i) in monthlyTrend" :key="i" class="trend-bar-group">
              <div class="trend-bar own" :style="{ height: m.ownCost / maxTrend * 150 + 'px' }" title="自有渠道"></div>
              <div class="trend-bar platform" :style="{ height: m.platformCost / maxTrend * 150 + 'px' }" title="平台活动"></div>
              <div class="trend-label">{{ m.month }}</div>
            </div>
          </div>
          <div class="trend-legend"><span class="legend-own">自有渠道</span><span class="legend-platform">平台活动</span></div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="渠道ROI对比" :bordered="true">
          <div v-for="c in channelROI" :key="c.name" class="channel-row">
            <div class="channel-name">{{ c.name }}</div>
            <div class="channel-bar-bg"><div class="channel-bar" :style="{ width: c.roi * 20 + '%', background: c.color }"></div></div>
            <span class="channel-roi">{{ c.roi.toFixed(1) }}</span>
          </div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="客户获取成本" :bordered="true">
          <div v-for="c in customerAcquisition" :key="c.name" class="acq-row">
            <span>{{ c.name }}</span>
            <span class="acq-cost">¥{{ c.cost.toFixed(1) }}</span>
            <t-tag :theme="c.change > 0 ? 'danger' : 'success'" size="small" variant="light">{{ c.change > 0 ? '+' : '' }}{{ c.change }}%</t-tag>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-card title="优惠券核销分析" :bordered="true">
      <t-table :data="couponAnalysis" :columns="couponColumns" row-key="templateId" hover stripe>
        <template #usageRate="{ row }">{{ (row.usageRate * 100).toFixed(1) }}%</template>
        <template #totalDiscount="{ row }">¥{{ row.totalDiscount.toLocaleString() }}</template>
        <template #revenueLift="{ row }">
          <t-tag :theme="row.revenueLift > 0 ? 'success' : 'default'" size="small" variant="light">+{{ (row.revenueLift * 100).toFixed(0) }}%</t-tag>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import marketing from '@mock/marketing.json'

const campaigns = marketing.campaigns
const platformActivities = marketing.platformActivities
const coupons = marketing.couponTemplates

const analysisStats = computed(() => {
  const totalCampaignCost = campaigns.reduce((s, c) => s + c.budgetUsed, 0)
  const totalPlatformCost = platformActivities.reduce((s, a) => s + a.cost, 0)
  const totalRevenue = platformActivities.reduce((s, a) => s + a.actualAmount, 0)
  return [
    { label: '本月营销总投入', value: '¥' + (totalCampaignCost + totalPlatformCost).toLocaleString(), color: '#D54941' },
    { label: '平台活动ROI', value: totalPlatformCost > 0 ? (totalRevenue / totalPlatformCost).toFixed(1) : '0', color: '#00A870' },
    { label: '活跃活动数', value: campaigns.filter(c => c.status === '进行中').length + platformActivities.filter(a => a.status === '进行中').length, color: '#0052D9' },
    { label: '优惠券核销率', value: (coupons.reduce((s, c) => s + c.usedQty, 0) / coupons.reduce((s, c) => s + c.totalQty, 0) * 100).toFixed(1) + '%', color: '#E37318' },
  ]
})

const monthlyTrend = [
  { month: '1月', ownCost: 2800, platformCost: 3500 },
  { month: '2月', ownCost: 3200, platformCost: 4000 },
  { month: '3月', ownCost: 3000, platformCost: 3800 },
  { month: '4月', ownCost: 3500, platformCost: 4200 },
  { month: '5月', ownCost: 4000, platformCost: 5000 },
]

const maxTrend = Math.max(...monthlyTrend.map(m => m.ownCost + m.platformCost))

const channelROI = computed(() => [
  { name: '美团', roi: 2.8, color: '#FFD100' },
  { name: '抖音', roi: 3.5, color: '#000' },
  { name: '自有渠道', roi: 4.2, color: '#0052D9' },
])

const customerAcquisition = [
  { name: '美团', cost: 12.5, change: -5.2 },
  { name: '抖音', cost: 9.8, change: -12.3 },
  { name: '自有渠道', cost: 5.2, change: 8.1 },
]

const couponAnalysis = computed(() => coupons.map(c => ({
  ...c,
  usageRate: c.totalQty > 0 ? c.usedQty / c.totalQty : 0,
  totalDiscount: c.usedQty * (c.faceValue || 20),
  revenueLift: 0.15 + Math.random() * 0.3,
})))

const couponColumns = [
  { colKey: 'name', title: '优惠券', width: 170 },
  { colKey: 'type', title: '类型', width: 60 },
  { colKey: 'usage', title: '使用量', width: 80 },
  { colKey: 'usageRate', title: '核销率', width: 80 },
  { colKey: 'totalDiscount', title: '优惠总额', width: 100 },
  { colKey: 'revenueLift', title: '收入提升', width: 80 },
]
</script>

<style scoped>

.trend-chart { display: flex; align-items: flex-end; gap: 16px; height: 180px; padding: 10px 0; }
.trend-bar-group { flex: 1; display: flex; align-items: flex-end; gap: 4px; justify-content: center; }
.trend-bar { width: 24px; border-radius: 4px 4px 0 0; min-height: 4px; }
.trend-bar.own { background: #0052D9; }
.trend-bar.platform { background: #FFD100; }
.trend-label { position: absolute; bottom: -20px; font-size: 10px; color: #999; }
.trend-bar-group { position: relative; display: flex; align-items: flex-end; gap: 4px; }
.trend-legend { display: flex; gap: 16px; justify-content: center; margin-top: 24px; font-size: 12px; }
.legend-own::before, .legend-platform::before { content: ''; display: inline-block; width: 12px; height: 12px; margin-right: 4px; border-radius: 2px; vertical-align: middle; }
.legend-own::before { background: #0052D9; }
.legend-platform::before { background: #FFD100; }

.channel-row { display: flex; align-items: center; gap: 8px; padding: 8px 0; }
.channel-name { min-width: 50px; font-size: 12px; color: #666; }
.channel-bar-bg { flex: 1; height: 10px; background: #f0f0f0; border-radius: 5px; overflow: hidden; }
.channel-bar { height: 100%; border-radius: 5px; }
.channel-roi { min-width: 30px; text-align: right; font-weight: 600; color: #333; }

.acq-row { display: flex; align-items: center; gap: 8px; padding: 10px 0; font-size: 13px; color: #666; border-bottom: 1px solid #f5f5f5; }
.acq-row:last-child { border-bottom: none; }
.acq-cost { flex: 1; text-align: right; font-weight: 600; color: #333; }
</style>
