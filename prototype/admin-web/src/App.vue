<template>
  <router-view v-if="isLoginPage" />

  <div class="app-layout" v-else>
    <aside :class="['app-aside', { 'is-collapsed': isCollapsed }]">
      <div class="sidebar-header">
        <span class="logo-text" v-show="!isCollapsed">高岸ERP</span>
        <span class="logo-text logo-compact" v-show="isCollapsed">高岸</span>
        <span class="logo-sub" v-show="!isCollapsed">盈隆店</span>
      </div>

      <t-menu
        :value="activeMenu"
        theme="dark"
        :collapsed="isCollapsed"
        @change="onMenuChange"
      >
        <t-menu-item value="/dashboard" v-if="hasPermission('MENU_DASHBOARD')">
          <template #icon><t-icon name="dashboard" /></template>
          门店总览
        </t-menu-item>
        <t-menu-item value="/rooms" v-if="hasPermission('MENU_ROOMS')">
          <template #icon><t-icon name="room" /></template>
          房间管理
        </t-menu-item>

        <t-menu-group title="供应链" v-show="!isCollapsed" v-if="hasPermission('MENU_PRODUCTS') || hasPermission('MENU_PURCHASES') || hasPermission('MENU_INVENTORY') || hasPermission('MENU_SUPPLIERS')">
          <t-menu-item value="/products" v-if="hasPermission('MENU_PRODUCTS')"><template #icon><t-icon name="gift" /></template>商品目录</t-menu-item>
          <t-menu-item value="/purchases" v-if="hasPermission('MENU_PURCHASES')"><template #icon><t-icon name="shopping-cart" /></template>采购配货</t-menu-item>
          <t-menu-item value="/inventory" v-if="hasPermission('MENU_INVENTORY')"><template #icon><t-icon name="archive" /></template>库存管理</t-menu-item>
          <t-menu-item value="/suppliers" v-if="hasPermission('MENU_SUPPLIERS')"><template #icon><t-icon name="user-business" /></template>供应商</t-menu-item>
        </t-menu-group>
        <t-menu-group title="财务" v-show="!isCollapsed" v-if="hasPermission('MENU_REVENUE') || hasPermission('MENU_EXPENSE') || hasPermission('MENU_SETTLEMENT') || hasPermission('MENU_RECONCILIATION') || hasPermission('MENU_DIVIDENDS') || hasPermission('MENU_REPORTS') || hasPermission('MENU_ASSETS')">
          <t-menu-item value="/revenue" v-if="hasPermission('MENU_REVENUE')"><template #icon><t-icon name="money" /></template>收入管理</t-menu-item>
          <t-menu-item value="/expense" v-if="hasPermission('MENU_EXPENSE')"><template #icon><t-icon name="expense" /></template>支出管理</t-menu-item>
          <t-menu-item value="/settlement" v-if="hasPermission('MENU_SETTLEMENT')"><template #icon><t-icon name="calendar" /></template>自动月结</t-menu-item>
          <t-menu-item value="/reconciliation" v-if="hasPermission('MENU_RECONCILIATION')"><template #icon><t-icon name="check-double" /></template>智能对账</t-menu-item>
          <t-menu-item value="/dividends" v-if="hasPermission('MENU_DIVIDENDS')"><template #icon><t-icon name="coin" /></template>股东分红</t-menu-item>
          <t-menu-item value="/reports" v-if="hasPermission('MENU_REPORTS')"><template #icon><t-icon name="file-excel" /></template>报表体系</t-menu-item>
          <t-menu-item value="/assets" v-if="hasPermission('MENU_ASSETS')"><template #icon><t-icon name="building" /></template>固定资产</t-menu-item>
        </t-menu-group>
        <t-menu-group title="人力资源" v-show="!isCollapsed" v-if="hasPermission('MENU_EMPLOYEES') || hasPermission('MENU_EXTERNAL_PERSONNEL') || hasPermission('MENU_SCHEDULING') || hasPermission('MENU_ATTENDANCE') || hasPermission('MENU_PAYROLL') || hasPermission('MENU_PERFORMANCE') || hasPermission('MENU_CLEANER')">
          <t-menu-item value="/employees" v-if="hasPermission('MENU_EMPLOYEES')"><template #icon><t-icon name="user" /></template>员工档案</t-menu-item>
          <t-menu-item value="/external-personnel" v-if="hasPermission('MENU_EXTERNAL_PERSONNEL')"><template #icon><t-icon name="user-add" /></template>外聘人员</t-menu-item>
          <t-menu-item value="/scheduling" v-if="hasPermission('MENU_SCHEDULING')"><template #icon><t-icon name="time" /></template>智能排班</t-menu-item>
          <t-menu-item value="/attendance" v-if="hasPermission('MENU_ATTENDANCE')"><template #icon><t-icon name="check-circle" /></template>考勤管理</t-menu-item>
          <t-menu-item value="/payroll" v-if="hasPermission('MENU_PAYROLL')"><template #icon><t-icon name="money" /></template>薪资核算</t-menu-item>
          <t-menu-item value="/performance" v-if="hasPermission('MENU_PERFORMANCE')"><template #icon><t-icon name="star" /></template>绩效考核</t-menu-item>
          <t-menu-item value="/cleaner" v-if="hasPermission('MENU_CLEANER')"><template #icon><t-icon name="clean" /></template>保洁员管理</t-menu-item>
        </t-menu-group>
        <t-menu-group title="市场营销" v-show="!isCollapsed" v-if="hasPermission('MENU_CAMPAIGNS') || hasPermission('MENU_COUPONS') || hasPermission('MENU_PLATFORM_ACTIVITIES') || hasPermission('MENU_ANALYSIS')">
          <t-menu-item value="/campaigns" v-if="hasPermission('MENU_CAMPAIGNS')"><template #icon><t-icon name="announcement" /></template>营销活动</t-menu-item>
          <t-menu-item value="/coupons" v-if="hasPermission('MENU_COUPONS')"><template #icon><t-icon name="coupon" /></template>优惠券</t-menu-item>
          <t-menu-item value="/platform-activities" v-if="hasPermission('MENU_PLATFORM_ACTIVITIES')"><template #icon><t-icon name="share" /></template>平台活动</t-menu-item>
          <t-menu-item value="/analysis" v-if="hasPermission('MENU_ANALYSIS')"><template #icon><t-icon name="chart" /></template>效果分析</t-menu-item>
        </t-menu-group>

        <t-menu-item value="/devices" v-if="hasPermission('MENU_DEVICES')">
          <template #icon><t-icon name="server" /></template>
          IoT设备管理
        </t-menu-item>
        <t-menu-item value="/scenes" v-if="hasPermission('MENU_SCENES')">
          <template #icon><t-icon name="control-platform" /></template>
          场景配置
        </t-menu-item>
        <t-menu-item value="/alerts" v-if="hasPermission('MENU_ALERTS')">
          <template #icon>
            <t-badge :count="alertCount" :offset="[-2, 4]">
              <t-icon name="error-circle" />
            </t-badge>
          </template>
          告警中心
        </t-menu-item>
        <t-menu-item value="/audit" v-if="hasPermission('MENU_AUDIT')">
          <template #icon><t-icon name="file-search" /></template>
          操作审计
        </t-menu-item>

        <t-menu-group title="系统管理" v-show="!isCollapsed" v-if="hasPermission('MENU_APPROVAL_TASKS') || hasPermission('MENU_WORKFLOW_DEFS') || hasPermission('MENU_ROLES') || hasPermission('MENU_PERMISSIONS') || hasPermission('MENU_USER_ROLES')">
          <t-menu-item value="/approval-tasks" v-if="hasPermission('MENU_APPROVAL_TASKS')"><template #icon><t-icon name="check-circle" /></template>审批中心</t-menu-item>
          <t-menu-item value="/workflow-defs" v-if="hasPermission('MENU_WORKFLOW_DEFS')"><template #icon><t-icon name="control-platform" /></template>流程定义</t-menu-item>
          <t-menu-item value="/roles" v-if="hasPermission('MENU_ROLES')"><template #icon><t-icon name="user-business" /></template>角色管理</t-menu-item>
          <t-menu-item value="/permissions" v-if="hasPermission('MENU_PERMISSIONS')"><template #icon><t-icon name="setting" /></template>权限配置</t-menu-item>
          <t-menu-item value="/user-roles" v-if="hasPermission('MENU_USER_ROLES')"><template #icon><t-icon name="user-add" /></template>用户角色分配</t-menu-item>
        </t-menu-group>
      </t-menu>

      <div class="collapse-trigger" @click="isCollapsed = !isCollapsed">
        <t-icon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" />
        <span v-show="!isCollapsed" class="collapse-text">收起菜单</span>
      </div>
    </aside>

    <div class="main-area">
      <header class="app-header">
        <div class="header-left">
          <t-button variant="text" shape="square" @click="isCollapsed = !isCollapsed">
            <template #icon><t-icon name="view-list" size="20px" /></template>
          </t-button>
          <span class="page-title">{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <t-tag v-if="alertCount" theme="danger" variant="light" style="cursor:pointer" @click="router.push('/alerts')">
            ⚠ {{ alertCount }} 条告警
          </t-tag>
          <t-tag :theme="heartbeatStatus === 'good' ? 'success' : heartbeatStatus === 'slow' ? 'warning' : 'danger'" variant="light" :style="{ cursor:'pointer' }" @click="resetHeartbeat">
            <span :class="['heartbeat-dot', heartbeatStatus]"></span>
            {{ heartbeatLabel }}
          </t-tag>
          <t-tag theme="success" variant="light">系统运行中</t-tag>
          <t-tag variant="light">{{ currentTime }}</t-tag>
          <span class="user-info" v-if="currentUser">
            <t-icon name="user-circle" size="18px" />
            {{ currentUser }}
          </span>
          <t-button size="small" variant="text" @click="handleLogout">退出登录</t-button>
        </div>
      </header>
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { hasPermission } from '@/utils/permission'
import { alerts } from '@/mock/data'

const router = useRouter()
const route = useRoute()

const isCollapsed = ref(false)
const currentTime = ref('')
const heartbeatStatus = ref<'good' | 'slow' | 'dead'>('good')
const heartbeatLabel = ref('IoT延迟 12ms')

// Simulate IoT heartbeat check (in production, ping HA or MQTT broker)
function checkHeartbeat() {
  const latency = Math.floor(Math.random() * 100 + 5)
  if (latency < 50) { heartbeatStatus.value = 'good'; heartbeatLabel.value = `IoT延迟 ${latency}ms` }
  else if (latency < 200) { heartbeatStatus.value = 'slow'; heartbeatLabel.value = `IoT延迟 ${latency}ms ⚠` }
  else { heartbeatStatus.value = 'dead'; heartbeatLabel.value = `IoT延迟 ${latency}ms 🚫` }
}
function resetHeartbeat() { heartbeatStatus.value = 'good'; heartbeatLabel.value = 'IoT延迟 12ms' }
let timer: ReturnType<typeof setInterval>

const isLoginPage = computed(() => route.meta.noAuth === true)
const currentUser = computed(() => localStorage.getItem('erp_user'))
const activeMenu = computed(() => {
  if (route.path.startsWith('/room-detail')) return '/rooms'
  return route.path
})
const pageTitle = computed(() => (route.meta.title as string) || '')

const alertCount = computed(() => {
  return alerts.alerts.filter(a => a.status === 'Unresolved').length
})

function onMenuChange(value: string) {
  router.push(value)
}

function handleLogout() {
  localStorage.removeItem('erp_logged_in')
  localStorage.removeItem('erp_user')
  router.push('/login')
}

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', { hour12: false })
}

