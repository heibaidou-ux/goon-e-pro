var API = require('../../../utils/api')

Page({
  data: {
    currentRoomId: "RM001",
    currentRoomName: "丰沙里",
    roomNames: ["丰沙里", "翡冷翠", "布拉格", "白沙瓦"],
    roomIds: ["RM001", "RM002", "RM003", "RM004"],
    devices: [],
    showLockConfirm: false, lockDeviceId: "",
    showRoomPicker: false,
    hasAC: false, acOn: false, acTemp: 24, acMode: "cool",
    hasLight: false, lightOn: false,
    hasCurtain: false, curtainOn: false, curtainPosition: 50,
    hasSpeaker: false, speakerOn: false, speakerVolume: 30,
    hasLock: false, lockLocked: false,
    hasFan: false,
  },
  onShow: function() { this.loadDevices(this.data.currentRoomId) },
  showRoomPicker: function() { this.setData({ showRoomPicker: true }) },
  hideRoomPicker: function() { this.setData({ showRoomPicker: false }) },
  selectRoom: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    this.setData({ showRoomPicker: false })
    this.setData({ currentRoomId: this.data.roomIds[idx], currentRoomName: this.data.roomNames[idx] })
    this.loadDevices(this.data.roomIds[idx])
  },
  loadDevices: function(roomId) {
    var self = this
    API.getRoomDevices(roomId).then(function(devices) {
      var labels = { Lock:"门锁", Light:"灯光", AC:"空调", Fan:"风扇", ExhaustFan:"换气扇", Curtain:"窗帘", BGM:"音响", Speaker:"音响" }
      var icons = { Lock:"🔒", Light:"💡", AC:"❄️", Fan:"🌀", ExhaustFan:"🌬️", Curtain:"🪟", BGM:"🎵", Speaker:"🔊" }
      for (var i = 0; i < devices.length; i++) {
        var d = devices[i], a = d.attributes || {}
        d.typeLabel = self.data.currentRoomName + " " + (labels[d.type] || d.type)
        d.typeIcon = icons[d.type] || "📡"
        if (d.type === "Light") d.on = a.power || (a.brightness || 0) > 0
        else if (d.type === "Fan" || d.type === "ExhaustFan") d.on = (a.speed || 0) > 0
        else if (d.type === "AC") d.on = a.mode && a.mode !== "off"
        else if (d.type === "BGM" || d.type === "Speaker") d.on = a.playing
        else if (d.type === "Curtain") d.on = a.position !== "closed"
        else if (d.type === "Lock") d.on = a.locked
      }
      self.setData({ devices: devices })
      self._syncParams(devices)
    })
  },
  _syncParams: function(devices) {
    var flat = { hasAC:false, acOn:false, acTemp:24, acMode:"cool",
      hasLight:false, lightOn:false,
      hasCurtain:false, curtainOn:false, curtainPosition:50,
      hasSpeaker:false, speakerOn:false, speakerVolume:30,
      hasLock:false, lockLocked:false, hasFan:false }
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i], a = d.attributes || {}
      if (d.type === "AC") { flat.hasAC = true; flat.acOn = d.on; flat.acTemp = a.target_temperature || a.temperature || 24; flat.acMode = a.mode || "cool" }
      if (d.type === "Light") { flat.hasLight = true; flat.lightOn = d.on }
      if (d.type === "Curtain") { flat.hasCurtain = true; flat.curtainOn = d.on; flat.curtainPosition = a.current_position || (d.on ? 100 : 0) }
      if (d.type === "Speaker" || d.type === "BGM") { flat.hasSpeaker = true; flat.speakerOn = d.on; flat.speakerVolume = a.volume || 30 }
      if (d.type === "Lock") { flat.hasLock = true; flat.lockLocked = a.locked !== false }
      if (d.type === "Fan" || d.type === "ExhaustFan") flat.hasFan = true
    }
    this.setData(flat)
  },
  toggleAC: function() {
    var self = this; var dev = this._findDev("AC"); if (!dev) return
    var on = !this.data.acOn
    API.controlDevice(dev.deviceId, { action: on ? "on" : "off" }).then(function() {
      dev.on = on; self.setData({ acOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  setACTemp: function(e) {
    var temp = parseInt(e.currentTarget.dataset.temp); this.setData({ acTemp: temp })
    var dev = this._findDev("AC")
    if (dev) API.controlDevice(dev.deviceId, { action: "temperature", temperature: temp }).catch(function(){})
  },
  setACMode: function(e) {
    var mode = e.currentTarget.dataset.mode; this.setData({ acMode: mode })
    var dev = this._findDev("AC")
    if (dev) API.controlDevice(dev.deviceId, { action: mode }).catch(function(){})
  },
  toggleLight: function() {
    var self = this; var dev = this._findDev("Light"); if (!dev) return
    var on = !this.data.lightOn
    API.controlDevice(dev.deviceId, { action: on ? "on" : "off" }).then(function() {
      dev.on = on; self.setData({ lightOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  toggleCurtain: function() {
    var self = this; var dev = this._findDev("Curtain"); if (!dev) return
    var on = !this.data.curtainOn
    API.controlDevice(dev.deviceId, { action: on ? "open" : "close" }).then(function() {
      dev.on = on; self.setData({ curtainOn: on, curtainPosition: on ? 100 : 0, devices: self.data.devices })
    }).catch(function(){})
  },
  stopCurtain: function() {
    var dev = this._findDev("Curtain")
    if (dev) API.controlDevice(dev.deviceId, { action: "stop" }).catch(function(){})
  },
  setCurtainPosition: function(e) {
    var pos = parseInt(e.detail.value); this.setData({ curtainPosition: pos })
    var dev = this._findDev("Curtain")
    if (dev) API.controlDevice(dev.deviceId, { action: "position", position: pos }).catch(function(){})
  },
  toggleSpeaker: function() {
    var self = this; var dev = this._findDev("Speaker") || this._findDev("BGM"); if (!dev) return
    var on = !this.data.speakerOn
    API.controlDevice(dev.deviceId, { action: on ? "on" : "off" }).then(function() {
      dev.on = on; self.setData({ speakerOn: on, devices: self.data.devices })
    }).catch(function(){})
  },
  setSpeakerVolume: function(e) {
    var vol = parseInt(e.detail.value); this.setData({ speakerVolume: vol })
    var dev = this._findDev("Speaker") || this._findDev("BGM")
    if (dev) API.controlDevice(dev.deviceId, { action: "volume", volume: vol }).catch(function(){})
  },
  unlockDoor: function(e) {
    this.setData({ showLockConfirm: true, lockDeviceId: e.currentTarget.dataset.id })
  },
  confirmUnlock: function() {
    var self = this; var id = this.data.lockDeviceId; if (!id) return
    API.controlDevice(id, { action: "unlock" }).then(function(res) {
      wx.showToast({ title: "🔓 门锁已开启", icon: "none" })
      self.setData({ lockLocked: false, showLockConfirm: false, lockDeviceId: "" })
    }).catch(function() { self.setData({ showLockConfirm: false }) })
  },
  cancelUnlock: function() { this.setData({ showLockConfirm: false, lockDeviceId: "" }) },
  toggleFan: function(e) {
    var id = e.currentTarget.dataset.id
    var on = e.detail && e.detail.value === true
    API.controlDevice(id, { action: on ? 'on' : 'off' }).catch(function(){})
  },
  _findDev: function(type) {
    var list = this.data.devices
    for (var i = 0; i < list.length; i++) { if (list[i].type === type) return list[i] }
    return null
  }
})
