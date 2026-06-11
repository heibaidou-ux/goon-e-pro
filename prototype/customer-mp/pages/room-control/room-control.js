var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '房间',
    countdown: '--:--', endTime: '--:--',
    // 设备
    devices: []
  },

  onLoad: function(e) {
    var roomId = e.roomId || 'RM004'
    var roomName = e.roomName ? decodeURIComponent(e.roomName) : '大茶室C'
    this.setData({ roomId: roomId, roomName: roomName })
    this.loadDevices()
    this.startCountdown()
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

  startCountdown: function() {
    var self = this
    // 假设结束时间为当前时间+2小时（演示用）
    var now = new Date()
    var endH = now.getHours() + 2
    var endM = now.getMinutes()
    self.setData({ endTime: String(endH%24).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })

    setInterval(function() {
      var n = new Date()
      var remaining = 2*3600 - (n.getHours()*3600 + n.getMinutes()*60 + n.getSeconds() - (now.getHours()*3600 + now.getMinutes()*60 + now.getSeconds()))
      if (remaining <= 0) { self.setData({ countdown: '00:00' }); return }
      var h = Math.floor(remaining/3600), m = Math.floor((remaining%3600)/60), s = remaining%60
      self.setData({ countdown: String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0') })
    }, 1000)
  },

  goBack: function() { wx.navigateBack() },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  renewOrder: function() { wx.showToast({ title: '续订功能开发中', icon: 'none' }) },

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
