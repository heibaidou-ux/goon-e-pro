var API = require('../../utils/api')

Page({
  data: {
    userName: '会员', levelLabel: '普通会员',
    balance: 0, balanceDisplay: '¥0', balanceVisible: true,
    totalSpent: 0, visitCount: 0,
    selectedAmount: 100,
    showPaymentModal: false,
    selectedPayment: 'WeChat'
  },

  onShow: function() {
    var self = this
    var user = API.getCurrentUser()
    if (user) {
      var levels = { Normal:'普通会员', Silver:'银卡会员', Gold:'金卡会员', Diamond:'钻石会员' }
      // 第10条：显示真实姓名
      var displayName = user.name || user.nickname || user.phone || '会员'
      self.setData({
        userName: displayName,
        levelLabel: levels[user.memberLevel] || '普通会员',
        totalSpent: user.totalSpent || 0,
        visitCount: user.visitCount || 0
      })
    }
    API.getBalance().then(function(b) {
      self.setData({ balance: b || 0 })
      self.updateBalanceDisplay()
    })
  },

  updateBalanceDisplay: function() {
    if (this.data.balanceVisible) {
      this.setData({ balanceDisplay: '¥' + this.data.balance })
    } else {
      this.setData({ balanceDisplay: '****' })
    }
  },

  // 第33条/第4条：隐藏/显示余额
  toggleBalance: function() {
    this.setData({ balanceVisible: !this.data.balanceVisible })
    this.updateBalanceDisplay()
  },

  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goCoupons: function() { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },

  selectAmount: function(e) {
    this.setData({ selectedAmount: parseInt(e.currentTarget.dataset.amount) })
  },

  // 第9条：支付方式选择
  doRecharge: function() {
    this.setData({ showPaymentModal: true, selectedPayment: 'WeChat' })
  },

  selectPayment: function(e) {
    this.setData({ selectedPayment: e.currentTarget.dataset.payment })
  },

  cancelPayment: function() {
    this.setData({ showPaymentModal: false })
  },

  confirmRecharge: function() {
    var self = this
    this.setData({ showPaymentModal: false })
    wx.showLoading({ title: '充值中...' })
    API.topUp(self.data.selectedAmount, self.data.selectedPayment).then(function(r) {
      wx.hideLoading()
      wx.showToast({
        title: '✅ 充值成功！¥' + r.amount + (r.bonus > 0 ? ' (赠送¥' + r.bonus + ')' : ''),
        icon: 'none', duration: 2000
      })
      self.setData({ balance: r.newBalance })
      self.updateBalanceDisplay()
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '充值失败', icon: 'none' })
    })
  }
})
