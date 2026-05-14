<template>
  <div>
    <h2 class="page-header">供应商管理</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-input v-model="searchText" placeholder="搜索供应商名称..." clearable>
          <template #prefix-icon><t-icon name="search" /></template>
        </t-input>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterCategory" placeholder="供应品类" clearable>
          <t-option value="茶叶" label="茶叶" />
          <t-option value="茶具" label="茶具" />
          <t-option value="茶点" label="茶点" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterStatus" placeholder="合作状态" clearable>
          <t-option value="合作中" label="合作中" />
          <t-option value="暂停合作" label="暂停合作" />
          <t-option value="已终止" label="已终止" />
        </t-select>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-table :data="filteredSuppliers" :columns="columns" row-key="supplierId" hover stripe>
        <template #status="{ row }">
          <t-tag :theme="row.status === '合作中' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #totalPurchase="{ row }">¥{{ row.totalPurchase.toLocaleString() }}</template>
        <template #ontimeRate="{ row }">{{ (row.ontimeRate * 100).toFixed(0) }}%</template>
        <template #qualityRate="{ row }">{{ (row.qualityRate * 100).toFixed(0) }}%</template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" @click="showEdit = true; editItem = row">编辑</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="drawerVisible" :header="selectedSupplier?.name" size="420px" :footer="false">
      <div v-if="selectedSupplier" class="detail-sections">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-row"><span>供应商编号</span><span>{{ selectedSupplier.supplierId }}</span></div>
          <div class="detail-row"><span>联系人</span><span>{{ selectedSupplier.contact }}</span></div>
          <div class="detail-row"><span>联系电话</span><span>{{ selectedSupplier.phone }}</span></div>
          <div class="detail-row"><span>供应品类</span><t-tag variant="light">{{ selectedSupplier.category }}</t-tag></div>
          <div class="detail-row"><span>合作状态</span><t-tag :theme="selectedSupplier.status === '合作中' ? 'success' : 'default'" size="small">{{ selectedSupplier.status }}</t-tag></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>财务信息</h4>
          <div class="detail-row"><span>信用代码</span><span>{{ selectedSupplier.creditCode }}</span></div>
          <div class="detail-row"><span>银行账户</span><span>{{ selectedSupplier.bankInfo }}</span></div>
          <div class="detail-row"><span>地址</span><span>{{ selectedSupplier.address }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>采购统计</h4>
          <div class="detail-row"><span>累计采购额</span><span class="price">¥{{ selectedSupplier.totalPurchase.toLocaleString() }}</span></div>
          <div class="detail-row"><span>到货及时率</span><span>{{ (selectedSupplier.ontimeRate * 100).toFixed(0) }}%</span></div>
          <div class="detail-row"><span>商品合格率</span><span>{{ (selectedSupplier.qualityRate * 100).toFixed(0) }}%</span></div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import supplyChain from '@mock/supply-chain.json'

const searchText = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const drawerVisible = ref(false)
const showEdit = ref(false)
const selectedSupplier = ref<any>(null)
const editItem = ref<any>(null)

const suppliers = supplyChain.suppliers

const filteredSuppliers = computed(() => {
  let list = suppliers
  if (searchText.value) list = list.filter(s => s.name.includes(searchText.value))
  if (filterCategory.value) list = list.filter(s => s.category === filterCategory.value)
  if (filterStatus.value) list = list.filter(s => s.status === filterStatus.value)
  return list
})

function viewDetail(s: any) { selectedSupplier.value = s; drawerVisible.value = true }

const columns = [
  { colKey: 'supplierId', title: '编号', width: 80 },
  { colKey: 'name', title: '供应商名称', width: 180, ellipsis: true },
  { colKey: 'contact', title: '联系人', width: 90 },
  { colKey: 'phone', title: '电话', width: 110 },
  { colKey: 'category', title: '品类', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'totalPurchase', title: '累计采购', width: 110 },
  { colKey: 'ontimeRate', title: '到货及时率', width: 90 },
  { colKey: 'qualityRate', title: '合格率', width: 80 },
  { colKey: 'actions', title: '操作', width: 120 },
]
</script>

<style scoped>
.detail-sections { padding: 8px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
