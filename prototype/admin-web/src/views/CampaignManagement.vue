<template>
  <div>
    <h2 class="page-header">营销活动管理</h2>

    <t-row :gutter="16" style="margin-bottom:16px">
      <t-col :span="3">
        <t-input v-model="searchText" placeholder="搜索活动名称..." clearable>
          <template #prefix-icon><t-icon name="search" /></template>
        </t-input>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterCampaignStatus" placeholder="活动状态" clearable>
          <t-option value="进行中" label="进行中" />
          <t-option value="待开始" label="待开始" />
          <t-option value="已结束" label="已结束" />
          <t-option value="已驳回" label="已驳回" />
        </t-select>
      </t-col>
      <t-col :span="2">
        <t-select v-model="filterCampaignType" placeholder="活动类型" clearable>
          <t-option value="限时折扣" label="限时折扣" />
          <t-option value="满减优惠" label="满减优惠" />
          <t-option value="新客礼包" label="新客礼包" />
          <t-option value="充值赠金" label="充值赠金" />
        </t-select>
      </t-col>
      <t-col :span="3" style="text-align:right">
        <t-button theme="primary" @click="showCreateCampaign = true" v-if="hasPermission('BTN_CREATE')">+ 创建活动</t-button>
      </t-col>
    </t-row>

    <t-row :gutter="16" style="margin-bottom:20px">
      <t-col :span="3" v-for="campaign in filteredCampaigns" :key="campaign.campaignId">
        <t-card :bordered="true" :class="['campaign-card', campaign.status === '已结束' ? 'ended' : '']" hover-shadow>
          <div class="campaign-header">
            <t-tag :theme="campaign.status === '进行中' ? 'success' : campaign.status === '待开始' ? 'primary' : campaign.status === '已驳回' ? 'danger' : 'default'" size="small" variant="light">{{ campaign.status }}</t-tag>
            <t-tag variant="light" size="small" style="margin-left:4px">{{ campaign.type }}</t-tag>
          </div>
          <div class="campaign-name">{{ campaign.name }}</div>
          <div class="campaign-date">{{ campaign.startDate }} ~ {{ campaign.endDate }}</div>
          <t-divider />
          <div class="campaign-metrics">
            <div class="metric"><span class="metric-label">曝光</span><span class="metric-val">{{ campaign.impressions.toLocaleString() }}</span></div>
            <div class="metric"><span class="metric-label">核销</span><span class="metric-val">{{ campaign.redemptions }}</span></div>
            <div class="metric"><span class="metric-label">ROI</span><span class="metric-val" :style="{color: campaign.roi > 1 ? '#00A870' : '#D54941'}">{{ campaign.roi.toFixed(1) }}</span></div>
          </div>
          <t-divider />
          <div class="campaign-footer">
            <span class="campaign-budget">预算 ¥{{ campaign.budget }} / 已用 ¥{{ campaign.budgetUsed }}</span>
            <t-button size="small" variant="text" theme="primary" @click="viewCampaign(campaign)">详情</t-button>
          </div>
        </t-card>
      </t-col>
    </t-row>

    <t-dialog v-model:visible="showCreateCampaign" header="创建营销活动" width="560px" :footer="false">
      <t-form layout="vertical">
        <t-form-item label="活动名称"><t-input v-model="newCampaignName" placeholder="请输入活动名称" /></t-form-item>
        <t-row :gutter="16">
          <t-col :span="8">
            <t-form-item label="活动类型">
              <t-select v-model="newCampaignType">
                <t-option value="限时折扣" label="限时折扣" />
                <t-option value="满减优惠" label="满减优惠" />
                <t-option value="新客礼包" label="新客礼包" />
                <t-option value="充值赠金" label="充值赠金" />
                <t-option value="会员专享" label="会员专享" />
              </t-select>
            </t-form-item>
          </t-col>
          <t-col :span="8">
            <t-form-item label="折扣力度"><t-input v-model="newCampaignDiscount" placeholder="如：0.85" /></t-form-item>
          </t-col>
        </t-row>
        <t-form-item label="活动时间"><t-date-range-picker v-model="newCampaignDate" style="width:100%" /></t-form-item>
        <t-form-item label="适用商品"><t-radio-group v-model="newCampaignScope"><t-radio value="全品类">全品类</t-radio><t-radio value="指定商品">指定商品</t-radio></t-radio-group></t-form-item>
        <t-form-item label="活动预算"><t-input v-model="newCampaignBudget" type="number" /></t-form-item>
        <div style="text-align:right">
          <t-button variant="outline" @click="showCreateCampaign = false">取消</t-button>
          <t-button theme="primary" style="margin-left:8px" @click="submitCampaign">提交审批</t-button>
        </div>
      </t-form>
    </t-dialog>

    <t-drawer v-model:visible="campaignDetailVisible" :header="selectedCampaign?.name" size="400px" :footer="false">
      <div v-if="selectedCampaign" class="detail-sections">
        <div class="detail-section">
          <div class="detail-row"><span>活动类型</span><t-tag variant="light">{{ selectedCampaign.type }}</t-tag></div>
          <div class="detail-row"><span>状态</span><t-tag :theme="selectedCampaign.status==='进行中'?'success':selectedCampaign.status==='待开始'?'primary':'default'" size="small">{{ selectedCampaign.status }}</t-tag></div>
          <div class="detail-row"><span>时间</span><span>{{ selectedCampaign.startDate }} ~ {{ selectedCampaign.endDate }}</span></div>
          <div class="detail-row"><span>适用门店</span><span>{{ selectedCampaign.storeScope }}</span></div>
          <div class="detail-row"><span>目标客群</span><span>{{ selectedCampaign.targetAudience }}</span></div>
          <div class="detail-row"><span>创建人</span><span>{{ selectedCampaign.createdBy }}</span></div>
        </div>
        <t-divider />
        <div class="detail-section">
          <h4>活动数据</h4>
          <div class="detail-row"><span>曝光量</span><span>{{ selectedCampaign.impressions.toLocaleString() }}</span></div>
          <div class="detail-row"><span>参与人数</span><span>{{ selectedCampaign.participants }}</span></div>
          <div class="detail-row"><span>核销量</span><span>{{ selectedCampaign.redemptions }}</span></div>
          <div class="detail-row"><span>ROI</span><span class="price">{{ selectedCampaign.roi.toFixed(1) }}</span></div>
          <div class="detail-row"><span>预算使用</span><span>¥{{ selectedCampaign.budgetUsed }} / ¥{{ selectedCampaign.budget }}</span></div>
        </div>
      </div>
    </t-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { hasPermission } from '@/utils/permission'
