<template>
  <div>
    <h2 class="page-header">薪资核算</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3">
        <t-select v-model="payrollPeriod" placeholder="选择薪资周期">
          <t-option value="2026年4月" label="2026年4月" />
          <t-option value="2026年3月" label="2026年3月" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-button theme="primary" @click="calcPayroll">计算薪资</t-button>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in payrollStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" style="margin-bottom:20px">
      <t-table :data="currentPayroll" :columns="payrollColumns" row-key="employeeId" hover stripe>
        <template #grossPay="{ row }">¥{{ row.grossPay.toLocaleString() }}</template>
        <template #netPay="{ row }">¥{{ row.netPay.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已发放' ? 'success' : 'warning'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-button size="small" variant="text" theme="primary" @click="viewPayroll(row)">薪资条</t-button>
        </template>
      </t-table>
    </t-card>

    <!-- Salary Grade Table -->
    <t-card title="薪资等级体系" :bordered="true">
      <t-table :data="salaryGrades" :columns="gradeColumns" row-key="grade" hover stripe size="small">
        <template #minSalary="{ row }">¥{{ row.minSalary.toLocaleString() }}</template>
        <template #midSalary="{ row }">¥{{ row.midSalary.toLocaleString() }}</template>
        <template #maxSalary="{ row }">¥{{ row.maxSalary.toLocaleString() }}</template>
      </t-table>
    </t-card>

    <t-dialog v-model:visible="payrollDetailVisible" header="薪资条" width="480px" :footer="false">
      <div v-if="payrollItem" class="payroll-slip">
        <div class="slip-header"><h3>{{ payrollItem.name }}</h3><span>{{ payrollItem.period }}</span></div>
        <t-divider />
        <div class="slip-section">
          <div class="slip-row"><span>基本工资</span><span>¥{{ payrollItem.baseSalary }}</span></div>
          <div class="slip-row"><span>岗位津贴</span><span>¥{{ payrollItem.allowance }}</span></div>
          <div class="slip-row"><span>加班费</span><span>¥{{ payrollItem.overtimePay }}</span></div>
          <div class="slip-row"><span>绩效工资</span><span>¥{{ payrollItem.performancePay }}</span></div>
          <t-divider />
          <div class="slip-row total"><span>应发合计</span><span>¥{{ payrollItem.grossPay.toLocaleString() }}</span></div>
          <div class="slip-row"><span>社保扣缴</span><span>-¥{{ payrollItem.socialSecurity }}</span></div>
          <div class="slip-row"><span>公积金扣缴</span><span>-¥{{ payrollItem.housingFund }}</span></div>
          <div class="slip-row"><span>个税</span><span>-¥{{ payrollItem.tax }}</span></div>
          <t-divider />
          <div class="slip-row net"><span>实发金额</span><span>¥{{ payrollItem.netPay.toLocaleString() }}</span></div>
        </div>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import hr from '@mock/hr.json'

const payrollPeriod = ref('2026年4月')
const payrollDetailVisible = ref(false)
const payrollItem = ref<any>(null)

const payrollRecords = hr.payrollRecords
const salaryGrades = hr.salaryGrades

const currentPayroll = computed(() => payrollRecords)

const payrollStats = computed(() => {
  const records = currentPayroll.value
  return [
    { label: '应发合计', value: '¥' + records.reduce((s: number, r: any) => s + r.grossPay, 0).toLocaleString(), color: '#D54941' },
    { label: '实发合计', value: '¥' + records.reduce((s: number, r: any) => s + r.netPay, 0).toLocaleString(), color: '#0052D9' },
    { label: '社保合计', value: '¥' + records.reduce((s: number, r: any) => s + r.socialSecurity, 0).toLocaleString(), color: '#E37318' },
    { label: '个税合计', value: '¥' + records.reduce((s: number, r: any) => s + r.tax, 0).toLocaleString(), color: '#999' },
  ]
})

function calcPayroll() { /* auto computed */ }
function viewPayroll(r: any) { payrollItem.value = r; payrollDetailVisible.value = true }

const payrollColumns = [
  { colKey: 'name', title: '姓名', width: 90 },
  { colKey: 'baseSalary', title: '基本工资', width: 90 },
  { colKey: 'allowance', title: '津贴', width: 70 },
  { colKey: 'grossPay', title: '应发合计', width: 100 },
  { colKey: 'socialSecurity', title: '社保', width: 70 },
  { colKey: 'tax', title: '个税', width: 70 },
  { colKey: 'netPay', title: '实发', width: 100 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 80 },
]

const gradeColumns = [
  { colKey: 'grade', title: '等级', width: 80 },
  { colKey: 'label', title: '名称', width: 120 },
  { colKey: 'minSalary', title: '下限', width: 100 },
  { colKey: 'midSalary', title: '中位值', width: 100 },
  { colKey: 'maxSalary', title: '上限', width: 100 },
]
</script>

<style scoped>
.payroll-slip { padding: 8px 0; }
.slip-header { display: flex; justify-content: space-between; align-items: center; }
.slip-header h3 { margin: 0; font-size: 16px; }
.slip-header span { color: #999; font-size: 13px; }
.slip-section { padding: 4px 0; }
.slip-row { display: flex; justify-content: space-between; padding: 6px 0; font-size: 13px; color: #666; }
.slip-row.total { font-weight: 600; color: #333; font-size: 14px; }
.slip-row.net { font-weight: 700; color: #0052D9; font-size: 16px; }
</style>
