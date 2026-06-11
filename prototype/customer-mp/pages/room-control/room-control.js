var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--', orderSlot: '', orderStart: '',
    devices: [],
    balance: 0,
    showExtendModal: false, showExtendPayModal: false,
    extendInfo: '', extendOptions: [], selectedExtendIdx: -1,
    extendPayInfo: '', extendPayAmount: 0, extendPayMethod: 'balance'
  },

  onLoad: function(e) {
    var roomId = e.roomId || 'RM004'
    var roomName = e.roomName ? decodeURIComponent(e.roomName) : '大茶室C'
    var duration = parseInt(e.duration) || 120
    var endStr = e.end || ''
    var startStr = e.start || ''
    this.setData({ roomId: roomId, roomName: roomName, orderStart: startStr })
    this.loadDevices()
    this.startCountdown(duration, endStr)
    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  loadDevices: function() {
    var self = this
    API.getRoomDevices(this.data.roomId).then(function(devices) {
      var labels = { Lock:'门锁', AC:'空调', Light:'灯光', Curtain:'窗帘', Speaker:'音响' }
      var icons = { Lock:'🔒', AC:'❄️', Light:'💡', Curtain:'🪟', Speaker:'🔊' }
      for (var i = 0; i < devices.length; i++) {
        devices[i].typeLabel = labels[devices[i].type] || devices[i].type
        devices[i].typeIcon = icons[devices[i].type] || '📡'
        if (devices[i].type === 'Curtain' && devices[i].position) {
          devices[i].positionNum = devices[i].position === 'open' ? 100 : (devices[i].position === 'closed' ? 0 : parseInt(devices[i].position) || 50)
        }
      }
      self.setData({ devices: devices })
    })
  },

  startCountdown: function(durationMin, endStr) {
    var self = this
    durationMin = durationMin || 120
    var now = new Date()

    if (endStr) {
      var ep = endStr.split(':')
      if (ep.length >= 2) {
        var eh = parseInt(ep[0]), em = parseInt(ep[1])
        var endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), eh, em)
        if (endDate <= now) endDate.setDate(endDate.getDate() + 1)
        var totalSec = Math.max(0, Math.round((endDate - now) / 1000))
        self.setData({ endTime: endStr })
        self._countdownTotal = totalSec
        self._endDate = endDate
        if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
        self.setData({ countdown: self._fmtCountdown(totalSec) })
        self._startTimer()
        self._updateSlot()
        return
      }
    }

    // fallback
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self._endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), endH, endM)
    var endStr2 = String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0')
    self.setData({ endTime: endStr2 })
    var totalSec = durationMin * 60
    self._countdownTotal = totalSec
    if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
    self.setData({ countdown: self._fmtCountdown(totalSec) })
    self._startTimer()
    self._updateSlot()
  },

  _updateSlot: function() {
    var start = this.data.orderStart
    var end = this.data.endTime
    if (end) {
      this.setData({ orderSlot: (start ? start : '--:--') + ' - ' + end })
    }
  },

  _startTimer: function() {
    var self = this
    if (self._countdownTimer) clearInterval(self._countdownTimer)
    // 延迟启动，避免与loadDevices的setData冲突
    setTimeout(function() {
      self._countdownTimer = setInterval(function() {
        self._countdownTotal = Math.max(0, self._countdownTotal - 1)
        self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      }, 1000)
    }, 300)
  },

  _fmtCountdown: function(s) {
    if (s <= 0) return '00:00'
    var m = Math.floor(s / 60), sec = s % 60
    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0')
  },

  preventBubble: function() {},
  onUnload: function() {
    if (this._countdownTimer) clearInterval(this._countdownTimer)
  },

  goBack: function() { wx.navigateBack() },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },

  showExtend: function() {
    var self = this
    // 直接用_endDate计算当前结束时间，与页面顶部显示一致
    var endDate = self._endDate ? new Date(self._endDate) : new Date()
    var eh = endDate.getHours()
    var em = endDate.getMinutes()
    var curEndStr = String(eh).padStart(2,'0') + ':' + String(em).padStart(2,'0')
    self.setData({ extendInfo: '当前将于 ' + curEndStr + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })
    var options = []
    for (var i = 1; i <= 24; i++) {
      var newDate = new Date(endDate.getTime() + i * 30 * 60000)
      var oh = newDate.getHours()
      var om = newDate.getMinutes()
      var extMin = i * 30
      var price = Math.round(120 * extMin / 60)
      options.push({ label: '至 ' + String(oh).padStart(2,'0') + ':' + String(om).padStart(2,'0'), minutes: extMin, price: price })
    }
    self.setData({ extendOptions: options, showExtendModal: true })
  },

  selectExtend: function(e) {
    this.setData({ selectedExtendIdx: parseInt(e.currentTarget.dataset.index) })
  },

  confirmExtend: function() {
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx]
    var self = this
    API.getBalance().then(function(b) {
      self.setData({
        balance: b || 0,
        extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ','') + '，+¥' + opt.price,
        extendPayAmount: opt.price,
        extendPayMethod: 'balance',
        showExtendModal: false,
        showExtendPayModal: true
      })
    })
  },

  selectExtendPay: function(e) {
    this.setData({ extendPayMethod: e.currentTarget.dataset.pay })
  },

  doExtendPayment: function() {
    var self = this
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx]
    var method = this.data.extendPayMethod
    var proceedExtend = function() {
      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      if (self._endDate) {
        self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000)
        var nh = self._endDate.getHours()
        var nm = self._endDate.getMinutes()
        self.setData({ endTime: String(nh).padStart(2,'0') + ':' + String(nm).padStart(2,'0') })
      }
      try {
        var bookings = wx.getStorageSync('mp_bookings') || []
        for (var i = 0; i < bookings.length; i++) {
          if (bookings[i].roomId === self.data.roomId && bookings[i].status === 'InUse') {
            var nh = self._endDate ? self._endDate.getHours() : 0
            var nm = self._endDate ? self._endDate.getMinutes() : 0
            bookings[i].endTime = String(nh).padStart(2,'0') + ':' + String(nm).padStart(2,'0')
            break
          }
        }
        wx.setStorageSync('mp_bookings', bookings)
      } catch(e) {}
      self._updateSlot()
      self.setData({ showExtendPayModal: false })
      wx.showToast({ title: '续订成功！已支付 ¥' + opt.price, icon: 'success' })
    }

    if (method === 'balance') {
      API.getBalance().then(function(balance) {
        if (balance < opt.price) {
          wx.showToast({ title: '余额不足（¥' + balance + '），请选择其他支付方式或充值', icon: 'none' })
          return
        }
        var newBalance = balance - opt.price
        var user = wx.getStorageSync('mp_user') || {}
        user.balance = newBalance
        wx.setStorageSync('mp_user', user)
        self.setData({ balance: newBalance })
        proceedExtend()
      })
    } else if (method === 'wechat' || method === 'alipay') {
      // 真实环境中调wx.requestPayment，目前mock直接成功
      wx.showLoading({ title: '支付中...' })
      setTimeout(function() {
        wx.hideLoading()
        proceedExtend()
      }, 800)
    }
  },

  hideExtend: function() { this.setData({ showExtendModal: false }) },
  cancelExtendPay: function() {
    this.setData({ showExtendPayModal: false })
    wx.showToast({ title: '已取消续订', icon: 'none' })
  },

  onLockToggle: function(e) { API.controlDevice(e.currentTarget.dataset.id, { locked: !e.detail.value }).catch(function(){}) },
  onTempChange: function(e) {
    var id = e.currentTarget.dataset.id
    var devices = this.data.devices
    for (var i = 0; i < devices.length; i++) { if (devices[i].deviceId === id && devices[i].type === 'AC') { devices[i].temperature = parseInt(e.detail.value); break } }
    this.setData({ devices: devices })
    API.controlDevice(id, { temperature: parseInt(e.detail.value) }).catch(function(){})
  },
  onAcToggle: function(e) { API.controlDevice(e.currentTarget.dataset.id, { mode: e.detail.value ? 'cool' : 'off' }).catch(function(){}) },
  onLightToggle: function(e) { API.controlDevice(e.currentTarget.dataset.id, { brightness: e.detail.value ? 80 : 0 }).catch(function(){}) },
  onCurtainChange: function(e) {
    var val = parseInt(e.detail.value)
    var position = val >= 80 ? 'open' : (val <= 20 ? 'closed' : val + '%')
    API.controlDevice(e.currentTarget.dataset.id, { position: position }).catch(function(){})
  },
  onSpeakerToggle: function(e) { API.controlDevice(e.currentTarget.dataset.id, { playing: e.detail.value }).catch(function(){}) }
})
