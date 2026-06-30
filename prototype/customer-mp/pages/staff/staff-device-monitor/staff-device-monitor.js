const STAFF_API = require('../../../utils/staff-api')
var API = require('../../../utils/api')
var ROOM_IDS = ['']
var ROOM_NAMES = ['全部房间']

Page({
  data: {
    rooms: [], devices: [], stats: { total: 0, online: 0, rate: '0%' },
    selectedRoomId: '', selectedRoomName: '全部房间'
  },

  onLoad: function() {
    var self = this
    API.getRooms(true).then(function(list) {
      if (list && list.length > 0) {
        var tabs = [{id:'', name:'全部房间'}]
        ROOM_IDS = ['']
        ROOM_NAMES = ['全部房间']
        for (var i = 0; i < list.length; i++) {
          ROOM_IDS.push(list[i].roomId)
          ROOM_NAMES.push(list[i].name)
          tabs.push({id:list[i].roomId, name:list[i].name})
        }
        self.setData({ roomTabs: tabs })
      }
    }).catch(function() {})
  },

  onShow() {
    var self = this
    Promise.all([STAFF_API.getRoomStatusList(), STAFF_API.getDeviceList(), STAFF_API.getDeviceStats()]).then(function(results) {
      var rooms = results[0] || [], devices = results[1] || [], stats = results[2] || {}
      var roomMap = {}
      for (var i = 0; i < rooms.length; i++) roomMap[rooms[i].roomId] = rooms[i].name
      devices = self._enrichDeviceNames(devices, roomMap)
      self.setData({ rooms: rooms, devices: devices, stats: stats })
    })
  },

  _enrichDeviceNames: function(devices, roomMap) {
    var labels = { Lock:'门锁', AC:'空调', Light:'灯光', Curtain:'窗帘', Speaker:'音响', Fan:'风扇', BGM:'音响' }
    var icons = { Lock:'🔒', AC:'❄️', Light:'💡', Curtain:'🪟', Speaker:'🔊', Fan:'🌀', BGM:'🎵' }
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i]
      var roomName = roomMap[d.roomId] || ''
      d.typeLabel = (roomName ? roomName + ' ' : '') + (labels[d.type] || d.type)
      d.typeIcon = icons[d.type] || '📡'
    }
    return devices
  },

  selectRoom: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    var self = this
    var roomId = ROOM_IDS[idx]
    var roomName = ROOM_NAMES[idx]
    self.setData({ selectedRoomId: roomId, selectedRoomName: roomName })
    var tabs = self.data.roomTabs || [{id:'',name:'全部房间'}]
    if (idx < tabs.length) self.setData({ selectedRoomId: tabs[idx].id, selectedRoomName: tabs[idx].name })

    if (!roomId) {
      STAFF_API.getDeviceList().then(function(devices) {
        var roomMap = {}
        for (var i = 0; i < self.data.rooms.length; i++) roomMap[self.data.rooms[i].roomId] = self.data.rooms[i].name
        devices = self._enrichDeviceNames(devices, roomMap)
        self.setData({ devices: devices })
      })
    } else {
      STAFF_API.getDeviceList(roomId).then(function(devices) {
        var roomMap = {}; roomMap[roomId] = roomName
        devices = self._enrichDeviceNames(devices, roomMap)
        self.setData({ devices: devices })
      })
    }
  }
})
