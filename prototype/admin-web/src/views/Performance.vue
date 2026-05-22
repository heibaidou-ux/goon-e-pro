<template>
  <div>
    <h2 class="page-header">绩效考核</h2>

    <!-- 统计卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in perfStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 筛选与操作 -->
    <t-card :bordered="true" style="margin-bottom:16px">
      <t-row :gutter="16" align="middle">
        <t-col :span="2">
          <t-select v-model="perfPeriod" placeholder="选择周期">
            <t-option value="2026年4月" label="2026年4月（月）" />
            <t-option value="2026年3月" label="2026年3月（月）" />
            <t-option value="2026年Q1" label="2026年Q1（季度）" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="perfStore" placeholder="选择门店" clearable>
            <t-option value="盈隆店" label="盈隆店" />
            <t-option value="盈丰店" label="盈丰店" />
            <t-option value="总部" label="总部" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterGrade" placeholder="考核等级" clearable>
            <t-option value="S" label="S 卓越" />
            <t-option value="A" label="A 优秀" />
            <t-option value="B" label="B 良好" />
            <t-option value="C" label="C 需改进" />
            <t-option value="D" label="D 不合格" />
          </t-select>
        </t-col>
        <t-col :span="6" style="text-align:right">
          <t-button theme="primary" @click="calcAllScores">自动评分</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="batchSubmit">批量提交</t-button>
        </t-col>
      </t-row>
    </t-card>

    <!-- 考核主表 -->
    <t-card :bordered="true">
      <t-table
        :data="filteredPerf"
        :columns="perfColumns"
        row-key="employeeId"
        hover
        stripe
        :pagination="{ pageSize: 20, total: filteredPerf.length }"
      >
        <template #grade="{ row }">
          <t-tag :theme="gradeTheme(row.grade)" size="small" variant="light" class="grade-tag">{{ row.grade }}</t-tag>
        </template>
        <template #kpiScore="{ row }">
          <div class="score-bar-wrap">
            <div class="score-bar" :style="{ width: row.kpiScore * 20 + '%', background: scoreColor(row.kpiScore) }"></div>
          </div>
          <span class="score-text">{{ row.kpiScore.toFixed(1) }}</span>
        </template>
        <template #managerScore="{ row }">
          <t-input-number v-model="row.managerScore" :min="0" :max="5" :step="0.5" size="small" theme="normal" style="width:100px" />
        </template>
        <template #finalScore="{ row }">
          <span :style="{ color: scoreColor(row.finalScore), fontWeight: 700, fontSize: '16px' }">{{ row.finalScore.toFixed(1) }}</span>
        </template>
        <template #result="{ row }">
          <t-tag v-if="row.submitted" theme="success" size="small" variant="light">已提交</t-tag>
          <t-button v-else size="small" theme="primary" variant="text" @click="submitPerf(row)">提交</t-button>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" theme="default" @click="openGoalDialog(row)">目标</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 目标管理对话框 -->
    <t-dialog v-model:visible="goalDialogVisible" :header="`${goalEmployee?.name} — KPI目标设置`" width="600px" :footer="false">
      <t-form layout="vertical">
        <t-form-item v-for="(goal, idx) in goalEmployee?.goals || []" :key="idx" :label="goal.dimension || '目标' + (idx+1)">
          <t-row :gutter="8">
            <t-col :span="8"><t-input v-model="goal.target" placeholder="目标值" /></t-col>
            <t-col :span="4"><t-input-number v-model="goal.weight" :min="0" :max="100" :step="5" size="small" />%</t-col>
          </t-row>
        </t-form-item>
      </t-form>
      <div style="text-align:right;margin-top:16px">
        <t-button variant="outline" @click="goalDialogVisible = false">取消</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="saveGoals">保存目标</t-button>
      </div>
    </t-dialog>

    <!-- 考核详情抽屉 -->
    <t-drawer v-model:visible="detailVisible" :header="`${detailEmployee?.name} 考核详情`" size="500px" :footer="false">
      <div v-if="detailEmployee" class="perf-detail">
        <t-card title="维度评分" :bordered="true" style="margin-bottom:16px">
          <div v-for="d in detailDimensions" :key="d.name" class="dimension-row">
            <div class="dim-header">
              <span class="dim-name">{{ d.name }}</span>
              <span class="dim-weight">{{ d.weight }}%</span>
              <span class="dim-score" :style="{ color: scoreColor(d.score) }">{{ d.score.toFixed(1) }}</span>
            </div>
            <div class="dim-bar-bg">
              <div class="dim-bar" :style="{ width: d.score * 20 + '%', background: scoreColor(d.score) }"></div>
            </div>
            <div class="dim-comment">{{ d.comment }}</div>
          </div>
        </t-card>
        <t-card title="综合评定" :bordered="true">
          <div class="final-grade">
            <span class="grade-label">考核等级：</span>
            <t-tag :theme="gradeTheme(detailEmployee.grade)" size="large" class="grade-tag">{{ detailEmployee.grade }} — {{ gradeLabel(detailEmployee.grade) }}</t-tag>
          </div>
          <div class="final-score">
            <span class="grade-label">综合得分：</span>
            <span class="score-big" :style="{ color: scoreColor(detailEmployee.finalScore) }">{{ detailEmployee.finalScore.toFixed(1) }}</span>
          </div>
          <t-divider />
          <div class="dimension-row">
            <span style="font-size:13px;color:#666;margin-bottom:8px;display:block;">店长评语：</span>
            <t-textarea v-model="detailEmployee.review" placeholder="输入评语..." :rows="3" />
          </div>
        </t-card>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import hr from '@mock/hr.json'

