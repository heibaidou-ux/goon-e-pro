var API = require('../../utils/api')
var STAFF_API = require('../../utils/staff-api')

const ALL_SCENES = [
  { id: 'Welcome', name: '欢迎', icon: '🚪', desc: '空调预开+开门+灯光+音乐', type: 'Auto', params: { temperature: 24, colorTemp: 3500, volume: 30 } },
  { id: 'TeaSession', name: '品茗', icon: '🍵', desc: '暖光+轻音乐', type: 'Manual', params: { temperature: 24, colorTemp: 3000, volume: 40 } },
  { id: 'Meeting', name: '会议', icon: '💡', desc: '冷白光+静音', type: 'Manual', params: { temperature: 24, colorTemp: 4000, volume: 0 } },
  { id: 'Karaoke', name: 'K歌', icon: '🎤', desc: '彩灯+音响', type: 'Manual', params: { temperature: 24, colorTemp: 3500, volume: 80 } },
  { id: 'EnergySave', name: '节能', icon: '♻️', desc: '全部关闭', type: 'Auto', params: { temperature: 26, colorTemp: 2700, volume: 0 } },
  { id: 'PreOpen', name: '预开', icon: '⏰', desc: '提前开启空调', type: 'Schedule', params: { temperature: 24, colorTemp: 3000, volume: 20 } },
  { id: 'Cleanup', name: '打扫', icon: '🧹', desc: '关灯关空调+关窗帘+关音乐', type: 'Auto', params: { temperature: 26, colorTemp: 2700, volume: 0 } }
]

const TYPE_LABELS = { Auto: '自动', Manual: '手动', Schedule: '定时' }

