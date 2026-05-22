<template>
  <div>
    <h2 class="page-header">保洁员考核与薪资管理</h2>

    <!-- 统计卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in cleanerStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 操作栏 -->
    <t-card :bordered="true" style="margin-bottom:16px">
      <t-row :gutter="16" align="middle">
        <t-col :span="3">
          <t-select v-model="cleanerStore" placeholder="选择门店">
            <t-option value="盈隆店" label="盈隆店" />
            <t-option value="盈丰店" label="盈丰店" />
          </t-select>
        </t-col>
        <t-col :span="3">
          <t-select v-model="cleanerTab" :options="cleanerTabs" style="width:100%" />
        </t-col>
        <t-col :span="6" style="text-align:right">
          <t-button variant="outline" @click="showAssignTask = true">+ 分配任务</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="showCleanerSchedule = true">排班视图</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="calcCleanerPay">计算本月薪资</t-button>
        </t-col>
      </t-row>
    </t-card>

    <!-- 薪资页 -->
    <t-card v-if="cleanerTab === 'payroll'" :bordered="true" title="保洁员薪资">
      <t-table :data="cleanerPayrollData" :columns="payColumns" row-key="cpId" hover stripe>
        <template #basePay="{ row }">¥{{ row.basePay.toLocaleString() }}</template>
        <template #bonus="{ row }"><span v-if="row.bonus" style="color:#00A870">+¥{{ row.bonus }}</span><span v-else>—</span></template>
        <template #penalty="{ row }"><span v-if="row.penalty" style="color:#D54941">-¥{{ row.penalty }}</span><span v-else>—</span></template>
        <template #netPay="{ row }">¥{{ row.netPay.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已发放' ? 'success' : 'warning'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-button size="small" variant="text" theme="primary" @click="viewCleanerDetail(row)">详情</t-button>
        </template>
      </t-table>
    </t-card>

    <!-- 质量考核页 -->
    <t-card v-if="cleanerTab === 'quality'" :bordered="true" title="保洁质量考核">
      <t-table :data="cleanerQualityData" :columns="qualityColumns" row-key="employeeId" hover stripe>
        <template #avgResponse="{ row }">{{ row.avgResponse }}分钟</template>
        <template #quality="{ row }">
          <div class="quality-stars">
            <span v-for="i in 5" :key="i" :class="['star', i <= row.quality ? 'filled' : '']" @click="row.quality = i">★</span>
            <span style="font-size:11px;color:#999;margin-left:4px">{{ row.quality }}/5</span>
          </div>
        </template>
        <template #completionRate="{ row }">{{ (row.completionRate * 100).toFixed(0) }}%</template>
        <template #inspectionPass="{ row }">{{ row.inspectionPass }}/{{ row.inspectionTotal }}</template>
      </t-table>
    </t-card>

    <!-- 任务列表页 -->
    <t-card v-if="cleanerTab === 'tasks'" :bordered="true" title="保洁任务">
      <t-table :data="cleanerTasks" :columns="taskColumns" row-key="taskId" hover stripe>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已完成' ? 'success' : row.status === '进行中' ? 'warning' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #priority="{ row }">
          <t-tag :theme="row.priority === '高' ? 'danger' : row.priority === '中' ? 'warning' : 'default'" size="small" variant="light">{{ row.priority }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button v-if="row.status !== '已完成'" size="small" variant="text" theme="success" @click="completeTask(row)">完成</t-button>
            <t-button size="small" variant="text" theme="primary" @click="viewTaskDetail(row)">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 分配任务对话框 -->
    <t-dialog v-model:visible="showAssignTask" header="分配保洁任务" width="500px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="选择保洁员">
          <t-select v-model="assignCleaner" placeholder="请选择">
            <t-option v-for="e in externalPersonnel" :key="e.epId" :value="e.epId" :label="e.name" />
          </t-select>
        </t-form-item>
        <t-form-item label="房间/区域">
          <t-select v-model="assignRoom" placeholder="请选择区域">
            <t-option value="大茶室C" label="大茶室C" />
            <t-option value="中茶室A" label="中茶室A" />
            <t-option value="中茶室B" label="中茶室B" />
            <t-option value="大会议室" label="大会议室" />
            <t-option value="大厅" label="大厅" />
            <t-option value="走廊" label="走廊" />
            <t-option value="卫生间" label="卫生间" />
          </t-select>
        </t-form-item>
        <t-form-item label="任务类型">
          <t-radio-group v-model="assignTaskType">
            <t-radio-button value="日常保洁">日常保洁</t-radio-button>
            <t-radio-button value="深度清洁">深度清洁</t-radio-button>
            <t-radio-button value="退房清洁">退房清洁</t-radio-button>
            <t-radio-button value="垃圾清理">垃圾清理</t-radio-button>
          </t-radio-group>
        </t-form-item>
        <t-form-item label="优先级别">
          <t-radio-group v-model="assignPriority">
            <t-radio-button value="高">高</t-radio-button>
            <t-radio-button value="中">中</t-radio-button>
            <t-radio-button value="低">低</t-radio-button>
          </t-radio-group>
        </t-form-item>
        <t-form-item label="备注">
          <t-textarea v-model="assignNote" placeholder="特殊清洁要求..." :rows="2" />
        </t-form-item>
      </t-form>
      <div style="text-align:right;margin-top:16px">
        <t-button variant="outline" @click="showAssignTask = false">取消</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="confirmAssign">确认分配</t-button>
      </div>
    </t-dialog>

    <!-- 排班视图对话框 -->
    <t-dialog v-model:visible="showCleanerSchedule" header="保洁员排班" width="700px" :footer="false">
      <t-table :data="cleanerWeekSchedule" :columns="cleanerScheduleColumns" row-key="epId" hover stripe>
        <template #mon="{ row }"><t-tag :theme="row.mon ? 'success' : 'default'" size="small" variant="light">{{ row.mon || '休' }}</t-tag></template>
        <template #tue="{ row }"><t-tag :theme="row.tue ? 'success' : 'default'" size="small" variant="light">{{ row.tue || '休' }}</t-tag></template>
        <template #wed="{ row }"><t-tag :theme="row.wed ? 'success' : 'default'" size="small" variant="light">{{ row.wed || '休' }}</t-tag></template>
        <template #thu="{ row }"><t-tag :theme="row.thu ? 'success' : 'default'" size="small" variant="light">{{ row.thu || '休' }}</t-tag></template>
        <template #fri="{ row }"><t-tag :theme="row.fri ? 'success' : 'default'" size="small" variant="light">{{ row.fri || '休' }}</t-tag></template>
        <template #sat="{ row }"><t-tag :theme="row.sat ? 'success' : 'default'" size="small" variant="light">{{ row.sat || '休' }}</t-tag></template>
        <template #sun="{ row }"><t-tag :theme="row.sun ? 'success' : 'default'" size="small" variant="light">{{ row.sun || '休' }}</t-tag></template>
      </t-table>
    </t-dialog>

    <!-- 任务详情抽屉 -->
    <t-drawer v-model:visible="taskDetailVisible" header="任务详情" size="400px" :footer="false">
      <div v-if="selectedTask" class="detail-sections">
        <div class="detail-row"><span>任务编号</span><span>{{ selectedTask.taskId }}</span></div>
        <div class="detail-row"><span>位置</span><span>{{ selectedTask.room }}</span></div>
        <div class="detail-row"><span>类型</span><span>{{ selectedTask.type }}</span></div>
        <div class="detail-row"><span>保洁员</span><span>{{ selectedTask.cleanerName }}</span></div>
        <div class="detail-row"><span>分配时间</span><span>{{ selectedTask.assignedAt }}</span></div>
        <div class="detail-row"><span>完成时间</span><span>{{ selectedTask.completedAt || '—' }}</span></div>
        <div class="detail-row"><span>备注</span><span>{{ selectedTask.note || '—' }}</span></div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import hr from '@mock/hr.json'

// ── State ──
const cleanerStore = ref('盈隆店')
const cleanerTab = ref('payroll')
const showAssignTask = ref(false)
const showCleanerSchedule = ref(false)
const taskDetailVisible = ref(false)
const selectedTask = ref<any>(null)
const assignCleaner = ref('')
const assignRoom = ref('')
const assignTaskType = ref('日常保洁')
const assignPriority = ref('中')
const assignNote = ref('')

const cleanerTabs = [
  { value: 'payroll', label: '薪资管理' },
  { value: 'quality', label: '质量考核' },
  { value: 'tasks', label: '任务列表' },
]

const cleanerPayrollData = hr.cleanerPayroll
const externalPersonnel = hr.externalPersonnel

// ── Stats ──
const cleanerStats = computed(() => {
  const totalPay = cleanerPayrollData.reduce((s: number, r: any) => s + r.netPay, 0)
  const totalTasks = cleanerPayrollData.reduce((s: number, r: any) => s + r.totalTasks, 0)
  return [
    { label: '保洁员总数', value: externalPersonnel.length + '人', color: '#0052D9' },
    { label: '本月总薪酬', value: '¥' + totalPay.toLocaleString(), color: '#D54941' },
    { label: '完成保洁任务', value: totalTasks + '单', color: '#00A870' },
    { label: '平均响应', value: '12分钟', color: '#E37318' },
  ]
})

// ── Quality Data ──
const cleanerQualityData = reactive([
  { employeeId: 'EP001', name: '刘阿姨', store: '盈隆店', totalTasks: 42, avgResponse: 8, quality: 4.5, faultReports: 2, completionRate: 0.98, inspectionPass: 40, inspectionTotal: 42 },
  { employeeId: 'EP002', name: '赵阿姨', store: '盈丰店', totalTasks: 38, avgResponse: 15, quality: 3.5, faultReports: 1, completionRate: 0.90, inspectionPass: 32, inspectionTotal: 38 },
])

function calcCleanerPay() {
  // Recalculate payroll from quality data
  for (const q of cleanerQualityData) {
    const payroll = cleanerPayrollData.find((p: any) => p.epId === q.employeeId)
    if (payroll) {
      payroll.totalTasks = q.totalTasks
      payroll.basePay = q.totalTasks * payroll.unitPrice
      payroll.bonus = q.quality >= 4.5 ? 100 : q.quality >= 4.0 ? 50 : 0
      payroll.penalty = q.faultReports > 1 ? q.faultReports * 25 : 0
      payroll.netPay = payroll.basePay + payroll.bonus - payroll.penalty
    }
  }
}

// ── Tasks ──
const cleanerTasks = reactive([
  { taskId: 'CT001', room: '大茶室C', type: '退房清洁', cleanerName: '刘阿姨', priority: '高', status: '已完成', assignedAt: '2026-05-20 14:30', completedAt: '2026-05-20 15:10', note: '客人刚退房，需尽快清洁迎接下批客人' },
  { taskId: 'CT002', room: '中茶室A', type: '日常保洁', cleanerName: '刘阿姨', priority: '中', status: '已完成', assignedAt: '2026-05-20 09:00', completedAt: '2026-05-20 09:25', note: '' },
  { taskId: 'CT003', room: '大会议室', type: '深度清洁', cleanerName: '赵阿姨', priority: '中', status: '进行中', assignedAt: '2026-05-20 10:00', completedAt: '', note: '需重点清洁地毯' },
  { taskId: 'CT004', room: '卫生间', type: '日常保洁', cleanerName: '刘阿姨', priority: '高', status: '待处理', assignedAt: '2026-05-20 16:00', completedAt: '', note: '' },
  { taskId: 'CT005', room: '走廊', type: '日常保洁', cleanerName: '赵阿姨', priority: '低', status: '待处理', assignedAt: '2026-05-20 11:00', completedAt: '', note: '' },
  { taskId: 'CT006', room: '中茶室B', type: '退房清洁', cleanerName: '刘阿姨', priority: '高', status: '待处理', assignedAt: '2026-05-20 15:30', completedAt: '', note: '烟味较重，需开窗通风' },
])

function completeTask(row: any) {
  row.status = '已完成'
  row.completedAt = new Date().toISOString().slice(0, 16).replace('T', ' ')
}

function viewTaskDetail(row: any) {
  selectedTask.value = row
  taskDetailVisible.value = true
}

function viewCleanerDetail(row: any) {
  // Placeholder for cleaner detail
}

function confirmAssign() {
  if (!assignCleaner.value || !assignRoom.value) return
  const cleaner = externalPersonnel.find(e => e.epId === assignCleaner.value)
  cleanerTasks.unshift({
    taskId: 'CT' + String(Date.now()).slice(-6),
    room: assignRoom.value,
    type: assignTaskType.value,
    cleanerName: cleaner?.name || '',
    priority: assignPriority.value,
    status: '待处理',
    assignedAt: new Date().toISOString().slice(0, 16).replace('T', ' '),
    completedAt: '',
    note: assignNote.value || '',
  })
  showAssignTask.value = false
  assignCleaner.value = ''
  assignRoom.value = ''
  assignNote.value = ''
}

// ── Schedule ──
const cleanerWeekSchedule = computed(() => {
  return externalPersonnel.filter(e => e.serviceStore === cleanerStore.value).map(e => ({
    epId: e.epId,
    name: e.name,
    mon: '09:00-18:00',
    tue: '09:00-18:00',
    wed: '09:00-18:00',
    thu: '休',
    fri: '09:00-18:00',
    sat: '09:00-12:00',
    sun: '休',
  }))
})

// ── Columns ──
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
  { colKey: 'actions', title: '操作', width: 70 },
]

