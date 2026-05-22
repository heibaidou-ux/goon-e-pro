<template>
  <div>
    <h2 class="page-header">外聘人员管理</h2>

    <!-- 统计卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in epStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 控制栏 -->
    <t-card :bordered="true" style="margin-bottom:16px">
      <t-row :gutter="16" align="middle">
        <t-col :span="2">
          <t-select v-model="epTab" :options="epTabs" style="width:100%" />
        </t-col>
        <t-col :span="2">
          <t-select v-model="epTypeFilter" placeholder="人员类型" clearable>
            <t-option value="保洁员" label="保洁员" />
            <t-option value="保安" label="保安" />
            <t-option value="兼职店员" label="兼职店员" />
            <t-option value="其他" label="其他" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="epStoreFilter" placeholder="服务门店" clearable>
            <t-option value="盈隆店" label="盈隆店" />
            <t-option value="盈丰店" label="盈丰店" />
          </t-select>
        </t-col>
        <t-col :span="6" style="text-align:right">
          <t-button theme="primary" @click="showAddDialog = true">+ 新增人员</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="showPaymentHistory = true">发放记录</t-button>
        </t-col>
      </t-row>
    </t-card>

    <!-- 主表 -->
    <t-card :bordered="true">
      <t-table :data="filteredEP" :columns="columns" row-key="epId" hover stripe>
        <template #payRate="{ row }">{{ row.payMethod === '按件计酬' ? `¥${row.payRate}/单` : `¥${row.payRate}/时` }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '在岗' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #contractEnd="{ row }">
          <t-tag v-if="isExpiring(row.contractEnd)" theme="danger" size="small" variant="light">
            ⚠ {{ row.contractEnd }} <span style="font-size:10px;opacity:.8">({{ daysToExpire(row.contractEnd) }}天)</span>
          </t-tag>
          <span v-else style="font-size:12px;color:#666">{{ row.contractEnd }}</span>
        </template>
        <template #monthlyPay="{ row }">
          <span style="font-weight:500">~¥{{ row.monthlyPay || estimateMonthly(row) }}/月</span>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" theme="default" @click="editPerson(row)">编辑</t-button>
            <t-button v-if="row.status === '在岗'" size="small" variant="text" theme="warning" @click="confirmTerminate(row)">终止</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 新增人员对话框 -->
    <t-dialog v-model:visible="showAddDialog" :header="editingPerson ? '编辑人员' : '新增外聘人员'" width="560px" :footer="false">
      <t-form :data="formData" layout="vertical">
        <t-row :gutter="16">
          <t-col :span="8">
            <t-form-item label="姓名">
              <t-input v-model="formData.name" placeholder="请输入姓名" />
            </t-form-item>
          </t-col>
          <t-col :span="4">
            <t-form-item label="性别">
              <t-select v-model="formData.gender" placeholder="选择">
                <t-option value="男" label="男" /><t-option value="女" label="女" />
              </t-select>
            </t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="手机号">
              <t-input v-model="formData.phone" placeholder="手机号" />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="人员类型">
              <t-select v-model="formData.personType" placeholder="选择类型">
                <t-option value="保洁员" label="保洁员" />
                <t-option value="保安" label="保安" />
                <t-option value="兼职店员" label="兼职店员" />
                <t-option value="其他" label="其他" />
              </t-select>
            </t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="所属公司">
              <t-input v-model="formData.company" placeholder="个人或无" />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="服务门店">
              <t-select v-model="formData.serviceStore" placeholder="选择门店">
                <t-option value="盈隆店" label="盈隆店" />
                <t-option value="盈丰店" label="盈丰店" />
              </t-select>
            </t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="计薪方式">
              <t-select v-model="formData.payMethod" placeholder="选择">
                <t-option value="按件计酬" label="按件计酬" />
                <t-option value="按时计酬" label="按时计酬" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="单价">
              <t-input v-model.number="formData.payRate" type="number" :prefix="formData.payMethod === '按件计酬' ? '¥/单' : '¥/时'" />
            </t-form-item>
          </t-col>
        </t-row>
        <t-form-item label="合同到期">
          <t-date-picker v-model="formData.contractEnd" style="width:100%" />
        </t-form-item>
      </t-form>
      <div style="text-align:right;margin-top:16px">
        <t-button variant="outline" @click="showAddDialog = false">取消</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="savePerson">{{ editingPerson ? '保存修改' : '确认新增' }}</t-button>
      </div>
    </t-dialog>

    <!-- 发放记录对话框 -->
    <t-dialog v-model:visible="showPaymentHistory" header="外聘人员发放记录" width="700px" :footer="false">
      <t-table :data="paymentHistory" :columns="paymentColumns" row-key="payId" hover stripe size="small">
        <template #amount="{ row }">¥{{ row.amount }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '已发放' ? 'success' : 'warning'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
      </t-table>
    </t-dialog>

    <!-- 详情抽屉 -->
    <t-drawer v-model:visible="epDetailVisible" header="外聘人员详情" size="420px" :footer="false">
      <div v-if="selectedEP" class="detail-sections">
        <t-card title="基本信息" :bordered="true" style="margin-bottom:16px">
          <div class="detail-row"><span>姓名</span><span class="detail-val">{{ selectedEP.name }}</span></div>
          <div class="detail-row"><span>手机号</span><span class="detail-val">{{ selectedEP.phone }}</span></div>
          <div class="detail-row"><span>人员类型</span><t-tag variant="light" size="small">{{ selectedEP.personType }}</t-tag></div>
          <div class="detail-row"><span>服务门店</span><span class="detail-val">{{ selectedEP.serviceStore }}</span></div>
          <div class="detail-row"><span>所属公司</span><span class="detail-val">{{ selectedEP.company || '个人' }}</span></div>
        </t-card>
        <t-card title="薪酬信息" :bordered="true" style="margin-bottom:16px">
          <div class="detail-row"><span>计薪方式</span><span class="detail-val">{{ selectedEP.payMethod }}</span></div>
          <div class="detail-row"><span>单价</span><span class="detail-val price">¥{{ selectedEP.payRate }}/{{ selectedEP.payMethod === '按件计酬' ? '单' : '时' }}</span></div>
          <div class="detail-row"><span>月均薪酬</span><span class="detail-val price">~¥{{ estimateMonthly(selectedEP) }}/月</span></div>
          <div class="detail-row"><span>开户银行</span><span class="detail-val">{{ selectedEP.bankName }}</span></div>
        </t-card>
        <t-card title="合同信息" :bordered="true">
          <div class="detail-row"><span>合同类型</span><span class="detail-val">{{ selectedEP.contractType }}</span></div>
          <div class="detail-row"><span>合同起期</span><span class="detail-val">{{ selectedEP.contractStart }}</span></div>
          <div class="detail-row"><span>合同到期</span>
            <t-tag v-if="isExpiring(selectedEP.contractEnd)" theme="danger" size="small" variant="light">⚠ {{ selectedEP.contractEnd }}</t-tag>
            <span v-else class="detail-val">{{ selectedEP.contractEnd }}</span>
          </div>
        </t-card>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import hr from '@mock/hr.json'

