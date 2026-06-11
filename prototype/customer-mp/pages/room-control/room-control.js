var API = require('../../utils/api')

// 每个房间的面板布局，与墙面物理开关一一对应
var PANEL_LAYOUTS = {
  // 会议室: 面板1(灯全开/灯全关/筒灯1/筒灯2) 面板2(吊灯/风扇1/风扇2/风扇3)
  RM001: {
    panel1: [
      { key: 'light_all_on',  label: '灯全开', icon: '💡', type: 'virtual', virtualAction: 'all_on' },
      { key: 'light_all_off', label: '灯全关', icon: '🔌', type: 'virtual', virtualAction: 'all_off' },
      { key: 'DEV001', label: '筒灯1', icon: '◯', type: 'Light' },
      { key: 'DEV002', label: '筒灯2', icon: '◯', type: 'Light' },
    ],
    panel2: [
      { key: 'DEV003', label: '吊灯', icon: '💡', type: 'Light' },
      { key: 'DEV004', label: '风扇1', icon: '🌀', type: 'Fan' },
      { key: 'DEV005', label: '风扇2', icon: '🌀', type: 'Fan' },
      { key: 'DEV006', label: '风扇3', icon: '🌀', type: 'Fan' },
    ]
  },
  // 小茶室: 面板1(灯全开/灯全关/吊灯/筒灯) 面板2(换气扇/风扇/窗帘开/窗帘关)
  RM002: {
    panel1: [
      { key: 'light_all_on',  label: '灯全开', icon: '💡', type: 'virtual', virtualAction: 'all_on' },
      { key: 'light_all_off', label: '灯全关', icon: '🔌', type: 'virtual', virtualAction: 'all_off' },
      { key: 'DEV009', label: '吊灯', icon: '💡', type: 'Light' },
      { key: 'DEV010', label: '筒灯', icon: '◯', type: 'Light' },
    ],
    panel2: [
      { key: 'DEV011', label: '换气扇', icon: '🌬️', type: 'ExhaustFan' },
      { key: 'DEV012', label: '风扇',   icon: '🌀', type: 'Fan' },
      { key: 'curtain_ctrl', label: '窗帘', icon: '🪟', type: 'virtual', virtualAction: 'scroll_curtain' },
      { key: 'dev_null', label: '', icon: '', type: 'blank' },
    ]
  },
  // 中茶室B: 面板1(灯全开/灯全关/吊灯/筒灯) 面板2(背景灯/风扇/窗帘开/窗帘关)
  RM003: {
    panel1: [
      { key: 'light_all_on',  label: '灯全开', icon: '💡', type: 'virtual', virtualAction: 'all_on' },
      { key: 'light_all_off', label: '灯全关', icon: '🔌', type: 'virtual', virtualAction: 'all_off' },
      { key: 'DEV016', label: '吊灯', icon: '💡', type: 'Light' },
      { key: 'DEV017', label: '筒灯', icon: '◯', type: 'Light' },
    ],
    panel2: [
      { key: 'DEV018', label: '背景灯', icon: '✨', type: 'Light' },
      { key: 'DEV019', label: '风扇',   icon: '🌀', type: 'Fan' },
      { key: 'curtain_ctrl', label: '窗帘', icon: '🪟', type: 'virtual', virtualAction: 'scroll_curtain' },
      { key: 'dev_null', label: '', icon: '', type: 'blank' },
    ]
  },
  // 大茶室C: 面板1(灯全开/灯全关/吊灯/筒灯) 面板2(背景灯/风扇/窗帘开/窗帘关)
  RM004: {
    panel1: [
      { key: 'light_all_on',  label: '灯全开', icon: '💡', type: 'virtual', virtualAction: 'all_on' },
      { key: 'light_all_off', label: '灯全关', icon: '🔌', type: 'virtual', virtualAction: 'all_off' },
      { key: 'DEV025', label: '吊灯', icon: '💡', type: 'Light' },
      { key: 'DEV026', label: '筒灯', icon: '◯', type: 'Light' },
    ],
    panel2: [
      { key: 'DEV027', label: '背景灯', icon: '✨', type: 'Light' },
      { key: 'DEV028', label: '风扇',   icon: '🌀', type: 'Fan' },
      { key: 'curtain_ctrl', label: '窗帘', icon: '🪟', type: 'virtual', virtualAction: 'scroll_curtain' },
      { key: 'dev_null', label: '', icon: '', type: 'blank' },
    ]
  },
  // 展厅: 仅背景音乐
  RM005: {
    panel1: [],
    panel2: []
  }
}

