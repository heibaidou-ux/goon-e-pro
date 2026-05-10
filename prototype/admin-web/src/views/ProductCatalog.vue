<template>
  <div>
    <h2 class="page-header">商品目录管理</h2>

    <t-card :bordered="true">
      <t-row :gutter="16" style="margin-bottom:16px">
        <t-col :span="3">
          <t-input v-model="searchText" placeholder="搜索商品名称/编码..." clearable>
            <template #prefix-icon><t-icon name="search" /></template>
          </t-input>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterCategory" placeholder="商品分类" clearable>
            <t-option value="茶叶" label="茶叶" />
            <t-option value="茶具" label="茶具" />
            <t-option value="茶点" label="茶点" />
            <t-option value="套餐" label="套餐" />
            <t-option value="其他" label="其他" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterStatus" placeholder="上架状态" clearable>
            <t-option value="上架" label="已上架" />
            <t-option value="下架" label="已下架" />
          </t-select>
        </t-col>
        <t-col :span="5" style="text-align:right">
          <t-button theme="primary" variant="outline" @click="showAddProduct = true">+ 新增商品</t-button>
          <t-button variant="outline" style="margin-left:8px">导入</t-button>
          <t-button variant="outline" style="margin-left:8px">导出</t-button>
        </t-col>
      </t-row>

      <t-table :data="filteredProducts" :columns="productColumns" row-key="productId" hover stripe @row-click="viewDetail">
        <template #category="{ row }">
          <t-tag variant="light">{{ row.category }} - {{ row.subCategory }}</t-tag>
        </template>
        <template #isFood="{ row }">
          <t-tag v-if="row.isFood" theme="warning" variant="light" size="small">食品</t-tag>
          <t-tag v-else variant="light" size="small">非食品</t-tag>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '上架' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click.stop="editProduct(row)">编辑</t-button>
            <t-button size="small" variant="text" :theme="row.status === '上架' ? 'warning' : 'success'" @click.stop="toggleStatus(row)">
              {{ row.status === '上架' ? '下架' : '上架' }}
            </t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- Product Detail Drawer -->
    <t-drawer v-model:visible="drawerVisible" :header="`${selectedProduct?.name} 详情`" size="420px" :footer="false">
      <div v-if="selectedProduct" class="detail-sections">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-row"><span>商品编码</span><span>{{ selectedProduct.code }}</span></div>
          <div class="detail-row"><span>商品名称</span><span>{{ selectedProduct.name }}</span></div>
          <div class="detail-row"><span>分类</span><span>{{ selectedProduct.category }} - {{ selectedProduct.subCategory }}</span></div>
          <div class="detail-row"><span>品牌</span><span>{{ selectedProduct.brand || '—' }}</span></div>
          <div class="detail-row"><span>规格</span><span>{{ selectedProduct.spec }}</span></div>
          <div class="detail-row"><span>单位</span><span>{{ selectedProduct.unit }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>价格信息</h4>
          <div class="detail-row"><span>内部结算价</span><span class="price">¥{{ selectedProduct.internalPrice }}</span></div>
          <div class="detail-row"><span>建议零售价</span><span class="price">¥{{ selectedProduct.retailPrice }}</span></div>
          <div class="detail-row"><span>市场参考采购价</span><span class="price">¥{{ selectedProduct.marketPrice }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>库存参数</h4>
          <div class="detail-row"><span>默认供应商</span><span>{{ selectedProduct.defaultSupplier }}</span></div>
          <div class="detail-row"><span>采购周期</span><span>{{ selectedProduct.leadTime }}天</span></div>
          <div class="detail-row"><span>安全库存</span><span>{{ selectedProduct.safeStock }}{{ selectedProduct.unit }}</span></div>
          <div class="detail-row"><span>最大库存</span><span>{{ selectedProduct.maxStock }}{{ selectedProduct.unit }}</span></div>
        </div>
      </div>
    </t-drawer>

    <!-- Add Product Dialog (simplified) -->
    <t-dialog v-model:visible="showAddProduct" header="新增商品" width="560px" :footer="false">
      <t-form :data="newProduct" layout="vertical">
        <t-row :gutter="16">
          <t-col :span="12">
            <t-form-item label="商品名称"><t-input v-model="newProduct.name" placeholder="请输入商品名称" /></t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="分类">
              <t-select v-model="newProduct.category" placeholder="选择分类">
                <t-option value="茶叶" label="茶叶" /><t-option value="茶具" label="茶具" />
                <t-option value="茶点" label="茶点" /><t-option value="套餐" label="套餐" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="规格"><t-input v-model="newProduct.spec" placeholder="如：250g/罐" /></t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="内部结算价"><t-input v-model="newProduct.internalPrice" type="number" /></t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="建议零售价"><t-input v-model="newProduct.retailPrice" type="number" /></t-form-item>
          </t-col>
        </t-row>
        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="showAddProduct = false">取消</t-button>
          <t-button theme="primary" @click="addProduct" style="margin-left:8px">提交审批</t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import supplyChain from '@mock/supply-chain.json'

const searchText = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const drawerVisible = ref(false)
const showAddProduct = ref(false)
const selectedProduct = ref<any>(null)

const newProduct = reactive({ name: '', category: '', spec: '', internalPrice: 0, retailPrice: 0 })

const products = supplyChain.products

const filteredProducts = computed(() => {
  let list = products
  if (searchText.value) { list = list.filter(p => p.name.includes(searchText.value) || p.code.includes(searchText.value)) }
  if (filterCategory.value) { list = list.filter(p => p.category === filterCategory.value) }
  if (filterStatus.value) { list = list.filter(p => p.status === filterStatus.value) }
  return list
})

const productColumns = [
  { colKey: 'code', title: '编码', width: 120 },
  { colKey: 'name', title: '商品名称', width: 150 },
  { colKey: 'category', title: '分类', width: 130 },
  { colKey: 'spec', title: '规格', width: 100 },
  { colKey: 'isFood', title: '食品', width: 70 },
  { colKey: 'internalPrice', title: '结算价', width: 80 },
  { colKey: 'retailPrice', title: '零售价', width: 80 },
  { colKey: 'safeStock', title: '安全库存', width: 80 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 140 },
]

function viewDetail({ row }: any) { selectedProduct.value = row; drawerVisible.value = true }
function editProduct(product: any) { selectedProduct.value = product; drawerVisible.value = true }
function toggleStatus(product: any) { product.status = product.status === '上架' ? '下架' : '上架' }
function addProduct() {
  if (!newProduct.name || !newProduct.category) return
  const id = 'P' + String(products.length + 1).padStart(3, '0')
  products.push({ productId: id, code: 'NEW-' + id, name: newProduct.name, category: newProduct.category, subCategory: '', brand: '', spec: newProduct.spec, unit: '份', isFood: false, shelfLife: null, internalPrice: Number(newProduct.internalPrice), retailPrice: Number(newProduct.retailPrice), marketPrice: 0, defaultSupplier: '', leadTime: 1, safeStock: 10, maxStock: 100, status: '上架', image: '' })
  showAddProduct.value = false
  Object.assign(newProduct, { name: '', category: '', spec: '', internalPrice: 0, retailPrice: 0 })
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.detail-sections { padding: 8px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
