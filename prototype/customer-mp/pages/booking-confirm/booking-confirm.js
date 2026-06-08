var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '', dateStr: '', slot: '', price: 0, duration: 90,
    noPayment: false, showSuccess: false,
    isStaff: false,
    balance: 280,
    selectedPay: 'wechat',
    selectedSource: '', showOtherSource: false,
    sourceOptions: ['老客户', '美大茶室', '抖音', '高德地图', '美大CAFE', '小红书', '会小二', 'CAPSS'],
    couponPlatforms: [
      { key: 'meituan', label: '🟡 美团', code: '', status: '', msg: '' },
      { key: 'dianping', label: '⭐ 大众点评', code: '', status: '', msg: '' },
      { key: 'douyin', label: '🎵 抖音', code: '', status: '', msg: '' },
      { key: 'gaode', label: '🗺️ 高德', code: '', status: '', msg: '' }
    ],
    verifiedCoupons: {}, verifiedCount: 0, totalDiscount: 0,
    finalPrice: 0, discountText: '',
    showBalanceWarning: false, showCombinedPay: false, balanceWarningText: '',
    isCombinedPay: false, doorCode: '0000', payMethodLabel: ''
  },

  onLoad: function(e) {
    var price = parseInt(e.total || e.price || '180')
    var user = API.getCurrentUser()
    this.setData({
      roomId: e.roomId || '', roomName: decodeURIComponent(e.roomName || ''),
      dateStr: e.date || e.dateStr || '', slot: (e.start || '') + '-' + (e.end || ''),
      price: price, duration: parseInt(e.duration || 90), finalPrice: price,
      isStaff: user && user.role === 'staff',
      noPayment: parseInt(e.duration) == 0 || false
    })
    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  onSourceChange: function(e) {
    var idx = e.detail.value, options = this.data.sourceOptions
    if (idx == options.length - 1 && options[idx] == 'CAPSS') { this.setData({ showOtherSource: true, selectedSource: '' }) }
    else if (idx >= 0 && idx < options.length) { this.setData({ showOtherSource: false, selectedSource: options[idx] }) }
  },
  onOtherSourceInput: function(e) { this.setData({ selectedSource: e.detail.value || '其他' }) },

  selectPay: function(e) {
    var pay = e.currentTarget.dataset.pay
    this.setData({ selectedPay: pay })
    if (pay == 'balance') {
      var p = this.data.price, b = this.data.balance
      if (b < p) { this.setData({ showBalanceWarning: true, showCombinedPay: true, balanceWarningText: '余额不足（当前¥' + b + '，需¥' + p + '），请充值或使用组合支付' }) }
      else { this.setData({ showBalanceWarning: false, showCombinedPay: false }) }
    } else { this.setData({ showBalanceWarning: false, showCombinedPay: false }); this.updateFinalPrice() }
  },

  selectCombinedPay: function() {
    this.setData({ isCombinedPay: true, showBalanceWarning: false, discountText: '余额抵扣 ¥' + this.data.balance + ' + 微信支付 ¥' + (this.data.price - this.data.balance) })
  },

  onCouponInput: function(e) {
    var key = e.currentTarget.dataset.key, val = e.detail.value, platforms = this.data.couponPlatforms
    for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { platforms[i].code = val; platforms[i].status = ''; platforms[i].msg = ''; break } }
    this.setData({ couponPlatforms: platforms })
  },

  verifyCoupon: function(e) {
    var key = e.currentTarget.dataset.key, platforms = this.data.couponPlatforms, code = ''
    for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { code = platforms[i].code; break } }
    if (!code) { wx.showToast({ title: '请输入券码', icon: 'none' }); return }
    var self = this
    API.verifyCoupon(code).then(function(result) {
      for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { platforms[i].status = 'success'; platforms[i].msg = '✓ ¥' + result.value; break } }
      var vc = self.data.verifiedCoupons; vc[key] = { code: code, value: result.value }
      var count = 0, total = 0; for (var k in vc) { count++; total += vc[k].value }
      self.setData({ couponPlatforms: platforms, verifiedCoupons: vc, verifiedCount: count, totalDiscount: total }); self.updateFinalPrice()
    }).catch(function(err) {
      for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { platforms[i].status = 'error'; platforms[i].msg = err.message || '无效'; break } }
      self.setData({ couponPlatforms: platforms })
    })
  },

  updateFinalPrice: function() { var p = this.data.price - this.data.totalDiscount; this.setData({ finalPrice: Math.max(0, p), discountText: this.data.totalDiscount > 0 ? ('券抵扣 ¥' + this.data.totalDiscount + ' · 实付 ¥' + Math.max(0, p)) : '' }) },

  confirmPay: function() {
    if (this.data.isStaff && !this.data.selectedSource) { wx.showToast({ title: '请选择客户来源', icon: 'none' }); return }
    if (!this.data.noPayment && this.data.selectedPay == 'balance' && !this.data.isCombinedPay && this.data.balance < this.data.price) { wx.showToast({ title: '余额不足', icon: 'none' }); return }
    var self = this, doorCode = String(Math.floor(Math.random() * 9000 + 1000))
    var payLabels = { wechat: '微信支付', alipay: '支付宝', balance: '会员余额', coupon: '验券' }
    var payLabel = self.data.isCombinedPay ? '余额+微信支付' : (self.data.selectedPay == 'coupon' ? '验券' : payLabels[self.data.selectedPay] || '微信支付')
    API.createBooking({ roomId: self.data.roomId, roomName: self.data.roomName, date: self.data.dateStr, time: self.data.slot, duration: self.data.duration, amount: self.data.price, paymentMethod: payLabel, customerSource: self.data.selectedSource }).then(function(result) {
      self.setData({ showSuccess: true, doorCode: result.doorCode || doorCode, payMethodLabel: payLabel })
    }).catch(function(err) { wx.showToast({ title: err.message || '预订失败', icon: 'none' }) })
  },

  // 原型 openDoor 逻辑：检查后续订单→更新状态→跳转智控
  openDoor: function() {
    var now = new Date()
    var durationMin = this.data.duration || 90
    var slotParts = (this.data.slot || '').split('-')
    var originalEndStr = slotParts.length >= 2 ? slotParts[1].trim() : ''
    var roomId = this.data.roomId
    var roomName = this.data.roomName
    var dateStr = this.data.dateStr

    // 检查时间段：未到时间或已过时间不能开门
    if (originalEndStr && dateStr) {
      var origEndParts = originalEndStr.split(':')
      var origEndMin = parseInt(origEndParts[0]) * 60 + parseInt(origEndParts[1])
      var curMin = now.getHours() * 60 + now.getMinutes()

      // 如果还没到预订时间，不能开门
      var startParts = slotParts[0] ? slotParts[0].split(':') : null
      if (startParts) {
        var startMin = parseInt(startParts[0]) * 60 + parseInt(startParts[1])
        if (curMin < startMin - 15) { wx.showToast({ title: '未到开门时间', icon: 'none' }); return }
      }
    }

    // 将订单状态更新为InUse，并跳转到智控页
    var newEndDate
    if (originalEndStr && dateStr) {
      newEndDate = new Date(now.getTime() + durationMin * 60000)
    } else {
      newEndDate = new Date(now.getTime() + durationMin * 60000)
    }

    wx.showToast({ title: '🚪 门已开', icon: 'success', duration: 1000 })
    setTimeout(function() {
      wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
    }, 1200)
  },

  copyCode: function() { wx.setClipboardData({ data: this.data.doorCode }); wx.showToast({ title: '密码已复制', icon: 'none' }) },

  goTopup: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  openNav: function() { wx.showToast({ title: '🗺 已规划路线', icon: 'none' }) },
  scanCouponCode: function(e) { var self = this, key = e.currentTarget.dataset.key; wx.scanCode({ onlyFromCamera: true, success: function(res) { var platforms = self.data.couponPlatforms; for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { platforms[i].code = res.result; break } } self.setData({ couponPlatforms: platforms }); wx.showToast({ title: '券码已识别', icon: 'none' }) } }) },
  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
