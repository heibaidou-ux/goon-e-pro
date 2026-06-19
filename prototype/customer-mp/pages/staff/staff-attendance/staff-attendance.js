var STAFF_API = require('../../../utils/staff-api')

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
    var type = e.currentTarget.dataset.type
    var records = this.data.records
    // 按日期排序（由近到远）
    var filtered = []
    var now = new Date()
    var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')

    if (type === 'week') {
      // 近7天
      var weekAgo = new Date(now)
      weekAgo.setDate(now.getDate() - 7)
      for (var i = 0; i < records.length; i++) {
        if (records[i].date >= weekAgo.toISOString().slice(0,10) && records[i].date <= todayStr) {
          filtered.push(records[i])
        }
      }
    } else if (type === 'month') {
      // 近30天
      var monthAgo = new Date(now)
      monthAgo.setDate(now.getDate() - 30)
      for (var i = 0; i < records.length; i++) {
        if (records[i].date >= monthAgo.toISOString().slice(0,10) && records[i].date <= todayStr) {
          filtered.push(records[i])
        }
      }
    } else {
      // 全年（全部记录）
      filtered = records.slice()
    }

    // 限制最多显示条数避免太长
    if (filtered.length > 60) filtered = filtered.slice(0, 60)

    this.setData({ queryType: type, displayRecords: filtered })
  }
})
