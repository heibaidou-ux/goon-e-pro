var API = require('../../utils/api')

Page({
  data: { roomId: '', roomName: '房间', devices: [] },

  onLoad: function(e) {
    var roomId = e.roomId || 'RM004'
    this.setData({ roomId: roomId, roomName: e.roomName || '房间' })
    this.loadDevices()
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

  goBack: function() { wx.navigateBack() },

  // 第26条：门锁开关
  onLockToggle: function(e) {
    var locked = !e.detail.value
    API.controlDevice(e.currentTarget.dataset.id, { locked: locked }).catch(function(){})
  },

  // 第27条：空调温度
  onTempUp: function(e) {
    var id = e.currentTarget.dataset.id
    var devices = this.data.devices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id && devices[i].type === 'AC') {
        var temp = (devices[i].temperature || 24) + 1
        if (temp > 30) temp = 30
        devices[i].temperature = temp
        break
      }
    }
    this.setData({ devices: devices })
    API.controlDevice(id, { temperature: temp || 25 }).catch(function(){})
  },

  onTempDown: function(e) {
    var id = e.currentTarget.dataset.id
    var devices = this.data.devices
    for (var i = 0; i < devices.length; i++) {
      if (devices[i].deviceId === id && devices[i].type === 'AC') {
        var temp = (devices[i].temperature || 24) - 1
        if (temp < 16) temp = 16
        devices[i].temperature = temp
        break
      }
    }
    this.setData({ devices: devices })
    API.controlDevice(id, { temperature: temp || 23 }).catch(function(){})
  },

  onAcToggle: function(e) {
    API.controlDevice(e.currentTarget.dataset.id, { mode: e.detail.value ? 'cool' : 'off' }).catch(function(){})
  },

  // 第28条：灯光开关
  onLightToggle: function(e) {
    var brightness = e.detail.value ? 80 : 0
    API.controlDevice(e.currentTarget.dataset.id, { brightness: brightness }).catch(function(){})
  },

  // 第29条：窗帘滑条
  onCurtainChange: function(e) {
    var val = parseInt(e.detail.value)
    var position = val >= 80 ? 'open' : (val <= 20 ? 'closed' : val + '%')
    API.controlDevice(e.currentTarget.dataset.id, { position: position }).catch(function(){})
  },

  // 第30条：音乐开关
  onSpeakerToggle: function(e) {
    API.controlDevice(e.currentTarget.dataset.id, { playing: e.detail.value }).catch(function(){})
  }
})
