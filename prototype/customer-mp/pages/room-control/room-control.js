var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--', orderSlot: '', orderStart: '',
    balance: 0,
    // 设备分组
    lightDevices: [],
    fanDevices: [],
    exhaustDevices: [],
    acDevice: null,
    curtainDevices: [],
    bgmDevice: null,
    // 续订
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
      var lights = [], fans = [], exhausts = [], ac = null, curtains = [], bgm = null
      for (var i = 0; i < devices.length; i++) {
        var d = devices[i]
        if (d.type === 'Light') {
          d.on = (d.brightness || 0) > 0
          lights.push(d)
        } else if (d.type === 'Fan') {
          d.on = (d.speed || 0) > 0
          fans.push(d)
        } else if (d.type === 'ExhaustFan') {
          d.on = (d.speed || 0) > 0
          exhausts.push(d)
        } else if (d.type === 'AC') {
          ac = d
        } else if (d.type === 'Curtain') {
          d.positionNum = d.position === 'open' ? 100 : (d.position === 'closed' ? 0 : parseInt(d.position) || 0)
          curtains.push(d)
        } else if (d.type === 'BGM') {
          bgm = d
        }
      }
      self.setData({
        lightDevices: lights,
        fanDevices: fans,
        exhaustDevices: exhausts,
        acDevice: ac,
        curtainDevices: curtains,
        bgmDevice: bgm
      })
    })
  },

  // ── 灯光 ──
  toggleLight: function(e) {
    var id = e.currentTarget.dataset.id
    var on = e.currentTarget.dataset.on === 'true' ? false : true
    var devices = this.data.lightDevices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id) { devices[i].on = on; break }
    }
    this.setData({ lightDevices: devices })
    API.controlDevice(id, { on: on }).catch(function(){})
  },

  // ── 风扇 ──
  toggleFan: function(e) {
    var id = e.currentTarget.dataset.id
    var on = e.currentTarget.dataset.on === 'true' ? false : true
    var devices = this.data.fanDevices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id) { devices[i].on = on; break }
    }
    this.setData({ fanDevices: devices })
    API.controlDevice(id, { on: on }).catch(function(){})
  },

  // ── 换气扇 ──
  toggleExhaust: function(e) {
    var id = e.currentTarget.dataset.id
    var on = e.currentTarget.dataset.on === 'true' ? false : true
    var devices = this.data.exhaustDevices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id) { devices[i].on = on; break }
    }
    this.setData({ exhaustDevices: devices })
    API.controlDevice(id, { on: on }).catch(function(){})
  },

  // ── 空调 ──
  toggleAC: function(e) {
    var id = e.currentTarget.dataset.id
    var ac = this.data.acDevice
    if (!ac) return
    var newMode = ac.mode === 'cool' ? 'off' : 'cool'
    ac.mode = newMode
    this.setData({ acDevice: ac })
    API.controlDevice(id, { mode: newMode }).catch(function(){})
  },

  acTempUp: function(e) {
    var id = e.currentTarget.dataset.id
    var ac = this.data.acDevice
    if (!ac) return
    var t = Math.min(30, (ac.temperature || 24) + 1)
    ac.temperature = t
    this.setData({ acDevice: ac })
    API.controlDevice(id, { temperature: t }).catch(function(){})
  },

  acTempDown: function(e) {
    var id = e.currentTarget.dataset.id
    var ac = this.data.acDevice
    if (!ac) return
    var t = Math.max(16, (ac.temperature || 24) - 1)
    ac.temperature = t
    this.setData({ acDevice: ac })
    API.controlDevice(id, { temperature: t }).catch(function(){})
  },

  // ── 窗帘 ──
  onCurtainChange: function(e) {
    var id = e.currentTarget.dataset.id
    var val = parseInt(e.detail.value)
    var position = val >= 80 ? 'open' : (val <= 20 ? 'closed' : val + '%')
    var devices = this.data.curtainDevices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id) {
        devices[i].positionNum = val
        devices[i].position = position
        break
      }
    }
    this.setData({ curtainDevices: devices })
    API.controlDevice(id, { position: position }).catch(function(){})
  },

  // ── 背景音乐 ──
  toggleBGM: function(e) {
    var id = e.currentTarget.dataset.id
    var bgm = this.data.bgmDevice
    if (!bgm) return
    bgm.playing = !bgm.playing
    this.setData({ bgmDevice: bgm })
    API.controlDevice(id, { playing: bgm.playing }).catch(function(){})
  },

  onBGMVolumeChange: function(e) {
    var id = e.currentTarget.dataset.id
    var val = parseInt(e.detail.value)
    var bgm = this.data.bgmDevice
    if (!bgm) return
    bgm.volume = val
    this.setData({ bgmDevice: bgm })
    API.controlDevice(id, { volume: val }).catch(function(){})
  },

  // ── 倒计时 ──
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
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self._endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), endH, endM)
    self.setData({ endTime: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })
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

  onUnload: function() {
    if (this._countdownTimer) clearInterval(this._countdownTimer)
  },

  preventBubble: function() {},

  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },

  // ── 续订 ──
  showExtend: function() {
    var self = this
    var endDate = self._endDate ? new Date(self._endDate) : new Date()
    var curEndStr = String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0')
    self.setData({ extendInfo: '当前将于 ' + curEndStr + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })
    var options = []
    for (var i = 1; i <= 24; i++) {
      var newDate = new Date(endDate.getTime() + i * 30 * 60000)
      var oh = newDate.getHours(), om = newDate.getMinutes()
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
        extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''),
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
        var nh = self._endDate.getHours(), nm = self._endDate.getMinutes()
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
    } else {
      wx.showLoading({ title: '支付中...' })
      setTimeout(function() { wx.hideLoading(); proceedExtend() }, 800)
    }
  },

  hideExtend: function() { this.setData({ showExtendModal: false }) },
  cancelExtendPay: function() {
    this.setData({ showExtendPayModal: false })
    wx.showToast({ title: '已取消续订', icon: 'none' })
  }
})
