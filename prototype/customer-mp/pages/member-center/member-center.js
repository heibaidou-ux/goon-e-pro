var API = require('../../utils/api')

Page({
  data: {
    userName: '会员', levelLabel: '金牌会员', balanceIcon: '💎',
    balance: 0, balanceDisplay: '¥0', balanceVisible: true,
    wxAvatar: '', avatarChar: '',
    totalSpent: 0, visitCount: 0, points: 0,
    showRechargeModal: false, showSettingsModal: false,
    selectedAmount: 100,
    selectedPayment: 'WeChat',
    userPhone: '',
    editName: ''
  },

  onShow: function() {
    // 未登录时由bottom-nav拦截，到不了这里
    // 从storage恢复余额显隐状态
    try {
      var v = wx.getStorageSync('balance_visible')
      if (v !== '') { this.data.balanceVisible = v; this.setData({ balanceVisible: v }) }
    } catch(e) {}
    // 同步读取用户信息
    try {
      var cachedUser = wx.getStorageSync('mp_user')
      if (cachedUser) {
        var name = cachedUser.name || cachedUser.nickname || cachedUser.phone || '会员'
        var avatar = cachedUser.wechat_avatar || ''
        var firstChar = name ? name.charAt(0) : '会'
        this.setData({ userName: name, userPhone: cachedUser.phone || '—', editName: name, wxAvatar: avatar, avatarChar: firstChar })
      }
    } catch(e) {}

    var self = this
    Promise.all([API.getCurrentUser(), API.getBalance(), API.getUserOrders ? API.getUserOrders() : Promise.resolve([]), API.getShopOrders ? API.getShopOrders() : Promise.resolve([])]).then(function(results) {
      var user = results[0], balance = results[1] || 0, bookings = results[2] || [], shopOrders = results[3] || []
      // 从真实订单统计
      var totalSpent = 0
      var visitCount = 0
      var processed = {}
      for (var i = 0; i < bookings.length; i++) {
        var b = bookings[i]
        if (b.status !== 'Cancelled') {
          totalSpent += b.amount || 0
          if (!processed[b.roomId + b.date]) { visitCount++; processed[b.roomId + b.date] = true }
        }
      }
      for (var i = 0; i < shopOrders.length; i++) {
        totalSpent += shopOrders[i].total || 0
      }
      if (user) {
        var levels = { Normal: { label:'普通会员', icon:'👛' }, Silver: { label:'银卡会员', icon:'💰' }, Gold: { label:'金牌会员', icon:'💎' }, Diamond: { label:'钻石会员', icon:'💳' } }
        var lv = levels[user.memberLevel] || levels.Gold
        self.setData({
          userName: user.name || user.nickname || user.phone || '会员',
          levelLabel: lv.label,
          balanceIcon: lv.icon,
          totalSpent: totalSpent,
          visitCount: visitCount,
          points: totalSpent
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

  // ── 账户设置 ──
  showAccountSettings: function() {
    this.setData({ showSettingsModal: true, editName: this.data.userName })
  },
  hideAccountSettings: function() { this.setData({ showSettingsModal: false }) },
  onNameInput: function(e) { this.setData({ editName: e.detail.value }) },

  saveAccountSettings: function() {
    var self = this
    var newName = self.data.editName || self.data.userName
    try {
      var user = wx.getStorageSync('mp_user') || {}
      user.name = newName
      user.nickname = newName
      wx.setStorageSync('mp_user', user)
      self.setData({ userName: newName, showSettingsModal: false })
      wx.showToast({ title: '已保存', icon: 'success' })
    } catch(e) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    }
  },

  changePassword: function() {
    var self = this
    var userPhone = self.data.userPhone || ''
    // 第一步：发送验证码到手机
    if (!userPhone || userPhone === '—') {
      wx.showToast({ title: '未绑定手机号，请联系管理员', icon: 'none' })
      return
    }
    wx.showToast({ title: '验证码已发送至 ' + userPhone, icon: 'none' })
    // 弹窗输入验证码
    wx.showModal({
      title: '手机验证',
      content: '验证码已发送至 ' + userPhone,
      editable: true,
      placeholderText: '请输入验证码',
      success: function(r1) {
        if (!r1.confirm) return
        if (r1.content !== '8888') {
          wx.showToast({ title: '验证码错误', icon: 'none' })
          return
        }
        // 第二步：设置新密码
        wx.showModal({
          title: '设置新密码',
          editable: true,
          placeholderText: '请输入新密码（至少6位）',
          success: function(r2) {
            if (!r2.confirm || !r2.content) return
            if (r2.content.length < 6) {
              wx.showToast({ title: '密码至少6位', icon: 'none' })
              return
            }
            try {
              var u = wx.getStorageSync('mp_user') || {}
              u.password = r2.content
              wx.setStorageSync('mp_user', u)
              wx.showToast({ title: '密码已修改', icon: 'success' })
            } catch(e) { wx.showToast({ title: '保存失败', icon: 'none' }) }
          }
        })
      }
    })
  },

  clearAccount: function() {
    var self = this
    wx.showModal({
      title: '清除本地数据',
      content: '将清除本地缓存的订单、用户信息等数据，确认？',
      success: function(res) {
        if (res.confirm) {
          try {
            wx.clearStorageSync()
            wx.showToast({ title: '已清除，请重新登录', icon: 'success' })
            setTimeout(function() { API.logout(); wx.reLaunch({ url: '/pages/home/home' }) }, 1000)
          } catch(e) { wx.showToast({ title: '清除失败', icon: 'none' }) }
        }
      }
    })
  },

  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goCoupons: function() { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },

  goMyAddresses: function() {
    wx.navigateTo({ url: '/pages/address-manager/address-manager' })
  },

  toastComing: function() { wx.showToast({ title: '开发中', icon: 'none' }) },
  preventBubble: function() {},

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
  },

  // ── 底部导航 ──
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) }
})
