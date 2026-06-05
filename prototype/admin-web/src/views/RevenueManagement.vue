<template>
  <div>
    <h2 class="page-header">收入管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-date-range-picker v-model="dateRange" style="width:100%" separator="至" @change="loadRevenue" />
      </t-col>
      <t-col :span="2">
        <t-select v-model="selectedStore" placeholder="选择门店" clearable @change="loadRevenue">
          <t-option v-for="s in stores" :key="s.storeId" :value="s.storeId" :label="s.name" />
        </t-select>
      </t-col>
      <t-col :span="4" style="text-align:right">
        <t-button theme="primary" @click="showAddDialog = true">+ 手动记一笔</t-button>
      </t-col>
    </t-row>

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading />
      <span style="color:#999">加载中...</span>
    </t-space>

    <!-- Error -->
    <t-alert v-else-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

    <template v-else>
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="6">
          <t-card title="日营收趋势" :bordered="true">
            <div class="chart-placeholder" v-if="revenueTrend.length">
              <div v-for="(d, i) in revenueTrend" :key="i" class="bar-wrapper" :style="{ height: d.amount / maxAmount * 160 + 'px' }">
                <div class="bar" :style="{ background: d.color }"></div>
                <div class="bar-label">{{ d.day.slice(5) }}</div>
              </div>
            </div>
            <t-empty v-else description="暂无趋势数据" />
          </t-card>
        </t-col>
        <t-col :span="3">
          <t-card title="收入方式分布" :bordered="true">
            <div v-for="item in paymentSummary" :key="item.name" class="account-row">
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
            <div class="summary-item"><span>总收入</span><span class="summary-val">¥{{ totalAmount.toLocaleString() }}</span></div>
            <div class="summary-item"><span>笔数</span><span class="summary-val">{{ totalCount }}</span></div>
            <div class="summary-item"><span>线上</span><span class="summary-val">¥{{ onlineAmount.toLocaleString() }}</span></div>
            <div class="summary-item"><span>线下</span><span class="summary-val green">¥{{ offlineAmount.toLocaleString() }}</span></div>
          </t-card>
        </t-col>
      </t-row>

      <t-card :bordered="true">
        <t-table :data="revenueList" :columns="revenueColumns" row-key="revenueId" hover stripe>
          <template #type="{ row }">
            <t-tag size="small" variant="light">{{ row.type }}</t-tag>
          </template>
          <template #paymentMethod="{ row }">
            <t-tag size="small" variant="outline">{{ row.paymentMethod }}</t-tag>
          </template>
        </t-table>
        <t-empty v-if="revenueList.length === 0" description="暂无收入记录" style="padding:40px" />
      </t-card>
    </template>

    <!-- Add Revenue Dialog -->
    <t-dialog v-model:visible="showAddDialog" header="记一笔收入" width="480px" :footer="false">
      <t-form layout="vertical">
        <t-row :gutter="16">
          <t-col :span="8">
            <t-form-item label="金额">
              <t-input v-model.number="addForm.amount" type="number" prefix="¥" placeholder="0.00" />
            </t-form-item>
          </t-col>
          <t-col :span="4">
            <t-form-item label="支付方式">
              <t-select v-model="addForm.paymentMethod">
                <t-option value="WeChat" label="微信" />
                <t-option value="Alipay" label="支付宝" />
                <t-option value="Cash" label="现金" />
                <t-option value="Card" label="银行卡" />
                <t-option value="Transfer" label="转账" />
              </t-select>
            </t-form-item>
          </t-col>
        </t-row>
        <t-form-item label="收入类型">
          <t-select v-model="addForm.type">
            <t-option value="RoomRental" label="房间租用" />
            <t-option value="ProductSales" label="商品零售" />
            <t-option value="Recharge" label="会员充值" />
            <t-option value="Deposit" label="押金" />
            <t-option value="Other" label="其他" />
          </t-select>
        </t-form-item>
        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="showAddDialog = false">取消</t-button>
          <t-button theme="primary" @click="saveRevenue" style="margin-left:8px" :loading="saving">保存</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { financeApi } from '../services/api'