const qualityColumns = [
  { colKey: 'name', title: '姓名', width: 90 },
  { colKey: 'store', title: '门店', width: 80 },
  { colKey: 'totalTasks', title: '任务数', width: 70 },
  { colKey: 'avgResponse', title: '平均响应', width: 90 },
  { colKey: 'quality', title: '完成质量', width: 140 },
  { colKey: 'faultReports', title: '故障上报', width: 80 },
  { colKey: 'completionRate', title: '完成率', width: 80 },
  { colKey: 'inspectionPass', title: '抽检合格', width: 80 },
]

const taskColumns = [
  { colKey: 'taskId', title: '编号', width: 80 },
  { colKey: 'room', title: '位置', width: 100 },
  { colKey: 'type', title: '类型', width: 90 },
  { colKey: 'cleanerName', title: '保洁员', width: 80 },
  { colKey: 'priority', title: '优先级', width: 70 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'assignedAt', title: '分配时间', width: 140 },
  { colKey: 'note', title: '备注', ellipsis: true },
  { colKey: 'actions', title: '操作', width: 110 },
]

const cleanerScheduleColumns = [
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'mon', title: '周一', width: 80 },
  { colKey: 'tue', title: '周二', width: 80 },
  { colKey: 'wed', title: '周三', width: 80 },
  { colKey: 'thu', title: '周四', width: 80 },
  { colKey: 'fri', title: '周五', width: 80 },
  { colKey: 'sat', title: '周六', width: 80 },
  { colKey: 'sun', title: '周日', width: 80 },
]
</script>

<style scoped>
.quality-stars { display: flex; align-items: center; gap: 2px; }
.star { font-size: 18px; color: #ddd; cursor: pointer; transition: color .15s; }
.star.filled { color: #ffb400; }
.star:hover { color: #ffb400; }

.detail-sections { padding: 8px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; border-bottom: 1px solid #f5f5f5; }
.detail-row:last-child { border-bottom: none; }
</style>