const perfPeriod = ref('2026年4月')
const perfStore = ref('盈隆店')
const filterGrade = ref('')
const detailVisible = ref(false)
const detailEmployee = ref<any>(null)
const goalDialogVisible = ref(false)
const goalEmployee = ref<any>(null)

// ── Data ──
const employees = hr.employees.filter(e => e.status === '在职')

const perfData = reactive(employees.map(e => {
  const baseScore = e.employeeId === 'E001' ? 4.5 : e.employeeId === 'E007' ? 4.8 : e.employeeId === 'E006' ? 4.3 : e.employeeId === 'E004' ? 4.6 : e.employeeId === 'E005' ? 3.8 : 4.0 + Math.random() * 0.5
  const kpiScore = Math.round(baseScore * 10) / 10
  return {
    employeeId: e.employeeId,
    name: e.name,
    position: e.position,
    store: e.store,
    hireDate: e.hireDate,
    kpiScore,
    managerScore: 0,
    finalScore: kpiScore,
    grade: calcGrade(kpiScore),
    submitted: false,
    review: '',
    goals: [
      { dimension: '工作业绩', target: '完成月度营收目标', weight: 40, score: kpiScore },
      { dimension: '客户满意度', target: '好评率≥95%', weight: 25, score: Math.min(5, kpiScore + 0.2) },
      { dimension: '团队协作', target: '无跨部门投诉', weight: 20, score: Math.min(5, kpiScore + 0.1) },
      { dimension: '出勤纪律', target: '全勤无迟到', weight: 15, score: Math.min(5, kpiScore + 0.3) },
    ],
  }
}))

function calcGrade(score: number): string {
  if (score >= 4.5) return 'S'
  if (score >= 4.0) return 'A'
  if (score >= 3.5) return 'B'
  if (score >= 3.0) return 'C'
  return 'D'
}

function calcAllScores() {
  for (const p of perfData) {
    const mgr = p.managerScore || 0
    p.finalScore = mgr > 0 ? Math.round((p.kpiScore * 0.6 + mgr * 0.4) * 10) / 10 : p.kpiScore
    p.grade = calcGrade(p.finalScore)
  }
}

function submitPerf(row: any) {
  if (row.managerScore > 0) {
    row.finalScore = Math.round((row.kpiScore * 0.6 + row.managerScore * 0.4) * 10) / 10
    row.grade = calcGrade(row.finalScore)
  }
  row.submitted = true
}

function batchSubmit() {
  for (const p of perfData) {
    if (!p.submitted) submitPerf(p)
  }
}

function viewDetail(row: any) {
  detailEmployee.value = row
  detailVisible.value = true
}