const dateRange = ref(['', ''])
const selectedStore = ref('')
const loading = ref(false)
const loadError = ref('')
const showAddDialog = ref(false)
const saving = ref(false)

const stores = ref<any[]>([])
const revenueList = ref<any[]>([])
const dailyStats = ref<any[]>([])

const addForm = ref({ amount: 0, paymentMethod: 'WeChat', type: 'RoomRental' })

const barColors = ['#0052D9','#00A870','#E37318','#9C27B0','#D54941','#2D9C9C','#F5A623']

// ── Load ──

async function loadStores() {
  try {
    const { storeApi } = await import('../services/api')
    stores.value = await storeApi.list()
  } catch { /* ignore */ }
}

async function loadRevenue() {
  loading.value = true
  loadError.value = ''
  try {
    const startDate = dateRange.value[0] || undefined
    const endDate = dateRange.value[1] || undefined

    const result = await financeApi.listRevenue({
      storeId: selectedStore.value || undefined,
      startDate,
      endDate,
      page_size: 200,
    })
    revenueList.value = result.items

    const stats = await financeApi.revenueStats({
      storeId: selectedStore.value || undefined,
      days: 30,
    })
    dailyStats.value = stats || []
  } catch (e: any) {
    loadError.value = '加载收入数据失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

// ── Computed ──

const totalAmount = computed(() => revenueList.value.reduce((s, r) => s + (r.amount || 0), 0))
const totalCount = computed(() => revenueList.value.length)
const onlineAmount = computed(() =>
  revenueList.value.filter(r => r.paymentMethod !== 'Cash').reduce((s, r) => s + (r.amount || 0), 0)
)
const offlineAmount = computed(() =>
  revenueList.value.filter(r => r.paymentMethod === 'Cash').reduce((s, r) => s + (r.amount || 0), 0)
)

const revenueTrend = computed(() =>
  (dailyStats.value || []).map((d: any, i: number) => ({
    ...d,
    amount: d.total || 0,
    color: barColors[i % barColors.length],
  }))
)

const maxAmount = computed(() => Math.max(...revenueTrend.value.map(d => d.amount), 1))

const paymentSummary = computed(() => {
  const byMethod: Record<string, number> = {}
  revenueList.value.forEach(r => {
    const m = r.paymentMethod || '其他'
    byMethod[m] = (byMethod[m] || 0) + (r.amount || 0)
  })
  const total = Object.values(byMethod).reduce((s, v) => s + v, 0)
  const colorMap: Record<string, string> = { WeChat: '#07C160', Alipay: '#1677FF', Cash: '#FAAD14', Card: '#0052D9', Transfer: '#9C27B0' }
  return Object.entries(byMethod).map(([name, amount]) => ({
    name, amount, color: colorMap[name] || '#999',
    percent: total > 0 ? Math.round(amount / total * 100) : 0,
  }))
})

const revenueColumns = [
  { colKey: 'receivedAt', title: '日期', width: 160 },
  { colKey: 'storeName', title: '门店', width: 80 },
  { colKey: 'amount', title: '金额', width: 90 },
  { colKey: 'type', title: '类型', width: 100 },
  { colKey: 'paymentMethod', title: '支付方式', width: 90 },
]

// ── Actions ──

async function saveRevenue() {
  if (!addForm.value.amount) return
  saving.value = true
  try {
    await financeApi.createRevenue({
      storeId: selectedStore.value || 'ST001',
      amount: addForm.value.amount,
      paymentMethod: addForm.value.paymentMethod,
      type: addForm.value.type,
    })
    showAddDialog.value = false
    addForm.value = { amount: 0, paymentMethod: 'WeChat', type: 'RoomRental' }
    await loadRevenue()
  } catch (e: any) {
    console.error('保存收入失败:', e)
  } finally {
    saving.value = false
  }
}

// ── Init ──

onMounted(async () => {
  await loadStores()
  await loadRevenue()
})
</script>

<style scoped>
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
