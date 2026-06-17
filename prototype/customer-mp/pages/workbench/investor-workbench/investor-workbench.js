var API = require('../../../utils/api')

Page({
  data: {},
  onShow: function() {},
  goHome: function() {
    API.logout()
    wx.reLaunch({ url: '/pages/home/home' })
  },
  goStaffLogin: function() {
    wx.reLaunch({ url: '/pages/staff/staff-login/staff-login' })
  }
})
