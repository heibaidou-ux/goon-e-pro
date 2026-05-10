<template>
  <div>
    <h2 class="page-header">绩效考核</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-select v-model="perfPeriod" placeholder="选择考核周期">
          <t-option value="2026年4月" label="2026年4月（月）" />
          <t-option value="2026年Q1" label="2026年Q1（季）" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="perfStore" placeholder="选择门店" clearable>
          <t-option value="盈隆店" label="盈隆店" />
          <t-option value="盈丰店" label="盈丰店" />
        </t-select>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-table :data="perfData" :columns="perfColumns" row-key="employeeId" hover stripe>
        <template #autoScore="{ row }">
          <t-rate :value="row.autoScore" disabled size="14px" />
          <span style="font-size:12px;color:#999;margin-left:4px">{{ row.autoScore }}/5</span>
        </template>
        <template #managerScore="{ row }">
          <t-rate v-model="row.managerScore" size="14px" />
          <span style="font-size:12px;color:#999;margin-left:4px">{{ row.managerScore }}/5</span>
        </template>
        <template #finalScore="{ row }">
          <t-tag :theme="row.finalScore >= 4 ? 'success' : row.finalScore >= 3 ? 'warning' : 'danger'" size="small" variant="light">{{ row.finalScore.toFixed(1) }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-button v-if="!row.submitted" size="small" theme="success" variant="text" @click="submitPerf(row)">提交</t-button>
          <span v-else style="color:#00A870;font-size:12px">已提交</span>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

const perfPeriod = ref('2026年4月')
const perfStore = ref('')
const perfData = reactive([
  { employeeId: 'E001', name: '张店长', position: '店长', orders: 86, complaints: 0, praise: 12, autoScore: 4.5, managerScore: 0, finalScore: 4.5, submitted: false },
  { employeeId: 'E002', name: '小林', position: '店员', orders: 52, complaints: 1, praise: 8, autoScore: 4.0, managerScore: 0, finalScore: 4.0, submitted: false },
  { employeeId: 'E003', name: '小陈', position: '店员', orders: 38, complaints: 0, praise: 5, autoScore: 4.2, managerScore: 0, finalScore: 4.2, submitted: false },
  { employeeId: 'E004', name: '阿强', position: '技术员', orders: 0, complaints: 0, praise: 3, autoScore: 4.8, managerScore: 0, finalScore: 4.8, submitted: false },
])

function submitPerf(row: any) {
  row.finalScore = (row.autoScore + row.managerScore) / 2
  row.submitted = true
}

const perfColumns = [
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'position', title: '岗位', width: 70 },
  { colKey: 'orders', title: '成交量', width: 70 },
  { colKey: 'complaints', title: '差评', width: 60 },
  { colKey: 'praise', title: '好评', width: 60 },
  { colKey: 'autoScore', title: '系统评分', width: 140 },
  { colKey: 'managerScore', title: '店长评分', width: 140 },
  { colKey: 'finalScore', title: '综合得分', width: 90 },
  { colKey: 'actions', title: '操作', width: 80 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
</style>
