var STAFF_API = require('../../utils/staff-api')

Page({
  data: {
    rooms: [],
    selectedRoom: '',
    selectedRoomName: '',
    inspectionItems: []
  },

  onShow: function() {
    var self = this
    STAFF_API.getInspectionRooms().then(function(rooms) {
      self.setData({ rooms: rooms })
      if (rooms.length) {
        self.selectRoomByData({ currentTarget: { dataset: { roomid: rooms[0].roomId } } })
      }
    })
  },

  selectRoom: function(e) {
    this.selectRoomByData(e)
  },

  selectRoomByData: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    var rooms = this.data.rooms
    for (var i = 0; i < rooms.length; i++) {
      if (rooms[i].roomId === roomId) {
        var items = (rooms[i].items || []).map(function(item) {
          return { name: item.name, ok: item.ok }
        })
        this.setData({
          selectedRoom: roomId,
          selectedRoomName: rooms[i].name,
          inspectionItems: items
        })
        break
      }
    }
  },

  toggleInspect: function(e) {
    var idx = e.currentTarget.dataset.index
    var items = this.data.inspectionItems
    if (idx >= 0 && idx < items.length) {
      items[idx].ok = !items[idx].ok
      this.setData({ inspectionItems: items })
    }
  },

  submitInspection: function() {
    var self = this
    STAFF_API.submitInspection(this.data.selectedRoom, this.data.inspectionItems).then(function() {
      wx.showToast({ title: '巡检报告已提交', icon: 'success' })
      // Reset items to default
      self.onShow()
    })
  },

  goBack: function() { wx.navigateBack() }
})
