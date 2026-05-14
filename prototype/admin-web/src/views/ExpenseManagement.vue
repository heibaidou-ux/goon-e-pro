<template>
  <div>
    <h2 class="page-header">支出管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in expenseStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-tabs v-model="expenseTab" :list="expenseTabs" style="margin-bottom:16px" />
      <t-table :data="filteredExpenses" :columns="expenseColumns" row-key="id" hover stripe>
        <template #type="{ row }">
          <t-tag :theme="row.type === '请款' ? 'warning' : 'primary'" variant="light" size="small">{{ row.type }}</t-tag>
        </template>
        <template #amount="{ row }">¥{{ row.amount.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已支付' ? 'success' : row.status === '待支付' ? 'warning' : 'primary'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status === '待审批' && hasPermission('BTN_APPROVE')" size="small" theme="success" variant="text" @click="row.status='待支付'">审批通过</t-button>
            <t-button v-if="row.status === '待支付' && hasPermission('BTN_PAY')" size="small" theme="primary" variant="text" @click="row.status='已支付'">确认付款</t-button>
            <t-button size="small" variant="text" theme="primary" @click="selectedExpense=row;detailVisible=true">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="detailVisible" :header="`${selectedExpense?.type}单 ${selectedExpense?.id}`" size="400px" :footer="false">
      <div v-if="selectedExpense" class="detail-sections">
        <div class="detail-section">
          <div class="detail-row"><span>类型</span><t-tag :theme="selectedExpense.type==='请款'?'warning':'primary'" variant="light" size="small">{{ selectedExpense.type }}</t-tag></div>
          <div class="detail-row"><span>申请人</span><span>{{ selectedExpense.applicant }}</span></div>
          <div class="detail-row"><span>科目</span><span>{{ selectedExpense.account }}</span></div>
          <div class="detail-row"><span>金额</span><span class="price">¥{{ selectedExpense.amount.toLocaleString() }}</span></div>
          <div class="detail-row"><span>用途</span><span>{{ selectedExpense.purpose }}</span></div>
          <div class="detail-row"><span>状态</span><t-tag :theme="selectedExpense.status==='已支付'?'success':'warning'" size="small">{{ selectedExpense.status }}</t-tag></div>
          <div class="detail-row"><span>创建日期</span><span>{{ selectedExpense.createdAt }}</span></div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { hasPermission } from '@/utils/permission'

const expenseTab = ref('all')
const detailVisible = ref(false)
const selectedExpense = ref<any>(null)

const expenseTabs = [
  { value: 'all', label: '全部' },
  { value: '待审批', label: '待审批' },
  { value: '待支付', label: '待支付' },
  { value: '已支付', label: '已支付' },
]

const allExpenses = [
  { id: 'EXP202605001', type: '请款', applicant: '张店长', amount: 3500, account: '营业成本-茶叶采购', purpose: '采购明前龙井30罐', status: '待审批', createdAt: '2026-05-08' },
  { id: 'EXP202605002', type: '报销', applicant: '小林', amount: 268, account: '管理费用-办公费', purpose: '购买办公用品（笔、笔记本、墨盒）', status: '待审批', createdAt: '2026-05-07' },
  { id: 'EXP202605003', type: '请款', applicant: '阿强', amount: 1200, account: '营业成本-水电费', purpose: '5月电费缴纳', status: '待支付', createdAt: '2026-05-06' },
  { id: 'EXP202605004', type: '报销', applicant: '王运营', amount: 880, account: '管理费用-办公费', purpose: '打印店招设计材料费', status: '已支付', createdAt: '2026-05-05' },
  { id: 'EXP202605005', type: '请款', applicant: '张店长', amount: 6000, account: '营业成本-场地成本', purpose: '5月门店租金', status: '待支付', createdAt: '2026-05-01' },
  { id: 'EXP202604001', type: '请款', applicant: '张店长', amount: 4500, account: '营业成本-茶叶采购', purpose: '铁观音、金骏眉补货', status: '已支付', createdAt: '2026-04-20' },
  { id: 'EXP202604002', type: '报销', applicant: '李财务', amount: 150, account: '管理费用-办公费', purpose: '银行回单打印费', status: '已支付', createdAt: '2026-04-15' },
]

const expenseStats = computed(() => [
  { label: '本月支出总额', value: '¥' + allExpenses.filter(e => e.createdAt.startsWith('2026-05')).reduce((s, e) => s + e.amount, 0).toLocaleString(), color: '#D54941' },
  { label: '待审批', value: allExpenses.filter(e => e.status === '待审批').length + '笔', color: '#E37318' },
  { label: '待支付', value: allExpenses.filter(e => e.status === '待支付').length + '笔', color: '#0052D9' },
  { label: '本月已支付', value: '¥' + allExpenses.filter(e => e.status === '已支付' && e.createdAt.startsWith('2026-05')).reduce((s, e) => s + e.amount, 0).toLocaleString(), color: '#00A870' },
])

const filteredExpenses = computed(() => {
  if (expenseTab.value === 'all') return allExpenses
  return allExpenses.filter(e => e.status === expenseTab.value)
})

const expenseColumns = [
  { colKey: 'id', title: '单据编号', width: 150 },
  { colKey: 'type', title: '类型', width: 60 },
  { colKey: 'applicant', title: '申请人', width: 80 },
  { colKey: 'amount', title: '金额', width: 100 },
  { colKey: 'account', title: '科目', width: 160, ellipsis: true },
  { colKey: 'purpose', title: '用途', ellipsis: true },
  { colKey: 'createdAt', title: '日期', width: 100 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 180 },
]
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #D54941; font-weight: 600; }
</style>
