<template>
  <div>
    <h2 class="page-header">优惠券管理</h2>

    <!-- 统计卡片 -->
    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="s in couponStats" :key="s.label">
        <t-card :bordered="true">
          <div class="stat-card"><div class="stat-num" :style="{color:s.color}">{{ s.value }}</div><div class="stat-label">{{ s.label }}</div></div>
        </t-card>
      </t-col>
    </t-row>

    <!-- 操作栏 -->
    <t-card :bordered="true" style="margin-bottom:16px">
      <t-row :gutter="16" align="middle">
        <t-col :span="3"><t-input v-model="searchText" placeholder="搜索优惠券名称..." clearable /></t-col>
        <t-col :span="2">
          <t-select v-model="filterCouponStatus" placeholder="状态" clearable>
            <t-option value="启用" label="启用" /><t-option value="待启用" label="待启用" />
          </t-select>
        </t-col>
        <t-col :span="2">
          <t-select v-model="filterCouponType" placeholder="券类型" clearable>
            <t-option value="满减券" label="满减券" /><t-option value="折扣券" label="折扣券" />
            <t-option value="现金券" label="现金券" /><t-option value="体验券" label="体验券" />
          </t-select>
        </t-col>
        <t-col :span="5" style="text-align:right">
          <t-button theme="primary" @click="openCreateDialog">+ 新建优惠券</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="showDistributeDialog = true">批量发放</t-button>
          <t-button variant="outline" style="margin-left:8px" @click="showAnalysis = !showAnalysis">效果分析</t-button>
        </t-col>
      </t-row>
    </t-card>

    <!-- 效果分析卡片 -->
    <t-card v-if="showAnalysis" :bordered="true" title="优惠券效果分析" style="margin-bottom:20px">
      <t-row :gutter="16">
        <t-col :span="3" v-for="a in analysisData" :key="a.label">
          <t-card :bordered="true" class="analysis-card">
            <div class="analysis-num" :style="{color:a.color}">{{ a.value }}</div>
            <div class="analysis-label">{{ a.label }}</div>
            <div class="analysis-trend" :style="{color:a.trendColor}">{{ a.trend }}</div>
          </t-card>
        </t-col>
      </t-row>
    </t-card>

    <!-- 优惠券列表 -->
    <t-card :bordered="true">
      <t-table :data="filteredCoupons" :columns="couponColumns" row-key="templateId" hover stripe>
        <template #faceValue="{ row }">
          <span v-if="row.type === '折扣券'">{{ (row.discountRate * 10).toFixed(0) }}折</span>
          <span v-else class="price">¥{{ row.faceValue }}</span>
        </template>
        <template #usage="{ row }">
          <div class="usage-bar-wrap">
            <div class="usage-bar" :style="{ width: (row.usedQty / Math.max(row.totalQty, 1) * 100) + '%' }"></div>
          </div>
          <span class="usage-text">{{ row.usedQty }}/{{ row.totalQty }}</span>
        </template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '启用' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-space size="small">
            <t-button size="small" variant="text" theme="primary" @click="viewCoupon(row)">详情</t-button>
            <t-button size="small" variant="text" theme="default" @click="editCoupon(row)">编辑</t-button>
            <t-button v-if="row.status === '启用'" size="small" variant="text" theme="warning" @click="toggleCouponStatus(row)">停用</t-button>
            <t-button v-else size="small" variant="text" theme="success" @click="toggleCouponStatus(row)">启用</t-button>
          </t-space>
        </template>
      </t-table>
    </t-card>

    <!-- 客户画像标签 -->
    <t-card title="客户画像标签" :bordered="true" style="margin-top:20px">
      <t-row :gutter="16">
        <t-col :span="3" v-for="tag in customerTags" :key="tag.tag">
          <t-card :bordered="true" class="tag-card">
            <div class="tag-name">{{ tag.tag }}</div>
            <div class="tag-count">{{ tag.count }}人</div>
            <div class="tag-desc">{{ tag.description }}</div>
          </t-card>
        </t-col>
      </t-row>
    </t-card>

    <!-- 新建/编辑优惠券对话框 -->
    <t-dialog v-model:visible="showCouponForm" :header="editingCoupon ? '编辑优惠券' : '新建优惠券'" width="560px" :footer="false">
      <t-form :data="couponForm" layout="vertical">
        <t-form-item label="优惠券名称">
          <t-input v-model="couponForm.name" placeholder="请输入优惠券名称" />
        </t-form-item>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="券类型">
              <t-select v-model="couponForm.type" placeholder="请选择">
                <t-option value="满减券" label="满减券" />
                <t-option value="折扣券" label="折扣券" />
                <t-option value="现金券" label="现金券" />
                <t-option value="体验券" label="体验券" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item :label="couponForm.type === '折扣券' ? '折扣率' : '面值'">
              <t-input v-if="couponForm.type === '折扣券'" v-model="couponForm.discountRate" type="number" suffix="折" />
              <t-input v-else v-model.number="couponForm.faceValue" type="number" prefix="¥" />
            </t-form-item>
          </t-col>
        </t-row>
        <t-row :gutter="16">
          <t-col :span="6">
            <t-form-item label="使用门槛">
              <t-input v-model.number="couponForm.minSpend" type="number" prefix="满¥" suffix="可用" placeholder="0=无门槛" />
            </t-form-item>
          </t-col>
          <t-col :span="6">
            <t-form-item label="有效期">
              <t-input v-model.number="couponForm.validDays" type="number" suffix="天" />
            </t-form-item>
          </t-col>
        </t-row>
        <t-form-item label="发放总量">
          <t-input v-model.number="couponForm.totalQty" type="number" suffix="张" />
        </t-form-item>
        <t-form-item label="适用品类">
          <t-radio-group v-model="couponForm.scope">
            <t-radio-button value="全品类">全品类</t-radio-button>
            <t-radio-button value="空间租用">空间租用</t-radio-button>
            <t-radio-button value="指定商品">指定商品</t-radio-button>
          </t-radio-group>
        </t-form-item>
        <t-form-item label="发放方式">
          <t-select v-model="couponForm.distributeMethod" placeholder="请选择">
            <t-option value="新会员注册自动发放" label="新会员注册自动发放" />
            <t-option value="消费后回赠" label="消费后回赠" />
            <t-option value="充值满额赠送" label="充值满额赠送" />
            <t-option value="手动定向发放" label="手动定向发放" />
          </t-select>
        </t-form-item>
      </t-form>
      <div style="text-align:right;margin-top:16px">
        <t-button variant="outline" @click="showCouponForm = false">取消</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="saveCoupon">{{ editingCoupon ? '保存修改' : '创建优惠券' }}</t-button>
      </div>
    </t-dialog>

    <!-- 批量发放对话框 -->
    <t-dialog v-model:visible="showDistributeDialog" header="批量发放优惠券" width="480px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="选择优惠券">
          <t-select v-model="distributeCouponId" placeholder="请选择">
            <t-option v-for="c in coupons" :key="c.templateId" :value="c.templateId" :label="c.name" />
          </t-select>
        </t-form-item>
        <t-form-item label="发放对象">
          <t-radio-group v-model="distributeTarget">
            <t-radio-button value="全部用户">全部用户</t-radio-button>
            <t-radio-button value="会员等级">按会员等级</t-radio-button>
            <t-radio-button value="画像标签">按画像标签</t-radio-button>
          </t-radio-group>
        </t-form-item>
        <t-form-item v-if="distributeTarget === '会员等级'" label="选择等级">
          <t-select placeholder="选择会员等级">
            <t-option value="Gold" label="黄金会员" />
            <t-option value="Silver" label="白银会员" />
            <t-option value="Bronze" label="青铜会员" />
          </t-select>
        </t-form-item>
        <t-form-item v-if="distributeTarget === '画像标签'" label="选择标签">
          <t-select placeholder="选择客户标签">
            <t-option v-for="tag in customerTags" :key="tag.tag" :value="tag.tag" :label="tag.tag" />
          </t-select>
        </t-form-item>
        <t-form-item label="发放数量">
          <t-input v-model.number="distributeQty" type="number" suffix="张" />
        </t-form-item>
      </t-form>
      <div style="text-align:right">
        <t-button variant="outline" @click="showDistributeDialog = false">取消</t-button>
        <t-button theme="primary" style="margin-left:8px" @click="confirmDistribute">确认发放</t-button>
      </div>
    </t-dialog>

    <!-- 详情抽屉 -->
    <t-drawer v-model:visible="couponDetailVisible" header="优惠券详情" size="420px" :footer="false">
      <div v-if="selectedCoupon" class="detail-sections">
        <t-card title="基本信息" :bordered="true" style="margin-bottom:16px">
          <div class="detail-row"><span>名称</span><span class="val">{{ selectedCoupon.name }}</span></div>
          <div class="detail-row"><span>类型</span><t-tag variant="light" size="small">{{ selectedCoupon.type }}</t-tag></div>
          <div class="detail-row"><span>面值</span><span class="val price">{{ selectedCoupon.type === '折扣券' ? (selectedCoupon.discountRate*10).toFixed(0)+'折' : '¥'+selectedCoupon.faceValue }}</span></div>
          <div class="detail-row"><span>使用门槛</span><span class="val">{{ selectedCoupon.minSpend ? '满¥'+selectedCoupon.minSpend : '无门槛' }}</span></div>
        </t-card>
        <t-card title="使用数据" :bordered="true" style="margin-bottom:16px">
          <div class="detail-row"><span>总量</span><span class="val">{{ selectedCoupon.totalQty }}张</span></div>
          <div class="detail-row"><span>已用</span><span class="val">{{ selectedCoupon.usedQty }}张</span></div>
          <div class="detail-row"><span>使用率</span><span class="val price">{{ (selectedCoupon.usedQty / Math.max(selectedCoupon.totalQty, 1) * 100).toFixed(1) }}%</span></div>
          <div class="detail-row"><span>核销总额</span><span class="val price">¥{{ (selectedCoupon.usedQty * (selectedCoupon.faceValue || 0)).toLocaleString() }}</span></div>
        </t-card>
        <t-card title="发放配置" :bordered="true">
          <div class="detail-row"><span>发放方式</span><span class="val">{{ selectedCoupon.distributeMethod }}</span></div>
          <div class="detail-row"><span>适用品类</span><span class="val">{{ selectedCoupon.scope }}</span></div>
          <div class="detail-row"><span>有效期</span><span class="val">{{ selectedCoupon.validDays }}天</span></div>
        </t-card>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import marketing from '@mock/marketing.json'

