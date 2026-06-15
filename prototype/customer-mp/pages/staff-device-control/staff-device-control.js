var API = require('../../utils/api')

Page({
  data: {
    currentRoomId: 'RM001',
    currentRoomName: '大会议室',
    roomNames: ['大会议室', '中茶室A', '中茶室B', '大茶室C'],
    roomIds: ['RM001', 'RM002', 'RM003', 'RM004'],
    devices: [],
    showLockConfirm: false, lockDeviceId: '',
    // 展平设备状态
    hasAC: false, acOn: false, acTemp: 24, acMode: 'cool',
    hasLight: false, lightOn: false, lightBrightness: 80, lightColorTemp: 4000,
    hasCurtain: false, curtainOn: false, curtainPosition: 50,
    hasSpeaker: false, speakerOn: false, speakerVolume: 30,
    hasLock: false, lockLocked: false,
    hasFan: false,
  },

  onShow: function() { this.loadDevices(this.data.currentRoomId) },

  switchRoom: function(e) {
    var idx = e.detail.value
    this.setData({
      currentRoomId: this.data.roomIds[idx],
      currentRoomName: this.data.roomNames[idx]
    })
    this.loadDevices(this.data.roomIds[idx])
  },

  loadDevices: function(roomId) {
    var self = this
    API.getRoomDevices(roomId).then(function(devices) {
      var labels = { Lock:'门锁', Light:'灯光', AC:'空调', Fan:'风扇', ExhaustFan:'换气扇', Curtain:'窗帘', BGM:'音响', Speaker:'音响' }
      var icons  = { Lock:'🔒', Light:'💡', AC:'❄️', Fan:'🌀', ExhaustFan:'🌬️', Curtain:'🪟', BGM:'🎵', Speaker:'🔊' }
      for (var i = 0; i < devices.length; i++) {
        devices[i].typeLabel = labels[devices[i].type] || devices[i].type
        devices[i].typeIcon = icons[devices[i].type] || '📡'
        var a = devices[i].attributes || {}
        if (devices[i].type === 'Light') devices[i].on = a.power || (a.brightness || 0) > 0
        else if (devices[i].type === 'Fan' || devices[i].type === 'ExhaustFan') devices[i].on = (a.speed || 0) > 0
        else if (devices[i].type === 'AC') devices[i].on = a.mode && a.mode !== 'off'
        else if (devices[i].type === 'BGM' || devices[i].type === 'Speaker') devices[i].on = a.playing
        else if (devices[i].type === 'Curtain') devices[i].on = a.position !== 'closed'
        else if (devices[i].type === 'Lock') devices[i].on = a.locked
      }
      self.setData({ devices: devices })
      self._syncParams(devices)
    })
  },

  _syncParams: function(devices) {
    var flat = { hasAC:false, acOn:false, acTemp:24, acMode:'cool',
      hasLight:false, lightOn:false, lightBrightness:80, lightColorTemp:4000,
      hasCurtain:false, curtainOn:false, curtainPosition:50,
      hasSpeaker:false, speakerOn:false, speakerVolume:30,
      hasLock:false, lockLocked:false, hasFan:false }
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i], a = d.attributes || {}
      if (d.type === 'AC') { flat.hasAC = true; flat.acOn = d.on; flat.acTemp = a.target_temperature || a.temperature || 24; flat.acMode = a.mode || 'cool' }
      if (d.type === 'Light') { flat.hasLight = true; flat.lightOn = d.on; flat.lightBrightness = a.brightness || 80; flat.lightColorTemp = a.color_temp || 4000 }
      if (d.type === 'Curtain') { flat.hasCurtain = true; flat.curtainOn = d.on; flat.curtainPosition = a.current_position || (d.on ? 100 : 0) }
      if (d.type === 'Speaker' || d.type === 'BGM') { flat.hasSpeaker = true; flat.speakerOn = d.on; flat.speakerVolume = a.volume || 30 }
      if (d.type === 'Lock') { flat.hasLock = true; flat.lockLocked = a.locked !== false }
      if (d.type === 'Fan' || d.type === 'ExhaustFan') flat.hasFan = true
    }
    this.setData(flat)
  },

  // ── AC ──
  toggleAC: function() {
    var self = this
    var dev = this._findDev('AC'); if (!dev) return
    var on = !this.data.acOn
    API.controlDevice(dev.deviceId, { action: on ? 'on' : 'off' }).then(function() {
      dev.on = on; self.setData({ acOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  setACTemp: function(e) {
    var temp = parseInt(e.currentTarget.dataset.temp)
    var self = this; this.setData({ acTemp: temp })
    var dev = this._findDev('AC')
    if (dev) API.controlDevice(dev.deviceId, { action: 'temperature', temperature: temp }).catch(function(){})
  },
  setACMode: function(e) {
    var mode = e.currentTarget.dataset.mode; var self = this
    this.setData({ acMode: mode })
    var dev = this._findDev('AC')
    if (dev) API.controlDevice(dev.deviceId, { action: mode }).catch(function(){})
  },

  // ── Light ──
  toggleLight: function() {
    var self = this; var dev = this._findDev('Light'); if (!dev) return
    var on = !this.data.lightOn
    API.controlDevice(dev.deviceId, { action: on ? 'on' : 'off' }).then(function() {
      dev.on = on; self.setData({ lightOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  setLightBrightness: function(e) {
    var val = parseInt(e.detail.value); this.setData({ lightBrightness: val })
    var dev = this._findDev('Light')
    if (dev) API.controlDevice(dev.deviceId, { action: 'brightness', brightness: val }).catch(function(){})
  },
  setLightColorTemp: function(e) {
    var temp = parseInt(e.currentTarget.dataset.temp); this.setData({ lightColorTemp: temp })
    var dev = this._findDev('Light')
    if (dev) API.controlDevice(dev.deviceId, { action: 'on', color_temp: temp }).catch(function(){})
  },

  // ── Curtain ──
  toggleCurtain: function() {
    var self = this; var dev = this._findDev('Curtain'); if (!dev) return
    var on = !this.data.curtainOn
    API.controlDevice(dev.deviceId, { action: on ? 'open' : 'close' }).then(function() {
      dev.on = on; self.setData({ curtainOn: on, curtainPosition: on ? 100 : 0, devices: self.data.devices })
    }).catch(function(){})
  },
  stopCurtain: function() {
    var dev = this._findDev('Curtain')
    if (dev) API.controlDevice(dev.deviceId, { action: 'stop' }).catch(function(){})
  },
  setCurtainPosition: function(e) {
    var pos = parseInt(e.detail.value); this.setData({ curtainPosition: pos })
    var dev = this._findDev('Curtain')
    if (dev) API.controlDevice(dev.deviceId, { action: 'position', position: pos }).catch(function(){})
  },

  // ── Speaker ──
  toggleSpeaker: function() {
    var self = this; var dev = this._findDev('Speaker') || this._findDev('BGM'); if (!dev) return
    var on = !this.data.speakerOn
    API.controlDevice(dev.deviceId, { action: on ? 'on' : 'off' }).then(function() {
      dev.on = on; self.setData({ speakerOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  setSpeakerVolume: function(e) {
    var vol = parseInt(e.detail.value); this.setData({ speakerVolume: vol })
    var dev = this._findDev('Speaker') || this._findDev('BGM')
    if (dev) API.controlDevice(dev.deviceId, { action: 'volume', volume: vol }).catch(function(){})
  },

  // ── Lock ──
  unlockDoor: function(e) {
    this.setData({ showLockConfirm: true, lockDeviceId: e.currentTarget.dataset.id })
  },
  confirmUnlock: function() {
    var self = this; var id = this.data.lockDeviceId; if (!id) return
    API.controlDevice(id, { action: 'unlock' }).then(function(res) {
      wx.showToast({ title: '🔓 门锁已开启', icon: 'none' })
      self.setData({ lockLocked: false, showLockConfirm: false, lockDeviceId: '' })
    }).catch(function() { self.setData({ showLockConfirm: false }) })
  },
  cancelUnlock: function() { this.setData({ showLockConfirm: false, lockDeviceId: '' }) },

  // ── 通用开关 ──
  toggleFan: function(e) {
    var id = e.currentTarget.dataset.id
    API.controlDevice(id, {}).catch(function(){})
  },

  _findDev: function(type) {
    var list = this.data.devices
    for (var i = 0; i < list.length; i++) { if (list[i].type === type) return list[i] }
    return null
  }
})
