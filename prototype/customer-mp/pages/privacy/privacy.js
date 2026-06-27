/**
 * 隐私协议页面
 */
Page({
  onLoad() {
    // 检查隐私授权状态
    if (wx.getPrivacySetting) {
      wx.getPrivacySetting({
        success: res => {
          if (res.needAuthorization) {
            // 需要用户授权
          }
        }
      })
    }
  },

  onAgree() {
    // 同意隐私协议后返回上一页
    wx.navigateBack({ delta: 1 })
  },

  onDisagree() {
    wx.showToast({
      title: '需要同意隐私协议才能使用',
      icon: 'none',
      duration: 3000
    })
  }
})
