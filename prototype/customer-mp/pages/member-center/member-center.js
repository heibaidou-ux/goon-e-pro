var API = require('../../utils/api')

Page({
  data: {
    userName: '会员', levelLabel: '金牌会员', balanceIcon: '💎',
    balance: 0, balanceDisplay: '¥0', balanceVisible: true,
    totalSpent: 0, visitCount: 0, points: 0,
    showRechargeModal: false,
    selectedAmount: 100,
    selectedPayment: 'WeChat'
  },

  onShow: function() {
    // 第一条：从storage恢复余额显隐状态
    try {
      var v = wx.getStorageSync('balance_visible')
      if (v !== '') { this.data.balanceVisible = v; this.setData({ balanceVisible: v }) }
    } catch(e) {}

    var self = this
    Promise.all([API.getCurrentUser(), API.getBalance()]).then(function(results) {
      var user = results[0], balance = results[1] || 0
      if (user) {
        var levels = { Normal: { label:'普通会员', icon:'👛' }, Silver: { label:'银卡会员', icon:'💰' }, Gold: { label:'金牌会员', icon:'💎' }, Diamond: { label:'钻石会员', icon:'💳' } }
        var lv = levels[user.memberLevel] || levels.Gold
        self.setData({
          userName: user.name || user.nickname || user.phone || '会员',
          levelLabel: lv.label,
          balanceIcon: lv.icon,
          totalSpent: user.totalSpent || 0,
          visitCount: user.visitCount || 0,
          points: user.totalSpent || 0
        })
      }
      self.setData({ balance: balance })
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

  toggleBalance: function() {
    var visible = !this.data.balanceVisible
    this.setData({ balanceVisible: visible })
    this.updateBalanceDisplay()
    try { wx.setStorageSync('balance_visible', visible) } catch(e) {}
  },

  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goCoupons: function() { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },
  toastComing: function() { wx.showToast({ title: '开发中', icon: 'none' }) },

  showTopup: function() {
    this.setData({ showRechargeModal: true, selectedAmount: 100, selectedPayment: 'WeChat' })
  },
  hideRecharge: function() { this.setData({ showRechargeModal: false }) },
  selectAmount: function(e) { this.setData({ selectedAmount: parseInt(e.currentTarget.dataset.amount) }) },
  selectPayment: function(e) { this.setData({ selectedPayment: e.currentTarget.dataset.payment }) },

  confirmRecharge: function() {
    var self = this
    var method = self.data.selectedPayment
    if (method === 'Balance') { wx.showToast({ title: '余额充值不支持余额支付', icon: 'none' }); return }
    this.setData({ showRechargeModal: false })
    wx.showLoading({ title: '充值中...' })
    API.topUp(self.data.selectedAmount, method).then(function(r) {
      wx.hideLoading()
      wx.showToast({ title: '✅ 充值成功！+¥' + r.amount + (r.bonus > 0 ? ' (赠送¥' + r.bonus + ')' : ''), icon: 'success' })
      self.setData({ balance: r.newBalance })
      self.updateBalanceDisplay()
    }).catch(function(err) { wx.hideLoading(); wx.showToast({ title: err.message || '充值失败', icon: 'none' }) })
  },

  handleLogout: function() {
    wx.showModal({
      title: '退出登录', content: '确定要退出当前账号吗？',
      success: function(res) { if (res.confirm) { API.logout(); wx.reLaunch({ url: '/pages/home/home' }) } }
    })
  }
})
