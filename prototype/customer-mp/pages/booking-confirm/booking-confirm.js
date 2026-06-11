var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '', dateStr: '', slot: '', price: 0, duration: 120,
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
    isCombinedPay: false, doorCode: '0000', payMethodLabel: '',
    // P0-4: 时间编辑区域
    showTimeEdit: false,
    editableStart: '',
    editableEnd: '',
    editableDuration: 120,
    timeOptions: [],
    selectedTimeLabel: '',
    durationOptions: [
      { label: '2小时', value: 120 },
      { label: '4小时', value: 240 },
      { label: '6小时', value: 360 },
      { label: '8小时', value: 480 }
    ]
  },

  // 工具：当前时间+N分钟，向上取整到30分钟
  calcRoundedTime: function(addMin) {
    var now = new Date()
    var totalMin = now.getHours() * 60 + now.getMinutes() + (addMin || 0)
    totalMin = Math.ceil(totalMin / 30) * 30
    return totalMin
  },

  // 工具：分钟数 → "HH:MM"
  minToStr: function(m) {
    var h = Math.floor(m / 60) % 24, min = m % 60
    return String(h).padStart(2, '0') + ':' + String(min).padStart(2, '0')
  },

  onLoad: function(e) {
    var price = parseInt(e.total || e.price || '180')
    var user = API.getCurrentUser()
    var duration = parseInt(e.duration || 120)
    var startStr = e.start || ''
    var endStr = e.end || ''
    var dateStr = e.date || e.dateStr || ''

    // 默认当前时间+1小时（取整到半点）
    if (!startStr) {
      var curMin = this.calcRoundedTime(60)
      startStr = this.minToStr(curMin)
      endStr = this.minToStr(curMin + duration)
      // 如果没传日期，用今天的日期
      if (!dateStr) {
        var d = new Date()
        dateStr = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
      }
    }

    this.setData({
      roomId: e.roomId || '',
      roomName: decodeURIComponent(e.roomName || ''),
      dateStr: dateStr,
      slot: startStr + '-' + endStr,
      price: price,
      duration: duration,
      finalPrice: price,
      isStaff: user && user.role === 'staff',
      noPayment: parseInt(e.duration) == 0 || false,
      editableStart: startStr,
      editableEnd: endStr,
      editableDuration: duration,
      selectedTimeLabel: startStr
    })

    this.populateTimeOptions()

    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  // ----- 时间编辑 -----
  toggleTimeEdit: function() {
    this.setData({ showTimeEdit: !this.data.showTimeEdit })
    if (this.data.showTimeEdit) this.populateTimeOptions()
  },

  populateTimeOptions: function() {
    var now = new Date()
    var curMin = now.getHours() * 60 + now.getMinutes()
    var startMin = Math.ceil(curMin / 30) * 30
    var options = []
    for (var m = startMin; m < 24 * 60 + 6 * 60; m += 30) {
      options.push(this.minToStr(m % (24 * 60)))
    }
    this.setData({ timeOptions: options })
  },

  selectNow: function() {
    var curMin = this.calcRoundedTime(0)
    var dur = this.data.editableDuration
    var startStr = this.minToStr(curMin)
    var endStr = this.minToStr(curMin + dur)
    this.setData({
      editableStart: startStr,
      editableEnd: endStr,
      slot: startStr + '-' + endStr,
      selectedTimeLabel: '⚡ 现在开始',
      showTimeEdit: false
    })
    this.recalcPrice()
  },

  pickTime: function(e) {
    var idx = e.detail.value
    var timeStr = this.data.timeOptions[idx]
    if (!timeStr) return
    var sp = timeStr.split(':')
    var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
    var endStr = this.minToStr(sMin + this.data.editableDuration)
    this.setData({
      editableStart: timeStr,
      editableEnd: endStr,
      slot: timeStr + '-' + endStr,
      selectedTimeLabel: timeStr,
      showTimeEdit: false
    })
    this.recalcPrice()
  },

  pickDuration: function(e) {
    var dur = parseInt(e.currentTarget.dataset.dur)
    this.setData({ editableDuration: dur })
    this.populateTimeOptions()
    if (this.data.editableStart) {
      var sp = this.data.editableStart.split(':')
      var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
      this.setData({
        editableEnd: this.minToStr(sMin + dur),
        slot: this.data.editableStart + '-' + this.minToStr(sMin + dur)
      })
    }
    this.recalcPrice()
  },

  recalcPrice: function() {
    var origDuration = this.data.duration || 120
    var newDuration = this.data.editableDuration || 120
    var origPrice = parseInt(this.data.price) || 0
    var newPrice = Math.round(origPrice * newDuration / origDuration)
    this.setData({ price: newPrice })
    this.updateFinalPrice()
  },

  // ----- 客户来源 -----
  onSourceChange: function(e) {
    var idx = e.detail.value, options = this.data.sourceOptions
    if (idx == options.length - 1 && options[idx] == 'CAPSS') { this.setData({ showOtherSource: true, selectedSource: '' }) }
    else if (idx >= 0 && idx < options.length) { this.setData({ showOtherSource: false, selectedSource: options[idx] }) }
  },
  onOtherSourceInput: function(e) { this.setData({ selectedSource: e.detail.value || '其他' }) },

  // ----- 支付方式 -----
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

  // ----- 券验 -----
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
    API.createBooking({ roomId: self.data.roomId, roomName: self.data.roomName, date: self.data.dateStr, time: self.data.slot, duration: self.data.editableDuration, amount: self.data.price, paymentMethod: payLabel, customerSource: self.data.selectedSource }).then(function(result) {
      self.setData({ showSuccess: true, doorCode: result.doorCode || doorCode, payMethodLabel: payLabel, createdOrderId: result.orderId || '' })
    }).catch(function(err) { wx.showToast({ title: err.message || '预订失败', icon: 'none' }) })
  },

  // 2.2 订房逻辑：提前到店/晚到时灵活处理
  openDoor: function() {
    var now = new Date()
    var durationMin = this.data.editableDuration || this.data.duration || 90
    var slotParts = (this.data.slot || '').split('-')
    var originalStartStr = slotParts.length >= 1 ? slotParts[0].trim() : ''
    var originalEndStr = slotParts.length >= 2 ? slotParts[1].trim() : ''
    var roomId = this.data.roomId
    var roomName = this.data.roomName
    var dateStr = this.data.dateStr
    var curMin = now.getHours() * 60 + now.getMinutes()
    var startParts = originalStartStr ? originalStartStr.split(':') : null
    var startMin = startParts ? parseInt(startParts[0]) * 60 + parseInt(startParts[1]) : 0
    var endParts = originalEndStr ? originalEndStr.split(':') : null
    var endMin = endParts ? parseInt(endParts[0]) * 60 + parseInt(endParts[1]) : curMin + durationMin

    var self = this

    // 获取该房间当日的所有未取消订单用于冲突判断
    API.getRoomBookings(roomId, dateStr).then(function(bookings) {
      if (!bookings) bookings = []
      // 排除当前订单（自己刚创建的预订不参与冲突检测）
      var myOrderId = self.data.createdOrderId || ''

      // 检查后续预订：找出所有在原始结束时间之后开始的预订
      var nextBooking = null
      for (var i = 0; i < bookings.length; i++) {
        var b = bookings[i]
        if (b.orderId === myOrderId) continue
        var bParts = (b.time || b.start || '').split('-')[0] && (b.time || b.start || '').split(':')
        if (!bParts || bParts.length < 2) continue
        var bStartMin = parseInt(bParts[0]) * 60 + parseInt(bParts[1])
        // 找到在原始时间段之后最近的预订
        if (bStartMin >= endMin - 15) {
          if (!nextBooking || bStartMin < nextBooking.startMin) {
            nextBooking = { startMin: bStartMin, booking: b }
          }
        }
      }

      // 情况1: 提前到店（早于预订时间15分钟以上）
      if (curMin < startMin - 15) {
        // 检查房间当前是否空闲（从curMin到originalEnd之间无冲突）
        var isRoomFree = true
        for (var i = 0; i < bookings.length; i++) {
          var b = bookings[i]
          if (b.orderId === myOrderId) continue
          var bTimeParts = (b.time || b.start || '').split('-')
          if (bTimeParts.length < 2) continue
          var bs = bTimeParts[0].split(':'), be = bTimeParts[1].split(':')
          var bsMin = parseInt(bs[0]) * 60 + parseInt(bs[1])
          var beMin = parseInt(be[0]) * 60 + parseInt(be[1])
          // 检查[curMin, endMin]时间段是否与现有预订冲突
          if (curMin < beMin + 15 && endMin > bsMin) { isRoomFree = false; break }
        }

        if (isRoomFree) {
          // 允许提前开始，更新开始时间为当前时间
          var newStartStr = String(Math.floor(curMin / 60)).padStart(2, '0') + ':' + String(curMin % 60).padStart(2, '0')
          var actualEndMin = curMin + durationMin
          // 如果有后续预订，提前开始不延长结束时间
          if (nextBooking) {
            var actualEnd = Math.min(actualEndMin, nextBooking.startMin - 15)
            var adjustEndStr = String(Math.floor(actualEnd / 60) % 24).padStart(2, '0') + ':' + String(actualEnd % 60).padStart(2, '0')
            self.setData({ slot: newStartStr + '-' + adjustEndStr, editableStart: newStartStr, editableEnd: adjustEndStr })
          } else {
            var adjustEndStr = String(Math.floor(actualEndMin / 60) % 24).padStart(2, '0') + ':' + String(actualEndMin % 60).padStart(2, '0')
            self.setData({ slot: newStartStr + '-' + adjustEndStr, editableStart: newStartStr, editableEnd: adjustEndStr })
          }
          wx.showToast({ title: '✅ 房间空闲，已提前开始', icon: 'success', duration: 1500 })
          setTimeout(function() {
            wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
          }, 1800)
        } else {
          wx.showToast({ title: '房间当前被占用，请在预订时间前来', icon: 'none' })
        }
        return
      }

      // 情况2: 晚到（当前时间晚于预订开始时间）
      if (curMin > startMin + 15) {
        var actualEndMin = curMin + durationMin
        // 检查原始结束时间
        if (curMin >= endMin) {
          // 已过结束时间，检查是否还有后续预订
          if (nextBooking) {
            wx.showToast({ title: '已过原预订时段，且后续有预约，请联系前台', icon: 'none' })
          } else {
            // 没有后续预订，自动延长到新时段
            var newEndStr = String(Math.floor(actualEndMin / 60) % 24).padStart(2, '0') + ':' + String(actualEndMin % 60).padStart(2, '0')
            wx.showToast({ title: '已过预订时间，房间空闲可继续使用至 ' + newEndStr, icon: 'none', duration: 2000 })
            self.setData({ slot: originalStartStr + '-' + newEndStr, editableEnd: newEndStr })
          }
          return
        }

        // 晚到但仍在时段内：如果有后续预订，调整结束时间
        if (nextBooking && actualEndMin > nextBooking.startMin - 15) {
          var adjustedEnd = Math.min(endMin, nextBooking.startMin - 15)
          if (adjustedEnd <= curMin + 15) {
            wx.showToast({ title: '剩余时间不足，后续有预订安排', icon: 'none' })
            return
          }
          var adjustEndStr = String(Math.floor(adjustedEnd / 60) % 24).padStart(2, '0') + ':' + String(adjustedEnd % 60).padStart(2, '0')
          wx.showToast({ title: '⏰ 后续有预订，结束时间调整为 ' + adjustEndStr, icon: 'none', duration: 2000 })
          self.setData({ slot: originalStartStr + '-' + adjustEndStr, editableEnd: adjustEndStr })
        }
      }

      // 情况3: 正常时间到店，开门
      proceedToOpen()
    }).catch(function() {
      // API失败时默认开门
      proceedToOpen()
    })

    function proceedToOpen() {
      wx.showToast({ title: '🚪 门已开', icon: 'success', duration: 1000 })
      setTimeout(function() {
        wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
      }, 1200)
    }
  },

  copyCode: function() { wx.setClipboardData({ data: this.data.doorCode }); wx.showToast({ title: '密码已复制', icon: 'none' }) },

  goTopup: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  openNav: function() {
    wx.openLocation({
      latitude: 23.1275,
      longitude: 113.3220,
      name: '高岸·富力盈隆广场',
      address: '广州市天河区珠江新城富力盈隆广场3801',
      scale: 18
    })
  },
  scanCouponCode: function(e) { var self = this, key = e.currentTarget.dataset.key; wx.scanCode({ onlyFromCamera: true, success: function(res) { var platforms = self.data.couponPlatforms; for (var i = 0; i < platforms.length; i++) { if (platforms[i].key === key) { platforms[i].code = res.result; break } } self.setData({ couponPlatforms: platforms }); wx.showToast({ title: '券码已识别', icon: 'none' }) } }) },
  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
