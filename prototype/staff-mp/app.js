/**
 * 高岸ERP 店员端 小程序入口
 */
const API = require('./utils/api')

App({
  globalData: {
    user: null,
    loggedIn: false,
    storeId: 'ST001'
  },

  onLaunch() {
    const user = API.getCurrentUser()
    if (user) {
      this.globalData.user = user
      this.globalData.loggedIn = true
    }
  },

  toast(msg) {
    wx.showToast({ title: msg, icon: 'none' })
  }
})
