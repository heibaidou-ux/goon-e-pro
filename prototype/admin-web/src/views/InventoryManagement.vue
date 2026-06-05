<template>
  <div>
    <h2 class="page-header">库存管理</h2>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3">
        <t-select v-model="selectedWarehouse" placeholder="选择仓库" clearable @change="loadInventory">
          <t-option v-for="w in warehouses" :key="w.warehouseId" :value="w.warehouseId" :label="w.name" />
        </t-select>
      </t-col>
      <t-col :span="3">
        <t-input v-model="searchText" placeholder="搜索商品..." clearable>
          <template #prefix-icon><t-icon name="search" /></template>
        </t-input>
      </t-col>
      <t-col :span="3">
        <t-button variant="outline" @click="showCheckDialog = true">发起盘点</t-button>
      </t-col>
    </t-row>

    <!-- Loading -->
    <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
      <t-loading :delay="0" />
      <span style="color:#999">加载中...</span>
    </t-space>

    <!-- Error -->
    <t-alert v-else-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

    <!-- Content -->
    <template v-else>
      <t-card :bordered="true">
        <t-tabs v-model="invTab" :list="invTabs" style="margin-bottom:16px" @change="onTabChange" />

        <!-- 全部 / 预警 tab -->
        <template v-if="invTab !== 'lots'">
          <t-table :data="filteredItems" :columns="invColumns" row-key="inventoryId" hover stripe>
            <template #productName="{ row }">
              {{ productNames[row.productId] || row.productId }}
            </template>
            <template #quantity="{ row }">
              <span :class="{ 'text-danger': row.quantity <= 0 }">{{ row.quantity }}</span>
            </template>
            <template #batchNo="{ row }">
              <span style="font-size:12px;color:#666">{{ row.batchNo || '—' }}</span>
            </template>
            <template #expiryDate="{ row }">
              <span v-if="!row.expiryDate" style="color:#999">—</span>
              <t-tag v-else-if="isExpiringSoon(row.expiryDate)" theme="danger" size="small" variant="light">{{ row.expiryDate }} ⚠</t-tag>
              <span v-else style="font-size:12px">{{ row.expiryDate }}</span>
            </template>
          </t-table>

          <!-- Empty -->
          <t-empty v-if="filteredItems.length === 0" description="暂无库存数据" style="padding:40px" />
        </template>

        <!-- 批次 tab -->
        <template v-if="invTab === 'lots'">
          <t-table :data="lotItems" :columns="lotColumns" row-key="lotId" hover stripe>
            <template #productName="{ row }">
              {{ productNames[row.productId] || row.productId }}
            </template>
            <template #expiryDate="{ row }">
              <span v-if="!row.expiryDate" style="color:#999">—</span>
              <t-tag v-else-if="isExpiringSoon(row.expiryDate)" theme="danger" size="small" variant="light">{{ row.expiryDate }} ⚠</t-tag>
              <span v-else style="font-size:12px">{{ row.expiryDate }}</span>
            </template>
            <template #status="{ row }">
              <t-tag :theme="row.status === 'Normal' ? 'success' : 'default'" size="small">{{ row.status }}</t-tag>
            </template>
          </t-table>
          <t-empty v-if="lotItems.length === 0" description="暂无批次数据" style="padding:40px" />
        </template>
      </t-card>
    </template>

    <!-- Check Dialog -->
    <t-dialog v-model:visible="showCheckDialog" header="发起盘点" width="400px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="盘点仓库">
          <t-select v-model="checkWarehouse" :options="warehouses.map(w=>({value:w.warehouseId,label:w.name}))" />
        </t-form-item>
        <t-form-item label="盘点备注">
          <t-input v-model="checkNote" placeholder="如：月度例行盘点" />
        </t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="showCheckDialog = false">取消</t-button>
          <t-button theme="primary" @click="startCheck" style="margin-left:8px" :loading="savingCheck">确认发起</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { productApi } from '../services/api'

