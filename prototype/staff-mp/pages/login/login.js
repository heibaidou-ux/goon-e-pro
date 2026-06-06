const API = require('../../utils/api')
Page({
  data: { username: 'admin', password: '8888', loading: false, error: '' },
  onUsername(e) { this.setData({ username: e.detail.value }) },
  onPassword(e) { this.setData({ password: e.detail.value }) },
  doLogin() {
    if (!this.data.username || !this.data.password) return
    this.setData({ loading: true, error: '' })
    API.login(this.data.username, this.data.password).then(user => {
      wx.reLaunch({ url: '/pages/dashboard/dashboard' })
    }).catch(err => {
      this.setData({ error: err.message || '登录失败', loading: false })
    })
  }
})