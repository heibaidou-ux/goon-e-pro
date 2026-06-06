const API = require('../../utils/api')
Page({
  data: { storeName: '盈隆店', stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0 }, todos: [] },
  onShow() {
    API.getDashboardStats().then(stats => this.setData({ stats }))
    API.getTodos().then(todos => this.setData({ todos }))
  },
  goRoomStatus() { wx.navigateTo({ url: '/pages/room-status/room-status' }) },
  goDeviceMonitor() { wx.navigateTo({ url: '/pages/device-monitor/device-monitor' }) },
  goCleaning() { wx.navigateTo({ url: '/pages/cleaning-task/cleaning-task' }) },
  goOrders() { wx.navigateTo({ url: '/pages/order-management/order-management' }) },
  goTodo() { wx.navigateTo({ url: '/pages/todo/todo' }) },
  goProfile() { wx.navigateTo({ url: '/pages/profile/profile' }) }
})