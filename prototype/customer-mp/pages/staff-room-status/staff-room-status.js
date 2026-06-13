var API = require('../../utils/api')

Page({
  data: { rooms: [], stats: { inUse: 0, available: 0 } },

  onShow: function() {
    var self = this
    var typeLabels = { TeaRoom: '茶室', MeetingRoom: '会议室', Exhibition: '展厅', Workspace: '工作间' }
    API.getRooms(true).then(function(rooms) {
      API.getUserOrders().then(function(orders) {
        var now = new Date()
        var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
        var curMin = now.getHours()*60+now.getMinutes()
        var inUse = 0, available = 0

        var roomList = rooms.map(function(r) {
          var currentOrder = null
          for (var i = 0; i < orders.length; i++) {
            var o = orders[i]
            if (o.roomId !== r.roomId) continue
            if (o.status === 'InUse') {
              currentOrder = { customerName: o.customerName || '客人', start: o.time ? o.time.split('-')[0] : '', end: o.time ? o.time.split('-')[1] : '' }
              break
            }
            if (o.date === todayStr && o.status === 'Booked') {
              var parts = o.time ? o.time.split('-') : []
              if (parts.length >= 2) {
                var sp = parts[0].split(':'), ep = parts[1].split(':')
                var sm = parseInt(sp[0])*60+parseInt(sp[1]), em = parseInt(ep[0])*60+parseInt(ep[1])
                if (curMin >= sm && curMin < em) { currentOrder = { customerName: o.customerName || '客人', start: parts[0], end: parts[1] }; break }
              }
            }
          }
          var statusClass = currentOrder ? 'inuse' : 'free'
          var statusLabel = currentOrder ? '使用中' : '空闲'
          if (statusClass === 'inuse') inUse++; else available++
          return { roomId: r.roomId, name: r.name, capacity: r.capacity, typeLabel: typeLabels[r.type] || '', statusClass: statusClass, statusLabel: statusLabel, currentOrder: currentOrder }
        })
        self.setData({ rooms: roomList, stats: { inUse: inUse, available: available } })
      })
    })
  },

  showDetail: function(e) {
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + e.currentTarget.dataset.roomid + '&roomName=' + encodeURIComponent(e.currentTarget.dataset.roomname || '') })
  },

  showRoomControl: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    var roomName = e.currentTarget.dataset.roomname || ''
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
  }
})