// 哪些key是灯光设备（用于全开/全关）
var LIGHT_DEVICE_IDS = {
  RM001: ['DEV001','DEV002','DEV003'],
  RM002: ['DEV009','DEV010'],
  RM003: ['DEV016','DEV017','DEV018'],
  RM004: ['DEV025','DEV026','DEV027'],
  RM005: []
}

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--', orderSlot: '', orderStart: '',
    balance: 0,
    panel1: [], panel2: [],
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
    this.setData({ roomId: roomId, roomName: roomName, orderStart: startStr })
    this.loadDevices()
    this.startCountdown(duration, endStr)
    var self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  loadDevices: function() {
    var self = this
    API.getRoomDevices(this.data.roomId).then(function(devices) {
      // 建立 deviceId → on状态映射
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

      // 构建面板
      var layout = PANEL_LAYOUTS[self.data.roomId]
      if (!layout) layout = { panel1: [], panel2: [] }

      var panel1 = []
      var allLightsOn = true
      var lightIds = LIGHT_DEVICE_IDS[self.data.roomId] || []
      for (var j = 0; j < lightIds.length; j++) {
        if (!stateMap[lightIds[j]]) { allLightsOn = false; break }
      }

      for (var j = 0; j < layout.panel1.length; j++) {
        var k = layout.panel1[j]
        if (k.type === 'virtual') {
          if (k.virtualAction === 'all_on') panel1.push({ key: k.key, label: k.label, icon: k.icon, type: 'virtual', active: allLightsOn })
          else if (k.virtualAction === 'all_off') panel1.push({ key: k.key, label: k.label, icon: k.icon, type: 'virtual', active: false })
          else panel1.push({ key: k.key, label: k.label, icon: k.icon, type: 'virtual', active: false })
        } else if (k.type === 'blank') {
          panel1.push({ key: 'blank', label: '', icon: '', type: 'blank', active: false })
        } else {
          panel1.push({ key: k.key, label: k.label, icon: k.icon, type: k.type, active: stateMap[k.key] || false })
        }
      }

      var panel2 = []
      for (var j = 0; j < layout.panel2.length; j++) {
        var k = layout.panel2[j]
        if (k.type === 'virtual') {
          panel2.push({ key: k.key, label: k.label, icon: k.icon, type: 'virtual', active: false })
        } else if (k.type === 'blank') {
          panel2.push({ key: 'blank', label: '', icon: '', type: 'blank', active: false })
        } else {
          panel2.push({ key: k.key, label: k.label, icon: k.icon, type: k.type, active: stateMap[k.key] || false })
        }
      }

      self.setData({
        panel1: panel1, panel2: panel2,
        acDevice: ac, curtainDevices: curtains, bgmDevice: bgm
      })
    })
  },

  onPanelKeyTap: function(e) {
    var key = e.currentTarget.dataset.key
    var type = e.currentTarget.dataset.type
    var roomId = this.data.roomId

    // 灯全开
    if (key === 'light_all_on') {
      this._setAllLights(true)
      return
    }
    // 灯全关
    if (key === 'light_all_off') {
      this._setAllLights(false)
      return
    }
    // 窗帘（滚动到窗帘区域）
    if (key === 'curtain_ctrl') {
      wx.showToast({ title: '请在下方窗帘区域调节', icon: 'none' })
      return
    }
    if (key === 'blank' || key === 'dev_null') return

    // 设备开关
    this._toggleDevice(key, type)
  },

  _setAllLights: function(on) {
    var self = this
    var lightIds = LIGHT_DEVICE_IDS[self.data.roomId] || []
    // 更新面板UI
    var panel1 = self.data.panel1
    for (var i = 0; i < panel1.length; i++) {
      if (panel1[i].type === 'virtual' && panel1[i].virtualAction === 'all_on') panel1[i].active = on
    }
    self.setData({ panel1: panel1 })
    wx.showLoading({ title: on ? '全开中...' : '全关中...' })
    // 逐个控制灯光设备
    var done = 0
    for (var i = 0; i < lightIds.length; i++) {
      API.controlDevice(lightIds[i], { brightness: on ? 80 : 0 }).then(function() {
        done++
        if (done >= lightIds.length) {
          wx.hideLoading()
          self.loadDevices()
        }
      }).catch(function() {
        done++
        if (done >= lightIds.length) { wx.hideLoading(); self.loadDevices() }
      })
    }
    if (lightIds.length === 0) { wx.hideLoading(); self.loadDevices() }
  },

  _toggleDevice: function(deviceId, type) {
    var self = this
    // 先取当前状态
    var currentOn = false
    for (var i = 0; i < self.data.panel1.length; i++) {
      if (self.data.panel1[i].key === deviceId) { currentOn = self.data.panel1[i].active; break }
    }
    for (var i = 0; i < self.data.panel2.length; i++) {
      if (self.data.panel2[i].key === deviceId) { currentOn = self.data.panel2[i].active; break }
    }
    var newState = !currentOn

    // 立即更新UI
    var p1 = self.data.panel1, p2 = self.data.panel2
    for (var i = 0; i < p1.length; i++) { if (p1[i].key === deviceId) { p1[i].active = newState; break } }
    for (var i = 0; i < p2.length; i++) { if (p2[i].key === deviceId) { p2[i].active = newState; break } }
    self.setData({ panel1: p1, panel2: p2 })

    var cmd = {}
    if (type === 'Light') cmd = { brightness: newState ? 80 : 0 }
    else if (type === 'Fan' || type === 'ExhaustFan') cmd = { speed: newState ? 3 : 0 }
    API.controlDevice(deviceId, cmd).catch(function() {})
  },

  // ── 空调 ──
  toggleAC: function(e) {
    var id = e.currentTarget.dataset.id
    var ac = this.data.acDevice
    if (!ac) return
    ac.mode = ac.mode === 'cool' ? 'off' : 'cool'
    this.setData({ acDevice: ac })
    API.controlDevice(id, { mode: ac.mode }).catch(function(){})
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
    var curEndStr = String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0')
    self.setData({ extendInfo: '当前将于 ' + curEndStr + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })
    var options = []
    for (var i = 1; i <= 24; i++) {
      var newDate = new Date(endDate.getTime() + i * 30 * 60000)
      var oh = newDate.getHours(), om = newDate.getMinutes()
      options.push({ label: '至 ' + String(oh).padStart(2,'0') + ':' + String(om).padStart(2,'0'), minutes: i * 30, price: Math.round(120 * i * 30 / 60) })
    }
    self.setData({ extendOptions: options, showExtendModal: true })
  },
  selectExtend: function(e) { this.setData({ selectedExtendIdx: parseInt(e.currentTarget.dataset.index) }) },
  confirmExtend: function() {
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx]
    var self = this
    API.getBalance().then(function(b) {
      self.setData({ balance: b || 0, extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''), extendPayAmount: opt.price, extendPayMethod: 'balance', showExtendModal: false, showExtendPayModal: true })
    })
  },
  selectExtendPay: function(e) { this.setData({ extendPayMethod: e.currentTarget.dataset.pay }) },
  doExtendPayment: function() {
    var self = this, idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx], method = this.data.extendPayMethod
    var p = function() {
      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      if (self._endDate) {
        self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000)
        self.setData({ endTime: String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0') })
      }
      try {
        var bookings = wx.getStorageSync('mp_bookings') || []
        for (var i = 0; i < bookings.length; i++) {
          if (bookings[i].roomId === self.data.roomId && bookings[i].status === 'InUse') {
            bookings[i].endTime = String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0')
            break
          }
        }
        wx.setStorageSync('mp_bookings', bookings)
      } catch(e) {}
      self._updateSlot(); self.setData({ showExtendPayModal: false })
      wx.showToast({ title: '续订成功！已支付 ¥' + opt.price, icon: 'success' })
    }
    if (method === 'balance') {
      API.getBalance().then(function(balance) {
        if (balance < opt.price) { wx.showToast({ title: '余额不足，请选择其他方式', icon: 'none' }); return }
        var user = wx.getStorageSync('mp_user') || {}; user.balance = balance - opt.price
        wx.setStorageSync('mp_user', user); self.setData({ balance: user.balance }); p()
      })
    } else { wx.showLoading({ title: '支付中...' }); setTimeout(function() { wx.hideLoading(); p() }, 800) }
  },
  hideExtend: function() { this.setData({ showExtendModal: false }) },
  cancelExtendPay: function() { this.setData({ showExtendPayModal: false }); wx.showToast({ title: '已取消续订', icon: 'none' }) }
})
