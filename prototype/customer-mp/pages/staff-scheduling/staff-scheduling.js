var STAFF_API = require('../../utils/staff-api')

Page({
  data: {
    dayLabels: ['一','二','三','四','五','六','日'],
    weekOffset: 0,
    schedule: { weekStart: '', weekEnd: '', staff: [] }
  },

  onShow: function() {
    this.loadSchedule(0)
  },

  loadSchedule: function(offset) {
    var self = this
    STAFF_API.getSchedule(offset).then(function(s) {
      self.setData({ schedule: s, weekOffset: offset })
    })
  },

  prevWeek: function() {
    this.loadSchedule(this.data.weekOffset - 1)
  },

  nextWeek: function() {
    this.loadSchedule(this.data.weekOffset + 1)
  },

  goBack: function() { wx.navigateBack() }
})
