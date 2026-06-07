var API = require('../../utils/api')

Page({
  data: { coupons: [] },
  onLoad: function() {
    var self = this
    API.getUserCoupons().then(function(coupons) { self.setData({ coupons: coupons }) })
  },

  // 第6-7条：点击优惠券可引导消费/核销
  useCoupon: function(e) {
    var ds = e.currentTarget.dataset
    if (ds.used === 'true') { wx.showToast({ title: '该券已使用', icon: 'none' }); return }
    wx.showModal({
      title: '使用优惠券',
      content: ds.desc + '\n价值 ¥' + ds.value + '\n是否前往验券？',
      success: function(res) {
        if (res.confirm) {
          wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify?code=' + ds.code })
        }
      }
    })
  },

  goBack: function() { wx.navigateBack() }
})