import marketing from '@mock/marketing.json'

const searchText = ref('')
const filterCampaignStatus = ref('')
const filterCampaignType = ref('')
const showCreateCampaign = ref(false)
const campaignDetailVisible = ref(false)
const selectedCampaign = ref<any>(null)

const newCampaignName = ref('')
const newCampaignType = ref('限时折扣')
const newCampaignDiscount = ref('')
const newCampaignDate = ref([])
const newCampaignScope = ref('全品类')
const newCampaignBudget = ref(0)

const campaigns = marketing.campaigns

const filteredCampaigns = computed(() => {
  let list = campaigns
  if (searchText.value) list = list.filter(c => c.name.includes(searchText.value))
  if (filterCampaignStatus.value) list = list.filter(c => c.status === filterCampaignStatus.value)
  if (filterCampaignType.value) list = list.filter(c => c.type === filterCampaignType.value)
  return list
})

function viewCampaign(c: any) { selectedCampaign.value = c; campaignDetailVisible.value = true }
function submitCampaign() { showCreateCampaign.value = false }
</script>

<style scoped>
.campaign-card { padding: 4px 0; }
.campaign-card.ended { opacity: 0.7; }
.campaign-header { margin-bottom: 8px; }
.campaign-name { font-size: 15px; font-weight: 600; color: #333; margin-bottom: 4px; }
.campaign-date { font-size: 11px; color: #999; margin-bottom: 8px; }
.campaign-metrics { display: flex; gap: 16px; }
.metric { flex: 1; text-align: center; }
.metric-label { display: block; font-size: 11px; color: #999; }
.metric-val { display: block; font-size: 16px; font-weight: 700; color: #333; margin-top: 2px; }
.campaign-footer { display: flex; justify-content: space-between; align-items: center; }
.campaign-budget { font-size: 11px; color: #999; }
.detail-sections { padding: 8px 0; }
.detail-section { margin-bottom: 8px; }
.detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 10px; color: #333; }
.detail-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 13px; color: #666; }
.detail-row .price { color: #0052D9; font-weight: 600; }
</style>
