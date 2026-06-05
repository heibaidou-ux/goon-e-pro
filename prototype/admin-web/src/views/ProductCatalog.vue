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
            <t-option v-for="c in categories" :key="c.categoryId" :value="c.categoryId" :label="c.name" />
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
        </t-col>
      </t-row>

      <!-- Loading state -->
      <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
        <t-loading :delay="0" />
        <span style="color:#999">加载中...</span>
      </t-space>

      <!-- Error state -->
      <t-alert v-else-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

      <!-- Empty state -->
      <t-empty v-else-if="products.length === 0" description="暂无商品数据" style="padding:40px">
        <t-button theme="primary" @click="openAddProduct">+ 新增商品</t-button>
      </t-empty>

      <!-- Data table -->
      <t-table v-else :data="filteredProducts" :columns="productColumns" row-key="productId" hover stripe>
        <template #image="{ row }">
          <div class="product-thumb" v-if="row.images?.length">
            <img :src="row.images[0].urlThumbnail || row.images[0].urlOriginal" :alt="row.name" />
          </div>
          <div class="product-thumb placeholder" v-else :style="{ background: nameGradient(row.name) }">
            {{ row.name.charAt(0) }}
          </div>
        </template>
        <template #categoryName="{ row }">
          <t-tag variant="light">{{ row.categoryName || '未分类' }}</t-tag>
        </template>
        <template #spec="{ row }">
          <t-tag size="small" variant="outline">{{ row.spec || '—' }}</t-tag>
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
            <t-button size="small" variant="text" :theme="row.status === '上架' ? 'warning' : 'success'" @click.stop="toggleStatus(row)" :loading="row._toggling">
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
        <div class="detail-header-img" v-if="selectedProduct.images?.length">
          <img :src="selectedProduct.images[0].urlOriginal" :alt="selectedProduct.name" />
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
            <div class="detail-row"><span class="label">分类</span><span><t-tag variant="light" size="small">{{ selectedProduct.categoryName || '未分类' }}</t-tag></span></div>
            <div class="detail-row"><span class="label">规格</span><span><t-tag variant="outline" size="small">{{ selectedProduct.spec }}</t-tag></span></div>
            <div class="detail-row"><span class="label">单位</span><span>{{ selectedProduct.unit || '—' }}</span></div>
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
              <div class="price-value" style="color:#0052D9">¥{{ selectedProduct.basePrice }}</div>
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
        <div class="detail-section" v-if="selectedProduct.story || selectedProduct.origin">
          <h4><span class="story-icon">📖</span> 产品故事</h4>
          <div class="story-box">
            <p v-if="selectedProduct.story">{{ selectedProduct.story }}</p>
            <div class="story-meta" v-if="selectedProduct.origin">
              <t-tag variant="light" size="small">📍 {{ selectedProduct.origin }}</t-tag>
            </div>
            <div class="brewing-tips" v-if="parsedBrewingTips">
              <div class="tips-title">冲泡建议</div>
              <div class="tips-grid">
                <span class="tip" v-if="parsedBrewingTips.waterTemp"><span class="tip-icon">🌡️</span> {{ parsedBrewingTips.waterTemp }}</span>
                <span class="tip" v-if="parsedBrewingTips.steepTime"><span class="tip-icon">⏱️</span> {{ parsedBrewingTips.steepTime }}</span>
                <span class="tip" v-if="parsedBrewingTips.vessel"><span class="tip-icon">🫖</span> {{ parsedBrewingTips.vessel }}</span>
                <span class="tip" v-if="parsedBrewingTips.method"><span class="tip-icon">💧</span> {{ parsedBrewingTips.method }}</span>
              </div>
            </div>
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
              <t-select v-model="formData.categoryId" placeholder="选择分类">
                <t-option v-for="c in categories" :key="c.categoryId" :value="c.categoryId" :label="c.name" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="商品编码">
              <t-input v-model="formData.code" placeholder="如：TEA-001" />
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
              <t-input v-model.number="formData.basePrice" type="number" prefix="¥" />
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

        <t-form-item label="产品故事">
          <t-textarea v-model="formData.story" placeholder="描述产品故事、产地特色等内容" :rows="2" />
        </t-form-item>
        <t-form-item label="产地">
          <t-input v-model="formData.origin" placeholder="如：杭州西湖" />
        </t-form-item>
        <t-form-item label="冲泡建议">
          <t-input v-model="formData.brewingTips" placeholder="如：85°C冲泡，等待3分钟" />
        </t-form-item>

        <div style="text-align:right;margin-top:16px">
          <t-button variant="outline" @click="showProductForm = false" :disabled="saving">取消</t-button>
          <t-button theme="primary" @click="saveProduct" style="margin-left:8px" :loading="saving">
            {{ editingProduct ? '保存修改' : '创建商品' }}
          </t-button>
        </div>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { productApi } from '../services/api'
import type { Product, ProductCategory } from '../services/types'

const searchText = ref('')
const filterCategory = ref('')
const filterStatus = ref('')
const drawerVisible = ref(false)
const showProductForm = ref(false)
const selectedProduct = ref<Product | null>(null)
const editingProduct = ref<Product | null>(null)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()
const loading = ref(false)
const saving = ref(false)
const loadError = ref('')

const products = ref<Product[]>([])
const categories = ref<ProductCategory[]>([])

const defaultForm = () => ({
  name: '', code: '', categoryId: '', brand: '高岸',
  spec: '', unit: '罐', isFood: true, shelfLife: 365,
  basePrice: 0, retailPrice: 0,
  story: '', origin: '', brewingTips: '',
  imagePreview: '', imageFile: null as File | null,
  imageFiles: [] as File[],
})
const formData = reactive(defaultForm())

