<template>
  <div>
    <h2 class="page-header">收入管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-date-range-picker v-model="dateRange" style="width:100%" separator="至" />
      </t-col>
      <t-col :span="2">
        <t-select v-model="selectedStore" placeholder="选择门店" clearable>
          <t-option value="盈隆店" label="盈隆店" />
          <t-option value="盈丰店" label="盈丰店" />
          <t-option value="金德店" label="金德店" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-button @click="loadRevenue">查询</t-button>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-card title="日营收趋势" :bordered="true">
          <div class="chart-placeholder">
            <div v-for="(d, i) in revenueTrend" :key="i" class="bar-wrapper" :style="{ height: d.amount / maxAmount * 160 + 'px' }">
              <div class="bar" :style="{ background: d.color || '#0052D9' }"></div>
              <div class="bar-label">{{ d.date.slice(5) }}</div>
            </div>
          </div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="收入科目分布" :bordered="true">
          <div v-for="item in accountSummary" :key="item.name" class="account-row">
            <span class="account-name">{{ item.name }}</span>
            <div class="account-bar-bg">
              <div class="account-bar" :style="{ width: item.percent + '%', background: item.color }"></div>
            </div>
            <span class="account-amount">¥{{ item.amount.toLocaleString() }}</span>
          </div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="收入汇总" :bordered="true">
          <div class="summary-item"><span>总收入</span><span class="summary-val">¥{{ totalRevenue.toLocaleString() }}</span></div>
          <div class="summary-item"><span>线上收入</span><span class="summary-val">¥{{ onlineRevenue.toLocaleString() }}</span></div>
          <div class="summary-item"><span>线下收入</span><span class="summary-val">¥{{ offlineRevenue.toLocaleString() }}</span></div>
          <t-divider />
          <div class="summary-item"><span>平台补贴</span><span class="summary-val green">¥{{ platformSubsidy.toLocaleString() }}</span></div>
          <div class="summary-item"><span>会员充值</span><span class="summary-val green">¥{{ memberRecharge.toLocaleString() }}</span></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-table :data="revenueData" :columns="revenueColumns" row-key="date+storeName" hover stripe>
        <template #platformBreakdown="{ row }">
          <t-space size="small">
            <t-tag v-for="(v, k) in row.platformBreakdown" :key="k" size="small" variant="light">{{ k }}: ¥{{ v }}</t-tag>
          </t-space>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import finance from '@mock/finance.json'

const dateRange = ref(['2026-04-25', '2026-05-04'])
const selectedStore = ref('')

const revenueData = finance.dailyRevenue

const filteredRevenue = computed(() => {
  let list = revenueData
  if (selectedStore.value) list = list.filter(r => r.storeName === selectedStore.value)
  return list
})

const revenueTrend = computed(() => {
  return filteredRevenue.value.map((r, i) => ({ ...r, amount: r.totalAmount, color: ['#0052D9','#00A870','#E37318','#9C27B0','#D54941','#2D9C9C','#F5A623'][i % 7] }))
})

const maxAmount = computed(() => Math.max(...revenueTrend.value.map(d => d.amount), 1))

const totalRevenue = computed(() => filteredRevenue.value.reduce((s, r) => s + r.totalAmount, 0))
const onlineRevenue = computed(() => filteredRevenue.value.reduce((s, r) => s + (r.platformBreakdown['美团'] || 0) + (r.platformBreakdown['抖音'] || 0) + (r.platformBreakdown['小程序'] || 0), 0))
const offlineRevenue = computed(() => filteredRevenue.value.reduce((s, r) => s + (r.platformBreakdown['线下'] || 0), 0))
const platformSubsidy = 1850
const memberRecharge = 3200

const accountSummary = computed(() => {
  const items = [
    { name: '空间租用', amount: Math.round(totalRevenue.value * 0.72), color: '#0052D9' },
    { name: '商品零售', amount: Math.round(totalRevenue.value * 0.18), color: '#00A870' },
    { name: '平台补贴', amount: platformSubsidy, color: '#E37318' },
    { name: '其他收入', amount: Math.round(totalRevenue.value * 0.1), color: '#9C27B0' },
  ]
  const total = items.reduce((s, i) => s + i.amount, 0)
  return items.map(i => ({ ...i, percent: total > 0 ? Math.round(i.amount / total * 100) : 0 }))
})

function loadRevenue() { /* trigger recompute */ }

const revenueColumns = [
  { colKey: 'date', title: '日期', width: 100 },
  { colKey: 'storeName', title: '门店', width: 80 },
  { colKey: 'totalAmount', title: '总金额', width: 100 },
  { colKey: 'orderCount', title: '订单数', width: 70 },
  { colKey: 'platformBreakdown', title: '平台分布', ellipsis: true },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.chart-placeholder { display: flex; align-items: flex-end; gap: 6px; height: 180px; padding: 10px 0; }
.bar-wrapper { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; }
.bar { width: 100%; min-height: 4px; border-radius: 4px 4px 0 0; }
.bar-label { font-size: 10px; color: #999; margin-top: 4px; }

.account-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; }
.account-name { min-width: 60px; color: #666; }
.account-bar-bg { flex: 1; height: 8px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }
.account-bar { height: 100%; border-radius: 4px; }
.account-amount { min-width: 70px; text-align: right; color: #333; font-weight: 500; }

.summary-item { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; color: #666; }
.summary-val { font-weight: 600; color: #0052D9; }
.summary-val.green { color: #00A870; }
</style>
