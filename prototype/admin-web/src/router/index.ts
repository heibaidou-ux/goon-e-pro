import { createRouter, createWebHashHistory } from 'vue-router'
import { hasPermission } from '@/utils/permission'

// Map routes to permission resourceIds
const routeResourceMap: Record<string, string> = {
  '/dashboard': 'MENU_DASHBOARD',
  '/rooms': 'MENU_ROOMS',
  '/room-detail': 'MENU_ROOMS',
  '/devices': 'MENU_DEVICES',
  '/scenes': 'MENU_SCENES',
  '/alerts': 'MENU_ALERTS',
  '/audit': 'MENU_AUDIT',
  '/products': 'MENU_PRODUCTS',
  '/purchases': 'MENU_PURCHASES',
  '/inventory': 'MENU_INVENTORY',
  '/suppliers': 'MENU_SUPPLIERS',
  '/revenue': 'MENU_REVENUE',
  '/expense': 'MENU_EXPENSE',
  '/settlement': 'MENU_SETTLEMENT',
  '/reconciliation': 'MENU_RECONCILIATION',
  '/dividends': 'MENU_DIVIDENDS',
  '/reports': 'MENU_REPORTS',
  '/assets': 'MENU_ASSETS',
  '/employees': 'MENU_EMPLOYEES',
  '/external-personnel': 'MENU_EXTERNAL_PERSONNEL',
  '/scheduling': 'MENU_SCHEDULING',
  '/attendance': 'MENU_ATTENDANCE',
  '/payroll': 'MENU_PAYROLL',
  '/performance': 'MENU_PERFORMANCE',
  '/cleaner': 'MENU_CLEANER',
  '/campaigns': 'MENU_CAMPAIGNS',
  '/coupons': 'MENU_COUPONS',
  '/platform-activities': 'MENU_PLATFORM_ACTIVITIES',
  '/analysis': 'MENU_ANALYSIS',
  '/workflow-defs': 'MENU_WORKFLOW_DEFS',
  '/approval-tasks': 'MENU_APPROVAL_TASKS',
  '/roles': 'MENU_ROLES',
  '/permissions': 'MENU_PERMISSIONS',
  '/user-roles': 'MENU_USER_ROLES',
}

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/login', name: 'Login', component: () => import('@/views/Login.vue'), meta: { title: '登录', noAuth: true } },
    { path: '/', redirect: '/dashboard' },
    { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue'), meta: { title: '门店总览' } },
    { path: '/rooms', name: 'RoomManagement', component: () => import('@/views/RoomManagement.vue'), meta: { title: '房间管理' } },
    { path: '/room-detail/:roomId', name: 'RoomDetail', component: () => import('@/views/RoomDetail.vue'), meta: { title: '房间详情' } },
    { path: '/devices', name: 'DeviceManagement', component: () => import('@/views/DeviceManagement.vue'), meta: { title: 'IoT设备管理' } },
    { path: '/scenes', name: 'SceneConfig', component: () => import('@/views/SceneConfig.vue'), meta: { title: '场景配置' } },
    { path: '/alerts', name: 'AlertCenter', component: () => import('@/views/AlertCenter.vue'), meta: { title: '告警中心' } },
    { path: '/audit', name: 'AuditLog', component: () => import('@/views/AuditLog.vue'), meta: { title: '操作审计' } },

    // D05 供应链域
    { path: '/products', name: 'ProductCatalog', component: () => import('@/views/ProductCatalog.vue'), meta: { title: '商品目录管理' } },
    { path: '/purchases', name: 'PurchaseManagement', component: () => import('@/views/PurchaseManagement.vue'), meta: { title: '采购与配货管理' } },
    { path: '/inventory', name: 'InventoryManagement', component: () => import('@/views/InventoryManagement.vue'), meta: { title: '库存管理' } },
    { path: '/suppliers', name: 'SupplierManagement', component: () => import('@/views/SupplierManagement.vue'), meta: { title: '供应商管理' } },

    // D06 财务域
    { path: '/revenue', name: 'RevenueManagement', component: () => import('@/views/RevenueManagement.vue'), meta: { title: '收入管理' } },
    { path: '/expense', name: 'ExpenseManagement', component: () => import('@/views/ExpenseManagement.vue'), meta: { title: '支出管理' } },
    { path: '/settlement', name: 'MonthlySettlement', component: () => import('@/views/MonthlySettlement.vue'), meta: { title: '自动月结' } },
    { path: '/reconciliation', name: 'Reconciliation', component: () => import('@/views/Reconciliation.vue'), meta: { title: '智能对账' } },
    { path: '/dividends', name: 'Dividends', component: () => import('@/views/Dividends.vue'), meta: { title: '股东分红' } },
    { path: '/reports', name: 'Reports', component: () => import('@/views/Reports.vue'), meta: { title: '报表体系' } },
    { path: '/assets', name: 'FixedAssets', component: () => import('@/views/FixedAssets.vue'), meta: { title: '固定资产管理' } },

    // D07 人力资源域
    { path: '/employees', name: 'EmployeeFiles', component: () => import('@/views/EmployeeFiles.vue'), meta: { title: '员工档案' } },
    { path: '/external-personnel', name: 'ExternalPersonnel', component: () => import('@/views/ExternalPersonnel.vue'), meta: { title: '外聘人员管理' } },
    { path: '/scheduling', name: 'Scheduling', component: () => import('@/views/Scheduling.vue'), meta: { title: '智能排班' } },
    { path: '/attendance', name: 'Attendance', component: () => import('@/views/Attendance.vue'), meta: { title: '考勤管理' } },
    { path: '/payroll', name: 'Payroll', component: () => import('@/views/Payroll.vue'), meta: { title: '薪资核算' } },
    { path: '/performance', name: 'Performance', component: () => import('@/views/Performance.vue'), meta: { title: '绩效考核' } },
    { path: '/cleaner', name: 'CleanerManagement', component: () => import('@/views/CleanerManagement.vue'), meta: { title: '保洁员考核与薪资' } },

    // D04 市场营销域
    { path: '/campaigns', name: 'CampaignManagement', component: () => import('@/views/CampaignManagement.vue'), meta: { title: '营销活动管理' } },
    { path: '/coupons', name: 'CouponManagement', component: () => import('@/views/CouponManagement.vue'), meta: { title: '优惠券管理' } },
    { path: '/platform-activities', name: 'PlatformActivities', component: () => import('@/views/PlatformActivities.vue'), meta: { title: '第三方平台活动' } },
    { path: '/analysis', name: 'Analysis', component: () => import('@/views/Analysis.vue'), meta: { title: '营销效果分析' } },

    // 系统管理 - 流程与权限
    { path: '/workflow-defs', name: 'WorkflowDefs', component: () => import('@/views/WorkflowDefs.vue'), meta: { title: '流程定义管理' } },
    { path: '/approval-tasks', name: 'ApprovalTasks', component: () => import('@/views/ApprovalTasks.vue'), meta: { title: '审批中心' } },
    { path: '/roles', name: 'RoleManagement', component: () => import('@/views/RoleManagement.vue'), meta: { title: '角色管理' } },
    { path: '/permissions', name: 'PermissionConfig', component: () => import('@/views/PermissionConfig.vue'), meta: { title: '权限配置' } },
    { path: '/user-roles', name: 'UserRoleAssignment', component: () => import('@/views/UserRoleAssignment.vue'), meta: { title: '用户角色分配' } },
  ]
})

function getRouteResourceId(path: string): string | null {
  // Handle parameterized routes like /room-detail/xxx
  for (const [prefix, resourceId] of Object.entries(routeResourceMap)) {
    if (path === prefix || path.startsWith(prefix + '/')) return resourceId
  }
  return null
}

router.beforeEach((to, _from, next) => {
  if (to.meta.noAuth) {
    next()
    return
  }
  const loggedIn = localStorage.getItem('erp_logged_in')
  if (loggedIn !== 'true') {
    next('/login')
    return
  }

  // Permission check
  const resourceId = getRouteResourceId(to.path)
  if (resourceId && !hasPermission(resourceId)) {
    next('/dashboard') // Redirect to dashboard if no permission
    return
  }

  next()
})

export default router
