<template>
  <div>
    <h2 class="page-header">保洁员考核与薪资管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in cleanerStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true" style="margin-bottom:20px">
      <t-tabs v-model="cleanerTab" :list="cleanerTabs" style="margin-bottom:16px" />
      <t-table :data="cleanerPayrollData" :columns="payColumns" row-key="cpId" hover stripe>
        <template #basePay="{ row }">¥{{ row.basePay }}</template>
        <template #bonus="{ row }"><span v-if="row.bonus" style="color:#00A870">+¥{{ row.bonus }}</span><span v-else>—</span></template>
        <template #penalty="{ row }"><span v-if="row.penalty" style="color:#D54941">-¥{{ row.penalty }}</span><span v-else>—</span></template>
        <template #netPay="{ row }">¥{{ row.netPay }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已发放' ? 'success' : 'warning'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
      </t-table>
    </t-card>

    <!-- Cleaner Quality Assessment -->
    <t-card title="保洁质量考核" :bordered="true">
      <t-table :data="cleanerQualityData" :columns="qualityColumns" row-key="employeeId" hover stripe>
        <template #avgResponse="{ row }">{{ row.avgResponse }}分钟</template>
        <template #quality="{ row }">
          <t-rate :value="row.quality" disabled size="12px" />
        </template>
        <template #completionRate="{ row }">{{ (row.completionRate * 100).toFixed(0) }}%</template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import hr from '@mock/hr.json'

const cleanerTab = ref('all')

const cleanerTabs = [
  { value: 'all', label: '全部' },
  { value: '已发放', label: '已发放' },
  { value: '待发放', label: '待发放' },
]

const cleanerPayrollData = hr.cleanerPayroll
const externalPersonnel = hr.externalPersonnel

const cleanerStats = computed(() => {
  const totalPay = cleanerPayrollData.reduce((s: number, r: any) => s + r.netPay, 0)
  const totalTasks = cleanerPayrollData.reduce((s: number, r: any) => s + r.totalTasks, 0)
  return [
    { label: '保洁员总数', value: externalPersonnel.length, color: '#0052D9' },
    { label: '本月总薪酬', value: '¥' + totalPay, color: '#D54941' },
    { label: '完成保洁任务', value: totalTasks + '单', color: '#00A870' },
    { label: '平均响应', value: '12分钟', color: '#E37318' },
  ]
})

const cleanerQualityData = reactive([
  { employeeId: 'EP001', name: '刘阿姨', totalTasks: 42, avgResponse: 8, quality: 4.5, faultReports: 2, completionRate: 0.98 },
  { employeeId: 'EP002', name: '赵阿姨', totalTasks: 38, avgResponse: 15, quality: 3.5, faultReports: 1, completionRate: 0.90 },
])

const payColumns = [
  { colKey: 'name', title: '姓名', width: 90 },
  { colKey: 'period', title: '周期', width: 100 },
  { colKey: 'totalTasks', title: '完成任务', width: 90 },
  { colKey: 'unitPrice', title: '单价', width: 60 },
  { colKey: 'basePay', title: '基础薪酬', width: 90 },
  { colKey: 'bonus', title: '奖励', width: 80 },
  { colKey: 'penalty', title: '扣减', width: 80 },
  { colKey: 'netPay', title: '实发', width: 90 },
  { colKey: 'status', title: '状态', width: 80 },
]

const qualityColumns = [
  { colKey: 'name', title: '姓名', width: 90 },
  { colKey: 'totalTasks', title: '任务数', width: 70 },
  { colKey: 'avgResponse', title: '平均响应', width: 90 },
  { colKey: 'quality', title: '完成质量', width: 120 },
  { colKey: 'faultReports', title: '故障上报', width: 80 },
  { colKey: 'completionRate', title: '完成率', width: 80 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
</style>
