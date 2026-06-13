var API = require('../../utils/api')

// 每个房间的灯光设备ID（用于灯全开/全关）
var LIGHT_DEVICE_IDS = {
  RM001: ['DEV001','DEV002','DEV003'],
  RM002: ['DEV009','DEV010'],
  RM003: ['DEV016','DEV017','DEV018'],
  RM004: ['DEV025','DEV026','DEV027'],
  RM005: []
}

// 每个房间的风扇/换气扇设备
var FAN_DEVICE_IDS = {
  RM001: ['DEV004','DEV005','DEV006'],
  RM002: ['DEV011','DEV012'],
  RM003: ['DEV019'],
  RM004: ['DEV028'],
  RM005: []
}

// 灯光图标 — 简笔画风格
var LIGHT_ICONS = { 'DEV001':'◯','DEV002':'◯','DEV003':'⊙','DEV009':'⊙','DEV010':'◯','DEV016':'⊙','DEV017':'◯','DEV018':'✦','DEV025':'⊙','DEV026':'◯','DEV027':'✦' }
var LIGHT_LABELS = { 'DEV001':'筒灯1','DEV002':'筒灯2','DEV003':'吊灯','DEV009':'吊灯','DEV010':'筒灯','DEV016':'吊灯','DEV017':'筒灯','DEV018':'背景灯','DEV025':'吊灯','DEV026':'筒灯','DEV027':'背景灯' }
var FAN_ICONS = { 'DEV004':'⏣','DEV005':'⏣','DEV006':'⏣','DEV011':'⏏','DEV012':'⏣','DEV019':'⏣','DEV028':'⏣' }
var FAN_LABELS = { 'DEV004':'风扇1','DEV005':'风扇2','DEV006':'风扇3','DEV011':'换气扇','DEV012':'风扇','DEV019':'风扇','DEV028':'风扇' }

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--', orderSlot: '', orderStart: '',
    balance: 0, hideBottomNav: false,
    devKeys: [], acModeLabel: '',
    acDevice: null, curtainDevices: [], bgmDevice: null,
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
    try { if (wx.getStorageSync('mp_user_role') === 'staff') this.setData({ hideBottomNav: true }) } catch(e) {}
    this.setData({ roomId: roomId, roomName: roomName, orderStart: startStr })
    this.loadDevices()
    this.startCountdown(duration, endStr)
    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  loadDevices: function() {
    var self = this
    API.getRoomDevices(this.data.roomId).then(function(devices) {
      var stateMap = {}
      var ac = null, curtains = [], bgm = null
      for (var i = 0; i < devices.length; i++) {
        var d = devices[i]
        if (d.type === 'Light') stateMap[d.deviceId] = (d.brightness || 0) > 0
        else if (d.type === 'Fan') stateMap[d.deviceId] = (d.speed || 0) > 0
        else if (d.type === 'ExhaustFan') stateMap[d.deviceId] = (d.speed || 0) > 0
        else if (d.type === 'AC') { ac = d; stateMap[d.deviceId] = d.mode === 'cool' }
        else if (d.type === 'Curtain') { d.positionNum = d.position === 'open' ? 100 : (d.position === 'closed' ? 0 : parseInt(d.position) || 0); curtains.push(d) }
        else if (d.type === 'BGM') { bgm = d; stateMap[d.deviceId] = d.playing }
      }

      // 合并灯光和风扇按键，田字格排列（严格2列）
      var roomId = self.data.roomId
      var lightIds = LIGHT_DEVICE_IDS[roomId] || []
      var allLightsOn = lightIds.length > 0
      for (var j = 0; j < lightIds.length; j++) {
        if (!stateMap[lightIds[j]]) { allLightsOn = false; break }
      }
      var devKeys = [
        { key: 'light_all_on',  label: '灯全开', icon: '◉', type: 'virtual', active: allLightsOn },
        { key: 'light_all_off', label: '灯全关', icon: '◎', type: 'virtual', active: false },
      ]
      for (var j = 0; j < lightIds.length; j++) {
        devKeys.push({ key: lightIds[j], label: LIGHT_LABELS[lightIds[j]] || lightIds[j], icon: LIGHT_ICONS[lightIds[j]] || '💡', type: 'Light', active: stateMap[lightIds[j]] || false })
      }
      var fanIds = FAN_DEVICE_IDS[roomId] || []
      for (var j = 0; j < fanIds.length; j++) {
        devKeys.push({ key: fanIds[j], label: FAN_LABELS[fanIds[j]] || fanIds[j], icon: FAN_ICONS[fanIds[j]] || '🌀', type: fanIds[j] === 'DEV011' ? 'ExhaustFan' : 'Fan', active: stateMap[fanIds[j]] || false })
      }

      self.setData({
        devKeys: devKeys,
        acDevice: ac, acModeLabel: ac ? self._acModeLabel(ac.mode) : '', curtainDevices: curtains, bgmDevice: bgm
      })
    })
  },

  onKeyTap: function(e) {
    var key = e.currentTarget.dataset.key
    var type = e.currentTarget.dataset.type

    if (key === 'light_all_on') { this._setAllLights(true); return }
    if (key === 'light_all_off') { this._setAllLights(false); return }

    // 设备开关
    var currentOn = false
    var keys = this.data.devKeys
    for (var i = 0; i < keys.length; i++) { if (keys[i].key === key) { currentOn = keys[i].active; break } }
    this._toggleDevice(key, type, !currentOn)
  },

  _setAllLights: function(on) {
    var self = this
    var lightIds = LIGHT_DEVICE_IDS[self.data.roomId] || []
    // UI立即更新
    var keys = self.data.devKeys
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].key === 'light_all_on') keys[i].active = on
      else if (keys[i].key === 'light_all_off') keys[i].active = false
      else if (keys[i].type === 'Light') keys[i].active = on
    }
    self.setData({ devKeys: keys })
    wx.showLoading({ title: on ? '全开中...' : '全关中...' })
    var done = 0
    for (var i = 0; i < lightIds.length; i++) {
      API.controlDevice(lightIds[i], { brightness: on ? 80 : 0 }).then(function() {
        done++; if (done >= lightIds.length) { wx.hideLoading(); self.loadDevices() }
      }).catch(function() {
        done++; if (done >= lightIds.length) { wx.hideLoading(); self.loadDevices() }
      })
    }
    if (lightIds.length === 0) { wx.hideLoading(); self.loadDevices() }
  },

  _toggleDevice: function(deviceId, type, newState) {
    var self = this
    var keys = self.data.devKeys
    for (var i = 0; i < keys.length; i++) { if (keys[i].key === deviceId) { keys[i].active = newState; break } }
    self.setData({ devKeys: keys })
    var cmd = {}
    if (type === 'Light') cmd = { brightness: newState ? 80 : 0 }
    else if (type === 'Fan' || type === 'ExhaustFan') cmd = { speed: newState ? 3 : 0 }
    API.controlDevice(deviceId, cmd).catch(function() {})
  },

  // ── 空调（制冷/制热/送风/关闭） ──
  toggleAC: function(e) {
    var id = e.currentTarget.dataset.id, ac = this.data.acDevice
    if (!ac) return
    ac.mode = ac.mode === 'off' ? 'cool' : 'off'
    this.setData({ acDevice: ac, acModeLabel: this._acModeLabel(ac.mode) })
    API.controlDevice(id, { mode: ac.mode }).catch(function(){})
  },
  setACMode: function(e) {
    var id = e.currentTarget.dataset.id, mode = e.currentTarget.dataset.mode, ac = this.data.acDevice
    if (!ac) return; ac.mode = mode
    this.setData({ acDevice: ac, acModeLabel: this._acModeLabel(mode) })
    API.controlDevice(id, { mode: mode }).catch(function(){})
  },
  acTempUp: function(e) {
    var id = e.currentTarget.dataset.id, ac = this.data.acDevice
    if (!ac) return; ac.temperature = Math.min(30, (ac.temperature || 24) + 1)
    this.setData({ acDevice: ac }); API.controlDevice(id, { temperature: ac.temperature }).catch(function(){})
  },
  acTempDown: function(e) {
    var id = e.currentTarget.dataset.id, ac = this.data.acDevice
    if (!ac) return; ac.temperature = Math.max(16, (ac.temperature || 24) - 1)
    this.setData({ acDevice: ac }); API.controlDevice(id, { temperature: ac.temperature }).catch(function(){})
  },
  _acModeLabel: function(mode) {
    if (mode === 'cool') return '制冷中'
    if (mode === 'heat') return '制热中'
    if (mode === 'fan') return '送风中'
    return '已关机'
  },

  // ── 窗帘 ──
  onCurtainChange: function(e) {
    var id = e.currentTarget.dataset.id, val = parseInt(e.detail.value)
    var position = val >= 80 ? 'open' : (val <= 20 ? 'closed' : val + '%')
    var devs = this.data.curtainDevices
    for (var i = 0; i < devs.length; i++) { if (devs[i].deviceId === id) { devs[i].positionNum = val; devs[i].position = position; break } }
    this.setData({ curtainDevices: devs }); API.controlDevice(id, { position: position }).catch(function(){})
  },

  // ── 背景音乐 ──
  toggleBGM: function(e) {
    var id = e.currentTarget.dataset.id, bgm = this.data.bgmDevice
    if (!bgm) return; bgm.playing = !bgm.playing
    this.setData({ bgmDevice: bgm }); API.controlDevice(id, { playing: bgm.playing }).catch(function(){})
  },
  onBGMVolumeChange: function(e) {
    var id = e.currentTarget.dataset.id, val = parseInt(e.detail.value), bgm = this.data.bgmDevice
    if (!bgm) return; bgm.volume = val; this.setData({ bgmDevice: bgm })
    API.controlDevice(id, { volume: val }).catch(function(){})
  },

  // ── 倒计时 ──
  startCountdown: function(durationMin, endStr) {
    var self = this; durationMin = durationMin || 120; var now = new Date()
    if (endStr) {
      var ep = endStr.split(':')
      if (ep.length >= 2) {
        var eh = parseInt(ep[0]), em = parseInt(ep[1])
        var endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), eh, em)
        if (endDate <= now) endDate.setDate(endDate.getDate() + 1)
        var totalSec = Math.max(0, Math.round((endDate - now) / 1000))
        self.setData({ endTime: endStr }); self._countdownTotal = totalSec; self._endDate = endDate
        if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
        self.setData({ countdown: self._fmtCountdown(totalSec) }); self._startTimer(); self._updateSlot(); return
      }
    }
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self._endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), endH, endM)
    self.setData({ endTime: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })
    var totalSec = durationMin * 60; self._countdownTotal = totalSec
    if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
    self.setData({ countdown: self._fmtCountdown(totalSec) }); self._startTimer(); self._updateSlot()
  },
  _updateSlot: function() {
    var s = this.data.orderStart, e = this.data.endTime
    if (e) this.setData({ orderSlot: (s || '--:--') + ' - ' + e })
  },
  _startTimer: function() {
    var self = this; if (self._countdownTimer) clearInterval(self._countdownTimer)
    setTimeout(function() {
      self._countdownTimer = setInterval(function() {
        self._countdownTotal = Math.max(0, self._countdownTotal - 1)
        self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      }, 1000)
    }, 300)
  },
  _fmtCountdown: function(s) { if (s <= 0) return '00:00'; var m = Math.floor(s / 60), sec = s % 60; return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0') },
  onUnload: function() { if (this._countdownTimer) clearInterval(this._countdownTimer) },
  preventBubble: function() {},
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },

  // ── 续订 ──
  showExtend: function() {
    var self = this
    var endDate = self._endDate ? new Date(self._endDate) : new Date()
    self.setData({ extendInfo: '当前将于 ' + String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0') + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })
    var options = []
    for (var i = 1; i <= 24; i++) {
      var nd = new Date(endDate.getTime() + i * 30 * 60000)
      options.push({ label: '至 ' + String(nd.getHours()).padStart(2,'0') + ':' + String(nd.getMinutes()).padStart(2,'0'), minutes: i * 30, price: Math.round(120 * i * 30 / 60) })
    }
    self.setData({ extendOptions: options, showExtendModal: true })
  },
  selectExtend: function(e) { this.setData({ selectedExtendIdx: parseInt(e.currentTarget.dataset.index) }) },
  confirmExtend: function() {
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx], self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0, extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''), extendPayAmount: opt.price, extendPayMethod: 'balance', showExtendModal: false, showExtendPayModal: true }) })
  },
  selectExtendPay: function(e) { this.setData({ extendPayMethod: e.currentTarget.dataset.pay }) },
  doExtendPayment: function() {
    var self = this, idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx], method = this.data.extendPayMethod
    var p = function() {
      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      if (self._endDate) { self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000); self.setData({ endTime: String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0') }) }
      try { var bk = wx.getStorageSync('mp_bookings') || []; for (var i = 0; i < bk.length; i++) { if (bk[i].roomId === self.data.roomId && bk[i].status === 'InUse') { bk[i].endTime = String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0'); break } }; wx.setStorageSync('mp_bookings', bk) } catch(e) {}
      self._updateSlot(); self.setData({ showExtendPayModal: false }); wx.showToast({ title: '续订成功！已支付 ¥' + opt.price, icon: 'success' })
    }
    if (method === 'balance') {
      API.getBalance().then(function(bal) { if (bal < opt.price) { wx.showToast({ title: '余额不足，请选择其他方式', icon: 'none' }); return }; var u = wx.getStorageSync('mp_user') || {}; u.balance = bal - opt.price; wx.setStorageSync('mp_user', u); self.setData({ balance: u.balance }); p() })
    } else { wx.showLoading({ title: '支付中...' }); setTimeout(function() { wx.hideLoading(); p() }, 800) }
  },
  hideExtend: function() { this.setData({ showExtendModal: false }) },
  cancelExtendPay: function() { this.setData({ showExtendPayModal: false }); wx.showToast({ title: '已取消续订', icon: 'none' }) }
})
