/**
 * 高岸ERP 客人端 小程序入口
 */
const API = require('./utils/api')

App({
  globalData: {
    user: null,
    loggedIn: false
  },

  onLaunch() {
    // 检查登录状态
    const user = API.getCurrentUser()
    if (user) {
      this.globalData.user = user
      this.globalData.loggedIn = true
    }
  },

  // 便捷方法：显示Toast
  toast(msg) {
    wx.showToast({ title: msg, icon: 'none' })
  }
})
