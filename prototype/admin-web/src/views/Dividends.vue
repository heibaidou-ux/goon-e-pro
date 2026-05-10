<template>
  <div>
    <h2 class="page-header">股东分红</h2>

    <t-alert message="分红计算基于已确认的月结报告。品牌股东和门店股东分红互不干扰。" theme="info" style="margin-bottom:20px" />

    <t-card title="品牌股东分红" :bordered="true" style="margin-bottom:20px">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="4">
          <t-select v-model="selectedPeriod" placeholder="选择月结周期">
            <t-option value="2026年4月" label="2026年4月" />
            <t-option value="2026年3月" label="2026年3月" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-button theme="primary" @click="calcDividend">计算分红</t-button>
        </t-col>
        <t-col :span="6" style="text-align:right">
          <span class="profit-label">品牌净利润：</span><span class="profit-val">¥{{ brandNetProfit.toLocaleString() }}</span>
        </t-col>
      </t-row>

      <t-table v-if="showBrandDividend" :data="brandDividends" :columns="brandColumns" row-key="name" hover stripe>
        <template #shareRatio="{ row }">{{ (row.shareRatio * 100).toFixed(0) }}%</template>
        <template #amount="{ row }">¥{{ row.amount.toLocaleString() }}</template>
      </t-table>
      <div v-else style="padding:40px;text-align:center;color:#999">请选择月结周期并点击"计算分红"</div>
    </t-card>

    <t-card title="门店股东分红" :bordered="true">
      <t-table v-if="showBrandDividend" :data="storeDividendList" :columns="storeColumns" row-key="name" hover stripe>
        <template #shareRatio="{ row }">{{ (row.shareRatio * 100).toFixed(0) }}%</template>
        <template #amount="{ row }">¥{{ row.amount.toLocaleString() }}</template>
      </t-table>
      <div v-else style="padding:40px;text-align:center;color:#999">请先计算品牌股东分红</div>
    </t-card>

    <!-- Dividend Record -->
    <t-card title="分红记录" :bordered="true" style="margin-top:20px">
      <t-table :data="dividendRecords" :columns="recordColumns" row-key="recordId" hover stripe size="small">
        <template #totalAmount="{ row }">¥{{ row.totalAmount.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已发放' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import finance from '@mock/finance.json'

const selectedPeriod = ref('2026年4月')
const showBrandDividend = ref(false)

const brandDividends = finance.dividends.brandShareholders
const storeShareholders = finance.dividends.storeShareholders

const brandNetProfit = 100000

const storeDividendList = computed(() => {
  const all: any[] = []
  Object.entries(storeShareholders).forEach(([store, list]: [string, any]) => {
    (list as any[]).forEach(s => all.push({ ...s, store }))
  })
  return all
})

function calcDividend() { showBrandDividend.value = true }

const dividendRecords = [
  { recordId: 'DIV202604', period: '2026年4月', totalAmount: 114460, status: '已发放', paidAt: '2026-04-28' },
  { recordId: 'DIV202603', period: '2026年3月', totalAmount: 98200, status: '已发放', paidAt: '2026-03-28' },
]

const brandColumns = [
  { colKey: 'name', title: '股东姓名', width: 150 },
  { colKey: 'shareRatio', title: '持股比例', width: 100 },
  { colKey: 'amount', title: '分红金额', width: 150 },
]

const storeColumns = [
  { colKey: 'store', title: '门店', width: 100 },
  { colKey: 'name', title: '股东姓名', width: 150 },
  { colKey: 'shareRatio', title: '持股比例', width: 100 },
  { colKey: 'amount', title: '分红金额', width: 150 },
]

const recordColumns = [
  { colKey: 'period', title: '周期', width: 120 },
  { colKey: 'totalAmount', title: '分红总额', width: 150 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'paidAt', title: '发放日期', width: 100 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.profit-label { font-size: 14px; color: #666; }
.profit-val { font-size: 16px; font-weight: 700; color: #00A870; }
</style>
