var STAFF_API = require('../../utils/staff-api')
var API = require('../../utils/api')

Page({
  data: {
    storeName: '盈隆店',
    timeStr: '',
    stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0, orderStatus: 0, alerts: 0 },
    todos: []
  },

  onLoad: function() {
    var role = API.getUserRole()
    if (role !== 'staff') { wx.reLaunch({ url: '/pages/home/home' }); return }
  },

  onShow: function() {
    this.updateTime()
    var self = this
    STAFF_API.getDashboardStats().then(function(stats) { self.setData({ stats: stats }) })
    STAFF_API.getTodos().then(function(todos) { self.setData({ todos: todos }) })
    // 用真实订单数据覆盖mock统计数据
    API.getAllOrders().then(function(orders) {
      if (!orders || !orders.length) return
      var todayStr = new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')+'-'+String(new Date().getDate()).padStart(2,'0')
      var todayOrders = orders.filter(function(o) { return o.date === todayStr || (o.created && o.created.indexOf(todayStr) === 0) })
      var inUse = 0, pending = 0
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].status === 'InUse') inUse++
        if (orders[i].status === 'Booked' || orders[i].status === 'InUse') pending++
      }
      var revenue = 0
      for (var i = 0; i < todayOrders.length; i++) revenue += todayOrders[i].amount || 0
      self.setData({ stats: { roomCount: { inUse: inUse }, todayRevenue: revenue, todayOrders: todayOrders.length, pendingTasks: pending, orderStatus: pending, alerts: 0 } })
    })
    // 从茶品订单中找出待发货的加入待办
    API.getShopOrders().then(function(shopOrders) {
      if (!shopOrders || !shopOrders.length) return
      var shipTodos = []
      for (var i = 0; i < shopOrders.length; i++) {
        var so = shopOrders[i]
        if (so.deliveryMethod === 'express' && (!so.status || so.status === 'PendingDelivery' || so.status === 'Paid')) {
          shipTodos.push({
            id: 'SHIP' + so.orderId,
            title: '📦 发货 — 茶品订单',
            type: 'shipping',
            priority: 'high',
            deadline: '尽快',
            status: 'pending'
          })
        }
      }
      if (shipTodos.length > 0) {
        self.setData({ todos: shipTodos.concat(self.data.todos) })
      }
    })
  },

  updateTime: function() {
    var now = new Date()
    var h = String(now.getHours()).padStart(2,'0')
    var m = String(now.getMinutes()).padStart(2,'0')
    this.setData({ timeStr: h + ':' + m })
  },

  // 四宫格跳转
  goTodo: function() { wx.navigateTo({ url: '/pages/staff-todo/staff-todo' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/staff-order-management/staff-order-management' }) },
  goDeviceMonitor: function() { wx.navigateTo({ url: '/pages/staff-device-monitor/staff-device-monitor' }) },

  // 快捷按钮：验券、开门、监控、对账
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },

  goOpenDoor: function() {
    var self = this
    wx.showActionSheet({
      itemList: ['大茶室C', '中茶室A', '中茶室B', '大会议室'],
      success: function(res) {
        var rooms = ['大茶室C', '中茶室A', '中茶室B', '大会议室']
        var roomIds = ['RM004', 'RM002', 'RM003', 'RM001']
        wx.navigateTo({
          url: '/pages/room-control/room-control?roomId=' + roomIds[res.tapIndex] + '&roomName=' + encodeURIComponent(rooms[res.tapIndex])
        })
      }
    })
  },

  goReconciliation: function() {
    wx.navigateTo({ url: '/pages/staff-reconciliation/staff-reconciliation' })
  },

  // 更多功能：考勤/商品管理/巡检/排班
  goAttendance: function() { wx.navigateTo({ url: '/pages/staff-attendance/staff-attendance' }) },
  goProducts: function() { wx.navigateTo({ url: '/pages/staff-product-management/staff-product-management' }) },
  goInspection: function() { wx.navigateTo({ url: '/pages/staff-inspection/staff-inspection' }) },
  goScheduling: function() { wx.navigateTo({ url: '/pages/staff-scheduling/staff-scheduling' }) },

  // 保留旧导航供其他引用
  goRoomStatus: function() { wx.navigateTo({ url: '/pages/staff-room-status/staff-room-status' }) },
  goCleaning: function() { wx.navigateTo({ url: '/pages/staff-cleaning-task/staff-cleaning-task' }) },
  goProfile: function() { wx.navigateTo({ url: '/pages/staff-profile/staff-profile' }) },

  // 退出登录
  doLogout: function() {
    var self = this
    wx.showModal({
      title: '退出登录',
      content: '确定退出店员端，返回客人首页？',
      success: function(res) {
        if (res.confirm) {
          API.logout()
          wx.reLaunch({ url: '/pages/home/home' })
        }
      }
    })
  }
})
