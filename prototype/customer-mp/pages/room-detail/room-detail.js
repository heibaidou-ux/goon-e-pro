var API = require('../../utils/api')

var ROOMS_DATA = [
  { roomId:"RM004", name:"大茶室C", type:"茶室", capacity:6, area:25, facilities:["茶台","K歌","投影","落地窗"], pricePerHour:120, bookable:true },
  { roomId:"RM001", name:"大会议室", type:"会议室", capacity:10, area:30, facilities:["投影","会议桌","K歌设备","落地窗"], pricePerHour:200, bookable:true },
  { roomId:"RM002", name:"中茶室A", type:"茶室", capacity:4, area:18, facilities:["茶台","落地窗","茶具套装"], pricePerHour:80, bookable:true },
  { roomId:"RM003", name:"中茶室B", type:"茶室", capacity:4, area:18, facilities:["茶台","落地窗","茶具套装"], pricePerHour:80, bookable:true },
  { roomId:"RM005", name:"展厅", type:"展厅", capacity:20, area:40, facilities:["前台","收银","茶具展示","休闲区"], bookable:false },
  { roomId:"RM006", name:"工作间", type:"工作间", capacity:2, area:12, facilities:["储物","机柜"], bookable:false },
]

var GRAD_MAP = { '茶室':'gradient-tea', '会议室':'gradient-meeting', '展厅':'gradient-exhibition', '工作间':'gradient-workshop' }
var HERO_MAP = { '茶室':'🍵', '会议室':'💼', '展厅':'🏛️', '工作间':'🔧' }

