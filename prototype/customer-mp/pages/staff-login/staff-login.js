var API = require('../../utils/api')
var app = getApp()

Page({
  data: {
    selectedRole: 'staff',
    account: 'admin',
    password: '8888',
    loading: false,
    error: ''
  },

  switchRole: function(e) {
    var role = e.currentTarget.dataset.role
    var account = role === 'staff' ? 'admin' : 'shareholder'
    this.setData({ selectedRole: role, account: account, error: '' })
  },

  onAccount: function(e) { this.setData({ account: e.detail.value }) },
  onPassword: function(e) { this.setData({ password: e.detail.value }) },

  doLogin: function() {
    var self = this
    if (!self.data.account || !self.data.password) return
    self.setData({ loading: true, error: '' })

    API.loginWithRole(self.data.account, self.data.password, self.data.selectedRole).then(function(user) {
      app.globalData.user = user
      app.globalData.loggedIn = true
      app.globalData.userRole = user.role

      // 根据角色跳转不同首页
      var homePage = ''
      if (user.role === 'staff') homePage = '/pages/staff-dashboard/staff-dashboard'
      else if (user.role === 'shareholder') homePage = '/pages/investor-workbench/investor-workbench'

      wx.reLaunch({ url: homePage })
    }).catch(function(err) {
      self.setData({ error: err.message || '登录失败', loading: false })
    })
  },

  goHome: function() {
    wx.reLaunch({ url: '/pages/home/home' })
  }
})
