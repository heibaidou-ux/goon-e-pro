<template>
  <div>
    <h2 class="page-header">自动月结</h2>

    <t-alert message="月结周期：上月25日至本月24日。每月25日凌晨自动触发月结。" theme="info" style="margin-bottom:20px" />

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in settlementStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" style="margin-bottom:20px">
      <t-table :data="settlements" :columns="settlementColumns" row-key="settlementId" hover stripe>
        <template #revenue="{ row }">¥{{ row.revenue.toLocaleString() }}</template>
        <template #expense="{ row }">¥{{ row.expense.toLocaleString() }}</template>
        <template #profit="{ row }">
          <span :style="{ color: row.profit >= 0 ? '#00A870' : '#D54941', fontWeight: 600 }">¥{{ (row.profit || 0).toLocaleString() }}</span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已月结' ? 'success' : row.status === '计算中' ? 'warning' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status === '已月结'" size="small" variant="text" theme="primary" @click="showReport(row)">查看报告</t-button>
            <t-button v-if="row.status === '计算中'" size="small" theme="warning" variant="text" @click="runSettlement(row)">执行月结</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- GL Entries -->
    <t-card title="日GL凭证记录" :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="3">
          <t-date-picker v-model="glDate" style="width:100%" />
        </t-col>
        <t-col :span="2">
          <t-select v-model="glStatus" placeholder="凭证状态" clearable>
            <t-option value="已过账" label="已过账" />
            <t-option value="待过账" label="待过账" />
          </t-select>
        </t-col>
      </t-row>
      <t-table :data="filteredGlEntries" :columns="glColumns" row-key="entryId" hover stripe>
        <template #debit="{ row }">¥{{ row.debit || '—' }}</template>
        <template #credit="{ row }">¥{{ row.credit || '—' }}</template>
        <template #status="{ row }">
          <t-tag theme="success" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="reportVisible" header="月结报告" width="760px" :footer="false">
      <div v-if="currentReport">
        <t-table :data="reportData" :columns="reportColumns" row-key="storeName" size="small" hover stripe>
          <template #revenue="{ row }">¥{{ row.revenue.toLocaleString() }}</template>
          <template #platformFee="{ row }">¥{{ row.platformFee.toLocaleString() }}</template>
          <template #marketingCost="{ row }">¥{{ row.marketingCost.toLocaleString() }}</template>
          <template #materialCost="{ row }">¥{{ row.materialCost.toLocaleString() }}</template>
          <template #laborCost="{ row }">¥{{ row.laborCost.toLocaleString() }}</template>
          <template #depreciation="{ row }">¥{{ row.depreciation.toLocaleString() }}</template>
          <template #operatingCost="{ row }">¥{{ row.operatingCost.toLocaleString() }}</template>
          <template #operatingProfit="{ row }">
            <span :style="{ color: row.operatingProfit >= 0 ? '#00A870' : '#D54941', fontWeight: 600 }">¥{{ row.operatingProfit.toLocaleString() }}</span>
          </template>
          <template #subsidy="{ row }">¥{{ (row.subsidy || 0).toLocaleString() }}</template>
          <template #netProfit="{ row }">
            <span :style="{ color: row.netProfit >= 0 ? '#00A870' : '#D54941', fontWeight: 600 }">¥{{ row.netProfit.toLocaleString() }}</span>
          </template>
        </t-table>
        <t-divider />
        <div class="summary" v-if="reportData.length">
          <div class="summary-row">
            <span>集团营业收入合计</span>
            <span class="summary-val" style="color:#0052D9">¥{{ totalGroupRevenue.toLocaleString() }}</span>
          </div>
          <div class="summary-row">
            <span>集团营业利润合计</span>
            <span class="summary-val" :style="{color:totalGroupOperatingProfit>=0?'#00A870':'#D54941'}">¥{{ totalGroupOperatingProfit.toLocaleString() }}</span>
          </div>
          <div class="summary-row">
            <span>集团净利润合计</span>
            <span class="summary-val" style="font-size:20px" :style="{color:totalGroupProfit>=0?'#00A870':'#D54941'}">¥{{ totalGroupProfit.toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </t-dialog>

    <!-- 房间挂账汇总 -->
    <t-card :bordered="true" style="margin-top:20px" title="房间挂账汇总">
      <template #subtitle>
        <t-tag variant="light" theme="warning">{{ roomBills.filter(b => b.settledAt === null).length }}笔未结算</t-tag>
      </template>
      <t-table :data="roomBills" :columns="roomBillColumns" row-key="billId" size="small" hover stripe>
        <template #status="{ row }">
          <t-tag :theme="row.settledAt ? 'success' : 'warning'" size="small" variant="light">
            {{ row.settledAt ? '已结算' : '未结算' }}
          </t-tag>
        </template>
        <template #actions="{ row }">
          <t-button v-if="!row.settledAt" size="small" variant="text" theme="success" @click="settleRoomBill(row)">标记结算</t-button>
          <span v-else style="color:#999;font-size:12px">{{ row.settledAt }}</span>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import finance from '@mock/finance.json'
import bills from '@mock/bills.json'

const glDate = ref('')
const glStatus = ref('')
const reportVisible = ref(false)
const currentReport = ref<any>(null)

const settlements = finance.monthlySettlements
const glEntries = finance.glEntries
const monthlyReport = finance.monthlyReport
const roomBills = ref(bills.bills)

const reportData = computed(() => {
  return monthlyReport.map(r => ({
    ...r,
    operatingProfit: r.revenue - r.platformFee - r.marketingCost - r.materialCost - r.laborCost - r.depreciation - r.operatingCost,
    netProfit: r.revenue - r.platformFee - r.marketingCost - r.materialCost - r.laborCost - r.depreciation - r.operatingCost + r.subsidy,
  }))
})

const totalGroupRevenue = computed(() => reportData.value.reduce((s, r) => s + r.revenue, 0))
const totalGroupOperatingProfit = computed(() => reportData.value.reduce((s, r) => s + r.operatingProfit, 0))
const totalGroupProfit = computed(() => reportData.value.reduce((s, r) => s + r.netProfit, 0))

const settlementStats = computed(() => {
  const last = settlements[0]
  return [
    { label: '最新月结营收', value: '¥' + (last?.revenue || 0).toLocaleString(), color: '#00A870' },
    { label: '最新月结利润', value: '¥' + (last?.profit || 0).toLocaleString(), color: '#0052D9' },
    { label: '未过账凭证', value: '0笔', color: '#00A870' },
    { label: '差异工单', value: '3笔待处理', color: '#E37318' },
  ]
})

const filteredGlEntries = computed(() => {
  let list = glEntries
  if (glDate.value) list = list.filter(e => e.date === glDate.value)
  if (glStatus.value) list = list.filter(e => e.status === glStatus.value)
  return list
})

function showReport(row: any) { currentReport.value = row; reportVisible.value = true }
function runSettlement(row: any) { row.status = '已月结'; row.revenue = 128600; row.expense = 89200; row.profit = 39400; row.generatedAt = new Date().toISOString().slice(0, 10) }

const settlementColumns = [
  { colKey: 'period', title: '结算周期', width: 160 },
  { colKey: 'revenue', title: '收入合计', width: 120 },
  { colKey: 'expense', title: '支出合计', width: 120 },
  { colKey: 'profit', title: '利润', width: 120 },
  { colKey: 'generatedAt', title: '月结日期', width: 100 },
  { colKey: 'status', title: '状态', width: 90 },
  { colKey: 'actions', title: '操作', width: 160 },
]

const glColumns = [
  { colKey: 'entryId', title: '凭证号', width: 160 },
  { colKey: 'date', title: '日期', width: 100 },
  { colKey: 'desc', title: '摘要', ellipsis: true },
  { colKey: 'account', title: '科目', width: 200 },
  { colKey: 'debit', title: '借方', width: 100 },
  { colKey: 'credit', title: '贷方', width: 100 },
  { colKey: 'status', title: '状态', width: 80 },
]

const reportColumns = [
  { colKey: 'storeName', title: '门店', width: 70 },
  { colKey: 'revenue', title: '营业收入', width: 90 },
  { colKey: 'platformFee', title: '平台费', width: 80 },
  { colKey: 'marketingCost', title: '营销费', width: 80 },
  { colKey: 'materialCost', title: '物料成本', width: 80 },
  { colKey: 'laborCost', title: '人工成本', width: 80 },
  { colKey: 'depreciation', title: '折旧', width: 80 },
  { colKey: 'operatingCost', title: '运营费', width: 80 },
  { colKey: 'operatingProfit', title: '营业利润', width: 90 },
  { colKey: 'subsidy', title: '补贴', width: 80 },
  { colKey: 'netProfit', title: '净利润', width: 90 },
]

const roomBillColumns = [
  { colKey: 'roomName', title: '房间', width: 100 },
  { colKey: 'period', title: '周期', width: 90 },
  { colKey: 'totalAmount', title: '挂账总额', width: 100 },
  { colKey: 'roomFee', title: '房费', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 120 },
]

function settleRoomBill(row: any) {
  row.settledAt = new Date().toLocaleString('zh-CN')
}
</script>

<style scoped>
.summary { padding: 12px; background: #f9f9f9; border-radius: 6px; margin-top: 8px; }
.summary-row { display: flex; justify-content: space-between; font-size: 15px; font-weight: 600; }
.summary-val { font-size: 18px; }
</style>
