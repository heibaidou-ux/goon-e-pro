var API = require('../../../utils/api')
var STAFF_API = require('../../../utils/staff-api')

Page({
  data: { user: { displayName: '店员' } },

  onShow() {
    // 从storage读取当前用户
    try {
      var user = wx.getStorageSync('mp_user') || {}
      this.setData({ user: user })
    } catch(e) {}
  },

  goOrders() { wx.navigateTo({ url: '/pages/staff/staff-order-management/staff-order-management' }) },
  goAttendance() { wx.navigateTo({ url: '/pages/staff/staff-attendance/staff-attendance' }) },
  goScheduling() { wx.navigateTo({ url: '/pages/staff/staff-scheduling/staff-scheduling' }) },
  goReceivable() { wx.navigateTo({ url: '/pages/staff/staff-receivable/staff-receivable' }) },
  goReconciliation() { wx.navigateTo({ url: '/pages/staff/staff-reconciliation/staff-reconciliation' }) },

  doLogout() {
    var self = this
    wx.showModal({
      title: '退出登录',
      content: '确定退出店员端？',
      success: function(res) {
        if (res.confirm) {
          API.logout()
          wx.reLaunch({ url: '/pages/home/home' })
        }
      }
    })
  }
})
