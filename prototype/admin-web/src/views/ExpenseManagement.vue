<template>
  <div>
    <h2 class="page-header">支出管理</h2>

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading />
      <span style="color:#999">加载中...</span>
    </t-space>

    <template v-else>
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="2" v-for="s in expenseStats" :key="s.label">
          <t-card :bordered="true">
            <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
          </t-card>
        </t-col>
      </t-row>

      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="2">
          <t-select v-model="filterCategory" placeholder="支出分类" clearable @change="loadExpenses">
            <t-option value="营业成本" label="营业成本" />
            <t-option value="管理费用" label="管理费用" />
            <t-option value="人力成本" label="人力成本" />
            <t-option value="场地成本" label="场地成本" />
          </t-select>
        </t-col>
        <t-col :span="6" style="text-align:right">
          <t-button theme="primary" @click="showAddDialog = true">+ 记一笔支出</t-button>
        </t-col>
      </t-row>

      <t-alert v-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

      <t-card :bordered="true">
        <t-tabs v-model="expenseTab" :list="expenseTabs" style="margin-bottom:16px" @change="loadExpenses" />
        <t-table :data="expenseList" :columns="expenseColumns" row-key="expenseId" hover stripe>
          <template #category="{ row }">
            <t-tag variant="light" size="small">{{ row.category }}</t-tag>
          </template>
          <template #amount="{ row }">¥{{ (row.amount || 0).toLocaleString() }}</template>
          <template #status="{ row }">
            <t-tag :theme="row.status === 'Paid' ? 'success' : row.status === 'Approved' ? 'warning' : 'default'" size="small" variant="light">
              {{ row.status === 'Paid' ? '已支付' : row.status === 'Approved' ? '待支付' : row.status === 'Draft' ? '待审批' : row.status }}
            </t-tag>
          </template>
          <template #actions="{ row }">
            <t-space size="small">
              <t-button v-if="row.status === 'Draft'" size="small" theme="success" variant="text" @click="updateStatus(row, 'Approved')">审批通过</t-button>
              <t-button v-if="row.status === 'Approved'" size="small" theme="primary" variant="text" @click="updateStatus(row, 'Paid')">确认付款</t-button>
              <t-button size="small" variant="text" theme="primary" @click="selectedExpense=row;detailVisible=true">详情</t-button>
            </t-space>
          </template>
        </t-table>
        <t-empty v-if="expenseList.length === 0" description="暂无支出记录" style="padding:40px" />
      </t-card>
    </template>

    <!-- Detail Drawer -->
    <t-drawer v-model:visible="detailVisible" :header="`支出单 ${selectedExpense?.expenseId}`" size="400px" :footer="false">
      <div v-if="selectedExpense" class="detail-sections">
        <div class="detail-section">
          <div class="detail-row"><span>分类</span><t-tag variant="light" size="small">{{ selectedExpense.category }}</t-tag></div>
          <div class="detail-row"><span>门店</span><span>{{ selectedExpense.storeName || '—' }}</span></div>
          <div class="detail-row"><span>金额</span><span class="price">¥{{ (selectedExpense.amount || 0).toLocaleString() }}</span></div>
          <div class="detail-row"><span>说明</span><span>{{ selectedExpense.description || '—' }}</span></div>
          <div class="detail-row"><span>状态</span><t-tag size="small">{{ selectedExpense.status }}</t-tag></div>
          <div class="detail-row"><span>发生日期</span><span>{{ selectedExpense.incurredDate || '—' }}</span></div>
          <div class="detail-row"><span>创建时间</span><span>{{ selectedExpense.createdAt || '—' }}</span></div>
        </div>
      </div>
    </t-drawer>

    <!-- Add Dialog -->
    <t-dialog v-model:visible="showAddDialog" header="记一笔支出" width="480px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="支出分类">
          <t-select v-model="addForm.category">
            <t-option value="营业成本" label="营业成本" />
            <t-option value="管理费用" label="管理费用" />
            <t-option value="人力成本" label="人力成本" />
            <t-option value="场地成本" label="场地成本" />
          </t-select>
        </t-form-item>
        <t-form-item label="金额">
          <t-input v-model.number="addForm.amount" type="number" prefix="¥" placeholder="0.00" />
        </t-form-item>
        <t-form-item label="说明">
          <t-input v-model="addForm.description" placeholder="支出用途说明" />
        </t-form-item>
        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="showAddDialog = false">取消</t-button>
          <t-button theme="primary" @click="saveExpense" style="margin-left:8px" :loading="saving">保存</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { financeApi } from '../services/api'
import { authApi } from '../services/api'

const expenseTab = ref('all')
const filterCategory = ref('')
const detailVisible = ref(false)
const showAddDialog = ref(false)
const selectedExpense = ref<any>(null)
const loading = ref(false)
const loadError = ref('')
const saving = ref(false)

const expenseList = ref<any[]>([])

const addForm = ref({ category: '营业成本', amount: 0, description: '' })

const expenseTabs = [
  { value: 'all', label: '全部' },
  { value: 'Draft', label: '待审批' },
  { value: 'Approved', label: '待支付' },
  { value: 'Paid', label: '已支付' },
]

// ── Stats ──

const expenseStats = computed(() => {
  const now = new Date()
  const thisMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  const monthly = expenseList.value.filter(e => (e.incurredDate || '').startsWith(thisMonth))
  const monthlyTotal = monthly.reduce((s, e) => s + (e.amount || 0), 0)
  return [
    { label: '本月支出总额', value: '¥' + monthlyTotal.toLocaleString(), color: '#D54941' },
    { label: '待审批', value: expenseList.value.filter(e => e.status === 'Draft').length + '笔', color: '#E37318' },
    { label: '待支付', value: expenseList.value.filter(e => e.status === 'Approved').length + '笔', color: '#0052D9' },
    { label: '本月已支付', value: '¥' + monthly.filter(e => e.status === 'Paid').reduce((s, e) => s + (e.amount || 0), 0).toLocaleString(), color: '#00A870' },
  ]
})

// ── Load ──

async function loadExpenses() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await financeApi.listExpenses({
      category: filterCategory.value || undefined,
      status: expenseTab.value === 'all' ? undefined : expenseTab.value,
    })
    expenseList.value = result.items || []
  } catch (e: any) {
    loadError.value = '加载支出数据失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

// ── Actions ──

async function updateStatus(row: any, newStatus: string) {
  try {
    const updated = await financeApi.updateExpense(row.expenseId, { status: newStatus })
    Object.assign(row, updated)
    await loadExpenses()
  } catch (e: any) {
    console.error('更新状态失败:', e)
  }
}

async function saveExpense() {
  if (!addForm.value.amount) return
  saving.value = true
  try {
    const userInfo = authApi.isLoggedIn() ? JSON.parse(localStorage.getItem('erp_user') || '{}') : {}
    await financeApi.createExpense({
      storeId: 'ST001',
      category: addForm.value.category,
      amount: addForm.value.amount,
      description: addForm.value.description,
      incurredDate: new Date().toISOString().slice(0, 10),
      applicantId: userInfo.id || 'admin',
    })
    showAddDialog.value = false
    addForm.value = { category: '营业成本', amount: 0, description: '' }
    await loadExpenses()
  } catch (e: any) {
    console.error('保存支出失败:', e)
  } finally {
    saving.value = false
  }
}

// ── Init ──

onMounted(loadExpenses)
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #D54941; font-weight: 600; }
</style>
