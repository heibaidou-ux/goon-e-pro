<template>
  <div>
    <h2 class="page-header">报表体系</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="r in reportTypes" :key="r.name">
        <t-card :bordered="true" hover-shadow class="report-card" @click="openReport(r)">
          <div class="report-icon" :style="{ background: r.color + '15', color: r.color }">{{ r.icon }}</div>
          <div class="report-name">{{ r.name }}</div>
          <div class="report-desc">{{ r.desc }}</div>
        </t-card>
      </t-col>
    </t-row>

    <!-- Revenue Trend Chart (simulated) -->
    <t-card title="日营收走势图" :bordered="true" style="margin-bottom:20px">
      <div class="chart-container">
        <div v-for="(d, i) in revenueData" :key="i" class="chart-bar-col">
          <div class="chart-bar" :style="{ height: d.totalAmount / maxRev * 200 + 'px' }">
            <span class="chart-bar-val">¥{{ d.totalAmount }}</span>
          </div>
          <div class="chart-bar-label">{{ d.date.slice(5) }}</div>
        </div>
      </div>
    </t-card>

    <t-row :gutter="16">
      <t-col :span="8">
        <t-card title="月度经营报告对比" :bordered="true">
          <t-table :data="monthlyComparision" :columns="comparisonColumns" row-key="storeName" hover stripe>
            <template #revenue="{ row }">¥{{ row.revenue.toLocaleString() }}</template>
            <template #netProfit="{ row }">
              <span :style="{ color: row.netProfit >= 0 ? '#00A870' : '#D54941', fontWeight: 600 }">¥{{ row.netProfit.toLocaleString() }}</span>
            </template>
          </t-table>
        </t-card>
      </t-col>
      <t-col :span="4">
        <t-card title="利润排名" :bordered="true">
          <div v-for="(r, i) in profitRanking" :key="r.storeName" class="rank-row">
            <span class="rank-num" :style="{ background: rankColor(i) }">{{ i + 1 }}</span>
            <span class="rank-name">{{ r.storeName }}</span>
            <span class="rank-profit" :style="{ color: r.netProfit >= 0 ? '#00A870' : '#D54941' }">¥{{ r.netProfit.toLocaleString() }}</span>
          </div>
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import finance from '@mock/finance.json'

const revenueData = finance.dailyRevenue
const maxRev = computed(() => Math.max(...revenueData.map(d => d.totalAmount), 1))

const monthlyReport = finance.monthlyReport

const monthlyComparision = computed(() => {
  return monthlyReport.map(r => ({
    ...r,
    netProfit: r.revenue - r.platformFee - r.marketingCost - r.materialCost - r.laborCost - r.depreciation - r.operatingCost + r.subsidy,
  }))
})

const profitRanking = computed(() => {
  return [...monthlyComparision.value].sort((a, b) => b.netProfit - a.netProfit)
})

function rankColor(i: number): string {
  if (i === 0) return '#D54941'
  if (i === 1) return '#E37318'
  if (i === 2) return '#F5A623'
  return '#999'
}

function openReport(r: any) { /* In prototype, just show the report */ }

const reportTypes = [
  { name: '月度经营报告', desc: '门店利润表、收入明细、支出明细', color: '#0052D9', icon: '📊' },
  { name: '日营收走势', desc: '本月每日营收趋势图表', color: '#00A870', icon: '📈' },
  { name: '同比/环比分析', desc: '与上月/去年同期对比', color: '#E37318', icon: '📉' },
  { name: '合并报表', desc: '各门店收入/支出/利润对比', color: '#9C27B0', icon: '📋' },
]

const comparisonColumns = [
  { colKey: 'storeName', title: '门店', width: 100 },
  { colKey: 'revenue', title: '营收', width: 120 },
  { colKey: 'netProfit', title: '净利润', width: 120 },
]
</script>

<style scoped>
.report-card { cursor: pointer; text-align: center; padding: 16px 0; transition: box-shadow 0.2s; }
.report-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.12); }
.report-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; margin: 0 auto 12px; }
.report-name { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 6px; }
.report-desc { font-size: 12px; color: #999; }
.chart-container { display: flex; align-items: flex-end; gap: 8px; height: 240px; padding: 10px 0; overflow-x: auto; }
.chart-bar-col { display: flex; flex-direction: column; align-items: center; flex: 1; min-width: 40px; }
.chart-bar { width: 32px; background: linear-gradient(to top, #0052D9, #366EF4); border-radius: 4px 4px 0 0; display: flex; align-items: flex-start; justify-content: center; padding-top: 4px; min-height: 8px; position: relative; }
.chart-bar-val { font-size: 9px; color: #fff; white-space: nowrap; }
.chart-bar-label { font-size: 10px; color: #999; margin-top: 4px; }
.rank-row { display: flex; align-items: center; gap: 8px; padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.rank-row:last-child { border-bottom: none; }
.rank-num { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 12px; font-weight: 600; }
.rank-name { flex: 1; font-size: 13px; color: #333; }
.rank-profit { font-weight: 600; font-size: 13px; }
</style>
