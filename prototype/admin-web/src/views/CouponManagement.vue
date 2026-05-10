<template>
  <div>
    <h2 class="page-header">优惠券管理</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3"><t-input v-model="searchText" placeholder="搜索优惠券名称..." clearable></t-input></t-col>
      <t-col :span="2"><t-select v-model="filterCouponStatus" placeholder="状态" clearable>
        <t-option value="启用" label="启用" /><t-option value="待启用" label="待启用" />
      </t-select></t-col>
      <t-col :span="2"><t-select v-model="filterCouponType" placeholder="券类型" clearable>
        <t-option value="满减券" label="满减券" /><t-option value="折扣券" label="折扣券" />
        <t-option value="现金券" label="现金券" /><t-option value="体验券" label="体验券" />
      </t-select></t-col>
    </t-row>

    <t-card :bordered="true" style="margin-bottom:20px">
      <t-table :data="filteredCoupons" :columns="couponColumns" row-key="templateId" hover stripe>
        <template #faceValue="{ row }">
          <span v-if="row.type === '折扣券'">{{ (row.discountRate * 10).toFixed(0) }}折</span>
          <span v-else>¥{{ row.faceValue }}</span>
        </template>
        <template #usage="{ row }">{{ row.usedQty }}/{{ row.totalQty }}</template>
        <template #status="{ row }">
          <t-tag :theme="row.status === '启用' ? 'success' : 'default'" size="small" variant="light">{{ row.status }}</t-tag>
        </template>
        <template #actions="{ row }">
          <t-button size="small" variant="text" theme="primary" @click="selectedCoupon=row;couponDetailVisible=true">详情</t-button>
        </template>
      </t-table>
    </t-card>

    <!-- Customer Tags -->
    <t-card title="客户画像标签" :bordered="true">
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

    <t-drawer v-model:visible="couponDetailVisible" header="优惠券详情" size="400px" :footer="false">
      <div v-if="selectedCoupon" class="detail-sections">
        <div class="detail-row"><span>名称</span><span>{{ selectedCoupon.name }}</span></div>
        <div class="detail-row"><span>类型</span><t-tag variant="light">{{ selectedCoupon.type }}</t-tag></div>
        <div class="detail-row"><span>面值</span><span class="price">{{ selectedCoupon.type === '折扣券' ? (selectedCoupon.discountRate*10).toFixed(0)+'折' : '¥'+selectedCoupon.faceValue }}</span></div>
        <div class="detail-row"><span>使用门槛</span><span>{{ selectedCoupon.minSpend ? '满¥'+selectedCoupon.minSpend : '无门槛' }}</span></div>
        <div class="detail-row"><span>有效期</span><span>{{ selectedCoupon.validDays }}天</span></div>
        <div class="detail-row"><span>发放方式</span><span>{{ selectedCoupon.distributeMethod }}</span></div>
        <div class="detail-row"><span>使用量</span><span>{{ selectedCoupon.usedQty }}/{{ selectedCoupon.totalQty }}</span></div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import marketing from '@mock/marketing.json'

const searchText = ref('')
const filterCouponStatus = ref('')
const filterCouponType = ref('')
const couponDetailVisible = ref(false)
const selectedCoupon = ref<any>(null)

const coupons = marketing.couponTemplates
const customerTags = marketing.customerTags

const filteredCoupons = computed(() => {
  let list = coupons
  if (searchText.value) list = list.filter(c => c.name.includes(searchText.value))
  if (filterCouponStatus.value) list = list.filter(c => c.status === filterCouponStatus.value)
  if (filterCouponType.value) list = list.filter(c => c.type === filterCouponType.value)
  return list
})

const couponColumns = [
  { colKey: 'name', title: '优惠券名称', width: 170 },
  { colKey: 'type', title: '类型', width: 70 },
  { colKey: 'faceValue', title: '面值', width: 70 },
  { colKey: 'minSpend', title: '门槛', width: 70 },
  { colKey: 'validDays', title: '有效期', width: 60 },
  { colKey: 'distributeMethod', title: '发放方式', width: 160, ellipsis: true },
  { colKey: 'usage', title: '使用量', width: 80 },
  { colKey: 'status', title: '状态', width: 70 },
  { colKey: 'actions', title: '操作', width: 70 },
]
</script>

<style scoped>
.page-header { margin-bottom: 20px; font-size: 20px; font-weight: 600; }
.tag-card { text-align: center; padding: 8px 0; }
.tag-name { font-size: 14px; font-weight: 600; color: #333; margin-bottom: 4px; }
.tag-count { font-size: 24px; font-weight: 700; color: #0052D9; margin-bottom: 4px; }
.tag-desc { font-size: 11px; color: #999; }
.detail-sections { padding: 8px 0; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
