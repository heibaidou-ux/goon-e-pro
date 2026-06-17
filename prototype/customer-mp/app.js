const API = require('./utils/api')

// 页面权限映射
const PAGE_ROLES = {
  'pages/home/home': ['guest', 'staff'],
  'pages/room-list/room-list': ['guest', 'staff'],
  'pages/room-detail/room-detail': ['guest', 'staff'],
  'pages/booking-confirm/booking-confirm': ['guest', 'staff'],
  'pages/tea-shop/tea-shop': ['guest'],
  'pages/my-orders/my-orders': ['guest', 'staff'],
  'pages/member-center/member-center': ['guest'],
  'pages/room-control/room-control': ['guest', 'staff'],
  'pages/my-coupons/my-coupons': ['guest'],
  'pages/coupon-verify/coupon-verify': ['guest'],
}

App({
  globalData: {
    user: null,
    loggedIn: false,
    userRole: null,
    _preheatTimer: null
  },

  onLaunch() {
    var user = API.getCurrentUser()
    if (user) {
      this.globalData.user = user
      this.globalData.loggedIn = true
      this.globalData.userRole = user.role || API.getUserRole() || 'guest'
    }
    // 启动空调预开轮询
    this.startPreheatScheduler()
  },

  // ── 空调预开调度器 ──
  // 每分钟检查一次，如有订单在5分钟内开始则触发预开场景
  startPreheatScheduler: function() {
    var self = this
    if (this.globalData._preheatTimer) return
    this.globalData._preheatTimer = setInterval(function() {
      self.checkPreheat()
    }, 60000)
    // 启动时立即检查一次
    setTimeout(function() { self.checkPreheat() }, 3000)
  },

  checkPreheat: function() {
    var now = new Date()
    var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    var curMin = now.getHours()*60 + now.getMinutes()
    var checked = {}

    // 从API获取所有订单（含mock数据）
    var ctx = this
    try {
      var utilApi = require('./utils/api')
      utilApi.getAllOrders().then(function(bookings) {
        if (!bookings || !bookings.length) return
        for (var i = 0; i < bookings.length; i++) {
          var b = bookings[i]
          if (b.status !== 'Booked' || b.date !== todayStr || !b.time) continue
          if (checked[b.roomId]) continue

          var parts = b.time.split('-')
          if (parts.length < 2) continue
          var sp = parts[0].split(':')
          var startMin = parseInt(sp[0])*60 + parseInt(sp[1])

          var diff = startMin - curMin
          // 距开始1-2分钟才触发，避免过早开空调
          if (diff >= 1 && diff <= 2) {
            checked[b.roomId] = true
            try { utilApi.executeScene(b.roomId, 'PreOpen').catch(function(){}) } catch(e) {}
          }
        }
      }).catch(function() {})
    } catch(e) {}
  },

  checkPageAccess(pagePath) {
    var role = this.globalData.userRole || 'guest'
    var allowed = PAGE_ROLES[pagePath]
    if (!allowed) return true
    return allowed.indexOf(role) >= 0
  },

  getHomePage() {
    var role = this.globalData.userRole || 'guest'
    switch (role) {
      case 'staff': return 'pages/staff/staff-dashboard/staff-dashboard'
      case 'shareholder': return 'pages/workbench/investor-workbench/investor-workbench'
      default: return 'pages/home/home'
    }
  },

  toast(msg) {
    wx.showToast({ title: msg, icon: 'none' })
  }
})
