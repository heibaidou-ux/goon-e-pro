<template>
  <div>
    <h2 class="page-header">股东分红</h2>

    <t-alert message="分红计算基于已确认的月结报告。品牌股东和门店股东分红互不干扰。" theme="info" style="margin-bottom:20px" />

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading />
      <span style="color:#999">加载中...</span>
    </t-space>

    <template v-else>
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
          <template #shareRatio="{ row }">{{ ((row.shareRatio || 0) * 100).toFixed(0) }}%</template>
          <template #amount="{ row }">¥{{ (row.amount || 0).toLocaleString() }}</template>
        </t-table>
        <div v-else style="padding:40px;text-align:center;color:#999">请选择月结周期并点击"计算分红"</div>
      </t-card>

      <t-card title="门店股东分红" :bordered="true">
        <t-table v-if="showBrandDividend" :data="storeDividendList" :columns="storeColumns" row-key="name" hover stripe>
          <template #shareRatio="{ row }">{{ ((row.shareRatio || 0) * 100).toFixed(0) }}%</template>
          <template #amount="{ row }">¥{{ (row.amount || 0).toLocaleString() }}</template>
        </t-table>
        <div v-else style="padding:40px;text-align:center;color:#999">请先计算品牌股东分红</div>
      </t-card>

      <t-card title="分红记录" :bordered="true" style="margin-top:20px">
        <t-table :data="dividendRecords" :columns="recordColumns" row-key="dividendId" hover stripe size="small">
          <template #totalAmount="{ row }">¥{{ (row.totalAmount || row.amount || 0).toLocaleString() }}</template>
          <template #status="{ row }">
            <t-tag :theme="row.status === '已发放' || row.status === 'Paid' ? 'success' : 'default'" size="small" variant="light">
              {{ row.status === 'Paid' ? '已发放' : row.status === 'Pending' ? '待发放' : row.status }}
            </t-tag>
          </template>
        </t-table>
        <t-empty v-if="dividendRecords.length === 0" description="暂无分红记录" style="padding:40px" />
      </t-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { financeApi } from '../services/api'

const loading = ref(false)
const loadError = ref('')

const selectedPeriod = ref('2026年4月')
const showBrandDividend = ref(false)

const dividendRecords = ref<any[]>([])

const brandDividends = [
  { name: '品牌创始人A', shareRatio: 0.40, amount: 40000 },
  { name: '品牌创始人B', shareRatio: 0.30, amount: 30000 },
  { name: '品牌合伙人C', shareRatio: 0.20, amount: 20000 },
  { name: '员工持股平台', shareRatio: 0.10, amount: 10000 },
]

const storeShareholders: Record<string, any[]> = {
  '盈隆店': [
    { name: '门店股东甲', shareRatio: 0.50, amount: 2230 },
    { name: '门店股东乙', shareRatio: 0.30, amount: 1338 },
    { name: '门店合伙人丙', shareRatio: 0.20, amount: 892 },
  ],
}

const brandNetProfit = 100000

const storeDividendList = computed(() => {
  const all: any[] = []
  Object.entries(storeShareholders).forEach(([store, list]) => {
    list.forEach(s => all.push({ ...s, store }))
  })
  return all
})

function calcDividend() { showBrandDividend.value = true }

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

async function loadDividends() {
  try {
    const records = await financeApi.listDividends()
    dividendRecords.value = (records || []).map((r: any) => ({
      dividendId: r.dividendId,
      period: r.monthlySettlementId || '—',
      totalAmount: r.amount || 0,
      amount: r.amount || 0,
      status: r.status,
      paidAt: r.paidAt || (r.createdAt ? r.createdAt.slice(0, 10) : '—'),
    }))
  } catch { /* ignore */ }
}

onMounted(loadDividends)
</script>

<style scoped>
.profit-label { font-size: 14px; color: #666; }
.profit-val { font-size: 16px; font-weight: 700; color: #00A870; }
</style>
