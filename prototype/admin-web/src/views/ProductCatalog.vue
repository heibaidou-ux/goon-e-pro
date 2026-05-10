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
          <t-button theme="primary" @click="openAddProduct">+ 新增商品</t-button>
          <t-button variant="outline" style="margin-left:8px">导入</t-button>
          <t-button variant="outline" style="margin-left:8px">导出</t-button>
        </t-col>
      </t-row>

      <t-table :data="filteredProducts" :columns="productColumns" row-key="productId" hover stripe>
        <template #image="{ row }">
          <div class="product-thumb" v-if="row.image">
            <img :src="row.image" :alt="row.name" @error="row.image = ''" />
          </div>
          <div class="product-thumb placeholder" v-else :style="{ background: nameGradient(row.name) }">
            {{ row.name.charAt(0) }}
          </div>
        </template>
        <template #category="{ row }">
          <t-tag variant="light">{{ row.category }} - {{ row.subCategory }}</t-tag>
        </template>
        <template #spec="{ row }">
          <t-tag size="small" variant="outline">{{ row.spec }}</t-tag>
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
            <t-button size="small" variant="text" theme="primary" @click.stop="viewDetail(row)">详情</t-button>
            <t-button size="small" variant="text" theme="default" @click.stop="openEditProduct(row)">编辑</t-button>
            <t-button size="small" variant="text" :theme="row.status === '上架' ? 'warning' : 'success'" @click.stop="toggleStatus(row)">
              {{ row.status === '上架' ? '下架' : '上架' }}
            </t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- Product Detail Drawer -->
    <t-drawer v-model:visible="drawerVisible" :header="selectedProduct?.name || '商品详情'" size="460px" :footer="false">
      <div v-if="selectedProduct" class="detail-wrap">
        <!-- Header Image -->
        <div class="detail-header-img" v-if="selectedProduct.image">
          <img :src="selectedProduct.image" :alt="selectedProduct.name" />
        </div>
        <div class="detail-header-img placeholder" v-else :style="{ background: nameGradient(selectedProduct.name) }">
          <span class="placeholder-text">{{ selectedProduct.name.charAt(0) }}</span>
        </div>

        <!-- 基本信息卡片 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-row"><span class="label">商品编码</span><span>{{ selectedProduct.code }}</span></div>
            <div class="detail-row"><span class="label">商品名称</span><span class="name">{{ selectedProduct.name }}</span></div>
            <div class="detail-row"><span class="label">品牌</span><span>{{ selectedProduct.brand || '—' }}</span></div>
            <div class="detail-row"><span class="label">分类</span><span><t-tag variant="light" size="small">{{ selectedProduct.category }} / {{ selectedProduct.subCategory }}</t-tag></span></div>
            <div class="detail-row"><span class="label">规格</span><span><t-tag variant="outline" size="small">{{ selectedProduct.spec }}</t-tag></span></div>
            <div class="detail-row"><span class="label">单位</span><span>{{ selectedProduct.unit }}</span></div>
            <div class="detail-row"><span class="label">食品标识</span><span><t-tag :theme="selectedProduct.isFood ? 'warning' : 'default'" size="small" variant="light">{{ selectedProduct.isFood ? '食品' : '非食品' }}</t-tag></span></div>
            <div class="detail-row" v-if="selectedProduct.isFood && selectedProduct.shelfLife"><span class="label">保质期</span><span>{{ selectedProduct.shelfLife }}天</span></div>
          </div>
        </div>

        <t-divider />

        <!-- 价格卡片 -->
        <div class="detail-section">
          <h4>价格信息</h4>
          <div class="price-cards">
            <div class="price-card">
              <div class="price-label">内部结算价</div>
              <div class="price-value" style="color:#0052D9">¥{{ selectedProduct.internalPrice }}</div>
            </div>
            <div class="price-card">
              <div class="price-label">建议零售价</div>
              <div class="price-value" style="color:#E37318">¥{{ selectedProduct.retailPrice }}</div>
            </div>
            <div class="price-card">
              <div class="price-label">市场采购参考</div>
              <div class="price-value" style="color:#999">¥{{ selectedProduct.marketPrice }}</div>
            </div>
          </div>
        </div>

        <t-divider />

        <!-- 故事/冲泡建议 -->
        <div class="detail-section" v-if="selectedProduct.story">
          <h4><span class="story-icon">📖</span> 产品故事</h4>
          <div class="story-box">
            <p>{{ selectedProduct.story }}</p>
            <div class="story-meta" v-if="selectedProduct.origin">
              <t-tag variant="light" size="small">📍 {{ selectedProduct.origin }}</t-tag>
            </div>
            <div class="brewing-tips" v-if="selectedProduct.brewingTips">
              <div class="tips-title">冲泡建议</div>
              <div class="tips-grid">
                <span class="tip" v-if="selectedProduct.brewingTips.waterTemp !== '—'"><span class="tip-icon">🌡️</span> {{ selectedProduct.brewingTips.waterTemp }}</span>
                <span class="tip" v-if="selectedProduct.brewingTips.steepTime !== '—'"><span class="tip-icon">⏱️</span> {{ selectedProduct.brewingTips.steepTime }}</span>
                <span class="tip" v-if="selectedProduct.brewingTips.vessel !== '—'"><span class="tip-icon">🫖</span> {{ selectedProduct.brewingTips.vessel }}</span>
                <span class="tip" v-if="selectedProduct.brewingTips.method !== '—'"><span class="tip-icon">💧</span> {{ selectedProduct.brewingTips.method }}</span>
              </div>
            </div>
          </div>
        </div>

        <t-divider />

        <!-- 库存参数 -->
        <div class="detail-section">
          <h4>库存参数</h4>
          <div class="detail-grid">
            <div class="detail-row"><span class="label">默认供应商</span><span>{{ selectedProduct.defaultSupplier || '—' }}</span></div>
            <div class="detail-row"><span class="label">采购周期</span><span>{{ selectedProduct.leadTime }}天</span></div>
            <div class="detail-row"><span class="label">安全库存</span><span>{{ selectedProduct.safeStock }}{{ selectedProduct.unit }}</span></div>
            <div class="detail-row"><span class="label">最大库存</span><span>{{ selectedProduct.maxStock }}{{ selectedProduct.unit }}</span></div>
          </div>
        </div>

        <t-divider />

        <t-button block variant="outline" theme="primary" @click="openEditProduct(selectedProduct)">✏️ 编辑商品</t-button>
      </div>
    </t-drawer>

    <!-- Add/Edit Product Dialog -->
    <t-dialog v-model:visible="showProductForm" :header="editingProduct ? '编辑商品' : '新增商品'" width="640px" :footer="false">
      <t-form :data="formData" layout="vertical">
        <!-- Image Upload -->
        <t-form-item label="商品图片">
          <div class="upload-zone"
            @dragover.prevent="dragOver = true"
            @dragleave.prevent="dragOver = false"
            @drop.prevent="handleDrop"
            @paste="handlePaste"
            :class="{ 'drag-over': dragOver }"
            tabindex="0"
            @click="triggerFilePicker">
            <input type="file" ref="fileInput" accept="image/*" style="display:none" @change="handleFileChange" />
            <div v-if="formData.imagePreview" class="upload-preview">
              <img :src="formData.imagePreview" alt="预览" />
              <div class="upload-overlay">
                <span class="upload-overlay-btn" @click.stop="removeImage">删除</span>
                <span class="upload-overlay-btn" @click.stop="triggerFilePicker">更换</span>
              </div>
            </div>
            <div v-else class="upload-placeholder">
              <span class="upload-icon">📷</span>
              <span>点击、拖拽图片至此或粘贴上传</span>
              <span class="upload-hint">支持 JPG / PNG / GIF，建议 1:1 比例</span>
            </div>
          </div>
        </t-form-item>

        <t-row :gutter="16">
          <t-col :span="8">
            <t-form-item label="商品名称">
              <t-input v-model="formData.name" placeholder="请输入商品名称" />
            </t-form-item>
          </t-col>
          <t-col :span="4">
            <t-form-item label="品牌">
              <t-input v-model="formData.brand" placeholder="品牌" />
            </t-form-item>
          </t-col>
        </t-row>

        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="分类">
              <t-select v-model="formData.category" placeholder="选择分类" @change="onCategoryChange">
                <t-option value="茶叶" label="茶叶" />
                <t-option value="茶具" label="茶具" />
                <t-option value="茶点" label="茶点" />
                <t-option value="套餐" label="套餐" />
                <t-option value="其他" label="其他" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="子分类">
              <t-select v-model="formData.subCategory" placeholder="选择子分类">
                <t-option v-for="s in subCategoryOptions" :key="s" :value="s" :label="s" />
              </t-select>
            </t-form-item>
          </t-col>
        </t-row>

        <t-row :gutter="16">
          <t-col :span="12">
            <t-form-item label="规格">
              <div class="spec-wrapper">
                <t-input v-model="formData.spec" placeholder="如：250g/罐" />
                <div class="spec-quick-tags">
                  <t-tag
                    v-for="opt in specOptions"
                    :key="opt"
                    size="small"
                    variant="outline"
                    :theme="formData.spec === opt ? 'primary' : 'default'"
                    style="cursor:pointer;margin-right:4px;margin-bottom:4px"
                    @click="formData.spec = opt">
                    {{ opt }}
                  </t-tag>
                </div>
              </div>
            </t-form-item>
          </t-col>
        </t-row>

        <t-row :gutter="16">
          <t-col :span="4">
            <t-form-item label="单位">
              <t-select v-model="formData.unit" placeholder="选择">
                <t-option value="罐" label="罐" />
                <t-option value="饼" label="饼" />
                <t-option value="份" label="份" />
                <t-option value="盒" label="盒" />
                <t-option value="只" label="只" />
                <t-option value="把" label="把" />
                <t-option value="套" label="套" />
                <t-option value="件" label="件" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="4">
            <t-form-item label="内部结算价">
              <t-input v-model.number="formData.internalPrice" type="number" prefix="¥" />
            </t-form-item>
          </t-col>
          <t-col :span="4">
            <t-form-item label="建议零售价">
              <t-input v-model.number="formData.retailPrice" type="number" prefix="¥" />
            </t-form-item>
          </t-col>
        </t-row>

        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="食品标识">
              <t-switch v-model="formData.isFood" />
            </t-form-item>
          </t-col>
          <t-col :span="6" v-if="formData.isFood">
            <t-form-item label="保质期（天）">
              <t-input v-model.number="formData.shelfLife" type="number" />
            </t-form-item>
          </t-col>
        </t-row>

        <t-form-item label="产品故事 / 冲泡建议">
          <t-textarea v-model="formData.story" placeholder="描述产品故事、产地特色、冲泡建议等内容，将展示在客人端" :rows="3" />
        </t-form-item>
        <t-form-item label="产地">
          <t-input v-model="formData.origin" placeholder="如：杭州西湖" />
        </t-form-item>

        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="showProductForm = false">取消</t-button>
          <t-button theme="primary" @click="saveProduct" style="margin-left:8px">{{ editingProduct ? '保存修改' : '提交审批' }}</t-button>
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
const showProductForm = ref(false)
const selectedProduct = ref<any>(null)
const editingProduct = ref<any>(null)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

