const API = require('../../utils/api')
Page({
  data: { user: {} },
  onShow() { const user = API.getCurrentUser(); if (user) this.setData({ user }) },
  goOrders() { wx.navigateTo({ url: '/pages/order-management/order-management' }) },
  goAttendance() { wx.navigateTo({ url: '/pages/attendance/attendance' }) },
  goScheduling() { wx.navigateTo({ url: '/pages/scheduling/scheduling' }) },
  goReceivable() { wx.navigateTo({ url: '/pages/receivable/receivable' }) },
  goReconciliation() { wx.navigateTo({ url: '/pages/reconciliation/reconciliation' }) },
  doLogout() { API.logout(); wx.reLaunch({ url: '/pages/login/login' }) }
})