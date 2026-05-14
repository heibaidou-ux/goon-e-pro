<template>
  <div>
    <h2 class="page-header">库存管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3">
        <t-select v-model="selectedStore" placeholder="选择仓库/门店" clearable @change="loadInventory">
          <t-option v-for="s in stores" :key="s.storeId" :value="s.storeId" :label="s.storeName" />
        </t-select>
      </t-col>
      <t-col :span="3">
        <t-input v-model="searchText" placeholder="搜索商品..." clearable>
          <template #prefix-icon><t-icon name="search" /></template>
        </t-input>
      </t-col>
      <t-col :span="3">
        <t-button variant="outline" @click="showCheckDialog = true">发起盘点</t-button>
        <t-button variant="outline" style="margin-left:8px" @click="showAlerts = !showAlerts">库存预警</t-button>
      </t-col>
    </t-row>

    <!-- Stock alerts -->
    <t-alert v-if="showAlerts" theme="warning" message="以下商品库存低于安全库存线，建议及时补货" style="margin-bottom:16px" />
    <t-row v-if="showAlerts" :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="a in stockAlerts" :key="a.productId">
        <t-card :bordered="true" theme="warning">
          <div class="alert-item"><span>{{ a.productName }}</span><span class="alert-qty">{{ a.currentQty }}/{{ a.safeStock }}</span></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-tabs v-model="invTab" :list="invTabs" style="margin-bottom:16px" />
      <t-table :data="currentItems" :columns="invColumns" row-key="productId" hover stripe>
        <template #expiryDate="{ row }">
          <span v-if="!row.expiryDate" style="color:#999">—</span>
          <t-tag v-else-if="isExpiringSoon(row.expiryDate)" theme="danger" size="small" variant="light">{{ row.expiryDate }} ⚠</t-tag>
          <span v-else style="font-size:12px">{{ row.expiryDate }}</span>
        </template>
        <template #batch="{ row }"><span style="font-size:12px;color:#666">{{ row.batch || '—' }}</span></template>
      </t-table>
    </t-card>

    <!-- Check Dialog -->
    <t-dialog v-model:visible="showCheckDialog" header="发起盘点" width="400px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="盘点仓库"><t-select v-model="checkStore" :options="stores.map(s=>({value:s.storeId,label:s.storeName}))" /></t-form-item>
        <t-form-item label="盘点备注"><t-input v-model="checkNote" placeholder="如：月度例行盘点" /></t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="showCheckDialog = false">取消</t-button>
          <t-button theme="primary" @click="startCheck" style="margin-left:8px">确认发起</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import supplyChain from '@mock/supply-chain.json'

const selectedStore = ref('STORE-YL')
const searchText = ref('')
const showAlerts = ref(false)
const showCheckDialog = ref(false)
const checkStore = ref('')
const checkNote = ref('')
const invTab = ref('all')

const stores = supplyChain.inventory
const products = supplyChain.products

const invTabs = [
  { value: 'all', label: '全部' },
  { value: '预警', label: '库存预警' },
  { value: '临期', label: '临近到期' },
]

const currentInventory = computed(() => {
  const inv = stores.find(s => s.storeId === selectedStore.value)
  return inv ? inv.items : []
})

const stockAlerts = computed(() => {
  return currentInventory.value.filter(item => {
    const p = products.find(pr => pr.productId === item.productId)
    return p && item.qty < p.safeStock
  }).map(item => {
    const p = products.find(pr => pr.productId === item.productId)
    return { productId: item.productId, productName: item.productName, currentQty: item.qty, safeStock: p?.safeStock || 0 }
  })
})

const isExpiringSoon = (date: string | null) => {
  if (!date) return false
  const days = (new Date(date).getTime() - Date.now()) / 86400000
  return days < 30
}

const currentItems = computed(() => {
  let list = currentInventory.value
  if (searchText.value) list = list.filter(i => i.productName.includes(searchText.value))
  if (invTab.value === '预警') {
    const alertIds = new Set(stockAlerts.value.map(a => a.productId))
    list = list.filter(i => alertIds.has(i.productId))
  }
  if (invTab.value === '临期') list = list.filter(i => isExpiringSoon(i.expiryDate))
  return list
})

function loadInventory() { /* tab switch auto recomputes */ }
function startCheck() { showCheckDialog.value = false }

const invColumns = [
  { colKey: 'productName', title: '商品名称', width: 140 },
  { colKey: 'batch', title: '批次号', width: 120 },
  { colKey: 'qty', title: '库存数量', width: 80 },
  { colKey: 'expiryDate', title: '到期日', width: 110 },
]
</script>

<style scoped>
/* .page-header, .empty-state from global */
.alert-item { display: flex; justify-content: space-between; align-items: center; font-size: 13px; padding: 4px 0; }
.alert-qty { color: #D54941; font-weight: 600; }
</style>
