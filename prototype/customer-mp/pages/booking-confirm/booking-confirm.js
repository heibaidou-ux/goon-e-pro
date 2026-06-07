var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '', dateStr: '', slot: '', price: 0, duration: 90,
    noPayment: false, showSuccess: false,
    isStaff: false,  // 第14条：区分客人端和店员端
    balance: 280,
    selectedPay: 'wechat',
    selectedSource: '',
    showOtherSource: false,
    sourceOptions: ['老客户', '美大茶室', '抖音', '高德地图', '美大CAFE', '小红书', '会小二', 'CAPSS'],
    couponPlatforms: [
      { key: 'meituan', label: '🟡 美团', code: '', status: '', msg: '' },
      { key: 'dianping', label: '⭐ 大众点评', code: '', status: '', msg: '' },
      { key: 'douyin', label: '🎵 抖音', code: '', status: '', msg: '' }
    ],
    verifiedCoupons: {},
    verifiedCount: 0,
    totalDiscount: 0,
    finalPrice: 0,
    discountText: '',
    showBalanceWarning: false,
    showCombinedPay: false,
    balanceWarningText: '',
    isCombinedPay: false,
    doorCode: '0000',
    payMethodLabel: ''
  },

  onLoad: function(e) {
    var price = parseInt(e.total || e.price || '180')
    // 第14-15条：判断登录角色
    var user = API.getCurrentUser()
    var isStaff = user && user.role === 'staff'
    this.setData({
      roomId: e.roomId || '',
      roomName: decodeURIComponent(e.roomName || ''),
      dateStr: e.date || e.dateStr || '',
      slot: (e.start || '') + '-' + (e.end || ''),
      price: price,
      duration: parseInt(e.duration || 90),
      finalPrice: price,
      isStaff: isStaff,
      sourceOptions: ['老客户', '美大茶室', '抖音', '高德地图', '美大CAFE', '小红书', '会小二', 'CAPSS'],
      noPayment: parseInt(e.duration) == 0 || false
    })
    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  onSourceChange: function(e) {
    var idx = e.detail.value
    var options = this.data.sourceOptions
    if (idx == options.length - 1 && options[idx] == 'CAPSS') {
      this.setData({ showOtherSource: true, selectedSource: '' })
    } else if (idx >= 0 && idx < options.length) {
      this.setData({ showOtherSource: false, selectedSource: options[idx] })
    }
  },

  onOtherSourceInput: function(e) {
    this.setData({ selectedSource: e.detail.value || '其他' })
  },

  selectPay: function(e) {
    var pay = e.currentTarget.dataset.pay
    this.setData({ selectedPay: pay })
    if (pay == 'balance') {
      var p = this.data.price
      var b = this.data.balance
      if (b < p) {
        this.setData({
          showBalanceWarning: true,
          showCombinedPay: true,
          balanceWarningText: '余额不足（当前¥' + b + '，需¥' + p + '），请充值或使用组合支付'
        })
      } else {
        this.setData({ showBalanceWarning: false, showCombinedPay: false })
      }
    } else {
      this.setData({ showBalanceWarning: false, showCombinedPay: false })
      this.updateFinalPrice()
    }
  },

  selectCombinedPay: function() {
    this.setData({
      isCombinedPay: true,
      showBalanceWarning: false,
      discountText: '余额抵扣 ¥' + this.data.balance + ' + 微信支付 ¥' + (this.data.price - this.data.balance)
    })
  },

  onCouponInput: function(e) {
    var key = e.currentTarget.dataset.key
    var val = e.detail.value
    var platforms = this.data.couponPlatforms
    for (var i = 0; i < platforms.length; i++) {
      if (platforms[i].key === key) { platforms[i].code = val; platforms[i].status = ''; platforms[i].msg = ''; break }
    }
    this.setData({ couponPlatforms: platforms })
  },

  verifyCoupon: function(e) {
    var key = e.currentTarget.dataset.key
    var platforms = this.data.couponPlatforms
    var code = ''
    for (var i = 0; i < platforms.length; i++) {
      if (platforms[i].key === key) { code = platforms[i].code; break }
    }
    if (!code) { wx.showToast({ title: '请输入券码', icon: 'none' }); return }

    var self = this
    API.verifyCoupon(code).then(function(result) {
      for (var i = 0; i < platforms.length; i++) {
        if (platforms[i].key === key) { platforms[i].status = 'success'; platforms[i].msg = '✓ ¥' + result.value; break }
      }
      var vc = self.data.verifiedCoupons
      vc[key] = { code: code, value: result.value }
      var count = 0, total = 0
      for (var k in vc) { count++; total += vc[k].value }
      self.setData({ couponPlatforms: platforms, verifiedCoupons: vc, verifiedCount: count, totalDiscount: total })
      self.updateFinalPrice()
    }).catch(function(err) {
      for (var i = 0; i < platforms.length; i++) {
        if (platforms[i].key === key) { platforms[i].status = 'error'; platforms[i].msg = err.message || '无效'; break }
      }
      self.setData({ couponPlatforms: platforms })
    })
  },

  updateFinalPrice: function() {
    var p = this.data.price - this.data.totalDiscount
    this.setData({
      finalPrice: Math.max(0, p),
      discountText: this.data.totalDiscount > 0 ? ('券抵扣 ¥' + this.data.totalDiscount + ' · 实付 ¥' + Math.max(0, p)) : ''
    })
  },

  confirmPay: function() {
    if (!this.data.selectedSource) { wx.showToast({ title: '请选择客户来源', icon: 'none' }); return }
    if (!this.data.noPayment) {
      if (this.data.selectedPay == 'balance' && !this.data.isCombinedPay && this.data.balance < this.data.price) {
        wx.showToast({ title: '余额不足，请选择组合支付或先充值', icon: 'none' }); return
      }
    }

    var self = this
    var doorCode = String(Math.floor(Math.random() * 9000 + 1000))
    var payLabels = { wechat: '微信支付', alipay: '支付宝', balance: '会员余额', coupon: '验券' }
    var payLabel = ''
    if (self.data.isCombinedPay) payLabel = '余额+微信支付'
    else if (self.data.selectedPay == 'coupon') payLabel = '验券'
    else payLabel = payLabels[self.data.selectedPay] || '微信支付'

    API.createBooking({
      roomId: self.data.roomId, roomName: self.data.roomName,
      date: self.data.dateStr, time: self.data.slot,
      duration: self.data.duration, amount: self.data.price,
      paymentMethod: payLabel, customerSource: self.data.selectedSource
    }).then(function(result) {
      self.setData({
        showSuccess: true,
        doorCode: result.doorCode || doorCode,
        payMethodLabel: payLabel
      })
    }).catch(function(err) {
      wx.showToast({ title: err.message || '预订失败', icon: 'none' })
    })
  },

  openDoor: function() {
    wx.showToast({ title: '🚪 门已开', icon: 'none' })
  },

  copyCode: function() {
    wx.setClipboardData({ data: this.data.doorCode })
    wx.showToast({ title: '密码已复制', icon: 'none' })
  },

  goTopup: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  openNav: function() { wx.showToast({ title: '🗺 已规划路线', icon: 'none' }) },

  // 第17条：扫码输入券码
  scanCouponCode: function(e) {
    var self = this
    var key = e.currentTarget.dataset.key
    wx.scanCode({ onlyFromCamera: true, success: function(res) {
      var platforms = self.data.couponPlatforms
      for (var i = 0; i < platforms.length; i++) {
        if (platforms[i].key === key) { platforms[i].code = res.result; break }
      }
      self.setData({ couponPlatforms: platforms })
      wx.showToast({ title: '券码已识别', icon: 'none' })
    }})
  },
  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