// ── State ──
const epTab = ref('all')
const epTypeFilter = ref('')
const epStoreFilter = ref('')
const epDetailVisible = ref(false)
const showAddDialog = ref(false)
const showPaymentHistory = ref(false)
const selectedEP = ref<any>(null)
const editingPerson = ref<any>(null)

const defaultForm = () => ({
  name: '', gender: '男', phone: '', personType: '保洁员',
  company: '', serviceStore: '盈隆店', payMethod: '按件计酬',
  payRate: 25, contractEnd: '',
})
const formData = reactive(defaultForm())

const epTabs = [
  { value: 'all', label: '全部' },
  { value: '在岗', label: '在岗' },
  { value: '离职', label: '离职' },
]

const externalPersonnel = hr.externalPersonnel

// ── Computed ──
function isExpiring(end: string): boolean {
  if (!end) return false
  return (new Date(end).getTime() - Date.now()) < 30 * 86400000
}

function daysToExpire(end: string): number {
  if (!end) return 0
  return Math.max(0, Math.ceil((new Date(end).getTime() - Date.now()) / 86400000))
}

function estimateMonthly(row: any): number {
  if (row.payMethod === '按件计酬') return row.payRate * 40 // ~40 tasks/month
  return row.payRate * 160 // ~160 hours/month
}

