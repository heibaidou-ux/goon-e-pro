<template>
  <div>
    <h2 class="page-header">考勤管理</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-date-picker v-model="attendancePeriod" style="width:100%" />
      </t-col>
      <t-col :span="2">
        <t-select v-model="attendanceStore" placeholder="选择门店" clearable>
          <t-option value="盈隆店" label="盈隆店" />
          <t-option value="盈丰店" label="盈丰店" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-button @click="refresh">查询</t-button>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="6">
        <t-card title="月考勤汇总" :bordered="true">
          <t-table :data="attendanceData" :columns="attendanceColumns" row-key="recordId" hover stripe>
            <template #lateCount="{ row }">
              <t-tag v-if="row.lateCount > 0" theme="warning" size="small" variant="light">{{ row.lateCount }}次</t-tag>
              <span v-else style="color:#00A870">0</span>
            </template>
            <template #absentDays="{ row }">
              <t-tag v-if="row.absentDays > 0" theme="danger" size="small" variant="light">{{ row.absentDays }}天</t-tag>
              <span v-else style="color:#00A870">0</span>
            </template>
          </t-table>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="请假审批" :bordered="true">
          <div v-for="l in leaveRequests" :key="l.id" class="leave-item">
            <div class="leave-header"><span class="leave-name">{{ l.name }}</span><t-tag :theme="l.status==='待审批'?'warning':'success'" size="small" variant="light">{{ l.status }}</t-tag></div>
            <div class="leave-type">{{ l.type }} · {{ l.date }}</div>
            <div class="leave-actions" v-if="l.status === '待审批'">
              <t-button v-if="hasPermission('BTN_APPROVE')" size="small" theme="success" variant="text" @click="l.status='已通过'">通过</t-button>
              <t-button v-if="hasPermission('BTN_REJECT')" size="small" theme="danger" variant="text" @click="l.status='已驳回'">驳回</t-button>
            </div>
          </div>
          <div v-if="!leaveRequests.length" style="text-align:center;padding:20px;color:#999">暂无请假申请</div>
        </t-card>
      </t-col>
      <t-col :span="3">
        <t-card title="打卡记录" :bordered="true">
          <div class="clock-card">
            <div class="clock-time">今日打卡</div>
            <div class="clock-count"><span class="clocked">{{ clockedCount }}</span><span class="clock-total">/{{ totalEmployees }}</span></div>
            <div class="clock-detail">
              <div>已打卡：<strong>{{ clockedCount }}</strong> 人</div>
              <div>未打卡：<strong style="color:#D54941">{{ totalEmployees - clockedCount }}</strong> 人</div>
            </div>
          </div>
        </t-card>
      </t-col>
    </t-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { hasPermission } from '@/utils/permission'
import hr from '@mock/hr.json'

const attendancePeriod = ref('2026-04')
const attendanceStore = ref('')
const clockedCount = ref(3)

const attendanceData = hr.attendance
const totalEmployees = computed(() => hr.employees.length)

const leaveRequests = ref([
  { id: 'LV001', name: '小林', type: '病假', date: '2026-04-15', status: '待审批' },
  { id: 'LV002', name: '小陈', type: '事假', date: '2026-04-22', status: '待审批' },
  { id: 'LV003', name: '阿强', type: '年假', date: '2026-05-06', status: '已通过' },
])

function refresh() { /* trigger recompute */ }

const attendanceColumns = [
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'workDays', title: '出勤天数', width: 90 },
  { colKey: 'absentDays', title: '缺勤', width: 70 },
  { colKey: 'lateCount', title: '迟到', width: 70 },
  { colKey: 'earlyLeaveCount', title: '早退', width: 70 },
  { colKey: 'otHours', title: '加班时长', width: 80 },
]
</script>

<style scoped>
.leave-item { padding: 10px 0; border-bottom: 1px solid #f5f5f5; }
.leave-item:last-child { border-bottom: none; }
.leave-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
.leave-name { font-weight: 600; font-size: 13px; }
.leave-type { font-size: 12px; color: #999; }
.leave-actions { margin-top: 6px; display: flex; gap: 4px; }
.clock-card { text-align: center; padding: 12px 0; }
.clock-time { font-size: 13px; color: #999; margin-bottom: 8px; }
.clock-count { margin-bottom: 12px; }
.clock-count .clocked { font-size: 36px; font-weight: 700; color: #0052D9; }
.clock-count .clock-total { font-size: 16px; color: #999; }
.clock-detail { font-size: 13px; color: #666; }
.clock-detail div { padding: 4px 0; }
</style>