// ── State ──
const searchText = ref('')
const filterCouponStatus = ref('')
const filterCouponType = ref('')
const couponDetailVisible = ref(false)
const showCouponForm = ref(false)
const showDistributeDialog = ref(false)
const showAnalysis = ref(false)
const selectedCoupon = ref<any>(null)
const editingCoupon = ref<any>(null)
const distributeCouponId = ref('')
const distributeTarget = ref('全部用户')
const distributeQty = ref(100)

const defaultCouponForm = () => ({
  name: '', type: '满减券', faceValue: 30, discountRate: 9, minSpend: 100,
  validDays: 30, totalQty: 500, scope: '全品类', distributeMethod: '手动定向发放',
})
const couponForm = reactive(defaultCouponForm())

const coupons = marketing.couponTemplates
const customerTags = marketing.customerTags

// ── Stats ──
const couponStats = computed(() => {
  const total = coupons.length
  const active = coupons.filter(c => c.status === '启用').length
  const totalUsed = coupons.reduce((s, c) => s + c.usedQty, 0)
  const totalIssued = coupons.reduce((s, c) => s + c.totalQty, 0)
  const usageRate = totalIssued > 0 ? (totalUsed / totalIssued * 100).toFixed(1) : '0'
  return [
    { label: '优惠券总数', value: total + '种', color: '#0052D9' },
    { label: '启用中', value: active + '种', color: '#00A870' },
    { label: '累计发放', value: totalIssued + '张', color: '#E37318' },
    { label: '综合使用率', value: usageRate + '%', color: '#366EF4' },
  ]
})

