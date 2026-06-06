<template>
  <div>
    <h2 class="page-header">扫码账单管理</h2>

    <t-card :bordered="true">
      <!-- Stats bar -->
      <t-row :gutter="16" style="margin-bottom:20px">
        <t-col :span="6">
          <t-statistic title="进行中挂账" :value="activeCount" :loading="loading" :style="{ color: '#366EF4' }" />
        </t-col>
        <t-col :span="6">
          <t-statistic title="今日扫码单数" :value="todayCount" :loading="loading" />
        </t-col>
        <t-col :span="6">
          <t-statistic title="今日扫码金额" :value="`¥${todayAmount.toFixed(2)}`" :loading="loading" :style="{ color: '#B8860B' }" />
        </t-col>
        <t-col :span="6" style="text-align:right">
          <t-button theme="primary" @click="loadData" :loading="loading">🔄 刷新</t-button>
        </t-col>
      </t-row>

      <!-- Loading -->
      <t-space v-if="loading" direction="vertical" style="align-items:center;padding:40px">
        <t-loading />
        <span style="color:#999">加载中...</span>
      </t-space>

      <template v-else>
        <!-- Error -->
        <t-alert v-if="loadError" theme="error" :message="loadError" close style="margin-bottom:16px" />

        <!-- Empty -->
        <t-empty v-if="rooms.length === 0" description="暂无进行中的扫码挂账" style="padding:60px" />

        <!-- Room Bill Cards -->
        <t-space v-else direction="vertical" style="width:100%" size="medium">
          <t-card v-for="room in roomsWithOrders" :key="room.roomId" :title="`🏠 ${room.name}`" :header-bordered="{ style: 'border-bottom-color:#f0f0f0' }" size="small">
            <t-row :gutter="16">
              <t-col :span="4">
                <div class="bill-stat"><span class="bill-stat-label">房间订单号</span><span class="bill-stat-value">{{ room.activeOrderId }}</span></div>
              </t-col>
              <t-col :span="4">
                <div class="bill-stat"><span class="bill-stat-label">扫码订单数</span><span class="bill-stat-value">{{ room.scanOrders?.length || 0 }} 笔</span></div>
              </t-col>
              <t-col :span="4">
                <div class="bill-stat"><span class="bill-stat-label">挂账合计</span><span class="bill-stat-value" style="color:#B8860B;font-weight:700">¥{{ room.billSummary?.scanTotal?.toFixed(2) || '0.00' }}</span></div>
              </t-col>
              <t-col :span="4">
                <div class="bill-stat"><span class="bill-stat-label">操作</span>
                  <t-space>
                    <t-button size="small" variant="outline" @click="viewBillDetail(room)">查看明细</t-button>
                    <t-button v-if="room.scanOrders?.length > 0" size="small" theme="primary" @click="settleBill(room)">结算</t-button>
                  </t-space>
                </div>
              </t-col>
            </t-row>
          </t-card>
        </t-space>
      </template>
    </t-card>

    <!-- Bill Detail Dialog -->
    <t-dialog v-model:visible="billDetailVisible" :header="`${detailRoom?.name} — 扫码明细`" width="640px" :footer="false">
      <t-table v-if="detailOrders.length" :data="detailOrders" :columns="detailColumns" row-key="orderId" size="small" style="margin-bottom:16px" />
      <t-empty v-else description="暂无扫码记录" style="padding:30px" />
      <t-divider />
      <div class="bill-total">
        <span>合计金额</span>
        <span style="font-size:20px;font-weight:700;color:#B8860B">¥{{ detailTotal.toFixed(2) }}</span>
      </div>
      <t-space style="margin-top:12px" size="small">
        <t-button theme="primary" @click="settleBill(detailRoom)">结算全部</t-button>
        <t-button variant="outline" @click="billDetailVisible = false">关闭</t-button>
      </t-space>
    </t-dialog>

    <!-- Settle Dialog -->
    <t-dialog v-model:visible="settleDialogVisible" header="结算挂账" width="420px" :confirm-btn="{ content: '确认结算', loading: settling }" :cancel-btn="{}" @confirm="doSettle">
      <div style="margin-bottom:16px">
        <div class="settle-room-name">{{ settleRoom?.name }}</div>
        <div class="settle-amount">待结算金额：<strong style="color:#B8860B">¥{{ settleTotal.toFixed(2) }}</strong></div>
        <div style="font-size:12px;color:#999;margin-top:4px">共 {{ settleRoom?.scanOrders?.length || 0 }} 笔扫码订单</div>
      </div>

      <t-form layout="vertical">
        <t-form-item label="支付方式">
          <t-select v-model="settlePaymentMethod">
            <t-option value="WxPay" label="微信支付" />
            <t-option value="AliPay" label="支付宝" />
            <t-option value="MemberBalance" label="会员余额" />
            <t-option value="Cash" label="现金" />
            <t-option value="BankTransfer" label="银行转账" />
          </t-select>
        </t-form-item>
        <t-form-item label="会员余额抵扣">
          <t-switch v-model="settleUseBalance" />
        </t-form-item>
        <t-form-item label="开具发票">
          <t-switch v-model="settleIssueInvoice" />
        </t-form-item>
      </t-form>
    </t-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { scanApi } from '../services/api'