const detailDimensions = computed(() => {
  if (!detailEmployee.value) return []
  return detailEmployee.value.goals || []
})

function openGoalDialog(row: any) {
  goalEmployee.value = row
  goalDialogVisible.value = true
}

function saveGoals() {
  if (!goalEmployee.value) return
  // Recalc KPI score from weighted goals
  const goals = goalEmployee.value.goals
  if (goals && goals.length > 0) {
    const totalWeight = goals.reduce((s: number, g: any) => s + (g.weight || 0), 0)
    if (totalWeight > 0) {
      const weighted = goals.reduce((s: number, g: any) => s + (g.score || 0) * (g.weight || 0), 0)
      goalEmployee.value.kpiScore = Math.round(weighted / totalWeight * 10) / 10
      goalEmployee.value.finalScore = goalEmployee.value.kpiScore
      goalEmployee.value.grade = calcGrade(goalEmployee.value.finalScore)
    }
  }
  goalDialogVisible.value = false
}

function gradeTheme(grade: string): string {
  return grade === 'S' ? 'danger' : grade === 'A' ? 'success' : grade === 'B' ? 'warning' : grade === 'C' ? 'default' : 'danger'
}

function gradeLabel(grade: string): string {
  return grade === 'S' ? '卓越' : grade === 'A' ? '优秀' : grade === 'B' ? '良好' : grade === 'C' ? '需改进' : '不合格'
}

function scoreColor(score: number): string {
  if (score >= 4.5) return '#D54941'
  if (score >= 4.0) return '#00A870'
  if (score >= 3.5) return '#E37318'
  if (score >= 3.0) return '#366EF4'
  return '#999'
}

// ── Filtered data ──
const filteredPerf = computed(() => {
  let list = perfData
  if (perfStore.value) list = list.filter(p => p.store === perfStore.value)
  if (filterGrade.value) list = list.filter(p => p.grade === filterGrade.value)
  return list
})

// ── Stats ──
const perfStats = computed(() => {
  const total = perfData.length
  const submitted = perfData.filter(p => p.submitted).length
  const avgScore = total > 0 ? perfData.reduce((s, p) => s + p.finalScore, 0) / total : 0
  const sCount = perfData.filter(p => p.grade === 'S').length
  return [
    { label: '考核人数', value: total + '人', color: '#0052D9' },
    { label: '已提交', value: submitted + '/' + total, color: '#00A870' },
    { label: '平均得分', value: avgScore.toFixed(1), color: '#E37318' },
    { label: 'S级人数', value: sCount + '人', color: '#D54941' },
  ]
})

// ── Columns ──
const perfColumns = [
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'position', title: '岗位', width: 70 },
  { colKey: 'grade', title: '等级', width: 60 },
  { colKey: 'kpiScore', title: '系统评分', width: 130 },
  { colKey: 'managerScore', title: '店长评分', width: 120 },
  { colKey: 'finalScore', title: '综合得分', width: 80 },
  { colKey: 'result', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 100 },
]
</script>

<style scoped>
.score-bar-wrap { display: inline-block; width: 80px; height: 8px; background: #f0f0f0; border-radius: 4px; vertical-align: middle; overflow: hidden; }
.score-bar { height: 100%; border-radius: 4px; transition: width .3s; }
.score-text { font-size: 13px; font-weight: 600; margin-left: 6px; vertical-align: middle; }
.grade-tag { font-weight: 700; }

.perf-detail { padding: 4px 0; }
.dimension-row { margin-bottom: 14px; }
.dim-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.dim-name { font-size: 13px; font-weight: 600; color: #333; flex: 1; }
.dim-weight { font-size: 11px; color: #999; }
.dim-score { font-size: 15px; font-weight: 700; min-width: 36px; text-align: right; }
.dim-bar-bg { width: 100%; height: 6px; background: #f0f0f0; border-radius: 3px; overflow: hidden; }
.dim-bar { height: 100%; border-radius: 3px; transition: width .3s; }
.dim-comment { font-size: 11px; color: #999; margin-top: 4px; }

.final-grade, .final-score { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.grade-label { font-size: 14px; color: #333; font-weight: 500; }
.score-big { font-size: 28px; font-weight: 800; }
</style>
