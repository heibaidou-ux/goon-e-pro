var API = require('../../../utils/api')

Page({
  data: {
    rooms: [], stats: { inUse: 0, available: 0, booked: 0, cleaning: 0 },
    showBookingModal: false, bookRoomId: '', bookRoomName: '',
    bookName: '', bookPhone: '', bookDate: '', bookStart: '', bookEnd: '', bookSource: '',
    sourceOptions: ['到店','美团','抖音','大众点评','高德地图','小红书','会小二','老客户','电话预约','其他'],
    timeOptions: [],
    // 菜单弹窗
    showRoomMenu: false, menuRoomId: '', menuRoomName: '', menuStatus: '', menuOrderId: '',
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

            // ── InUse订单：检查是否真的还在使用中（时间未过期）──
            if (o.status === 'InUse' && o.date === todayStr && o.time) {
              var ep = o.time.split('-')[1].split(':')
              var endMin = parseInt(ep[0])*60+parseInt(ep[1])
              if (curMin < endMin) {
                // 还没结束
                currentOrder = {
                  orderId: o.orderId,
                  customerName: o.customerName || o.phone || '客人',
                  start: o.time.split('-')[0], end: o.time.split('-')[1]
                }
                break
              }
              // 已过结束时间，当作无订单处理
            }

            if (o.date === todayStr && o.status === 'Booked' && o.time) {
              var parts = o.time.split('-')
              if (parts.length >= 2) {
                var sp = parts[0].split(':'), ep = parts[1].split(':')
                var sm = parseInt(sp[0])*60+parseInt(sp[1]), em = parseInt(ep[0])*60+parseInt(ep[1])
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
                // 已到时段/已过时段不自动转为InUse，等店员手动确认
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
            currentOrder: currentOrder, deviceStatus: ''
          }
        })
        self.setData({ rooms: roomList, stats: { inUse: inUse, available: available, booked: booked, cleaning: cleaning } })
        // 异步加载设备状态
        self.loadDeviceStatus()
      })
    })
  },

  loadDeviceStatus: function() {
    var self = this
    var roomIds = self.data.rooms.map(function(r){return r.roomId})
    var deviceStatusMap = {}
    var loaded = 0
    for (var ri = 0; ri < roomIds.length; ri++) {
      (function(rid) {
        API.getRoomDevices(rid).then(function(devices) {
          var lightsOn = 0, lightsTotal = 0, acOn = false, curtainOpen = false, speakerOn = false
          for (var di = 0; di < devices.length; di++) {
            var d = devices[di], a = d.attributes || {}
            if (d.type === 'Light') { lightsTotal++; if (a.power || a.brightness > 0) lightsOn++ }
            if (d.type === 'AC') acOn = a.mode && a.mode !== 'off'
            if (d.type === 'Curtain') curtainOpen = a.position !== 'closed'
            if (d.type === 'Speaker' || d.type === 'BGM') speakerOn = a.playing
          }
          deviceStatusMap[rid] = { lightsOn: lightsOn, lightsTotal: lightsTotal, acOn: acOn, curtainOpen: curtainOpen, speakerOn: speakerOn }
          loaded++
          if (loaded >= roomIds.length) self.applyDeviceStatus(deviceStatusMap)
        }).catch(function(){loaded++;if(loaded>=roomIds.length)self.applyDeviceStatus(deviceStatusMap)})
      })(roomIds[ri])
    }
  },

  applyDeviceStatus: function(map) {
    var rooms = this.data.rooms
    for (var i = 0; i < rooms.length; i++) {
      var ds = map[rooms[i].roomId]
      if (!ds) continue
      var parts = []
      if (ds.lightsTotal > 0) parts.push('💡' + (ds.lightsOn > 0 ? '开' : '关'))
      parts.push(ds.curtainOpen ? '🪟开' : '🪟关')
      parts.push(ds.acOn ? '❄️开' : '❄️关')
      parts.push(ds.speakerOn ? '🔊开' : '🔊关')
      rooms[i].deviceStatus = parts.join(' ')
    }
    this.setData({ rooms: rooms })
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
    this.setData({ showRoomMenu: true, menuRoomId: roomId, menuRoomName: roomName, menuStatus: status, menuOrderId: orderId })
  },

  hideRoomMenu: function() { this.setData({ showRoomMenu: false }) },

  menuBooking: function() {
    this.hideRoomMenu()
    var now = new Date()
    var dateStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    var h = now.getHours(), m = Math.ceil(now.getMinutes()/30)*30
    if (m >= 60) { h++; m = 0 }
    var startTime = String(h%24).padStart(2,'0')+':'+String(m).padStart(2,'0')
    this.setData({
      showBookingModal: true, bookRoomId: this.data.menuRoomId, bookRoomName: this.data.menuRoomName,
      bookName: '', bookPhone: '', bookDate: dateStr, bookStart: startTime, bookEnd: '', bookSource: ''
    })
  },

  menuClean: function() {
    this.hideRoomMenu()
    wx.showToast({ title: '🧹 已安排保洁', icon: 'none' })
  },

  menuDevice: function() {
    this.hideRoomMenu()
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+this.data.menuRoomId+'&roomName='+encodeURIComponent(this.data.menuRoomName) })
  },

  menuCheckIn: function() {
    this.hideRoomMenu()
    var api=require('../../../utils/api')
    if(this.data.menuRoomId) api.executeScene(this.data.menuRoomId,'Welcome').catch(function(){})
    wx.showToast({ title: '✅ 已开始使用', icon: 'none' })
    this.loadRooms()
  },

  menuCancelBooking: function() {
    this.hideRoomMenu()
    wx.showToast({ title: '预约已取消', icon: 'none' })
    this.loadRooms()
  },

  menuForceCheckout: function() {
    this.hideRoomMenu()
    wx.showToast({ title: '🏁 已强制退房', icon: 'none' })
    this.loadRooms()
  },

  showBooking: function(e) { this.onRoomTap(e) },
  showRoomControl: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    var roomName = e.currentTarget.dataset.roomname || ''
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
  },

  // ── 预订表单 ──
  onBookName: function(e) { this.setData({ bookName: e.detail.value }) },
  onBookPhone: function(e) { this.setData({ bookPhone: e.detail.value }) },
  onBookDate: function(e) { this.setData({ bookDate: e.detail.value }) },
  onBookSource: function(e) { this.setData({ bookSource: this.data.sourceOptions[e.detail.value] }) },
  onBookStart: function(e) { this.setData({ bookStart: this.data.timeOptions[e.detail.value] }) },
  onBookEnd: function(e) { this.setData({ bookEnd: this.data.timeOptions[e.detail.value] }) },

  confirmBooking: function() {
    var self = this
    if (!self.data.bookName || !self.data.bookStart || !self.data.bookEnd || !self.data.bookSource) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' }); return
    }
    var booking = {
      orderId: 'ORD'+String(Date.now()).slice(-6),
      roomId: self.data.bookRoomId, roomName: self.data.bookRoomName,
      customerName: self.data.bookName, phone: self.data.bookPhone || '',
      date: self.data.bookDate, time: self.data.bookStart + '-' + self.data.bookEnd,
      amount: 0, status: 'Booked', customerSource: self.data.bookSource,
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
