<template>
  <div>
    <h2 class="page-header">智能排班</h2>

    <!-- 统计卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in scheduleStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 控制栏 -->
    <t-card :bordered="true" style="margin-bottom:16px">
      <t-row :gutter="16" align="middle">
        <t-col :span="2">
          <t-select v-model="scheduleStore" placeholder="选择门店">
            <t-option value="盈隆店" label="盈隆店" />
            <t-option value="盈丰店" label="盈丰店" />
            <t-option value="金德店" label="金德店" />
          </t-select>
        </t-col>
        <t-col :span="3">
          <div class="week-nav">
            <t-button variant="text" shape="square" @click="prevWeek">
              <template #icon><t-icon name="chevron-left" /></template>
            </t-button>
            <span class="week-label">{{ currentWeekLabel }}</span>
            <t-button variant="text" shape="square" @click="nextWeek">
              <template #icon><t-icon name="chevron-right" /></template>
            </t-button>
            <t-button size="small" variant="outline" @click="resetWeek" style="margin-left:8px">今天</t-button>
          </div>
        </t-col>
        <t-col :span="3">
          <t-button variant="outline" @click="genSchedule">生成建议排班</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="showSwapDialog = true">换班申请</t-button>
        </t-col>
        <t-col :span="4" style="text-align:right">
          <t-tag variant="light" style="margin-right:8px"><span class="shift-dot shift-morning"></span> 早班 09:00-18:00</t-tag>
          <t-tag variant="light" style="margin-right:8px"><span class="shift-dot shift-afternoon"></span> 中班 14:00-22:00</t-tag>
          <t-tag variant="light"><span class="shift-dot shift-night"></span> 晚班 18:00-23:00</t-tag>
        </t-col>
      </t-row>
    </t-card>

    <!-- AI排班建议 -->
    <t-alert v-if="showSuggestion" theme="info" style="margin-bottom:16px" close>
      <template #message>
        <strong>AI排班建议：</strong>下周预测客流高峰时段为周五~周六14:00-18:00，建议安排2名店员同时当值。
        周一至周三预计客流较低，可适当安排休息。已根据历史客流数据自动优化排班表。
      </template>
    </t-alert>

    <!-- 排班主表 -->
    <t-card :bordered="true">
      <t-table
        :data="scheduleData"
        :columns="scheduleColumns"
        row-key="employeeId"
        hover
        stripe
        header-row-class="schedule-header"
      >
        <template #mon="{ row }">
          <span v-if="row.mon" :class="['shift-badge', shiftClass(row.mon)]" @click="editShift(row, 'mon')">{{ row.mon }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'mon')">休</span>
        </template>
        <template #tue="{ row }">
          <span v-if="row.tue" :class="['shift-badge', shiftClass(row.tue)]" @click="editShift(row, 'tue')">{{ row.tue }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'tue')">休</span>
        </template>
        <template #wed="{ row }">
          <span v-if="row.wed" :class="['shift-badge', shiftClass(row.wed)]" @click="editShift(row, 'wed')">{{ row.wed }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'wed')">休</span>
        </template>
        <template #thu="{ row }">
          <span v-if="row.thu" :class="['shift-badge', shiftClass(row.thu)]" @click="editShift(row, 'thu')">{{ row.thu }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'thu')">休</span>
        </template>
        <template #fri="{ row }">
          <span v-if="row.fri" :class="['shift-badge', shiftClass(row.fri)]" @click="editShift(row, 'fri')">{{ row.fri }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'fri')">休</span>
        </template>
        <template #sat="{ row }">
          <span v-if="row.sat" :class="['shift-badge', shiftClass(row.sat)]" @click="editShift(row, 'sat')">{{ row.sat }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'sat')">休</span>
        </template>
        <template #sun="{ row }">
          <span v-if="row.sun" :class="['shift-badge', shiftClass(row.sun)]" @click="editShift(row, 'sun')">{{ row.sun }}</span>
          <span v-else class="shift-off" @click="editShift(row, 'sun')">休</span>
        </template>
        <template #totalHours="{ row }">
          <span :class="['total-hours', row.totalHours >= 40 ? 'full' : '']">{{ row.totalHours }}h</span>
        </template>
        <template #actions="{ row }">
          <t-dropdown :options="actionOptions" @click="handleAction($event, row)">
            <t-button size="small" variant="text" theme="primary">操作</t-button>
          </t-dropdown>
        </template>
      </t-table>
    </t-card>

    <!-- 排班编辑对话框 -->
    <t-dialog v-model:visible="editDialogVisible" :header="`编辑排班 — ${editEmployee?.name}`" width="400px" :footer="false">
      <t-form layout="vertical" v-if="editEmployee">
        <t-form-item :label="weekDayLabel(editDay)">
          <t-radio-group v-model="editValue">
            <t-radio-button value="">休</t-radio-button>
            <t-radio-button value="早班">早班 09:00-18:00</t-radio-button>
            <t-radio-button value="中班">中班 14:00-22:00</t-radio-button>
            <t-radio-button value="晚班">晚班 18:00-23:00</t-radio-button>
          </t-radio-group>
        </t-form-item>
      </t-form>
      <div style="text-align:right;margin-top:16px">
        <t-button variant="outline" @click="editDialogVisible = false">取消</t-button>
        <t-button theme="primary" @click="saveShift" style="margin-left:8px">保存</t-button>
      </div>
    </t-dialog>

    <!-- 换班申请对话框 -->
    <t-dialog v-model:visible="showSwapDialog" header="换班申请" width="480px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="申请人">
          <t-select v-model="swapFrom" placeholder="选择员工">
            <t-option v-for="e in employees" :key="e.employeeId" :value="e.employeeId" :label="e.name" />
          </t-select>
        </t-form-item>
        <t-form-item label="换班日期">
          <t-date-picker v-model="swapDate" style="width:100%" />
        </t-form-item>
        <t-form-item label="换班后班次">
          <t-radio-group v-model="swapShift">
            <t-radio-button value="早班">早班</t-radio-button>
            <t-radio-button value="中班">中班</t-radio-button>
            <t-radio-button value="晚班">晚班</t-radio-button>
            <t-radio-button value="">休息</t-radio-button>
          </t-radio-group>
        </t-form-item>
        <t-form-item label="对方员工">
          <t-select v-model="swapTo" placeholder="选择换班对象">
            <t-option v-for="e in employees" :key="e.employeeId" :value="e.employeeId" :label="e.name" />
          </t-select>
        </t-form-item>
        <t-form-item label="换班原因">
          <t-textarea v-model="swapReason" placeholder="请输入换班原因" :rows="2" />
        </t-form-item>
      </t-form>
      <div style="text-align:right">
        <t-button variant="outline" @click="showSwapDialog = false">取消</t-button>
        <t-button theme="primary" @click="submitSwap" style="margin-left:8px">提交申请</t-button>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import hr from '@mock/hr.json'