function handleResize() {
  if (window.innerWidth < 1024) isCollapsed.value = true
}
let hbTimer: ReturnType<typeof setInterval>

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
  // Heartbeat check every 5 seconds
  checkHeartbeat()
  hbTimer = setInterval(checkHeartbeat, 5000)
  // Responsive sidebar
  handleResize()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  clearInterval(timer)
  clearInterval(hbTimer)
  window.removeEventListener('resize', handleResize)
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.app-aside {
  width: 232px;
  flex-shrink: 0;
  height: 100%;
  background: #1a1a1a !important;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 100;
  transition: width 0.3s ease;
}

.app-aside.is-collapsed {
  width: 64px;
}

/* TDesign menu: fill remaining sidebar space, scroll if needed */
.app-aside .t-menu {
  flex: 1;
  overflow-y: auto;
}

/* Ensure menu items don't clip badge content */
.app-aside .t-menu .t-menu__item {
  overflow: visible;
}

.sidebar-header {
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}
.logo-text {
  display: block;
  color: #fff;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
}
.logo-compact {
  font-size: 16px;
  letter-spacing: 1px;
}
.logo-sub {
  display: block;
  color: rgba(255,255,255,0.5);
  font-size: 12px;
  margin-top: 4px;
}

.collapse-trigger {
  margin-top: auto;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  border-top: 1px solid rgba(255,255,255,0.1);
  font-size: 13px;
  transition: color .15s;
  user-select: none;
  flex-shrink: 0;
}
.collapse-trigger:hover { color: rgba(255,255,255,0.85); background: rgba(255,255,255,0.05); }
.collapse-text { font-size: 12px; }

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f5f7fa;
  min-width: 0;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e7e7e7;
  height: 56px;
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 8px; }
.page-title { font-size: 16px; font-weight: 600; color: #333; }
.header-right { display: flex; align-items: center; gap: 12px; }

.user-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.heartbeat-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; vertical-align:middle; }
.heartbeat-dot.good { background:#00A870; box-shadow:0 0 6px rgba(0,168,112,.5); animation: pulse-green 2s infinite; }
.heartbeat-dot.slow { background:#E37318; box-shadow:0 0 6px rgba(227,115,24,.5); animation: pulse-orange 1.5s infinite; }
.heartbeat-dot.dead { background:#D54941; box-shadow:0 0 6px rgba(213,73,65,.5); animation: pulse-red 1s infinite; }
@keyframes pulse-green { 0%,100% { opacity:1 } 50% { opacity:0.5 } }
@keyframes pulse-orange { 0%,100% { opacity:1; transform:scale(1) } 50% { opacity:0.6; transform:scale(1.3) } }
@keyframes pulse-red { 0%,100% { opacity:1; transform:scale(1) } 50% { opacity:0.4; transform:scale(1.5) } }

.app-content {
  flex: 1;
  padding: 24px;
  background: #f5f7fa;
  overflow-y: auto;
}
</style>
