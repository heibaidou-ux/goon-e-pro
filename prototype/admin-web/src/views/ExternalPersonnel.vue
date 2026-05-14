<template>
  <div>
    <h2 class="page-header">外聘人员管理</h2>

    <t-card :bordered="true">
      <t-tabs v-model="epTab" :list="epTabs" style="margin-bottom:16px" />
      <t-table :data="filteredEP" :columns="columns" row-key="epId" hover stripe>
        <template #payRate="{ row }">{{ row.payMethod === '按件计酬' ? `¥${row.payRate}/单` : `¥${row.payRate}/时` }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '在岗' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #contractEnd="{ row }">
          <t-tag v-if="isExpiring(row.contractEnd)" theme="danger" size="small" variant="light">⚠ {{ row.contractEnd }}</t-tag>
          <span v-else style="font-size:12px">{{ row.contractEnd }}</span>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="selectedEP=row;epDetailVisible=true">详情</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="epDetailVisible" header="外聘人员详情" size="400px" :footer="false">
      <div v-if="selectedEP" class="detail-sections">
        <div class="detail-row"><span>姓名</span><span>{{ selectedEP.name }}</span></div>
        <div class="detail-row"><span>手机号</span><span>{{ selectedEP.phone }}</span></div>
        <div class="detail-row"><span>服务门店</span><span>{{ selectedEP.serviceStore }}</span></div>
        <div class="detail-row"><span>所属公司</span><span>{{ selectedEP.company || '个人' }}</span></div>
        <div class="detail-row"><span>计薪方式</span><span>{{ selectedEP.payMethod }}，¥{{ selectedEP.payRate }}/单</span></div>
        <div class="detail-row"><span>合同到期</span><span>{{ selectedEP.contractEnd }}</span></div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import hr from '@mock/hr.json'

const epTab = ref('all')
const epDetailVisible = ref(false)
const selectedEP = ref<any>(null)

const externalPersonnel = hr.externalPersonnel

const epTabs = [
  { value: 'all', label: '全部' },
  { value: '在岗', label: '在岗' },
  { value: '离职', label: '离职' },
]

function isExpiring(end: string): boolean {
  return (new Date(end).getTime() - Date.now()) < 30 * 86400000
}

const filteredEP = computed(() => {
  if (epTab.value === 'all') return externalPersonnel
  return externalPersonnel.filter((e: any) => e.status === epTab.value)
})

const columns = [
  { colKey: 'epId', title: '编号', width: 80 },
  { colKey: 'name', title: '姓名', width: 80 },
  { colKey: 'phone', title: '手机号', width: 110 },
  { colKey: 'serviceStore', title: '服务门店', width: 90 },
  { colKey: 'company', title: '所属公司', width: 130, ellipsis: true },
  { colKey: 'payRate', title: '计薪单价', width: 100 },
  { colKey: 'contractEnd', title: '合同到期', width: 100 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 80 },
]
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
</style>
