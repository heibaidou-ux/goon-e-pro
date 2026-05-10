<template>
  <div>
    <h2 class="page-header">固定资产管理</h2>

    <t-alert message="固定资产标准：单价≥2000元且使用年限超过一年。支持直线折旧法。" theme="info" style="margin-bottom:20px" />

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="2" v-for="s in assetStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="3">
          <t-input v-model="searchText" placeholder="搜索资产名称/编号..." clearable>
            <template #prefix-icon><t-icon name="search" /></template>
          </t-input>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterAssetStatus" placeholder="资产状态" clearable>
            <t-option value="使用中" label="使用中" />
            <t-option value="闲置" label="闲置" />
            <t-option value="维修" label="维修" />
            <t-option value="已报废" label="已报废" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterCategory" placeholder="资产类别" clearable>
            <t-option value="电器" label="电器" />
            <t-option value="电子设备" label="电子设备" />
            <t-option value="家具" label="家具" />
          </t-select>
        </t-col>
      </t-row>

      <t-table :data="filteredAssets" :columns="columns" row-key="assetId" hover stripe>
        <template #originalValue="{ row }">¥{{ row.originalValue.toLocaleString() }}</template>
        <template #currentValue="{ row }">¥{{ row.currentValue.toLocaleString() }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '使用中' ? 'success' : row.status === '闲置' ? 'default' : row.status === '维修' ? 'warning' : 'danger'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" @click="showDispose(row)" v-if="hasPermission('BTN_DISPOSE')">处置</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <t-drawer v-model:visible="detailVisible" :header="`${selectedAsset?.name} 详情`" size="400px" :footer="false">
      <div v-if="selectedAsset" class="detail-sections">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-row"><span>资产编号</span><span>{{ selectedAsset.assetId }}</span></div>
          <div class="detail-row"><span>类别</span><t-tag variant="light">{{ selectedAsset.category }}</t-tag></div>
          <div class="detail-row"><span>购入日期</span><span>{{ selectedAsset.purchaseDate }}</span></div>
          <div class="detail-row"><span>原值</span><span class="price">¥{{ selectedAsset.originalValue.toLocaleString() }}</span></div>
          <div class="detail-row"><span>当前净值</span><span class="price">¥{{ selectedAsset.currentValue.toLocaleString() }}</span></div>
          <div class="detail-row"><span>使用部门</span><span>{{ selectedAsset.department }}</span></div>
          <div class="detail-row"><span>存放位置</span><span>{{ selectedAsset.location }}</span></div>
          <div class="detail-row"><span>供应商</span><span>{{ selectedAsset.supplier }}</span></div>
          <div class="detail-row"><span>状态</span><t-tag :theme="selectedAsset.status==='使用中'?'success':'default'" size="small">{{ selectedAsset.status }}</t-tag></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>折旧信息</h4>
          <div class="detail-row"><span>折旧年限</span><span>{{ selectedAsset.depreciationYears }}年</span></div>
          <div class="detail-row"><span>残值率</span><span>{{ (selectedAsset.residualRate * 100).toFixed(0) }}%</span></div>
          <div class="detail-row"><span>月折旧额</span><span class="price">¥{{ monthlyDepreciation.toLocaleString() }}</span></div>
        </div>
      </div>
    </t-drawer>

    <t-dialog v-model:visible="disposeVisible" header="资产处置" width="400px" :footer="false">
      <div v-if="disposeAsset">
        <div class="detail-row" style="margin-bottom:12px"><span>处置资产</span><span class="price">{{ disposeAsset.name }}</span></div>
        <t-form layout="vertical">
          <t-form-item label="处置类型">
            <t-select v-model="disposeType">
              <t-option value="报废" label="报废" />
              <t-option value="出售" label="出售" />
              <t-option value="调拨" label="调拨" />
            </t-select>
          </t-form-item>
          <t-form-item label="处置原因"><t-input v-model="disposeReason" placeholder="请填写处置原因" /></t-form-item>
          <div style="text-align:right">
            <t-button variant="outline" @click="disposeVisible = false">取消</t-button>
            <t-button theme="primary" @click="confirmDispose" style="margin-left:8px">提交申请</t-button>
          </div>
        </t-form>
      </div>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { hasPermission } from '@/utils/permission'
import finance from '@mock/finance.json'

const searchText = ref('')
const filterAssetStatus = ref('')
const filterCategory = ref('')
const detailVisible = ref(false)
const disposeVisible = ref(false)
const selectedAsset = ref<any>(null)
const disposeAsset = ref<any>(null)
const disposeType = ref('报废')
const disposeReason = ref('')

const assets = finance.fixedAssets

const monthlyDepreciation = computed(() => {
  if (!selectedAsset.value) return 0
  const a = selectedAsset.value
  return Math.round(a.originalValue * (1 - a.residualRate) / a.depreciationYears / 12)
})

const assetStats = computed(() => {
  const total = assets.reduce((s, a) => s + a.originalValue, 0)
  return [
    { label: '资产总数', value: assets.length, color: '#0052D9' },
    { label: '资产原值', value: '¥' + total.toLocaleString(), color: '#E37318' },
    { label: '使用中', value: assets.filter(a => a.status === '使用中').length, color: '#00A870' },
    { label: '月折旧合计', value: '¥' + assets.reduce((s, a) => s + Math.round(a.originalValue * (1 - a.residualRate) / a.depreciationYears / 12), 0).toLocaleString(), color: '#D54941' },
  ]
})

const filteredAssets = computed(() => {
  let list = assets
  if (searchText.value) list = list.filter(a => a.name.includes(searchText.value) || a.assetId.includes(searchText.value))
  if (filterAssetStatus.value) list = list.filter(a => a.status === filterAssetStatus.value)
  if (filterCategory.value) list = list.filter(a => a.category === filterCategory.value)
  return list
})

function viewDetail(a: any) { selectedAsset.value = a; detailVisible.value = true }
function showDispose(a: any) { disposeAsset.value = a; disposeVisible.value = true }
function confirmDispose() {
  if (disposeAsset.value) { disposeAsset.value.status = '已报废' }
  disposeVisible.value = false
}

const columns = [
  { colKey: 'assetId', title: '编号', width: 70 },
  { colKey: 'name', title: '资产名称', width: 150 },
  { colKey: 'category', title: '类别', width: 80 },
  { colKey: 'purchaseDate', title: '购入日期', width: 100 },
  { colKey: 'originalValue', title: '原值', width: 100 },
  { colKey: 'currentValue', title: '净值', width: 100 },
  { colKey: 'department', title: '使用部门', width: 90 },
  { colKey: 'location', title: '位置', width: 100 },
  { colKey: 'status', title: '状态', width: 80 },
  { colKey: 'actions', title: '操作', width: 120 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.stat-card { text-align: center; padding: 8px 0; }
.stat-num { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: #999; }
.detail-sections { padding: 8px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
