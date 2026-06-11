const API = require('./utils/api')

// 页面权限映射：哪些角色可以访问哪些页面
const PAGE_ROLES = {
  // 客人端页面（guest + staff都能访问，staff需要管理客人时）
  'pages/home/home': ['guest', 'staff'],
  'pages/room-list/room-list': ['guest', 'staff'],
  'pages/room-detail/room-detail': ['guest', 'staff'],
  'pages/booking-confirm/booking-confirm': ['guest', 'staff'],
  'pages/tea-shop/tea-shop': ['guest'],
  'pages/my-orders/my-orders': ['guest', 'staff'],
  'pages/member-center/member-center': ['guest'],
  'pages/scan-landing/scan-landing': ['guest'],
  'pages/scan-order/scan-order': ['guest'],
  'pages/scan-bill/scan-bill': ['guest'],
  'pages/room-control/room-control': ['guest', 'staff'],
  'pages/my-coupons/my-coupons': ['guest'],
  'pages/coupon-verify/coupon-verify': ['guest'],

  // 店员端页面（只有staff）
  'pages/staff-login/staff-login': ['guest', 'staff', 'shareholder'],
  'pages/staff-dashboard/staff-dashboard': ['staff'],
  'pages/staff-room-status/staff-room-status': ['staff'],
  'pages/staff-device-monitor/staff-device-monitor': ['staff'],
  'pages/staff-device-control/staff-device-control': ['staff'],
  'pages/staff-scene-control/staff-scene-control': ['staff'],
  'pages/staff-cleaning-task/staff-cleaning-task': ['staff'],
  'pages/staff-inspection/staff-inspection': ['staff'],
  'pages/staff-order-management/staff-order-management': ['staff'],
  'pages/staff-product-management/staff-product-management': ['staff'],
  'pages/staff-attendance/staff-attendance': ['staff'],
  'pages/staff-scheduling/staff-scheduling': ['staff'],
  'pages/staff-todo/staff-todo': ['staff'],
  'pages/staff-profile/staff-profile': ['staff'],
  'pages/staff-receivable/staff-receivable': ['staff'],
  'pages/staff-reconciliation/staff-reconciliation': ['staff'],

  // 股东端页面（shareholder）
  'pages/investor-workbench/investor-workbench': ['shareholder'],
  'pages/gm-workbench/gm-workbench': ['shareholder'],
  'pages/finance-workbench/finance-workbench': ['shareholder'],

  // 工作台页面（所有角色可访问，内容不同）
  'pages/finance-workbench/finance-workbench': ['shareholder'],
  'pages/gm-workbench/gm-workbench': ['shareholder', 'staff'],
  'pages/technician-workbench/technician-workbench': ['staff'],
}

App({
  globalData: {
    user: null,
    loggedIn: false,
    userRole: null
  },

  onLaunch() {
    var user = API.getCurrentUser()
    if (user) {
      this.globalData.user = user
      this.globalData.loggedIn = true
      this.globalData.userRole = user.role || API.getUserRole() || 'guest'
    }
  },

  // 检查当前页面是否有权限访问
  checkPageAccess(pagePath) {
    var role = this.globalData.userRole || 'guest'
    var allowed = PAGE_ROLES[pagePath]
    if (!allowed) return true  // 未配置权限的页面默认开放
    return allowed.indexOf(role) >= 0
  },

  // 获取角色首页
  getHomePage() {
    var role = this.globalData.userRole || 'guest'
    switch (role) {
      case 'staff': return 'pages/staff-dashboard/staff-dashboard'
      case 'shareholder': return 'pages/investor-workbench/investor-workbench'
      default: return 'pages/home/home'
    }
  },

  toast(msg) {
    wx.showToast({ title: msg, icon: 'none' })
  }
})