// ── Analysis ──
const analysisData = [
  { label: '本月发放量', value: '1,280张', color: '#0052D9', trend: '↑ 较上月+23%', trendColor: '#00A870' },
  { label: '本月核销量', value: '576张', color: '#00A870', trend: '↑ 核销率45%', trendColor: '#00A870' },
  { label: '平均折扣率', value: '8.2折', color: '#E37318', trend: '→ 环比持平', trendColor: '#999' },
  { label: '带动消费额', value: '¥52,600', color: '#D54941', trend: '↑ ROI 3.2x', trendColor: '#00A870' },
]

// ── Filtered ──
const filteredCoupons = computed(() => {
  let list = coupons
  if (searchText.value) list = list.filter(c => c.name.includes(searchText.value))
  if (filterCouponStatus.value) list = list.filter(c => c.status === filterCouponStatus.value)
  if (filterCouponType.value) list = list.filter(c => c.type === filterCouponType.value)
  return list
})

// ── Actions ──
function openCreateDialog() {
  editingCoupon.value = null
  Object.assign(couponForm, defaultCouponForm())
  showCouponForm.value = true
}

function editCoupon(row: any) {
  editingCoupon.value = row
  couponForm.name = row.name
  couponForm.type = row.type
  couponForm.faceValue = row.faceValue || 0
  couponForm.discountRate = row.discountRate ? row.discountRate * 10 : 9
  couponForm.minSpend = row.minSpend || 0
  couponForm.validDays = row.validDays || 30
  couponForm.totalQty = row.totalQty || 200
  couponForm.scope = row.scope || '全品类'
  couponForm.distributeMethod = row.distributeMethod || '手动定向发放'
  showCouponForm.value = true
}

