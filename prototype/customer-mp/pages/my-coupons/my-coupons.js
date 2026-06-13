var API = require('../../utils/api')

// 平台名称映射
var platformLabels = {
  Meituan: '美团', Douyin: '抖音', Dianping: '点评', Gaode: '高德', System: '系统赠送'
}

Page({
  data: {
    coupons: [],
    filteredCoupons: [],
    activeTab: 'available',
    availableCount: 0,
    usedCount: 0
  },

  onLoad: function() {
    if (!require('../../utils/api').isLoggedIn()) { wx.reLaunch({ url: '/pages/home/home?showLogin=1' }); return }
    var self = this
    API.getUserCoupons().then(function(coupons) {
      self.setData({ coupons: coupons })
      self.filterCoupons()
    })
  },

  // 切换tab后重新过滤
  filterCoupons: function() {
    var coupons = this.data.coupons
    var activeTab = this.data.activeTab
    // 给每条数据附加平台中文标签
    var enriched = coupons.map(function(c) {
      return {
        code: c.code, value: c.value, type: c.type, desc: c.desc,
        platform: c.platform, used: c.used, expiry: c.expiry,
        platformLabel: platformLabels[c.platform] || c.platform
      }
    })
    var available = enriched.filter(function(c) { return !c.used })
    var used = enriched.filter(function(c) { return c.used })
    this.setData({
      availableCount: available.length,
      usedCount: used.length,
      filteredCoupons: activeTab === 'available' ? available : used
    })
  },

  switchTab: function(e) {
    var tab = e.currentTarget.dataset.tab
    if (tab === this.data.activeTab) return
    this.setData({ activeTab: tab })
    this.filterCoupons()
  },

  // 点击可用券 → 验券
  useCoupon: function(e) {
    var ds = e.currentTarget.dataset
    wx.showModal({
      title: '使用优惠券',
      content: ds.desc + '\n价值 ¥' + ds.value + '\n是否前往验券？',
      success: function(res) {
        if (res.confirm) {
          wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify?code=' + ds.code })
        }
      }
    })
  }
})
