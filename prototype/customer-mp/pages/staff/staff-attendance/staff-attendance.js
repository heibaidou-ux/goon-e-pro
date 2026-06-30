var STAFF_API = require('../utils/staff-api')

Page({
  data: {
    checkedIn: false, checkedOut: false, todayStatus: '未打卡',
    checkInTime: '', checkOutTime: '', workHours: 0,
    records: [], displayRecords: [],
    queryType: 'week'
  },

  onShow: function() {
    this.loadAttendance()
  },

  loadAttendance: function() {
    var self = this
    STAFF_API.getAttendance().then(function(a) {
      var checkedOut = !!a.checkOutTime && a.checkOutTime.length > 0
      var checkedIn = a.checkedIn || (!checkedOut && a.checkInTime && a.checkInTime !== '—')
      self.setData({
        checkedIn: checkedIn,
        checkedOut: checkedOut,
        checkInTime: a.checkInTime || '',
        checkOutTime: a.checkOutTime || '',
        todayStatus: checkedOut ? '已签退' : (checkedIn ? '在岗' : '未打卡'),
        workHours: a.workHours || 0,
        records: a.records || []
      })
      // 默认显示本周
      self.switchQuery({ currentTarget: { dataset: { type: 'week' } } })
    })
  },

  doCheckIn: function() {
    var self = this
    STAFF_API.checkIn().then(function(r) {
      self.setData({ checkedIn: true, checkedOut: false, todayStatus: '在岗', checkInTime: r.time })
      wx.showToast({ title: '签到成功 ' + r.time, icon: 'none' })
      self.loadAttendance()
    })
  },

  doCheckOut: function() {
    var self = this
    if (!this.data.checkedIn) return
    STAFF_API.checkOut().then(function(r) {
      self.setData({ checkedOut: true, todayStatus: '已签退', checkOutTime: r.time })
      wx.showToast({ title: '签退成功 ' + r.time, icon: 'none' })
      self.loadAttendance()
    })
  },

  switchQuery: function(e) {
    var self = this
    var type = e.currentTarget.dataset.type
    self.setData({ queryType: type })
    // 从API重新获取最新记录（含签到后的新数据）
    STAFF_API.getAttendance().then(function(a) {
      var records = a.records || []
      var filtered = []
      var now = new Date()
      var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')

      if (type === 'week') {
        var weekAgo = new Date(now)
        weekAgo.setDate(now.getDate() - 7)
        var weekStart = weekAgo.getFullYear()+'-'+String(weekAgo.getMonth()+1).padStart(2,'0')+'-'+String(weekAgo.getDate()).padStart(2,'0')
        for (var i = 0; i < records.length; i++) {
          if (records[i].date >= weekStart && records[i].date <= todayStr) {
            filtered.push(records[i])
          }
        }
      } else if (type === 'month') {
        var monthAgo = new Date(now)
        monthAgo.setDate(now.getDate() - 30)
        var monthStart = monthAgo.getFullYear()+'-'+String(monthAgo.getMonth()+1).padStart(2,'0')+'-'+String(monthAgo.getDate()).padStart(2,'0')
        for (var i = 0; i < records.length; i++) {
          if (records[i].date >= monthStart && records[i].date <= todayStr) {
            filtered.push(records[i])
          }
        }
      } else {
        filtered = records.slice()
      }

      if (filtered.length > 60) filtered = filtered.slice(0, 60)
      self.setData({ displayRecords: filtered })
    })
  }
})