Page({
  data: {
    room: {}, roomId: '', hourRate: 0, heroIcon: '🏠', gradClass: 'gradient-tea', bookable: true,
    today: new Date(), selectedDate: null, dateChips: [], weekNames: ['日','一','二','三','四','五','六'],
    selectedDuration: null, isCustomMode: false, customHours: '', showTimeRow: false,
    timeOptions: [], selectedTimeLabel: '', selectedTimeValue: '', selectedStart: null, selectedEnd: null,
    canBook: false, totalPrice: 0, totalDetail: '请选择时长',
    conflictMsg: '', suggestTime: '',
    showCalModal: false, calYear: 0, calMonth: 0, calDays: [],
    // 真实订单列表（用于冲突检测）
    existingOrders: []
  },

  onLoad: function(e) {
    var roomId = e.roomId || e.id || 'RM004'
    var room = null
    for (var i = 0; i < ROOMS_DATA.length; i++) { if (ROOMS_DATA[i].roomId === roomId) { room = ROOMS_DATA[i]; break } }
    if (!room) room = ROOMS_DATA[0]

    var now = new Date()
    var todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    this.setData({
      room: room, roomId: room.roomId, hourRate: room.pricePerHour || 120,
      heroIcon: HERO_MAP[room.type] || '🏠', gradClass: GRAD_MAP[room.type] || 'gradient-tea',
      bookable: room.bookable !== false, today: now, selectedDate: todayStart,
      calYear: now.getFullYear(), calMonth: now.getMonth()
    })
    this.renderDateBar()

    // 加载真实订单用于冲突检测
    var self = this
    API.getUserOrders().then(function(orders) { self.setData({ existingOrders: orders || [] }) })
  },

  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },

  renderDateBar: function() {
    var chips = [], selected = this.data.selectedDate, today = this.data.today, weekNames = ['日','一','二','三','四','五','六']
    for (var i = 0; i < 5; i++) {
      var d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i)
      chips.push({ week: '周' + weekNames[d.getDay()], day: d.getDate(), month: d.getMonth() + 1, date: d, isToday: d.toDateString() === today.toDateString(), isSelected: d.toDateString() === selected.toDateString(), ts: d.getTime() })
    }
    this.setData({ dateChips: chips })
  },

  pickDate: function(e) {
    var idx = e.currentTarget.dataset.index, chip = this.data.dateChips[idx]
    if (!chip) return
    this.setData({ selectedDate: new Date(chip.ts) })
    this.resetSelection()
    this.renderDateBar()
  },

  pickDuration: function(e) {
    var dur = parseInt(e.currentTarget.dataset.dur)
    this.setData({ selectedDuration: dur, isCustomMode: false, customHours: '', showTimeRow: true, selectedStart: null, selectedEnd: null, conflictMsg: '', suggestTime: '' })
    this.populateTimeOptions()
    this.updateBilling()
  },

  pickCustomDuration: function() { this.setData({ selectedDuration: null, isCustomMode: true, customHours: '', showTimeRow: false, selectedStart: null, selectedEnd: null, conflictMsg: '', suggestTime: '' }); this.updateBilling() },

  onCustomHoursInput: function(e) {
    var val = e.detail.value, hours = parseFloat(val)
    this.setData({ customHours: val })
    if (!hours || hours < 0.5) { this.setData({ selectedDuration: null, showTimeRow: false }); this.updateBilling(); return }
    hours = Math.min(hours, 24)
    this.setData({ selectedDuration: Math.round(hours * 60), showTimeRow: true })
    this.populateTimeOptions()
    this.updateBilling()
  },

  // 时间段选择 — 过滤已过时段 + 冲突检测
  populateTimeOptions: function() {
    var selectedDate = this.data.selectedDate, today = this.data.today
    var isToday = selectedDate.toDateString() === today.toDateString()
    var curMin = isToday ? today.getHours() * 60 + today.getMinutes() : 0
    var startMin = Math.ceil(curMin / 30) * 30
    var duration = this.data.selectedDuration, roomId = this.data.roomId
    if (!duration) return

    var dateStr = selectedDate.getFullYear() + '-' + String(selectedDate.getMonth()+1).padStart(2,'0') + '-' + String(selectedDate.getDate()).padStart(2,'0')
    var options = []

    for (var m = startMin; m < 24 * 60 + 6 * 60; m += 30) {
      var minInDay = m % (24 * 60), h = Math.floor(minInDay / 60), min = minInDay % 60
      var timeStr = String(h).padStart(2,'0') + ':' + String(min).padStart(2,'0')
      var eMin = m + duration
      // 检查真实订单冲突
      if (!this.isTimeBlocked(m, eMin, roomId, dateStr)) {
        options.push(timeStr)
      }
    }
    this.setData({ timeOptions: options, selectedTimeLabel: '', selectedTimeValue: '' })
  },

  pickTimeFromSelect: function(e) {
    var idx = e.detail.value, options = this.data.timeOptions
    if (idx < 0 || idx >= options.length) return
    var timeStr = options[idx]
    if (!timeStr || !this.data.selectedDuration) return
    var sp = timeStr.split(':'), sMin = parseInt(sp[0]) * 60 + parseInt(sp[1]), eMin = sMin + this.data.selectedDuration
    var dateStr = this.data.selectedDate.getFullYear() + '-' + String(this.data.selectedDate.getMonth()+1).padStart(2,'0') + '-' + String(this.data.selectedDate.getDate()).padStart(2,'0')

    if (this.isTimeBlocked(sMin, eMin, this.data.roomId, dateStr)) { this.showConflictSuggestion(sMin, this.data.selectedDuration, dateStr); return }

    var endH = Math.floor(eMin / 60) % 24, endM = eMin % 60
    this.setData({ selectedStart: timeStr, selectedEnd: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0'), selectedTimeLabel: timeStr, conflictMsg: '', suggestTime: '' })
    this.updateBilling()
  },

  pickNow: function() {
    if (!this.data.selectedDuration) { wx.showToast({ title: '请先选择时长', icon: 'none' }); return }
    var now = new Date(), curMin = now.getHours() * 60 + now.getMinutes(), duration = this.data.selectedDuration, eMin = curMin + duration
    var dateStr = this.data.selectedDate.getFullYear() + '-' + String(this.data.selectedDate.getMonth()+1).padStart(2,'0') + '-' + String(this.data.selectedDate.getDate()).padStart(2,'0')

    if (this.isTimeBlocked(curMin, eMin, this.data.roomId, dateStr)) { this.showConflictSuggestion(curMin, duration, dateStr); return }

    var startH = Math.floor(curMin / 60), startM = curMin % 60, endH = Math.floor(eMin / 60) % 24, endM = eMin % 60
    this.setData({ selectedStart: String(startH).padStart(2,'0') + ':' + String(startM).padStart(2,'0'), selectedEnd: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0'), selectedTimeLabel: '现在开始', conflictMsg: '', suggestTime: '' })
    this.updateBilling()
  },

  // 冲突检测：从真实订单+硬编码数据获取已预订时段
  isTimeBlocked: function(checkStart, checkEnd, roomId, dateStr) {
    var orders = this.data.existingOrders
    for (var i = 0; i < orders.length; i++) {
      var o = orders[i]
      if (o.roomId !== roomId && o.roomName !== this.data.room.name) continue
      if (o.status === 'Cancelled' || o.status === 'Completed') continue
      if (o.date !== dateStr) continue
      var parts = (o.time || '').split('-')
      if (parts.length < 2) continue
      var sp = parts[0].split(':'), ep = parts[1].split(':')
      var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1]), eMin = parseInt(ep[0]) * 60 + parseInt(ep[1])
      if (checkStart < eMin + 15 && checkEnd > sMin) return true
    }
    return false
  },

  showConflictSuggestion: function(checkMin, duration, dateStr) {
    var found = -1
    for (var m = checkMin + 30; m < 24 * 60; m += 30) { if (!this.isTimeBlocked(m, m + duration, this.data.roomId, dateStr)) { found = m; break } }
    if (found >= 0) { var h = Math.floor(found / 60) % 24, min = found % 60; this.setData({ conflictMsg: '该时段已被预约', suggestTime: String(h).padStart(2,'0') + ':' + String(min).padStart(2,'0') }) }
    else { this.setData({ conflictMsg: '该时段已被预约，请选择其他日期', suggestTime: '' }) }
  },

  applySuggested: function() { /* 用户手动选择 */ },

  updateBilling: function() {
    var price = 0, detail = '', canBook = false
    if (this.data.selectedDuration && this.data.selectedStart && this.data.selectedEnd) {
      var sp = this.data.selectedStart.split(':'), ep = this.data.selectedEnd.split(':')
      var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1]), eMin = parseInt(ep[0]) * 60 + parseInt(ep[1])
      if (eMin <= sMin) eMin += 24 * 60
      price = Math.round(this.data.hourRate * (eMin - sMin) / 60)
      detail = this.data.selectedStart + '-' + this.data.selectedEnd + ' · ' + Math.floor((eMin - sMin) / 60) + '小时'
      canBook = true
    } else if (this.data.selectedDuration) { detail = '请选择开始时间' } else { detail = '请选择时长' }
    this.setData({ totalPrice: price, totalDetail: detail, canBook: canBook })
  },

  showCalModal: function() { this.renderCalendar(); this.setData({ showCalModal: true }) },
  hideCalModal: function() { this.setData({ showCalModal: false }) },
  calChangeMonth: function(e) {
    var dir = parseInt(e.currentTarget.dataset.dir), year = this.data.calYear, month = this.data.calMonth + dir
    if (month < 0) { month = 11; year-- }; if (month > 11) { month = 0; year++ }
    this.setData({ calYear: year, calMonth: month }); this.renderCalendar()
  },
  renderCalendar: function() {
    var year = this.data.calYear, month = this.data.calMonth, firstDay = new Date(year, month, 1).getDay(), daysInMonth = new Date(year, month + 1, 0).getDate(), daysInPrev = new Date(year, month, 0).getDate()
    var today = this.data.today, selectedDate = this.data.selectedDate, maxDate = new Date(today); maxDate.setDate(today.getDate() + 90)
    var days = []
    for (var i = firstDay - 1; i >= 0; i--) { days.push({ day: daysInPrev - i, isEmpty: true, isOther: true }) }
    for (var d = 1; d <= daysInMonth; d++) {
      var dt = new Date(year, month, d), isToday = dt.toDateString() === today.toDateString(), isPast = dt < new Date(today.getFullYear(), today.getMonth(), today.getDate()), isTooFar = dt > maxDate, isSelected = dt.toDateString() === selectedDate.toDateString()
      days.push({ day: d, month: month, year: year, isToday: isToday, isSelected: isSelected, isPast: isPast || isTooFar, isEmpty: false })
    }
    var remaining = 42 - firstDay - daysInMonth
    for (var d = 1; d <= remaining; d++) { days.push({ day: d, isEmpty: true, isOther: true }) }
    this.setData({ calDays: days })
  },
  calPick: function(e) {
    var dataset = e.currentTarget.dataset; if (dataset.past === 'true') return
    this.setData({ selectedDate: new Date(parseInt(dataset.year), parseInt(dataset.month), parseInt(dataset.day)) })
    this.resetSelection(); this.renderDateBar(); this.hideCalModal()
  },

  resetSelection: function() { this.setData({ selectedDuration: null, isCustomMode: false, customHours: '', showTimeRow: false, selectedStart: null, selectedEnd: null, selectedTimeLabel: '', conflictMsg: '', suggestTime: '', canBook: false, totalPrice: 0, totalDetail: '请选择时长' }) },

  goPay: function() {
    if (!this.data.canBook) return
    var d = this.data
    var dateStr = d.selectedDate.getFullYear() + '-' + String(d.selectedDate.getMonth()+1).padStart(2,'0') + '-' + String(d.selectedDate.getDate()).padStart(2,'0')
    wx.navigateTo({ url: '/pages/booking-confirm/booking-confirm?roomId=' + d.roomId + '&roomName=' + encodeURIComponent(d.room.name) + '&date=' + dateStr + '&start=' + d.selectedStart + '&end=' + d.selectedEnd + '&total=' + d.totalPrice + '&duration=' + (parseFloat(d.selectedDuration) || 120) })
  }
})
