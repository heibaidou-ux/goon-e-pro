<template>
  <div>
    <h2 class="page-header">员工档案</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-input v-model="searchText" placeholder="搜索姓名/手机号..." clearable>
          <template #prefix-icon><t-icon name="search" /></template>
        </t-input>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterStore" placeholder="所属门店" clearable>
          <t-option value="盈隆店" label="盈隆店" />
          <t-option value="盈丰店" label="盈丰店" />
          <t-option value="金德店" label="金德店" />
          <t-option value="总部" label="总部" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterPosition" placeholder="岗位" clearable>
          <t-option value="店长" label="店长" />
          <t-option value="店员" label="店员" />
          <t-option value="技术员" label="技术员" />
          <t-option value="财务" label="财务" />
          <t-option value="总部运营" label="总部运营" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterEmpStatus" placeholder="员工状态" clearable>
          <t-option value="在职" label="在职" />
          <t-option value="离职" label="离职" />
        </t-select>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-table :data="filteredEmployees" :columns="columns" row-key="employeeId" hover stripe>
        <template #status="{ row }">
          <t-tag :theme="row.status === '在职' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #contractType="{ row }">
          <t-tag variant="light" size="small">{{ row.contractType }}</t-tag>
        </template>
        <template #salaryGrade="{ row }">{{ row.salaryGrade }} - {{ gradeLabel(row.salaryGrade) }}</template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" @click="editEmployee(row)">编辑</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="detailVisible" :header="`${selectedEmployee?.name} 档案`" size="460px" :footer="false">
      <div v-if="selectedEmployee" class="detail-sections">
        <div class="detail-section"><h4>基本信息</h4>
          <div class="detail-row"><span>员工编号</span><span>{{ selectedEmployee.employeeId }}</span></div>
          <div class="detail-row"><span>姓名</span><span>{{ selectedEmployee.name }}</span></div>
          <div class="detail-row"><span>性别</span><span>{{ selectedEmployee.gender }}</span></div>
          <div class="detail-row"><span>手机号码</span><span>{{ selectedEmployee.phone }}</span></div>
          <div class="detail-row"><span>学历</span><span>{{ selectedEmployee.education }}</span></div>
          <div class="detail-row"><span>毕业院校</span><span>{{ selectedEmployee.school }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section"><h4>岗位信息</h4>
          <div class="detail-row"><span>所属门店</span><span>{{ selectedEmployee.store }}</span></div>
          <div class="detail-row"><span>岗位</span><span>{{ selectedEmployee.position }}</span></div>
          <div class="detail-row"><span>薪资等级</span><span>{{ selectedEmployee.salaryGrade }}</span></div>
          <div class="detail-row"><span>入职日期</span><span>{{ selectedEmployee.hireDate }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section"><h4>合同信息</h4>
          <div class="detail-row"><span>合同类型</span><span>{{ selectedEmployee.contractType }}</span></div>
          <div class="detail-row"><span>合同周期</span><span>{{ selectedEmployee.contractStart }} ~ {{ selectedEmployee.contractEnd }}</span></div>
          <div v-if="selectedEmployee.contractEnd" class="detail-row">
            <span>合同到期提醒</span>
            <t-tag v-if="isContractExpiring(selectedEmployee.contractEnd)" theme="danger" size="small">即将到期</t-tag>
            <span v-else style="color:#999">未到期</span>
          </div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import hr from '@mock/hr.json'

const searchText = ref('')
const filterStore = ref('')
const filterPosition = ref('')
const filterEmpStatus = ref('')
const detailVisible = ref(false)
const selectedEmployee = ref<any>(null)

const employees = hr.employees.filter((e: any) => e.position !== '保洁员') // cleaner handled separately
const grades = hr.salaryGrades

function gradeLabel(grade: string): string {
  const g = grades.find((g: any) => g.grade === grade)
  return g ? g.label : grade
}

function isContractExpiring(end: string): boolean {
  if (!end) return false
  return (new Date(end).getTime() - Date.now()) < 30 * 86400000
}

const filteredEmployees = computed(() => {
  let list = employees
  if (searchText.value) list = list.filter((e: any) => e.name.includes(searchText.value) || e.phone.includes(searchText.value))
  if (filterStore.value) list = list.filter((e: any) => e.store === filterStore.value)
  if (filterPosition.value) list = list.filter((e: any) => e.position === filterPosition.value)
  if (filterEmpStatus.value) list = list.filter((e: any) => e.status === filterEmpStatus.value)
  return list
})

function viewDetail(e: any) { selectedEmployee.value = e; detailVisible.value = true }
function editEmployee(e: any) { selectedEmployee.value = e; detailVisible.value = true }

const columns = [
  { colKey: 'employeeId', title: '编号', width: 80 },
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'phone', title: '手机号', width: 110 },
  { colKey: 'store', title: '门店', width: 90 },
  { colKey: 'position', title: '岗位', width: 80 },
  { colKey: 'salaryGrade', title: '薪资等级', width: 120 },
  { colKey: 'contractType', title: '合同类型', width: 80 },
  { colKey: 'hireDate', title: '入职日期', width: 100 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 120 },
]
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
</style>
