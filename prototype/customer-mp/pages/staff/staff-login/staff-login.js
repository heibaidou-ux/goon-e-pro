var API = require('../../../utils/api')
var app = getApp()

Page({
  data: {
    selectedRole: 'staff',
    account: '',
    password: '',
    showPwd: false,
    rememberPwd: false,
    loading: false,
    error: ''
  },

  onLoad: function() {
    // 恢复上次账号和记住的密码
    try {
      var saved = wx.getStorageSync('staff_login_remember') || {}
      if (saved.account) {
        this.setData({
          account: saved.account,
          password: saved.password || '',
          rememberPwd: !!(saved.password)
        })
      }
    } catch(e) {}
  },

  switchRole: function(e) {
    var role = e.currentTarget.dataset.role
    this.setData({ selectedRole: role, account: '', password: '', error: '' })
  },

  onAccount: function(e) { this.setData({ account: e.detail.value }) },
  onPassword: function(e) { this.setData({ password: e.detail.value }) },
  togglePwd: function() { this.setData({ showPwd: !this.data.showPwd }) },
  toggleRemember: function() { this.setData({ rememberPwd: !this.data.rememberPwd }) },

  doLogin: function() {
    var self = this
    if (!self.data.account || !self.data.password) return
    self.setData({ loading: true, error: '' })

    API.loginWithRole(self.data.account, self.data.password, self.data.selectedRole).then(function(user) {
      // 记住密码
      if (self.data.rememberPwd) {
        try { wx.setStorageSync('staff_login_remember', { account: self.data.account, password: self.data.password }) } catch(e) {}
      } else {
        try { wx.setStorageSync('staff_login_remember', { account: self.data.account, password: '' }) } catch(e) {}
      }

      app.globalData.user = user
      app.globalData.loggedIn = true
      app.globalData.userRole = user.role

      // 根据角色跳转不同首页
      var homePage = ''
      if (user.role === 'staff') homePage = '/pages/staff/staff-dashboard/staff-dashboard'
      else if (user.role === 'shareholder') homePage = '/pages/workbench/investor-workbench/investor-workbench'

      wx.reLaunch({ url: homePage })
    }).catch(function(err) {
      self.setData({ error: err.message || '登录失败', loading: false })
    })
  },

  goHome: function() {
    wx.reLaunch({ url: '/pages/home/home' })
  }
})