Page({
  data: {
    rooms: [],
    roomIndex: 0,
    roomName: '大茶室C',
    roomBookable: true,
    activeSceneId: 'Welcome',
    activeSceneName: '欢迎模式',
    activeSceneTrigger: '自动触发',
    isManualOverride: false,
    showRoomPicker: false,
    showConfirm: false,
    pendingSceneId: null,
    confirmTitle: '',
    confirmDesc: '',
    temperature: 24,
    colorTemp: 3000,
    volume: 40,
    scenes: ALL_SCENES,
    typeLabels: TYPE_LABELS
  },

  onShow: function() {
    var self = this
    STAFF_API.getRoomStatusList().then(function(rooms) {
      var list = rooms.filter(function(r) { return r.roomId !== 'RM005' && r.roomId !== 'RM006' })
      self.setData({ rooms: list })
    })
  },

  getActiveScene: function() {
    for (var i = 0; i < ALL_SCENES.length; i++) {
      if (ALL_SCENES[i].id === this.data.activeSceneId) return ALL_SCENES[i]
    }
    return ALL_SCENES[0]
  },

  updateSceneDisplay: function() {
    var scene = this.getActiveScene()
    var name = scene.name + '模式'
    var trigger = scene.type === 'Auto' ? '自动触发' : '手动触发'
    this.setData({
      activeSceneName: name,
      activeSceneTrigger: trigger
    })
  },

  updateRoomBookable: function() {
    var room = this.data.rooms[this.data.roomIndex]
    var bookable = room ? (room.type === 'TeaRoom' || room.type === 'MeetingRoom') : true
    this.setData({ roomBookable: bookable })
  },

  showRoomPicker: function() {
    this.setData({ showRoomPicker: true })
  },

  hideRoomPicker: function() {
    this.setData({ showRoomPicker: false })
  },

  selectRoom: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    var room = this.data.rooms[idx]
    this.setData({
      roomIndex: idx,
      roomName: room ? room.name : '大茶室C',
      showRoomPicker: false,
      activeSceneId: 'Welcome',
      isManualOverride: false
    })
    this.applySceneParams('Welcome')
    this.updateSceneDisplay()
    this.updateRoomBookable()
  },

  triggerScene: function(e) {
    var sceneId = e.currentTarget.dataset.id
    var room = this.data.rooms[this.data.roomIndex]
    var isBookable = room ? (room.type === 'TeaRoom' || room.type === 'MeetingRoom') : true

    if (!isBookable && sceneId !== 'EnergySave') {
      wx.showToast({ title: '该空间仅支持节能模式', icon: 'none' })
      return
    }

    if (sceneId === this.data.activeSceneId) {
      wx.showToast({ title: '已是当前场景', icon: 'none' })
      return
    }

    var curScene = this.getActiveScene()
    var targetScene = null
    for (var i = 0; i < ALL_SCENES.length; i++) {
      if (ALL_SCENES[i].id === sceneId) { targetScene = ALL_SCENES[i]; break }
    }
    if (!targetScene) return

    var willOverride = curScene.type === 'Auto'
    this.setData({
      showConfirm: true,
      pendingSceneId: sceneId,
      confirmTitle: '切换到「' + targetScene.name + '」模式？',
      confirmDesc: willOverride
        ? '将覆盖「' + curScene.name + '」自动场景，自动触发将被抑制'
        : '将向「' + room.name + '」下发场景指令'
    })
  },

  confirmScene: function() {
    var sceneId = this.data.pendingSceneId
    if (!sceneId) return
    var prevScene = this.getActiveScene()

    this.setData({
      isManualOverride: prevScene.type === 'Auto' ? true : this.data.isManualOverride,
      activeSceneId: sceneId,
      showConfirm: false,
      pendingSceneId: null
    })

    this.applySceneParams(sceneId)
    this.updateSceneDisplay()

    var scene = this.getActiveScene()
    wx.showToast({ title: '「' + scene.name + '」场景已激活', icon: 'none' })

    var room = this.data.rooms[this.data.roomIndex]
    if (room) API.executeScene(room.roomId, sceneId)
  },

  hideConfirm: function() {
    this.setData({ showConfirm: false, pendingSceneId: null })
  },

  applySceneParams: function(sceneId) {
    for (var i = 0; i < ALL_SCENES.length; i++) {
      if (ALL_SCENES[i].id === sceneId) {
        var p = ALL_SCENES[i].params
        this.setData({
          temperature: p.temperature,
          colorTemp: p.colorTemp,
          volume: p.volume
        })
        break
      }
    }
  },

  onTempChange: function(e) {
    this.setData({ temperature: parseInt(e.currentTarget.dataset.temp) })
  },

  onColorTempChange: function(e) {
    this.setData({ colorTemp: parseInt(e.currentTarget.dataset.temp) })
  },

  onVolumeChange: function(e) {
    this.setData({ volume: e.detail.value })
  },

  saveParams: function() {
    var d = this.data
    for (var i = 0; i < ALL_SCENES.length; i++) {
      if (ALL_SCENES[i].id === d.activeSceneId) {
        ALL_SCENES[i].params.temperature = d.temperature
        ALL_SCENES[i].params.colorTemp = d.colorTemp
        ALL_SCENES[i].params.volume = d.volume
        break
      }
    }
    wx.showToast({ title: '场景默认参数已保存', icon: 'success' })
  },

  resetParams: function() {
    var defaults = {
      Welcome: { temperature: 24, colorTemp: 3500, volume: 30 },
      TeaSession: { temperature: 24, colorTemp: 3000, volume: 40 },
      Meeting: { temperature: 24, colorTemp: 4000, volume: 0 },
      Karaoke: { temperature: 24, colorTemp: 3500, volume: 80 },
      EnergySave: { temperature: 26, colorTemp: 2700, volume: 0 },
      PreOpen: { temperature: 24, colorTemp: 3000, volume: 20 },
      Cleanup: { temperature: 26, colorTemp: 2700, volume: 0 }
    }
    var def = defaults[this.data.activeSceneId]
    if (def) {
      this.setData({
        temperature: def.temperature,
        colorTemp: def.colorTemp,
        volume: def.volume
      })
      for (var i = 0; i < ALL_SCENES.length; i++) {
        if (ALL_SCENES[i].id === this.data.activeSceneId) {
          ALL_SCENES[i].params = { temperature: def.temperature, colorTemp: def.colorTemp, volume: def.volume }
          break
        }
      }
    }
    wx.showToast({ title: '已恢复系统默认参数', icon: 'none' })
  }
})