const defaultForm = () => ({
  name: '', category: '茶叶', subCategory: '绿茶', brand: '高岸',
  spec: '', unit: '罐', isFood: true, shelfLife: 365,
  internalPrice: 0, retailPrice: 0,
  story: '', origin: '',
  imagePreview: '', imageData: '',
})
const formData = reactive(defaultForm())

const specOptions = ['250g/罐', '200g/罐', '357g/饼', '150g/盒', '200g/份', '单只装', '100g/罐', '1份', '200ml']
const subCategoryMap: Record<string, string[]> = {
  '茶叶': ['绿茶', '红茶', '乌龙茶', '普洱茶'],
  '茶具': ['茶壶', '茶杯', '茶道配件'],
  '茶点': ['糕点', '坚果'],
  '套餐': ['双人套餐', '商务套餐'],
  '其他': ['其他'],
}
const subCategoryOptions = computed(() => subCategoryMap[formData.category] || ['其他'])

function onCategoryChange(val: string) {
  const opts = subCategoryMap[val] || ['其他']
  formData.subCategory = opts[0]
}

const products = supplyChain.products

const filteredProducts = computed(() => {
  let list = products
  if (searchText.value) list = list.filter(p => p.name.includes(searchText.value) || p.code.includes(searchText.value))
  if (filterCategory.value) list = list.filter(p => p.category === filterCategory.value)
  if (filterStatus.value) list = list.filter(p => p.status === filterStatus.value)
  return list
})