const selectedWarehouse = ref('')
const searchText = ref('')
const showCheckDialog = ref(false)
const checkWarehouse = ref('')
const checkNote = ref('')
const invTab = ref('all')
const loading = ref(false)
const loadError = ref('')
const savingCheck = ref(false)

const warehouses = ref<any[]>([])
const inventoryItems = ref<any[]>([])
const lotItems = ref<any[]>([])
const productNames = ref<Record<string, string>>({})

const invTabs = [
  { value: 'all', label: '全部库存' },
  { value: '预警', label: '库存预警' },
  { value: 'lots', label: '批次明细' },
]

const invColumns = [
  { colKey: 'productName', title: '商品名称', width: 160 },
  { colKey: 'quantity', title: '数量', width: 80 },
  { colKey: 'lastCountDate', title: '最近盘点', width: 110 },
]

const lotColumns = [
  { colKey: 'productName', title: '商品名称', width: 140 },
  { colKey: 'batchNo', title: '批次号', width: 130 },
  { colKey: 'quantity', title: '数量', width: 60 },
  { colKey: 'unitPrice', title: '单价', width: 70 },
  { colKey: 'productionDate', title: '生产日', width: 110 },
  { colKey: 'expiryDate', title: '到期日', width: 110 },
  { colKey: 'status', title: '状态', width: 70 },
]

// ── Load ──

async function loadWarehouses() {
  try {
    warehouses.value = await productApi.warehouses()
    if (warehouses.value.length > 0 && !selectedWarehouse.value) {
      selectedWarehouse.value = warehouses.value[0].warehouseId
    }
  } catch (e: any) {
    console.warn('加载仓库失败:', e)
  }
}

async function loadInventory() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await productApi.inventory({
      page_size: 200,
      warehouseId: selectedWarehouse.value || undefined,
    })
    inventoryItems.value = result.items

    // Fetch product names
    const names: Record<string, string> = {}
    for (const item of result.items) {
      if (!names[item.productId]) {
        try {
          const p = await productApi.get(item.productId)
          names[item.productId] = p.name
        } catch { names[item.productId] = item.productId }
      }
    }
    productNames.value = { ...productNames.value, ...names }
  } catch (e: any) {
    loadError.value = '加载库存失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

async function loadLots() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await productApi.inventoryLots({
      page_size: 200,
      warehouseId: selectedWarehouse.value || undefined,
    })
    lotItems.value = result.items || []

    const names: Record<string, string> = {}
    for (const item of lotItems.value) {
      if (!names[item.productId]) {
        try {
          const p = await productApi.get(item.productId)
          names[item.productId] = p.name
        } catch { names[item.productId] = item.productId }
      }
    }
    productNames.value = { ...productNames.value, ...names }
  } catch (e: any) {
    loadError.value = '加载批次数据失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

// ── Computed ──

const filteredItems = computed(() => {
  let list = inventoryItems.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(i =>
      (productNames.value[i.productId] || '').toLowerCase().includes(q) ||
      i.productId.toLowerCase().includes(q)
    )
  }
  if (invTab.value === '预警') {
    list = list.filter(i => i.quantity <= 0)
  }
  return list
})

const isExpiringSoon = (date: string) => {
  if (!date) return false
  const days = (new Date(date).getTime() - Date.now()) / 86400000
  return days < 30
}

// ── Actions ──

function onTabChange(val: string) {
  if (val === 'lots') loadLots()
}

async function startCheck() {
  if (!checkWarehouse.value) return
  savingCheck.value = true
  try {
    await productApi.createStockCount({
      warehouseId: checkWarehouse.value,
      type: 'Full',
      lines: inventoryItems.value.map((i: any) => ({
        productId: i.productId,
        bookQuantity: i.quantity,
        actualQuantity: i.quantity,
        unitPrice: 0,
      })),
    })
    showCheckDialog.value = false
  } catch (e: any) {
    console.error('发起盘点失败:', e)
  } finally {
    savingCheck.value = false
  }
}

// ── Init ──

onMounted(async () => {
  await loadWarehouses()
  await loadInventory()
})
</script>

<style scoped>
.text-danger { color: #D54941; font-weight: 600; }
</style>
