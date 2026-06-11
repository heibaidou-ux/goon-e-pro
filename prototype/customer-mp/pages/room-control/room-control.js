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
        var totalSec = Math.max(0, Math.round((endDate - now) / 1000))
        self.setData({ endTime: endStr })
        self._countdownTotal = totalSec
        if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
        self.setData({ countdown: self._fmtCountdown(totalSec) })
        setInterval(function() {
          self._countdownTotal = Math.max(0, self._countdownTotal - 1)
          self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
        }, 1000)
        return
      }
    }

    // fallback: 用当前时间+duration
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self.setData({ endTime: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })
    var totalSec = durationMin * 60
    if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
    self.setData({ countdown: self._fmtCountdown(totalSec) })
    setInterval(function() {
      totalSec = Math.max(0, totalSec - 1)
      self.setData({ countdown: self._fmtCountdown(totalSec) })
    }, 1000)
  },

  _fmtCountdown: function(s) {
    if (s <= 0) return '00:00'
    var m = Math.floor(s / 60), sec = s % 60
    return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0')
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
