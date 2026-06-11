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
  goProfile: function() { wx.navigateTo({ url: '/pages/staff-profile/staff-profile' }) }
})