function saveCoupon() {
  if (!couponForm.name || !couponForm.type) return
  if (editingCoupon.value) {
    const c = editingCoupon.value
    c.name = couponForm.name
    c.type = couponForm.type
    c.faceValue = couponForm.type === '折扣券' ? null : couponForm.faceValue
    c.discountRate = couponForm.type === '折扣券' ? couponForm.discountRate / 10 : null
    c.minSpend = couponForm.minSpend
    c.validDays = couponForm.validDays
    c.totalQty = couponForm.totalQty
    c.scope = couponForm.scope
    c.distributeMethod = couponForm.distributeMethod
  } else {
    coupons.push({
      templateId: 'CT' + String(coupons.length + 1).padStart(3, '0'),
      name: couponForm.name,
      type: couponForm.type,
      faceValue: couponForm.type === '折扣券' ? null : couponForm.faceValue,
      discountRate: couponForm.type === '折扣券' ? couponForm.discountRate / 10 : null,
      minSpend: couponForm.minSpend,
      validDays: couponForm.validDays,
      scope: couponForm.scope,
      distributeMethod: couponForm.distributeMethod,
      totalQty: couponForm.totalQty,
      usedQty: 0,
      status: '启用',
      createdAt: new Date().toISOString().slice(0, 10),
    })
  }
  showCouponForm.value = false
  editingCoupon.value = null
}

function viewCoupon(row: any) {
  selectedCoupon.value = row
  couponDetailVisible.value = true
}

function toggleCouponStatus(row: any) {
  row.status = row.status === '启用' ? '停用' : '启用'
}

function confirmDistribute() {
  if (!distributeCouponId.value) return
  const coupon = coupons.find(c => c.templateId === distributeCouponId.value)
  if (coupon) {
    coupon.totalQty += distributeQty.value
  }
  showDistributeDialog.value = false
  distributeCouponId.value = ''
}

// ── Columns ──
const couponColumns = [
  { colKey: 'name', title: '优惠券名称', width: 170 },
  { colKey: 'type', title: '类型', width: 70 },
  { colKey: 'faceValue', title: '面值', width: 70 },
  { colKey: 'minSpend', title: '门槛', width: 70 },
  { colKey: 'validDays', title: '有效期', width: 60 },
  { colKey: 'distributeMethod', title: '发放方式', width: 160, ellipsis: true },
  { colKey: 'usage', title: '使用量', width: 110 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 160 },
]
</script>

<style scoped>
.analysis-card { text-align: center; padding: 8px 0; }
.analysis-num { font-size: 24px; font-weight: 700; }
.analysis-label { font-size: 12px; color: #999; margin: 4px 0; }
.analysis-trend { font-size: 12px; font-weight: 500; }

.tag-card { text-align: center; padding: 8px 0; }
.tag-name { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
.tag-count { font-size: 24px; font-weight: 700; color: #0052D9; margin-bottom: 4px; }
.tag-desc { font-size: 11px; color: #999; }

.usage-bar-wrap { display: inline-block; width: 60px; height: 6px; background: #f0f0f0; border-radius: 3px; vertical-align: middle; overflow: hidden; margin-right: 6px; }
.usage-bar { height: 100%; background: #0052D9; border-radius: 3px; }
.usage-text { font-size: 12px; vertical-align: middle; }

.detail-sections { padding: 4px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.detail-row .val { color: #333; font-weight: 500; }
.detail-row .val.price { color: #0052D9; font-weight: 600; }
.price { color: #0052D9; font-weight: 600; }
</style>