const filteredEP = computed(() => {
  let list = externalPersonnel
  if (epTab.value === '在岗') list = list.filter((e: any) => e.status === '在岗')
  else if (epTab.value === '离职') list = list.filter((e: any) => e.status === '离职')
  if (epTypeFilter.value) list = list.filter((e: any) => e.personType === epTypeFilter.value)
  if (epStoreFilter.value) list = list.filter((e: any) => e.serviceStore === epStoreFilter.value)
  return list
})

const epStats = computed(() => {
  const active = externalPersonnel.filter((e: any) => e.status === '在岗').length
  const expiring = externalPersonnel.filter((e: any) => isExpiring(e.contractEnd)).length
  const totalMonthly = externalPersonnel.reduce((s: number, e: any) => s + estimateMonthly(e), 0)
  return [
    { label: '总人数', value: externalPersonnel.length + '人', color: '#0052D9' },
    { label: '在岗', value: active + '人', color: '#00A870' },
    { label: '合同临期', value: expiring + '人', color: '#D54941' },
    { label: '月总薪酬', value: '~¥' + totalMonthly.toLocaleString(), color: '#E37318' },
  ]
})

// ── Actions ──
function viewDetail(row: any) {
  selectedEP.value = row
  epDetailVisible.value = true
}

function editPerson(row: any) {
  editingPerson.value = row
  formData.name = row.name
  formData.gender = row.gender
  formData.phone = row.phone
  formData.personType = row.personType
  formData.company = row.company
  formData.serviceStore = row.serviceStore
  formData.payMethod = row.payMethod
  formData.payRate = row.payRate
  formData.contractEnd = row.contractEnd
  showAddDialog.value = true
}

function savePerson() {
  if (!formData.name || !formData.phone) return
  if (editingPerson.value) {
    Object.assign(editingPerson.value, { ...formData })
  } else {
    const newPerson: any = {
      epId: 'EP' + String(externalPersonnel.length + 1).padStart(3, '0'),
      ...formData,
      serviceStart: new Date().toISOString().slice(0, 10),
      contractType: '劳务协议',
      contractStart: new Date().toISOString().slice(0, 10),
      bankName: '',
      bankAccount: '',
      emergencyContact: '',
      emergencyPhone: '',
      status: '在岗',
    }
    externalPersonnel.push(newPerson)
  }
  showAddDialog.value = false
  editingPerson.value = null
  Object.assign(formData, defaultForm())
}

function confirmTerminate(row: any) {
  row.status = '离职'
}

// ── Payment History ──
const paymentHistory = [
  { payId: 'PAY202605_EP001', name: '刘阿姨', period: '2026年5月', amount: 1150, status: '待发放', paidAt: '' },
  { payId: 'PAY202604_EP001', name: '刘阿姨', period: '2026年4月', amount: 1150, status: '已发放', paidAt: '2026-04-28' },
  { payId: 'PAY202603_EP001', name: '刘阿姨', period: '2026年3月', amount: 980, status: '已发放', paidAt: '2026-03-28' },
  { payId: 'PAY202605_EP002', name: '赵阿姨', period: '2026年5月', amount: 900, status: '待发放', paidAt: '' },
  { payId: 'PAY202604_EP002', name: '赵阿姨', period: '2026年4月', amount: 900, status: '已发放', paidAt: '2026-04-28' },
]

const paymentColumns = [
  { colKey: 'payId', title: '编号', width: 120 },
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'period', title: '周期', width: 100 },
  { colKey: 'amount', title: '金额', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'paidAt', title: '发放日期', width: 100 },
]

// ── Table columns ──
const columns = [
  { colKey: 'epId', title: '编号', width: 70 },
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'phone', title: '手机号', width: 110 },
  { colKey: 'personType', title: '类型', width: 80 },
  { colKey: 'serviceStore', title: '服务门店', width: 90 },
  { colKey: 'company', title: '所属公司', width: 130, ellipsis: true },
  { colKey: 'payRate', title: '计薪单价', width: 90 },
  { colKey: 'monthlyPay', title: '月均薪酬', width: 100 },
  { colKey: 'contractEnd', title: '合同到期', width: 130 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 140 },
]
</script>

<style scoped>
.detail-sections { padding: 4px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.detail-val { color: #333; font-weight: 500; }
.detail-val.price { color: #0052D9; font-weight: 600; }
</style>