const specOptions = ['250g/罐', '200g/罐', '357g/饼', '150g/盒', '200g/份', '单只装', '100g/罐', '1份', '200ml']

// ── Load data ──

async function loadProducts() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await productApi.list({ page: 1, page_size: 100 })
    products.value = result.items
  } catch (e: any) {
    loadError.value = '加载商品失败: ' + (e.message || e)
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    categories.value = await productApi.categories()
  } catch (e: any) {
    console.warn('加载分类失败:', e)
  }
}

// ── Computed ──

const filteredProducts = computed(() => {
  let list = products.value
  if (searchText.value) {
    const q = searchText.value.toLowerCase()
    list = list.filter(p => p.name.toLowerCase().includes(q) || p.code.toLowerCase().includes(q))
  }
  if (filterCategory.value) list = list.filter(p => p.categoryId === filterCategory.value)
  if (filterStatus.value) list = list.filter(p => p.status === filterStatus.value)
  return list
})

const productColumns = [
  { colKey: 'image', title: '图片', width: 70 },
  { colKey: 'code', title: '编码', width: 110 },
  { colKey: 'name', title: '商品名称', width: 140 },
  { colKey: 'categoryName', title: '分类', width: 130 },
  { colKey: 'spec', title: '规格', width: 100 },
  { colKey: 'isFood', title: '食品', width: 65 },
  { colKey: 'basePrice', title: '结算价', width: 75 },
  { colKey: 'retailPrice', title: '零售价', width: 75 },
  { colKey: 'status', title: '状态', width: 65 },
  { colKey: 'actions', title: '操作', width: 180 },
]

const nameGradients = ['#e8f5e9','#fff3e0','#fce4ec','#e3f2fd','#f3e5f5','#f1f8e9','#fff8e1','#efebe9']
function nameGradient(name: string): string {
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return nameGradients[Math.abs(hash) % nameGradients.length]
}

const parsedBrewingTips = computed(() => {
  const tips = selectedProduct.value?.brewingTips
  if (!tips) return null
  try {
    const parsed = JSON.parse(tips)
    return typeof parsed === 'object' ? parsed : null
  } catch {
    return null
  }
})

// ── Actions ──

function viewDetail(product: Product) {
  selectedProduct.value = product
  drawerVisible.value = true
}

function openAddProduct() {
  editingProduct.value = null
  Object.assign(formData, defaultForm())
  showProductForm.value = true
}

function openEditProduct(product: Product) {
  editingProduct.value = product
  Object.assign(formData, {
    name: product.name,
    code: product.code,
    categoryId: product.categoryId || '',
    brand: product.brand || '高岸',
    spec: product.spec || '',
    unit: product.unit || '罐',
    isFood: product.isFood,
    shelfLife: product.shelfLife || 365,
    basePrice: product.basePrice,
    retailPrice: product.retailPrice,
    marketPrice: product.marketPrice,
    story: product.story || '',
    origin: product.origin || '',
    brewingTips: product.brewingTips || '',
    imagePreview: (product.images?.length ? product.images[0].urlThumbnail || product.images[0].urlOriginal : ''),
    imageFile: null,
    imageFiles: [],
  })
  showProductForm.value = true
}

async function toggleStatus(product: any) {
  const newStatus = product.status === '上架' ? '下架' : '上架'
  product._toggling = true
  try {
    const updated = await productApi.update(product.productId, { status: newStatus })
    Object.assign(product, updated)
  } catch (e: any) {
    console.error('切换状态失败:', e)
  } finally {
    product._toggling = false
  }
}

async function saveProduct() {
  if (!formData.name || !formData.code) return
  saving.value = true

  try {
    const payload: any = {
      name: formData.name,
      code: formData.code,
      categoryId: formData.categoryId || undefined,
      brand: formData.brand,
      spec: formData.spec,
      unit: formData.unit,
      basePrice: Number(formData.basePrice) || 0,
      retailPrice: Number(formData.retailPrice) || 0,
      isFood: formData.isFood,
      shelfLife: formData.isFood ? (Number(formData.shelfLife) || null) : null,
      story: formData.story || undefined,
      origin: formData.origin || undefined,
      brewingTips: formData.brewingTips || undefined,
    }

    if (editingProduct.value) {
      // Update existing product
      const updated = await productApi.update(editingProduct.value.productId, payload)
      const idx = products.value.findIndex(p => p.productId === editingProduct.value!.productId)
      if (idx >= 0) products.value[idx] = updated

      // Upload new image if selected
      if (formData.imageFile) {
        await productApi.uploadImages(editingProduct.value.productId, [formData.imageFile])
        await loadProducts()
      }
    } else {
      // Create new product
      const created = await productApi.create(payload)
      // Upload image if selected
      if (formData.imageFile) {
        await productApi.uploadImages(created.productId, [formData.imageFile])
        // Reload to get images
        const fresh = await productApi.get(created.productId)
        products.value.unshift(fresh)
      } else {
        products.value.unshift(created)
      }
    }

    showProductForm.value = false
  } catch (e: any) {
    console.error('保存商品失败:', e)
    alert('保存失败: ' + (e.message || e))
  } finally {
    saving.value = false
  }
}

// ── Image handling ──

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
  formData.imageFile = file
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.imagePreview = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

function removeImage() {
  formData.imagePreview = ''
  formData.imageFile = null
}

// ── Init ──

onMounted(() => {
  loadProducts()
  loadCategories()
})
</script>

<style scoped>

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
.tip { background: #fff; border-radius: 14px; padding: 4px 10px; font-size: 11px; color: #666; display: inline-flex; align-items: center; gap: 3px; }
.tip-icon { font-size: 12px; }
</style>