const loading = ref(false)
const loadError = ref('')

const rooms = ref<any[]>([])

// Bill detail
const billDetailVisible = ref(false)
const detailRoom = ref<any>(null)
const detailOrders = ref<any[]>([])
const detailTotal = computed(() => detailOrders.value.reduce((s: number, o: any) => s + (o.totalAmount || 0), 0))

// Settle
const settleDialogVisible = ref(false)
const settleRoom = ref<any>(null)
const settling = ref(false)
const settlePaymentMethod = ref('WxPay')
const settleUseBalance = ref(false)
const settleIssueInvoice = ref(false)
const settleTotal = computed(() => {
  if (!settleRoom.value?.scanOrders) return 0
  return settleRoom.value.scanOrders.reduce((s: number, o: any) => s + (o.totalAmount || 0), 0)
})

// Stats
const activeCount = computed(() => rooms.value.filter((r: any) => r.scanOrders?.length > 0).length)
const todayCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  let count = 0
  rooms.value.forEach((r: any) => {
    r.scanOrders?.forEach((o: any) => {
      if (o.createdAt?.startsWith(today)) count++
    })
  })
  return count
})
const todayAmount = computed(() => {
  const today = new Date().toISOString().slice(0, 10)
  let sum = 0
  rooms.value.forEach((r: any) => {
    r.scanOrders?.forEach((o: any) => {
      if (o.createdAt?.startsWith(today)) sum += o.totalAmount || 0
    })
  })
  return sum
})

const roomsWithOrders = computed(() => rooms.value.filter((r: any) => r.scanOrders?.length > 0 || r.billSummary?.scanTotal > 0))

const detailColumns = [
  { colKey: 'orderNumber', title: '订单号', width: 140 },
  { colKey: 'time', title: '下单时间', width: 140 },
  { colKey: 'itemsText', title: '商品', minWidth: 150 },
  { colKey: 'totalAmount', title: '金额', width: 80 },
  { colKey: 'status', title: '状态', width: 80 },
]

async function loadData() {
  loading.value = true
  loadError.value = ''
  try {
    const storeId = localStorage.getItem('erp_store_id') || 'S001'
    const roomData = await scanApi.getRoomBill('all')
    // For admin: we need to iterate rooms. Use roomApi to get active rooms,
    // then fetch bill for each.
    const { roomApi } = await import('../services/api')
    const allRooms = await roomApi.list().catch(() => [])
    const results = []
    for (const room of (allRooms || []).slice(0, 50)) {
      try {
        const bill = await scanApi.getRoomBill(room.room_id || room.roomId)
        if (bill.scanOrders?.length > 0 || bill.billSummary?.scanTotal > 0) {
          results.push({
            ...bill,
            roomId: bill.roomId,
            name: bill.roomName || room.name,
            roomOrder: bill.activeOrderId,
            scanOrders: bill.scanOrders?.map((o: any) => ({
              ...o,
              time: o.createdAt?.replace('T', ' ')?.slice(0, 16) || '',
              itemsText: o.items?.map((i: any) => `${i.productName}×${i.quantity}`).join('、') || '',
            })),
          })
        }
      } catch {
        // no active bill for this room
      }
    }
    rooms.value = results
  } catch (e: any) {
    loadError.value = '加载账单数据失败: ' + (e.message || e)
    rooms.value = []
  } finally {
    loading.value = false
  }
}

function viewBillDetail(room: any) {
  detailRoom.value = room
  detailOrders.value = room.scanOrders || []
  billDetailVisible.value = true
}

function settleBill(room: any) {
  settleRoom.value = room
  settlePaymentMethod.value = 'WxPay'
  settleUseBalance.value = false
  settleIssueInvoice.value = false
  settleDialogVisible.value = true
}

async function doSettle() {
  if (!settleRoom.value) return
  settling.value = true
  try {
    const res = await scanApi.settleRoomBill(settleRoom.value.roomId, {
      paymentMethod: settlePaymentMethod.value,
      useMemberBalance: settleUseBalance.value,
      issueInvoice: settleIssueInvoice.value,
    })
    settleDialogVisible.value = false
    showToast(`✅ 结算成功！共 ${res.ordersSettled} 笔，金额 ¥${res.totalAmount.toFixed(2)}` + (res.invoiceNumber ? ` 发票号: ${res.invoiceNumber}` : ''))
    await loadData()
  } catch (e: any) {
    showToast('❌ 结算失败: ' + (e.message || e))
  } finally {
    settling.value = false
  }
}

function showToast(msg: string) {
  const el = document.createElement('div')
  el.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,.85);color:#fff;padding:10px 22px;border-radius:8px;font-size:14px;z-index:9999'
  el.textContent = msg
  document.body.appendChild(el)
  setTimeout(() => el.remove(), 2000)
}

onMounted(loadData)
</script>

<style scoped>
.bill-stat { padding: 4px 0; }
.bill-stat-label { display:block; font-size:11px; color:#999; margin-bottom:2px; }
.bill-stat-value { font-size:14px; color:#333; }
.bill-total { display:flex; justify-content:space-between; align-items:center; padding:0 4px; }
.settle-room-name { font-size:16px; font-weight:600; margin-bottom:6px; }
.settle-amount { font-size:14px; color:#666; }
</style>
