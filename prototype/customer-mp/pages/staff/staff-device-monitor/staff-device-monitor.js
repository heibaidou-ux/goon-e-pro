const STAFF_API = require('../../../utils/staff-api')
const API = require('../../../utils/api')
Page({
  data: {
    rooms: [], devices: [], stats: { total: 0, online: 0, rate: '0%' },
    selectedRoomId: '', selectedRoomName: '全部房间', roomOptions: ['全部房间'],
    showRoomPicker: false
  },

  onShow() {
    var self = this
    Promise.all([STAFF_API.getRoomStatusList(), STAFF_API.getDeviceList(), STAFF_API.getDeviceStats()]).then(function(results) {
      var rooms = results[0] || [], devices = results[1] || [], stats = results[2] || {}
      var names = rooms.map(function(r) { return r.name })
      // 构建房间名称到ID的映射
      var roomMap = {}
      for (var i = 0; i < rooms.length; i++) roomMap[rooms[i].name] = rooms[i].roomId
      // 给设备加上房间名
      devices = self._enrichDeviceNames(devices, roomMap)
      self.setData({ rooms: rooms, devices: devices, stats: stats, roomOptions: ['全部房间'].concat(names) })
    })
  },

  _enrichDeviceNames: function(devices, roomMap) {
    var labels = { Lock:'门锁', AC:'空调', Light:'灯光', Curtain:'窗帘', Speaker:'音响', Fan:'风扇', BGM:'音响' }
    var icons = { Lock:'🔒', AC:'❄️', Light:'💡', Curtain:'🪟', Speaker:'🔊', Fan:'🌀', BGM:'🎵' }
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i]
      var roomName = ''
      for (var r in roomMap) { if (roomMap[r] === d.roomId) { roomName = r; break } }
      d.typeLabel = (roomName ? roomName + ' ' : '') + (labels[d.type] || d.type)
      d.typeIcon = icons[d.type] || '📡'
    }
    return devices
  },

  // ── 居中房间选择弹窗 ──
  showRoomPicker: function() { this.setData({ showRoomPicker: true }) },
  hideRoomPicker: function() { this.setData({ showRoomPicker: false }) },

  selectRoom: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    var self = this
    this.setData({ showRoomPicker: false })
    var name = this.data.roomOptions[idx]
    if (idx === 0) {
      STAFF_API.getDeviceList().then(function(devices) {
        var roomMap = {}
        for (var i = 0; i < self.data.rooms.length; i++) roomMap[self.data.rooms[i].name] = self.data.rooms[i].roomId
        devices = self._enrichDeviceNames(devices, roomMap)
        self.setData({ devices: devices, selectedRoomId: '', selectedRoomName: name })
      })
    } else {
      var room = self.data.rooms[idx - 1]
      STAFF_API.getDeviceList(room.roomId).then(function(devices) {
        var roomMap = {}; roomMap[room.name] = room.roomId
        devices = self._enrichDeviceNames(devices, roomMap)
        self.setData({ devices: devices, selectedRoomId: room.roomId, selectedRoomName: name })
      })
    }
  }
})