const productColumns = [
  { colKey: 'image', title: '图片', width: 70 },
  { colKey: 'code', title: '编码', width: 110 },
  { colKey: 'name', title: '商品名称', width: 140 },
  { colKey: 'category', title: '分类', width: 130 },
  { colKey: 'spec', title: '规格', width: 100 },
  { colKey: 'isFood', title: '食品', width: 65 },
  { colKey: 'internalPrice', title: '结算价', width: 75 },
  { colKey: 'retailPrice', title: '零售价', width: 75 },
  { colKey: 'safeStock', title: '安全库存', width: 75 },
  { colKey: 'status', title: '状态', width: 65 },
  { colKey: 'actions', title: '操作', width: 180 },
]

const nameGradients = ['#e8f5e9','#fff3e0','#fce4ec','#e3f2fd','#f3e5f5','#f1f8e9','#fff8e1','#efebe9']
function nameGradient(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return nameGradients[Math.abs(hash) % nameGradients.length]
}

function viewDetail(product: any) {
  selectedProduct.value = product
  drawerVisible.value = true
}

function openAddProduct() {
  editingProduct.value = null
  Object.assign(formData, defaultForm())
  showProductForm.value = true
}

function openEditProduct(product: any) {
  editingProduct.value = product
  drawerVisible.value = true
  // Populate form
  formData.name = product.name
  formData.category = product.category
  formData.subCategory = product.subCategory
  formData.brand = product.brand || '高岸'
  formData.spec = product.spec
  formData.unit = product.unit
  formData.isFood = product.isFood
  formData.shelfLife = product.shelfLife || 365
  formData.internalPrice = product.internalPrice
  formData.retailPrice = product.retailPrice
  formData.story = product.story || ''
  formData.origin = product.origin || ''
  formData.imagePreview = product.image || ''
  formData.imageData = product.image || ''
  showProductForm.value = true
}

