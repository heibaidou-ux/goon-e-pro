var STAFF_API = require('../../utils/staff-api')

Page({
  data: { tabIndex:0, rooms:[], selectedRoom:'', selectedRoomName:'', inspectionItems:[], reports:[] },

  onShow: function() { this.loadRooms(); this.loadReports() },

  loadRooms: function() {
    var self = this
    STAFF_API.getInspectionRooms().then(function(rooms) {
      self.setData({ rooms: rooms })
    })
  },

  loadReports: function() {
    var self = this
    STAFF_API.getInspectionReports().then(function(reports) { self.setData({ reports: reports }) })
  },

  switchTab: function(e) {
    this.setData({ tabIndex: parseInt(e.currentTarget.dataset.tab) })
    if (e.currentTarget.dataset.tab == '1') this.loadReports()
  },

  selectRoom: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    var rooms = this.data.rooms
    for (var i = 0; i < rooms.length; i++) {
      if (rooms[i].roomId === roomId) {
        this.setData({ selectedRoom: roomId, selectedRoomName: rooms[i].name, inspectionItems: rooms[i].items.map(function(item) { return { name: item.name, ok: item.ok } }) })
        break
      }
    }
  },

  toggleInspect: function(e) {
    var idx = e.currentTarget.dataset.index
    var items = this.data.inspectionItems
    if (idx >= 0 && idx < items.length) { items[idx].ok = !items[idx].ok; this.setData({ inspectionItems: items }) }
  },

  submitInspection: function() {
    var self = this
    STAFF_API.submitInspection(self.data.selectedRoom, self.data.inspectionItems).then(function(res) {
      wx.showToast({ title: res.message || '已提交', icon: 'success' })
      self.setData({ selectedRoom: '', selectedRoomName: '', inspectionItems: [] })
      self.loadRooms()
      self.loadReports()
    })
  },

  confirmReport: function(e) {
    var self = this
    STAFF_API.confirmInspectionReport(e.currentTarget.dataset.id).then(function() {
      wx.showToast({ title: '已复核', icon: 'success' })
      self.loadReports()
    })
  },

  cancelInspect: function() {
    this.setData({ selectedRoom: '', selectedRoomName: '', inspectionItems: [] })
  }
})
