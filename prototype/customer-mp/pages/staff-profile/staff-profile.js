const API = require('../../utils/staff-api')
Page({
  data: { user: {} },
  onShow() { const user = API.getCurrentUser(); if (user) this.setData({ user }) },
  goOrders() { wx.navigateTo({ url: '/pages/staff-order-management/order-management' }) },
  goAttendance() { wx.navigateTo({ url: '/pages/staff-attendance/attendance' }) },
  goScheduling() { wx.navigateTo({ url: '/pages/staff-scheduling/scheduling' }) },
  goReceivable() { wx.navigateTo({ url: '/pages/staff-receivable/receivable' }) },
  goReconciliation() { wx.navigateTo({ url: '/pages/staff-reconciliation/reconciliation' }) },
  doLogout() { API.logout(); wx.reLaunch({ url: '/pages/staff-login/login' }) }
})