function toggleStatus(product: any) {
  product.status = product.status === '上架' ? '下架' : '上架'
}

function triggerFilePicker() {
  fileInput.value?.click()
}

function handleFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (files?.length) processImage(files[0])
}

function handleDrop(e: DragEvent) {
  dragOver.value = false
  const files = e.dataTransfer?.files
  if (files?.length) processImage(files[0])
}

function handlePaste(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (let i = 0; i < items.length; i++) {
    if (items[i].type.startsWith('image/')) {
      const file = items[i].getAsFile()
      if (file) { processImage(file); break }
    }
  }
}

function processImage(file: File) {
  if (!file.type.startsWith('image/')) return
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.imagePreview = e.target?.result as string
    formData.imageData = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

function removeImage() {
  formData.imagePreview = ''
  formData.imageData = ''
}

function saveProduct() {
  if (!formData.name || !formData.spec) return

  if (editingProduct.value) {
    // Update existing
    const p = editingProduct.value
    p.name = formData.name
    p.category = formData.category
    p.subCategory = formData.subCategory
    p.brand = formData.brand
    p.spec = formData.spec
    p.unit = formData.unit
    p.isFood = formData.isFood
    p.shelfLife = formData.isFood ? formData.shelfLife : null
    p.internalPrice = Number(formData.internalPrice)
    p.retailPrice = Number(formData.retailPrice)
    p.story = formData.story
    p.origin = formData.origin
    if (formData.imageData) p.image = formData.imageData
  } else {
    // Add new
    const id = 'P' + String(products.length + 1).padStart(3, '0')
    const code = formData.category === '茶叶' ? 'TEA-' : formData.category === '茶具' ? 'CUP-' : formData.category === '茶点' ? 'SNK-' : 'PKG-'
    products.push({
      productId: id,
      code: code + 'NEW-' + id,
      name: formData.name,
      category: formData.category,
      subCategory: formData.subCategory,
      brand: formData.brand,
      spec: formData.spec,
      unit: formData.unit,
      isFood: formData.isFood,
      shelfLife: formData.isFood ? formData.shelfLife : null,
      internalPrice: Number(formData.internalPrice),
      retailPrice: Number(formData.retailPrice),
      marketPrice: 0,
      defaultSupplier: '',
      leadTime: 1,
      safeStock: 10,
      maxStock: 100,
      status: '上架',
      image: formData.imageData || '',
      story: formData.story,
      origin: formData.origin,
      brewingTips: null,
    })
  }

  showProductForm.value = false
  editingProduct.value = null
}
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }

