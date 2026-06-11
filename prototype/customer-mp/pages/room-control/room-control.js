var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--',
    // 设备
    devices: [],
    // 续订
    showExtendModal: false, showExtendPayModal: false,
    extendInfo: '', extendOptions: [], selectedExtendIdx: -1,
    extendPayInfo: '', extendPayAmount: 0
  },

  onLoad: function(e) {
    var roomId = e.roomId || 'RM004'
    var roomName = e.roomName ? decodeURIComponent(e.roomName) : '大茶室C'
    var duration = parseInt(e.duration) || 120
    var endStr = e.end || ''
    this.setData({ roomId: roomId, roomName: roomName })
    this.loadDevices()
    this.startCountdown(duration, endStr)
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
        // 如果结束时间已过，可能是次日
        if (endDate <= now) endDate.setDate(endDate.getDate() + 1)
        var totalSec = Math.max(0, Math.round((endDate - now) / 1000))
        self.setData({ endTime: endStr })
        self._countdownTotal = totalSec
        self._endDate = endDate
        if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
        self.setData({ countdown: self._fmtCountdown(totalSec) })
        if (self._countdownTimer) clearInterval(self._countdownTimer)
        self._countdownTimer = setInterval(function() {
          self._countdownTotal = Math.max(0, self._countdownTotal - 1)
          self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
        }, 1000)
        return
      }
    }

    // fallback: 用当前时间+duration
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self._endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), endH, endM)
    self.setData({ endTime: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })
    var totalSec = durationMin * 60
    self._countdownTotal = totalSec
    if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
    self.setData({ countdown: self._fmtCountdown(totalSec) })
    if (self._countdownTimer) clearInterval(self._countdownTimer)
    self._countdownTimer = setInterval(function() {
      self._countdownTotal = Math.max(0, self._countdownTotal - 1)
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
    }, 1000)
  },

  _fmtCountdown: function(s) {
    if (s <= 0) return '00:00'
    var m = Math.floor(s / 60), sec = s % 60
    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0')
  },

  goBack: function() { wx.navigateBack() },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },

  // ── 续订 ──
  showExtend: function() {
    var self = this
    var now = new Date()
    var curEndMin = now.getHours() * 60 + now.getMinutes() + Math.ceil((self._countdownTotal || 0) / 60)
    var roundedEndMin = Math.ceil(curEndMin / 30) * 30
    var h = Math.floor(roundedEndMin / 60) % 24
    var m = roundedEndMin % 60
    var curEndStr = String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0')

    self.setData({
      extendInfo: '当前将于 ' + curEndStr + ' 结束。请选择续订时长：',
      selectedExtendIdx: -1
    })

    var options = []
    for (var i = 1; i <= 8; i++) {
      var totalMin = roundedEndMin + i * 30
      var oh = Math.floor(totalMin / 60) % 24
      var om = totalMin % 60
      var extMin = i * 30
      var price = Math.round(120 * extMin / 60)
      options.push({
        label: '至 ' + String(oh).padStart(2,'0') + ':' + String(om).padStart(2,'0'),
        minutes: extMin,
        price: price
      })
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
    this.setData({
      extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ','') + '，+¥' + opt.price,
      extendPayAmount: opt.price,
      showExtendModal: false,
      showExtendPayModal: true
    })
  },

  doExtendPayment: function() {
    var self = this
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx]

    API.getBalance().then(function(balance) {
      if (balance < opt.price) {
        wx.showToast({ title: '余额不足，请充值', icon: 'none' })
        self.setData({ showExtendPayModal: false })
        return
      }
      // 扣余额
      var newBalance = balance - opt.price
      var user = wx.getStorageSync('mp_user') || {}
      user.balance = newBalance
      wx.setStorageSync('mp_user', user)

      // 更新倒计时
      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })

      // 更新结束时间
      if (self._endDate) {
        self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000)
        var nh = self._endDate.getHours()
        var nm = self._endDate.getMinutes()
        self.setData({ endTime: String(nh).padStart(2,'0') + ':' + String(nm).padStart(2,'0') })
      }

      // 持久化到booking
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

      self.setData({ showExtendPayModal: false })
      wx.showToast({ title: '续订成功！已扣除 ¥' + opt.price, icon: 'success' })
    })
  },

  hideExtend: function() {
    this.setData({ showExtendModal: false })
  },

  cancelExtendPay: function() {
    this.setData({ showExtendPayModal: false })
    wx.showToast({ title: '已取消续订', icon: 'none' })
  },

  // 设备控制
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
