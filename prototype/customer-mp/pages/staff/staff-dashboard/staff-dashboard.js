var STAFF_API = require('../utils/staff-api')
var API = require('../../../utils/api')

Page({
  data: {
    storeName: '花城广场店',
    timeStr: '',
    roomOverview: { idle: 0, inUse: 0, booked: 0, cleaning: 0 },
    stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0, orderStatus: 0, alerts: 0 },
    showDoorMenu: false, doorRooms: [], doorRoomIds: [],
    serviceCalls: [], serviceCallCount: 0
  },

  onLoad: function() {
    var role = API.getUserRole()
    if (role !== 'staff') { wx.reLaunch({ url: '/pages/home/home' }); return }
  },

  onShow: function() {
    this.updateTime()
    var self = this

    // 从房间列表+订单数据计算房态统计（与房态管理页逻辑一致）
    API.getRooms(true).then(function(rooms) {
      var totalRooms = rooms.length
      var todayStr = new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')+'-'+String(new Date().getDate()).padStart(2,'0')

      API.getAllOrders().then(function(orders) {
        var list = orders || []
        // 兼容"YYYY-MM-DD"和"YYYY-MM-DDT..."两种日期格式
        var todayOrders = list.filter(function(o) {
          var d = o.date || (o.created || '').slice(0, 10)
          return d === todayStr
        })

        var inUse = 0, booked = 0, revenue = 0

        // 与订单管理页一致的统计方式：按status字段+roomId匹配，不做时间过滤
        for (var ri = 0; ri < rooms.length; ri++) {
          var r = rooms[ri]
          var foundInUse = false, foundBooked = false
          for (var i = 0; i < list.length; i++) {
            var o = list[i]
            if (o.roomId !== r.roomId || o.status === 'Cancelled') continue
            if (o.status === 'InUse') { foundInUse = true; break }
            if (o.status === 'Booked') { foundBooked = true; break }
          }
          if (foundInUse) inUse++; else if (foundBooked) booked++
        }
        for (var i = 0; i < todayOrders.length; i++) revenue += todayOrders[i].amount || 0

        var idle = totalRooms - inUse - booked
        self.setData({
          roomOverview: { idle: idle, inUse: inUse, booked: booked, cleaning: 0 },
          stats: {
            roomCount: { inUse: inUse },
            todayRevenue: revenue,
            todayOrders: todayOrders.length,
            pendingTasks: inUse + booked,
            orderStatus: todayOrders.length,
            alerts: 0
          }
        })
      })
    })

    // 查询客服呼叫请求
    var calls = []; try { calls = JSON.parse(wx.getStorageSync('mp_service_calls') || '[]') } catch(e) {}
    var pendingCalls = calls.filter(function(c) { return c.status === 'pending' })
    self.setData({ serviceCalls: pendingCalls, serviceCallCount: pendingCalls.length })

    // 开门菜单的房间列表 — 从API动态拉取
    API.getRooms(true).then(function(list) {
      if (list && list.length > 0) {
        var names = [], ids = []
        for (var i = 0; i < list.length; i++) {
          names.push(list[i].name)
          ids.push(list[i].roomId)
        }
        self.setData({ doorRooms: names, doorRoomIds: ids })
      }
    }).catch(function() {
      self.setData({
        doorRooms: ['白沙瓦', '翡冷翠', '布拉格', '丰沙里'],
        doorRoomIds: ['RM004', 'RM002', 'RM003', 'RM001']
      })
    })
  },

  resolveServiceCall: function(e) {
    var id = e.currentTarget.dataset.id
    var calls = []; try { calls = JSON.parse(wx.getStorageSync('mp_service_calls') || '[]') } catch(e) {}
    for (var i = 0; i < calls.length; i++) { if (calls[i].id === id || calls[i].id === id) { calls[i].status = 'resolved'; break } }
    try { wx.setStorageSync('mp_service_calls', JSON.stringify(calls)) } catch(e) {}
    var pendingCalls = calls.filter(function(c) { return c.status === 'pending' })
    this.setData({ serviceCalls: pendingCalls, serviceCallCount: pendingCalls.length })
    wx.showToast({ title: '已处理', icon: 'none' })
  },

  updateTime: function() {
    var now = new Date()
    var h = String(now.getHours()).padStart(2,'0')
    var m = String(now.getMinutes()).padStart(2,'0')
    this.setData({ timeStr: h + ':' + m })
  },

  // 四宫格跳转
  goTodo: function() { wx.navigateTo({ url: '/pages/staff/staff-todo/staff-todo' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/staff/staff-order-management/staff-order-management' }) },
  goDeviceMonitor: function() { wx.navigateTo({ url: '/pages/staff/staff-device-monitor/staff-device-monitor' }) },

  // 快捷按钮
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },

  // ── 开门（居中菜单）──
  goOpenDoor: function() {
    this.setData({ showDoorMenu: true })
  },
  hideDoorMenu: function() {
    this.setData({ showDoorMenu: false })
  },
  selectDoorRoom: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    var roomId = this.data.doorRoomIds[idx]
    var roomName = this.data.doorRooms[idx]
    this.setData({ showDoorMenu: false })
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + roomId + '&roomName=' + encodeURIComponent(roomName) })
  },

  goReconciliation: function() {
    wx.navigateTo({ url: '/pages/staff/staff-reconciliation/staff-reconciliation' })
  },

  // 更多功能
  goAttendance: function() { wx.navigateTo({ url: '/pages/staff/staff-attendance/staff-attendance' }) },
  goProducts: function() { wx.navigateTo({ url: '/pages/staff/staff-product-management/staff-product-management' }) },
  goInspection: function() { wx.navigateTo({ url: '/pages/staff/staff-inspection/staff-inspection' }) },
  goScheduling: function() { wx.navigateTo({ url: '/pages/staff/staff-scheduling/staff-scheduling' }) },
  goRoomStatus: function() { wx.navigateTo({ url: '/pages/staff/staff-room-status/staff-room-status' }) },
  goCleaning: function() { wx.navigateTo({ url: '/pages/staff/staff-cleaning-task/staff-cleaning-task' }) },
  goProfile: function() { wx.navigateTo({ url: '/pages/staff/staff-profile/staff-profile' }) },

  // 退出登录
  doLogout: function() {
    var self = this
    wx.showModal({
      title: '退出登录',
      content: '确定退出店员端，返回客人首页？',
      success: function(res) {
        if (res.confirm) {
          API.logout()
          wx.reLaunch({ url: '/pages/home/home' })
        }
      }
    })
  }
})
