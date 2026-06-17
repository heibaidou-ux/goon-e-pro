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

    // 从全局存储中读取订单
    try {
      var bookings = wx.getStorageSync('mp_bookings') || []
      for (var i = 0; i < bookings.length; i++) {
        var b = bookings[i]
        if (b.status !== 'Booked' || b.date !== todayStr || !b.time) continue
        // 去重：同一房间只触发一次
        if (checked[b.roomId]) continue

        var parts = b.time.split('-')
        if (parts.length < 2) continue
        var sp = parts[0].split(':')
        var startMin = parseInt(sp[0])*60 + parseInt(sp[1])

        // 距开始还有1-5分钟时触发
        var diff = startMin - curMin
        if (diff >= 1 && diff <= 5) {
          checked[b.roomId] = true
          console.log('[预开] ' + b.roomName + ' 将在' + diff + '分钟后开始，触发空调预开')
          // 触发预开场景（只开空调+轻音乐，不动门锁灯光）
          try { API.executeScene(b.roomId, 'PreOpen').catch(function(){}) } catch(e) {}
        }
      }
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
