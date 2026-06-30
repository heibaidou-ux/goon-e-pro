var STAFF_API = require('../../../utils/staff-api')

Page({
  data: {
    dayLabels: ['一','二','三','四','五','六','日'],
    weekOffset: 0,
    schedule: { weekStart: '', weekEnd: '', staff: [] },
    showEditModal: false, editName: '', editDay: -1, editDayLabel: '', editCurShift: '', editNewShift: ''
  },

  onShow: function() { this.loadSchedule(0) },

  loadSchedule: function(offset) {
    var self = this
    STAFF_API.getSchedule(offset).then(function(s) {
      self.setData({ schedule: s, weekOffset: offset })
    })
  },

  prevWeek: function() { this.loadSchedule(this.data.weekOffset - 1) },
  nextWeek: function() { this.loadSchedule(this.data.weekOffset + 1) },

  editShift: function(e) {
    var name = e.currentTarget.dataset.name
    var day = parseInt(e.currentTarget.dataset.day)
    var shift = e.currentTarget.dataset.shift
    var dayLabels = ['周一','周二','周三','周四','周五','周六','周日']
    this.setData({
      showEditModal: true, editName: name, editDay: day,
      editDayLabel: dayLabels[day] || '',
      editCurShift: shift, editNewShift: shift
    })
  },

  setShift: function(e) {
    this.setData({ editNewShift: e.currentTarget.dataset.shift })
  },

  saveShift: function() {
    var self = this
    var name = self.data.editName, day = self.data.editDay, newShift = self.data.editNewShift
    var schedule = self.data.schedule
    
    // 验证：检查将此人改为休息后该班次是否还有人
    if (newShift === '休息') {
      var hasEarly = false, hasLate = false, hasAllDay = false
      for (var i = 0; i < schedule.staff.length; i++) {
        if (schedule.staff[i].name === name) continue
        var s = schedule.staff[i].schedule[day]
        if (s === '早班' || s === '全天') hasEarly = true
        if (s === '晚班' || s === '全天') hasLate = true
      }
      if (!hasEarly) { wx.showToast({ title: '早班至少需1人在岗', icon: 'none' }); return }
      if (!hasLate) { wx.showToast({ title: '晚班至少需1人在岗', icon: 'none' }); return }
    }
    
    for (var i = 0; i < schedule.staff.length; i++) {
      if (schedule.staff[i].name === name) { schedule.staff[i].schedule[day] = newShift; break }
    }
    self.setData({ schedule: schedule, showEditModal: false })
    STAFF_API.saveSchedule(name, day, newShift)
    wx.showToast({ title: name + ' ' + self.data.editDayLabel + ' → ' + newShift, icon: 'none' })
  },

  hideEditModal: function() { this.setData({ showEditModal: false }) },

  goBack: function() { wx.navigateBack() }
})
