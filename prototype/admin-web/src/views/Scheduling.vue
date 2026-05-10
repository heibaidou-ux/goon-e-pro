<template>
  <div>
    <h2 class="page-header">智能排班</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-select v-model="scheduleStore" placeholder="选择门店">
          <t-option value="盈隆店" label="盈隆店" />
          <t-option value="盈丰店" label="盈丰店" />
        </t-select>
      </t-col>
      <t-col :span="3">
        <t-date-picker v-model="scheduleWeek" style="width:100%" />
      </t-col>
      <t-col :span="2">
        <t-button variant="outline" @click="genSchedule">生成建议排班</t-button>
      </t-col>
    </t-row>

    <t-alert v-if="showSuggestion" theme="info" style="margin-bottom:16px">
      <template #message>系统建议：下周预测客流高峰时段为周五~周六14:00-18:00，建议安排2名店员在岗。</template>
    </t-alert>

    <t-card :bordered="true">
      <t-table :data="scheduleData" :columns="scheduleColumns" row-key="employeeId" hover stripe>
        <template #mon="{ row }"><t-tag :theme="row.mon ? 'success' : 'default'" size="small" variant="light">{{ row.mon || '休' }}</t-tag></template>
        <template #tue="{ row }"><t-tag :theme="row.tue ? 'success' : 'default'" size="small" variant="light">{{ row.tue || '休' }}</t-tag></template>
        <template #wed="{ row }"><t-tag :theme="row.wed ? 'success' : 'default'" size="small" variant="light">{{ row.wed || '休' }}</t-tag></template>
        <template #thu="{ row }"><t-tag :theme="row.thu ? 'success' : 'default'" size="small" variant="light">{{ row.thu || '休' }}</t-tag></template>
        <template #fri="{ row }"><t-tag :theme="row.fri ? 'success' : 'default'" size="small" variant="light">{{ row.fri || '休' }}</t-tag></template>
        <template #sat="{ row }"><t-tag :theme="row.sat ? 'success' : 'default'" size="small" variant="light">{{ row.sat || '休' }}</t-tag></template>
        <template #sun="{ row }"><t-tag :theme="row.sun ? 'success' : 'default'" size="small" variant="light">{{ row.sun || '休' }}</t-tag></template>
        <template #actions="{ row }">
          <t-button size="small" variant="text" theme="primary" @click="editSchedule(row)">调整</t-button>
        </template>
      </t-table>
    </t-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const scheduleStore = ref('盈隆店')
const scheduleWeek = ref('2026-05-11')
const showSuggestion = ref(false)

function genSchedule() { showSuggestion.value = true }

function editSchedule(row: any) { /* editable in production */ }

const scheduleData = [
  { employeeId: 'E001', name: '张店长', position: '店长', mon: '09:00-18:00', tue: '09:00-18:00', wed: '09:00-18:00', thu: '09:00-18:00', fri: '09:00-18:00', sat: '休', sun: '休' },
  { employeeId: 'E002', name: '小林', position: '店员', mon: '14:00-22:00', tue: '14:00-22:00', wed: '休', thu: '14:00-22:00', fri: '14:00-22:00', sat: '10:00-22:00', sun: '10:00-18:00' },
  { employeeId: 'E003', name: '小陈', position: '店员', mon: '09:00-18:00', tue: '09:00-18:00', wed: '09:00-18:00', thu: '休', fri: '09:00-18:00', sat: '09:00-18:00', sun: '休' },
  { employeeId: 'E004', name: '阿强', position: '技术员', mon: '09:00-18:00', tue: '休', wed: '09:00-18:00', thu: '09:00-18:00', fri: '09:00-18:00', sat: '休', sun: '休' },
]

const scheduleColumns = [
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'position', title: '岗位', width: 70 },
  { colKey: 'mon', title: '周一', width: 110 },
  { colKey: 'tue', title: '周二', width: 110 },
  { colKey: 'wed', title: '周三', width: 110 },
  { colKey: 'thu', title: '周四', width: 110 },
  { colKey: 'fri', title: '周五', width: 110 },
  { colKey: 'sat', title: '周六', width: 110 },
  { colKey: 'sun', title: '周日', width: 110 },
  { colKey: 'actions', title: '操作', width: 70 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
</style>
