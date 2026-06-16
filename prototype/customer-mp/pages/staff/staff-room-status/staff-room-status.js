var API = require('../../../utils/api')

Page({
  data: {
    rooms: [], stats: { inUse: 0, available: 0, booked: 0, cleaning: 0 },
    showBookingModal: false, bookRoomId: '', bookRoomName: '',
    bookName: '', bookPhone: '', bookDate: '', bookStart: '', bookDuration: 120, bookDurationLabel: '2小时', bookSource: '',
    sourceOptions: ['到店','美团','抖音','大众点评','高德地图','小红书','会小二','老客户','电话预约','其他'],
    timeOptions: [], durationOptions: ['1小时','2小时','3小时','4小时','6小时','8小时'],
    durationValues: [60, 120, 180, 240, 360, 480],
    // 弹窗
    showActionSheet: false, actionRoomId: '', actionRoomName: '', actionType: '',
    actionOrderId: '',
  },

  onShow: function() {
    this.loadRooms()
    this.generateTimeOptions()
  },

  loadRooms: function() {
    var self = this
    var typeLabels = { TeaRoom: '茶室', MeetingRoom: '会议室', Exhibition: '展厅', Workspace: '工作间' }
    API.getRooms(true).then(function(rooms) {
      API.getAllOrders().then(function(orders) {
        var now = new Date()
        var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
        var curMin = now.getHours()*60+now.getMinutes()

        var inUse = 0, available = 0, booked = 0, cleaning = 0

        var roomList = rooms.map(function(r) {
          var currentOrder = null
          var statusClass = 'free'
          var statusLabel = '空闲'

          // 查找该房间的所有订单
          var hasBookedLater = false
          for (var i = 0; i < orders.length; i++) {
            var o = orders[i]
            if (o.roomId !== r.roomId || o.status === 'Cancelled') continue

            if (o.status === 'InUse') {
              currentOrder = {
                orderId: o.orderId,
                customerName: o.customerName || o.phone || '客人',
                start: o.time ? o.time.split('-')[0] : '',
                end: o.time ? o.time.split('-')[1] : ''
              }
              break
            }

            if (o.date === todayStr && o.status === 'Booked' && o.time) {
              var parts = o.time.split('-')
              if (parts.length >= 2) {
                var sp = parts[0].split(':'), ep = parts[1].split(':')
                var sm = parseInt(sp[0])*60+parseInt(sp[1]), em = parseInt(ep[0])*60+parseInt(ep[1])
                if (curMin >= sm && curMin < em) {
                  // 当前时段已预订，视为使用中
                  currentOrder = {
                    orderId: o.orderId,
                    customerName: o.customerName || o.phone || '客人',
                    start: parts[0], end: parts[1]
                  }
                  break
                }
                if (curMin < sm && (!currentOrder || sm < parseInt(currentOrder.start.split(':')[0])*60+parseInt(currentOrder.start.split(':')[1]))) {
                  // 将来有预订
                  hasBookedLater = true
                  currentOrder = {
                    orderId: o.orderId,
                    customerName: o.customerName || o.phone || '客人',
                    start: parts[0], end: parts[1],
                    upcoming: true
                  }
                }
              }
            }
          }

          if (currentOrder && !currentOrder.upcoming) {
            statusClass = 'inuse'
            statusLabel = '使用中'
          } else if (currentOrder && currentOrder.upcoming) {
            statusClass = 'booked'
            statusLabel = '已预订'
          }

          if (statusClass === 'inuse') inUse++
          else if (statusClass === 'booked') booked++
          else available++

          return {
            roomId: r.roomId, name: r.name, capacity: r.capacity,
            typeLabel: typeLabels[r.type] || '',
            statusClass: statusClass, statusLabel: statusLabel,
            currentOrder: currentOrder
          }
        })
        self.setData({ rooms: roomList, stats: { inUse: inUse, available: available, booked: booked, cleaning: cleaning } })
      })
    })
  },

  generateTimeOptions: function() {
    var opts = []
    for (var h = 0; h < 24; h++) {
      for (var m = 0; m < 60; m += 30) {
        opts.push(String(h).padStart(2,'0')+':'+String(m).padStart(2,'0'))
      }
    }
    this.setData({ timeOptions: opts })
  },

  onRoomTap: function(e) {
    var status = e.currentTarget.dataset.status
    var roomId = e.currentTarget.dataset.roomid
    var roomName = e.currentTarget.dataset.roomname
    var orderId = e.currentTarget.dataset.orderid || ''

    if (status === 'free') {
      var now = new Date()
      var dateStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
      this.setData({
        showBookingModal: true, bookRoomId: roomId, bookRoomName: roomName,
        bookName: '', bookPhone: '', bookDate: dateStr, bookStart: '', bookDuration: 120, bookDurationLabel: '2小时', bookSource: ''
      })
    } else if (status === 'inuse') {
      this.setData({ showActionSheet: true, actionType: 'inuse', actionRoomId: roomId, actionRoomName: roomName, actionOrderId: orderId })
    } else if (status === 'booked') {
      this.setData({ showActionSheet: true, actionType: 'booked', actionRoomId: roomId, actionRoomName: roomName, actionOrderId: orderId })
    }
  },

  showBooking: function(e) { this.onRoomTap(e) },
  showRoomControl: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    var roomName = e.currentTarget.dataset.roomname || ''
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
  },

  // ── 操作弹窗 ──
  hideActionSheet: function() { this.setData({ showActionSheet: false }) },

  doCheckIn: function() { this.hideActionSheet(); wx.showToast({ title: '✅ 已确认到店', icon: 'none' }); this.loadRooms() },
  doCancelBooking: function() { this.hideActionSheet(); wx.showToast({ title: '预约已取消', icon: 'none' }); this.loadRooms() },
  doForceCheckout: function() { this.hideActionSheet(); wx.showToast({ title: '🏁 已强制退房', icon: 'none' }); this.loadRooms() },
  doExtend: function() {
    this.hideActionSheet()
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+this.data.actionRoomId+'&roomName='+encodeURIComponent(this.data.actionRoomName) })
  },

  // ── 预订表单 ──
  onBookName: function(e) { this.setData({ bookName: e.detail.value }) },
  onBookPhone: function(e) { this.setData({ bookPhone: e.detail.value }) },
  onBookDate: function(e) { this.setData({ bookDate: e.detail.value }) },
  onBookSource: function(e) { this.setData({ bookSource: this.data.sourceOptions[e.detail.value] }) },
  onBookStart: function(e) { this.setData({ bookStart: this.data.timeOptions[e.detail.value] }) },
  onBookDuration: function(e) {
    var idx = e.detail.value
    this.setData({ bookDuration: this.data.durationValues[idx], bookDurationLabel: this.data.durationOptions[idx] })
  },

  confirmBooking: function() {
    var self = this
    if (!self.data.bookName || !self.data.bookStart || !self.data.bookSource) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' }); return
    }
    var sp = self.data.bookStart.split(':')
    var startMin = parseInt(sp[0])*60+parseInt(sp[1])
    var endMin = startMin + self.data.bookDuration
    var endStr = String(Math.floor(endMin/60)%24).padStart(2,'0')+':'+String(endMin%60).padStart(2,'0')

    var booking = {
      orderId: 'ORD'+String(Date.now()).slice(-6),
      roomId: self.data.bookRoomId, roomName: self.data.bookRoomName,
      customerName: self.data.bookName, phone: self.data.bookPhone || '',
      date: self.data.bookDate, time: self.data.bookStart + '-' + endStr,
      amount: Math.round(120 * self.data.bookDuration / 60),
      status: 'Booked', customerSource: self.data.bookSource,
      created: new Date().toISOString(),
      doorCode: String(Math.floor(1000+Math.random()*9000))
    }

    try {
      var bookings = wx.getStorageSync('mp_bookings') || []
      bookings.push(booking)
      wx.setStorageSync('mp_bookings', bookings)
    } catch(e) { wx.showToast({ title: '保存失败', icon: 'none' }); return }

    wx.showToast({ title: '✅ 已为 '+self.data.bookName+' 预订', icon: 'success' })
    self.setData({ showBookingModal: false })
    self.loadRooms()
  },

  hideBookingModal: function() { this.setData({ showBookingModal: false }) }
})
