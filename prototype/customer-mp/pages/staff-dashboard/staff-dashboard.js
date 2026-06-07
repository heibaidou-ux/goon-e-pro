const API = require('../../utils/staff-api')
Page({
  data: { storeName: '盈隆店', stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0 }, todos: [] },
  onShow() {
    API.getDashboardStats().then(stats => this.setData({ stats }))
    API.getTodos().then(todos => this.setData({ todos }))
  },
  goRoomStatus() { wx.navigateTo({ url: '/pages/staff-room-status/staff-room-status' }) },
  goDeviceMonitor() { wx.navigateTo({ url: '/pages/staff-device-monitor/staff-device-monitor' }) },
  goCleaning() { wx.navigateTo({ url: '/pages/staff-cleaning-task/staff-cleaning-task' }) },
  goOrders() { wx.navigateTo({ url: '/pages/staff-order-management/staff-order-management' }) },
  goTodo() { wx.navigateTo({ url: '/pages/staff-todo/staff-todo' }) },
  goProfile() { wx.navigateTo({ url: '/pages/staff-profile/staff-profile' }) }
})

