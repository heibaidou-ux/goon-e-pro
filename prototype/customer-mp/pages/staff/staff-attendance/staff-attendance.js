var STAFF_API = require('../../../utils/staff-api')

Page({
  data: { attendance: { checkedIn: false, checkInTime: '—', checkOutTime: '—', todayStatus: '未打卡', workHours: 0, records: [] } },

  onShow: function() {
    this.loadData()
  },

  loadData: function() {
    var self = this
    STAFF_API.getAttendance().then(function(d) { self.setData({ attendance: d }) })
  },

  doCheckIn: function() {
    var self = this
    STAFF_API.checkIn().then(function(res) {
      wx.showToast({ title: '签到成功 ' + res.time, icon: 'success' })
      self.loadData()
    })
  },

  doCheckOut: function() {
    var self = this
    STAFF_API.checkOut().then(function(res) {
      wx.showToast({ title: '签退成功 ' + res.time, icon: 'success' })
      self.loadData()
    })
  },

  goBack: function() { wx.navigateBack() }
})