/* Image upload zone */
.upload-zone { width: 200px; height: 160px; border: 2px dashed #dcdcdc; border-radius: 12px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all .2s; background: #fafafa; position: relative; outline: none; }
.upload-zone.drag-over { border-color: #0052D9; background: #f0f5ff; }
.upload-placeholder { display: flex; flex-direction: column; align-items: center; gap: 6px; color: #999; font-size: 13px; text-align: center; padding: 12px; }
.upload-icon { font-size: 32px; }
.upload-hint { font-size: 11px; color: #ccc; }
.upload-preview { width: 100%; height: 100%; position: relative; border-radius: 10px; overflow: hidden; }
.upload-preview img { width: 100%; height: 100%; object-fit: cover; }
.upload-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,.6); display: flex; justify-content: center; gap: 16px; padding: 6px 0; opacity: 0; transition: opacity .2s; }
.upload-zone:hover .upload-overlay { opacity: 1; }
.upload-overlay-btn { color: #fff; font-size: 12px; cursor: pointer; }
.upload-overlay-btn:hover { text-decoration: underline; }

/* Table thumbnails */
.product-thumb { width: 48px; height: 48px; border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; }
.product-thumb img { width: 100%; height: 100%; object-fit: cover; }
.product-thumb.placeholder { font-size: 18px; font-weight: 700; color: #666; }

/* Spec quick tags */
.spec-wrapper { width: 100%; }
.spec-quick-tags { display: flex; flex-wrap: wrap; margin-top: 6px; }

/* Detail header image */
.detail-header-img { width: 100%; height: 200px; border-radius: 12px; overflow: hidden; margin-bottom: 16px; }
.detail-header-img img { width: 100%; height: 100%; object-fit: cover; }
.detail-header-img.placeholder { display: flex; align-items: center; justify-content: center; }
.placeholder-text { font-size: 56px; font-weight: 700; color: #666; opacity: .4; }

/* Detail sections */
.detail-wrap { padding: 4px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.story-icon { margin-right: 4px; }
.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px 16px; }
.detail-row { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #666; padding: 4px 0; }
.detail-row .label { color: #999; white-space: nowrap; margin-right: 8px; }
.detail-row .name { font-weight: 600; color: #333; }

/* Price cards */
.price-cards { display: flex; gap: 10px; }
.price-card { flex: 1; background: #f9f9f9; border-radius: 8px; padding: 12px; text-align: center; }
.price-label { font-size: 11px; color: #999; margin-bottom: 4px; }
.price-value { font-size: 18px; font-weight: 700; }

/* Story box */
.story-box { background: #f0fdf4; border-radius: 10px; padding: 14px; font-size: 13px; line-height: 1.7; color: #555; }
.story-box p { margin-bottom: 8px; }
.story-meta { margin-top: 8px; }
.brewing-tips { margin-top: 12px; padding-top: 10px; border-top: 1px solid #dcedc8; }
.tips-title { font-size: 12px; font-weight: 600; color: #558b2f; margin-bottom: 6px; }
.tips-grid { display: flex; flex-wrap: wrap; gap: 6px; }
.tip { background: #fff; border-radius: 14px; padding: 4px 10px; font-size: 11px; color: #666; display: flex; align-items: center; gap: 3px; }
.tip-icon { font-size: 12px; }
</style>
