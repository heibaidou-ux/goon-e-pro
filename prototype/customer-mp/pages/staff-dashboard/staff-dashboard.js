var STAFF_API = require('../../utils/staff-api')
var API = require('../../utils/api')

Page({
  data: { storeName: '盈隆店', stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0 }, todos: [] },

  onLoad: function() {
    var role = API.getUserRole()
    if (role !== 'staff') { wx.reLaunch({ url: '/pages/home/home' }); return }
  },

  onShow: function() {
    STAFF_API.getDashboardStats().then(stats => this.setData({ stats }))
    STAFF_API.getTodos().then(todos => this.setData({ todos }))
  },

  goRoomStatus: function() { wx.navigateTo({ url: '/pages/staff-room-status/staff-room-status' }) },
  goDeviceMonitor: function() { wx.navigateTo({ url: '/pages/staff-device-monitor/staff-device-monitor' }) },
  goCleaning: function() { wx.navigateTo({ url: '/pages/staff-cleaning-task/staff-cleaning-task' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/staff-order-management/staff-order-management' }) },
  goTodo: function() { wx.navigateTo({ url: '/pages/staff-todo/staff-todo' }) },
  goProfile: function() { wx.navigateTo({ url: '/pages/staff-profile/staff-profile' }) }
})