// ── State ──
const scheduleStore = ref('盈隆店')
const showSuggestion = ref(false)
const editDialogVisible = ref(false)
const editEmployee = ref<any>(null)
const editDay = ref('')
const editValue = ref('')
const showSwapDialog = ref(false)
const swapFrom = ref('')
const swapDate = ref('')
const swapShift = ref('早班')
const swapTo = ref('')
const swapReason = ref('')

// ── Week navigation ──
const weekOffset = ref(0)
const employees = hr.employees.filter(e => e.store === '盈隆店')

function getWeekStart(offset: number): Date {
  const now = new Date()
  const day = now.getDay()
  const diff = (day === 0 ? 6 : day - 1) // Monday as start
  const monday = new Date(now)
  monday.setDate(now.getDate() - diff + offset * 7)
  monday.setHours(0, 0, 0, 0)
  return monday
}

const weekStart = computed(() => getWeekStart(weekOffset.value))

const currentWeekLabel = computed(() => {
  const start = weekStart.value
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  const fmt = (d: Date) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${fmt(start)} — ${fmt(end)}`
})

function prevWeek() { weekOffset.value-- }
function nextWeek() { weekOffset.value++ }
function resetWeek() { weekOffset.value = 0 }

function genSchedule() { showSuggestion.value = true }

// ── Schedule data ──
const scheduleData = computed(() => {
  return employees.map(e => {
    const base = employeeBaseSchedule(e.employeeId)
    const hours = calcTotalHours(base)
    return { employeeId: e.employeeId, name: e.name, position: e.position, ...base, totalHours: hours }
  })
})

function employeeBaseSchedule(empId: string): Record<string, string> {
  // Generate varied schedules based on role
  const schedules: Record<string, Record<string, string>> = {
    'E001': { mon: '早班', tue: '早班', wed: '早班', thu: '早班', fri: '早班', sat: '', sun: '' },
    'E002': { mon: '中班', tue: '中班', wed: '', thu: '中班', fri: '中班', sat: '早班', sun: '早班' },
    'E003': { mon: '早班', tue: '早班', wed: '早班', thu: '', fri: '早班', sat: '早班', sun: '' },
    'E004': { mon: '早班', tue: '', wed: '早班', thu: '早班', fri: '早班', sat: '', sun: '' },
    'E005': { mon: '中班', tue: '中班', wed: '中班', thu: '中班', fri: '', sat: '中班', sun: '' },
  }
  return schedules[empId] || { mon: '早班', tue: '早班', wed: '', thu: '早班', fri: '早班', sat: '', sun: '' }
}

function calcTotalHours(week: Record<string, string>): number {
  const dayHours: Record<string, number> = { '早班': 9, '中班': 8, '晚班': 5 }
  let total = 0
  for (const day of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']) {
    if (week[day]) total += dayHours[week[day]] || 8
  }
  return total
}

// ── Shift dialog logic ──
function editShift(row: any, day: string) {
  editEmployee.value = row
  editDay.value = day
  editValue.value = row[day] || ''
  editDialogVisible.value = true
}

function weekDayLabel(day: string): string {
  const map: Record<string, string> = { mon: '周一', tue: '周二', wed: '周三', thu: '周四', fri: '周五', sat: '周六', sun: '周日' }
  return map[day] || day
}

function saveShift() {
  if (!editEmployee.value || !editDay.value) return
  const row = scheduleData.value.find((r: any) => r.employeeId === editEmployee.value.employeeId)
  if (row) {
    row[editDay.value] = editValue.value
    row.totalHours = calcTotalHours(row)
  }
  editDialogVisible.value = false
}

function shiftClass(shift: string): string {
  if (shift === '早班') return 'shift-morning'
  if (shift === '中班') return 'shift-afternoon'
  if (shift === '晚班') return 'shift-night'
  return ''
}

function submitSwap() {
  if (!swapFrom.value || !swapDate.value || !swapTo.value) {
    return
  }
  showSwapDialog.value = false
  swapFrom.value = ''
  swapTo.value = ''
  swapReason.value = ''
  swapDate.value = ''
  // In production, this would create a workflow approval task
  const fromName = employees.find(e => e.employeeId === swapFrom.value)?.name || ''
  const toName = employees.find(e => e.employeeId === swapTo.value)?.name || ''
}

const actionOptions = [
  { content: '编辑排班', value: 'edit' },
  { content: '申请换班', value: 'swap' },
  { content: '查看工时', value: 'hours' },
]

function handleAction(data: { value: string }, row: any) {
  if (data.value === 'edit') {
    editEmployee.value = row
    editDay.value = 'mon'
    editValue.value = row.mon || ''
    editDialogVisible.value = true
  } else if (data.value === 'swap') {
    swapFrom.value = row.employeeId
    showSwapDialog.value = true
  } else if (data.value === 'hours') {
    alert(`${row.name} 本周总工时：${row.totalHours}h`)
  }
}

// ── Stats ──
const scheduleStats = computed(() => {
  const totalEmployees = employees.length
  const onDuty = scheduleData.value.filter((r: any) => {
    const today = new Date().getDay()
    const dayMap = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']
    return r[dayMap[today]] !== ''
  }).length
  const totalHoursAll = scheduleData.value.reduce((s: number, r: any) => s + r.totalHours, 0)
  const avgHours = totalEmployees > 0 ? Math.round(totalHoursAll / totalEmployees) : 0
  return [
    { label: '员工总数', value: totalEmployees + '人', color: '#0052D9' },
    { label: '今日当值', value: onDuty + '人', color: '#00A870' },
    { label: '周总工时', value: totalHoursAll + 'h', color: '#E37318' },
    { label: '人均工时', value: avgHours + 'h/周', color: '#366EF4' },
  ]
})

// ── Columns ──
const scheduleColumns = [
  { colKey: 'name', title: '姓名', width: 80, fixed: 'left' as const },
  { colKey: 'position', title: '岗位', width: 70, fixed: 'left' as const },
  { colKey: 'mon', title: '周一', width: 100 },
  { colKey: 'tue', title: '周二', width: 100 },
  { colKey: 'wed', title: '周三', width: 100 },
  { colKey: 'thu', title: '周四', width: 100 },
  { colKey: 'fri', title: '周五', width: 100 },
  { colKey: 'sat', title: '周六', width: 100 },
  { colKey: 'sun', title: '周日', width: 100 },
  { colKey: 'totalHours', title: '总工时', width: 70 },
  { colKey: 'actions', title: '操作', width: 80, fixed: 'right' as const },
]
</script>

<style scoped>
.week-nav { display: flex; align-items: center; gap: 4px; }
.week-label { font-size: 14px; font-weight: 600; color: #333; min-width: 140px; text-align: center; }

.shift-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
.shift-dot.shift-morning { background: #0052D9; }
.shift-dot.shift-afternoon { background: #E37318; }
.shift-dot.shift-night { background: #9C27B0; }

.shift-badge {
  display: inline-block; padding: 4px 12px; border-radius: 14px; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all .15s; min-width: 70px; text-align: center;
}
.shift-badge:hover { opacity: 0.8; transform: scale(1.05); }
.shift-morning { background: #e8f0fe; color: #0052D9; }
.shift-afternoon { background: #fff3e0; color: #E37318; }
.shift-night { background: #f3e5f5; color: #9C27B0; }
.shift-off {
  display: inline-block; padding: 4px 12px; border-radius: 14px; font-size: 12px;
  color: #ccc; cursor: pointer; transition: all .15s; min-width: 70px; text-align: center;
}
.shift-off:hover { background: #f5f5f5; color: #999; }

.total-hours { font-size: 13px; font-weight: 600; color: #666; }
.total-hours.full { color: #0052D9; }

:deep(.schedule-header th) { background: #fafafa !important; font-weight: 600; }
</style>
