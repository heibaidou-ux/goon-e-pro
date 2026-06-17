var STAFF_API = require('../../../utils/staff-api')

Page({
  data: {
    checkedIn: false, checkedOut: false, todayStatus: '未打卡',
    checkInTime: '', checkOutTime: '', workHours: 0,
    records: [], weekRecords: [],
    queryType: 'week', queryValue: ''
  },

  onShow: function() { this.loadAttendance() },

  loadAttendance: function() {
    var self = this
    STAFF_API.getAttendance().then(function(a) {
      self.setData({
        checkedIn: a.checkedIn, checkInTime: a.checkInTime,
        checkedOut: !!a.checkOutTime, checkOutTime: a.checkOutTime || '',
        todayStatus: a.checkedOut ? '已签退' : (a.checkedIn ? '在岗' : '未打卡'),
        workHours: a.workHours || 0,
        records: a.records || []
      })
    })
  },

  doCheckIn: function() {
    var self = this
    STAFF_API.checkIn().then(function(r) {
      self.setData({ checkedIn: true, checkedOut: false, todayStatus: '在岗', checkInTime: r.time })
      wx.showToast({ title: '✅ 签到成功 ' + r.time, icon: 'none' })
      self.loadAttendance()
    })
  },

  doCheckOut: function() {
    var self = this
    if (!this.data.checkedIn) return
    STAFF_API.checkOut().then(function(r) {
      self.setData({ checkedOut: true, todayStatus: '已签退', checkOutTime: r.time })
      wx.showToast({ title: '🏁 签退成功 ' + r.time, icon: 'none' })
      self.loadAttendance()
    })
  },

  switchQuery: function(e) {
    var type = e.currentTarget.dataset.type
    this.setData({ queryType: type })
    if (type === 'week') this.setData({ weekRecords: this.data.records.slice(0, 7) })
    else if (type === 'month') this.setData({ weekRecords: this.data.records.slice(0, 30) })
    else this.setData({ weekRecords: this.data.records })
  }
}