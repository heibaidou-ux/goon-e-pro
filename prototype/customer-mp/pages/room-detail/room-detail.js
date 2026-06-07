var API = require('../../utils/api')

// Room data
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

var EXISTING_BOOKINGS = {
  RM004: [{ date:'2026-05-10', start:'08:00', end:'10:00' }, { date:'2026-05-10', start:'14:00', end:'16:00' }],
  RM001: [{ date:'2026-05-10', start:'09:00', end:'12:00' }],
  RM002: [{ date:'2026-05-10', start:'10:00', end:'12:30' }],
  RM003: [], RM005: [], RM006: []
}

Page({
  data: {
    room: {},
    roomId: '',
    hourRate: 0,
    heroIcon: '🏠',
    gradClass: 'gradient-tea',
    bookable: true,

    // Date
    today: new Date(),
    selectedDate: new Date(),
    dateChips: [],
    weekNames: ['日','一','二','三','四','五','六'],

    // Duration
    selectedDuration: null,
    isCustomMode: false,
    customHours: '',
    showTimeRow: false,

    // Time
    timeOptions: ['请先选择时长'],
    selectedTimeLabel: '',
    selectedTimeValue: '',
    selectedStart: null,
    selectedEnd: null,
    canBook: false,
    totalPrice: 0,
    totalDetail: '请选择时长',

    // Conflict
    conflictMsg: '',
    suggestTime: '',

    // Calendar
    showCalModal: false,
    calYear: 0,
    calMonth: 0,
    calDays: []
  },

  onLoad: function(e) {
    var roomId = e.roomId || e.id || 'RM004'
    var room = null
    for (var i = 0; i < ROOMS_DATA.length; i++) {
      if (ROOMS_DATA[i].roomId === roomId) { room = ROOMS_DATA[i]; break }
    }
    if (!room) room = ROOMS_DATA[0]

    var now = new Date()
    this.setData({
      room: room,
      roomId: room.roomId,
      hourRate: room.pricePerHour || 120,
      heroIcon: HERO_MAP[room.type] || '🏠',
      gradClass: GRAD_MAP[room.type] || 'gradient-tea',
      bookable: room.bookable !== false,
      today: now,
      selectedDate: new Date(now.getFullYear(), now.getMonth(), now.getDate()),
      calYear: now.getFullYear(),
      calMonth: now.getMonth()
    })

    this.renderDateBar()
  },

  // ── Navigation ──
  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },

  // ── Date bar ──
  renderDateBar: function() {
    var chips = []
    var selected = this.data.selectedDate
    var today = this.data.today
    var weekNames = ['日','一','二','三','四','五','六']

    // 显示5天填满屏幕宽度
    for (var i = 0; i < 5; i++) {
      var d = new Date(today.getFullYear(), today.getMonth(), today.getDate() + i)
      var isToday = d.toDateString() === today.toDateString()
      var isSelected = d.toDateString() === selected.toDateString()
      chips.push({
        week: '周' + weekNames[d.getDay()],
        day: d.getDate(),
        month: d.getMonth() + 1,
        date: d,
        isToday: isToday,
        isSelected: isSelected,
        ts: d.getTime()
      })
    }
    this.setData({ dateChips: chips })
  },

  pickDate: function(e) {
    var idx = e.currentTarget.dataset.index
    var chip = this.data.dateChips[idx]
    if (!chip) return
    this.setData({ selectedDate: new Date(chip.ts) })
    this.resetSelection()
    this.renderDateBar()
  },

  // ── Duration ──
  pickDuration: function(e) {
    var dur = parseInt(e.currentTarget.dataset.dur)
    this.setData({
      selectedDuration: dur,
      isCustomMode: false,
      customHours: '',
      showTimeRow: true,
      selectedStart: null,
      selectedEnd: null,
      conflictMsg: '',
      suggestTime: ''
    })
    this.populateTimeOptions()
    this.updateBilling()
  },

  pickCustomDuration: function() {
    this.setData({
      selectedDuration: null,
      isCustomMode: true,
      customHours: '',
      showTimeRow: false,
      selectedStart: null,
      selectedEnd: null,
      conflictMsg: '',
      suggestTime: ''
    })
    this.updateBilling()
  },

  onCustomHoursInput: function(e) {
    var val = e.detail.value
    var hours = parseFloat(val)
    this.setData({ customHours: val })
    if (!hours || hours < 0.5) {
      this.setData({ selectedDuration: null, showTimeRow: false })
      this.updateBilling()
      return
    }
    hours = Math.min(hours, 24)
    this.setData({ selectedDuration: Math.round(hours * 60), showTimeRow: true })
    this.populateTimeOptions()
    this.updateBilling()
  },

  // ── Time selection ──
  populateTimeOptions: function() {
    var selectedDate = this.data.selectedDate
    var today = this.data.today
    var isToday = selectedDate.toDateString() === today.toDateString()
    var curMin = isToday ? today.getHours() * 60 + today.getMinutes() : 0
    var startMin = Math.ceil(curMin / 30) * 30
    var duration = this.data.selectedDuration
    var roomId = this.data.roomId
    if (!duration) return

    var dateStr = selectedDate.getFullYear() + '-' + String(selectedDate.getMonth()+1).padStart(2,'0') + '-' + String(selectedDate.getDate()).padStart(2,'0')
    var options = []
    var maxMin = 24 * 60 + 6 * 60

    for (var m = startMin; m < maxMin; m += 30) {
      var minInDay = m % (24 * 60)
      var h = Math.floor(minInDay / 60)
      var min = minInDay % 60
      var timeStr = String(h).padStart(2,'0') + ':' + String(min).padStart(2,'0')
      var eMin = m + duration
      if (!this.isTimeBlocked(m, eMin, roomId, dateStr)) {
        options.push(timeStr)
      }
    }
    this.setData({ timeOptions: options, selectedTimeLabel: '', selectedTimeValue: '' })
  },

  pickTimeFromSelect: function(e) {
    var idx = e.detail.value
    var options = this.data.timeOptions
    if (idx < 0 || idx >= options.length) return
    var timeStr = options[idx]
    if (!timeStr || !this.data.selectedDuration) return

    var sp = timeStr.split(':')
    var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
    var eMin = sMin + this.data.selectedDuration
    var dateStr = this.data.selectedDate.getFullYear() + '-' +
      String(this.data.selectedDate.getMonth()+1).padStart(2,'0') + '-' +
      String(this.data.selectedDate.getDate()).padStart(2,'0')

    if (this.isTimeBlocked(sMin, eMin, this.data.roomId, dateStr)) {
      this.showConflictSuggestion(sMin, this.data.selectedDuration, dateStr)
      return
    }

    var endH = Math.floor(eMin / 60) % 24
    var endM = eMin % 60
    this.setData({
      selectedStart: timeStr,
      selectedEnd: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0'),
      selectedTimeLabel: timeStr,
      conflictMsg: '',
      suggestTime: ''
    })
    this.updateBilling()
  },

  pickNow: function() {
    if (!this.data.selectedDuration) {
      wx.showToast({ title: '请先选择时长', icon: 'none' })
      return
    }
    var today = new Date()
    var curMin = today.getHours() * 60 + today.getMinutes()
    var duration = this.data.selectedDuration
    var eMin = curMin + duration
    var dateStr = this.data.selectedDate.getFullYear() + '-' +
      String(this.data.selectedDate.getMonth()+1).padStart(2,'0') + '-' +
      String(this.data.selectedDate.getDate()).padStart(2,'0')

    if (this.isTimeBlocked(curMin, eMin, this.data.roomId, dateStr)) {
      this.showConflictSuggestion(curMin, duration, dateStr)
      return
    }

    var startH = Math.floor(curMin / 60)
    var startM = curMin % 60
    var endH = Math.floor(eMin / 60) % 24
    var endM = eMin % 60

    this.setData({
      selectedStart: String(startH).padStart(2,'0') + ':' + String(startM).padStart(2,'0'),
      selectedEnd: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0'),
      selectedTimeLabel: '现在开始',
      conflictMsg: '',
      suggestTime: ''
    })
    this.updateBilling()
  },

  // ── Conflict detection ──
  isTimeBlocked: function(checkStart, checkEnd, roomId, dateStr) {
    var blocks = EXISTING_BOOKINGS[roomId] || []
    var filtered = blocks.filter(function(b) { return b.date === dateStr })
    for (var i = 0; i < filtered.length; i++) {
      var b = filtered[i]
      var sp = b.start.split(':'), ep = b.end.split(':')
      var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
      var eMin = parseInt(ep[0]) * 60 + parseInt(ep[1])
      var cleaningEnd = eMin + 15
      if (checkStart < cleaningEnd && checkEnd > sMin) return true
    }
    return false
  },

  showConflictSuggestion: function(checkMin, duration, dateStr) {
    var maxSearch = 24 * 60
    var found = -1
    for (var m = checkMin + 30; m < maxSearch; m += 30) {
      if (!this.isTimeBlocked(m, m + duration, this.data.roomId, dateStr)) {
        found = m; break
      }
    }
    if (found >= 0) {
      var h = Math.floor(found / 60) % 24
      var min = found % 60
      var suggestTime = String(h).padStart(2,'0') + ':' + String(min).padStart(2,'0')
      this.setData({ conflictMsg: '该时段已被预约', suggestTime: suggestTime })
    } else {
      this.setData({ conflictMsg: '该时段已被预约', suggestTime: '' })
    }
  },

  applySuggested: function() {
    var timeStr = this.data.suggestTime
    if (!timeStr) return
    this.setData({ conflictMsg: '', suggestTime: '' })
    var options = this.data.timeOptions
    for (var i = 0; i < options.length; i++) {
      if (options[i] === timeStr) {
        // trigger selection
        break
      }
    }
  },

  // ── Billing ──
  updateBilling: function() {
    var price = 0
    var detail = ''
    var canBook = false

    if (this.data.selectedDuration && this.data.selectedStart && this.data.selectedEnd) {
      var sp = this.data.selectedStart.split(':')
      var ep = this.data.selectedEnd.split(':')
      var sMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
      var eMin = parseInt(ep[0]) * 60 + parseInt(ep[1])
      if (eMin <= sMin) eMin += 24 * 60
      var dur = eMin - sMin
      price = Math.round(this.data.hourRate * dur / 60)
      detail = this.data.selectedStart + '-' + this.data.selectedEnd + ' · ' + Math.floor(dur/60) + '小时'
      canBook = true
    } else if (this.data.selectedDuration) {
      detail = '请选择开始时间'
    } else {
      detail = '请选择时长'
    }

    this.setData({
      totalPrice: price,
      totalDetail: detail,
      canBook: canBook
    })
  },

  // ── Calendar ──
  showCalModal: function() {
    this.renderCalendar()
    this.setData({ showCalModal: true })
  },

  hideCalModal: function() {
    this.setData({ showCalModal: false })
  },

  calChangeMonth: function(e) {
    var dir = parseInt(e.currentTarget.dataset.dir)
    var year = this.data.calYear
    var month = this.data.calMonth + dir
    if (month < 0) { month = 11; year-- }
    if (month > 11) { month = 0; year++ }
    this.setData({ calYear: year, calMonth: month })
    this.renderCalendar()
  },

  renderCalendar: function() {
    var year = this.data.calYear
    var month = this.data.calMonth
    var firstDay = new Date(year, month, 1).getDay()
    var daysInMonth = new Date(year, month + 1, 0).getDate()
    var daysInPrev = new Date(year, month, 0).getDate()
    var today = this.data.today
    var selectedDate = this.data.selectedDate
    var maxDate = new Date(today)
    maxDate.setDate(today.getDate() + 90)

    var days = []

    // Previous month days
    for (var i = firstDay - 1; i >= 0; i--) {
      days.push({ day: daysInPrev - i, isEmpty: true, isOther: true })
    }

    // Current month days
    for (var d = 1; d <= daysInMonth; d++) {
      var dt = new Date(year, month, d)
      var isToday = dt.toDateString() === today.toDateString()
      var isPast = dt < new Date(today.getFullYear(), today.getMonth(), today.getDate())
      var isTooFar = dt > maxDate
      var isSelected = dt.toDateString() === selectedDate.toDateString()
      days.push({
        day: d, month: month, year: year,
        isToday: isToday,
        isSelected: isSelected,
        isPast: isPast || isTooFar,
        isEmpty: false
      })
    }

    // Fill remaining cells
    var remaining = 42 - firstDay - daysInMonth
    for (var d = 1; d <= remaining; d++) {
      days.push({ day: d, isEmpty: true, isOther: true })
    }

    this.setData({ calDays: days })
  },

  calPick: function(e) {
    var dataset = e.currentTarget.dataset
    if (dataset.past === 'true') return
    var d = new Date(parseInt(dataset.year), parseInt(dataset.month), parseInt(dataset.day))
    this.setData({ selectedDate: d })
    this.resetSelection()
    this.renderDateBar()
    this.hideCalModal()
  },

  // ── Reset ──
  resetSelection: function() {
    this.setData({
      selectedDuration: null,
      isCustomMode: false,
      customHours: '',
      showTimeRow: false,
      selectedStart: null,
      selectedEnd: null,
      selectedTimeLabel: '',
      conflictMsg: '',
      suggestTime: '',
      canBook: false,
      totalPrice: 0,
      totalDetail: '请选择时长'
    })
  },

  // ── Go to booking confirm ──
  goPay: function() {
    if (!this.data.canBook) return
    var d = this.data
    var dateStr = d.selectedDate.getFullYear() + '-' +
      String(d.selectedDate.getMonth()+1).padStart(2,'0') + '-' +
      String(d.selectedDate.getDate()).padStart(2,'0')

    wx.navigateTo({
      url: '/pages/booking-confirm/booking-confirm?' +
        'roomId=' + d.roomId +
        '&roomName=' + encodeURIComponent(d.room.name) +
        '&date=' + dateStr +
        '&start=' + d.selectedStart +
        '&end=' + d.selectedEnd +
        '&total=' + d.totalPrice +
        '&duration=' + (parseFloat(d.selectedDuration) || 120)
    })
  }
})
