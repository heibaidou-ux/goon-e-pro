var STAFF_API = require('../../../utils/staff-api')
var API = require('../../../utils/api')

Page({
  data: {
    storeName: '盈隆店',
    timeStr: '',
    roomOverview: { idle: 0, inUse: 0, booked: 0, cleaning: 0 },
    stats: { roomCount: { inUse: 0 }, todayRevenue: 0, todayOrders: 0, pendingTasks: 0, orderStatus: 0, alerts: 0 },
    todos: []
  },

  onLoad: function() {
    var role = API.getUserRole()
    if (role !== 'staff') { wx.reLaunch({ url: '/pages/home/home' }); return }
  },

  onShow: function() {
    this.updateTime()
    var self = this

    // 统一从订单数据计算所有统计
    var roomNames = ['RM001', 'RM002', 'RM003', 'RM004']
    var totalRooms = roomNames.length
    var bookedCount = 0, inUseCount = 0
    var todayStr = new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')+'-'+String(new Date().getDate()).padStart(2,'0')
    var todayRevenue = 0, todayOrderCount = 0

    API.getAllOrders().then(function(orders) {
      var allOrders = orders || []
      var todayOrders = allOrders.filter(function(o) { return o.date === todayStr || (o.created && o.created.indexOf(todayStr) === 0) })

      for (var i = 0; i < allOrders.length; i++) {
        var o = allOrders[i]
        if (roomNames.indexOf(o.roomId) === -1) continue
        if (o.status === 'Booked') bookedCount++
        if (o.status === 'InUse') inUseCount++
      }
      for (var i = 0; i < todayOrders.length; i++) todayRevenue += todayOrders[i].amount || 0
      todayOrderCount = todayOrders.length

      var idleCount = totalRooms - inUseCount - bookedCount
      self.setData({
        roomOverview: { idle: idleCount, inUse: inUseCount, booked: bookedCount, cleaning: 0 },
        stats: {
          roomCount: { inUse: inUseCount },
          todayRevenue: todayRevenue,
          todayOrders: todayOrderCount,
          pendingTasks: inUseCount + bookedCount,
          orderStatus: todayOrderCount,
          alerts: 0
        }
      })
    })

    // 待办事项：从订单数据统一生成（与待办详情页同源）
    API.getAllOrders().then(function(orders) {
      var list = orders || []
      var todos = []
      var todayStr2 = new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')+'-'+String(new Date().getDate()).padStart(2,'0')
      var nowMin = new Date().getHours()*60 + new Date().getMinutes()

      // 进行中订单
      var inUseRooms = []
      for (var i = 0; i < list.length; i++) {
        var o = list[i]
        if (o.status === 'InUse' && o.roomName && inUseRooms.indexOf(o.roomName) === -1) {
          inUseRooms.push(o.roomName)
          todos.push({ id:'IU'+o.orderId, title:'🟢 '+o.roomName+' 使用中', type:'active', priority:'high', deadline:'进行中' })
        }
      }
      // 今日待入住
      for (var i = 0; i < list.length; i++) {
        var o = list[i]
        if (o.status === 'Booked' && o.date === todayStr2 && o.time) {
          var sp = o.time.split('-')[0].split(':')
          var startMin = parseInt(sp[0])*60+parseInt(sp[1])
          if (startMin > nowMin && startMin - nowMin < 120) {
            todos.push({ id:'BK'+o.orderId, title:'📋 '+o.roomName+' 即将到店', type:'order', priority:'high', deadline:o.time })
          }
        }
      }
      // 待发货
      API.getShopOrders().then(function(shopOrders) {
        if (shopOrders && shopOrders.length) {
          for (var i = 0; i < shopOrders.length; i++) {
            if (shopOrders[i].deliveryMethod === 'express' && (!shopOrders[i].status || shopOrders[i].status === 'PendingDelivery')) {
              todos.push({ id:'SH'+shopOrders[i].orderId, title:'📦 茶品订单待发货', type:'shipping', priority:'high', deadline:'尽快' })
            }
          }
        }
        self.setData({ todos: todos.slice(0, 8) })
      })
    })

    // 房态总览背景数据：房间总数
    self.setData({ roomOverview: { idle: totalRooms, inUse: 0, booked: 0, cleaning: 0 } })
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

  // 快捷按钮：验券、开门、监控、对账
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },

  goOpenDoor: function() {
    var self = this
    wx.showActionSheet({
      itemList: ['大茶室C', '中茶室A', '中茶室B', '大会议室'],
      success: function(res) {
        var rooms = ['大茶室C', '中茶室A', '中茶室B', '大会议室']
        var roomIds = ['RM004', 'RM002', 'RM003', 'RM001']
        wx.navigateTo({
          url: '/pages/room-control/room-control?roomId=' + roomIds[res.tapIndex] + '&roomName=' + encodeURIComponent(rooms[res.tapIndex])
        })
      }
    })
  },

  goReconciliation: function() {
    wx.navigateTo({ url: '/pages/staff/staff-reconciliation/staff-reconciliation' })
  },

  // 更多功能：考勤/商品管理/巡检/排班
  goAttendance: function() { wx.navigateTo({ url: '/pages/staff/staff-attendance/staff-attendance' }) },
  goProducts: function() { wx.navigateTo({ url: '/pages/staff/staff-product-management/staff-product-management' }) },
  goInspection: function() { wx.navigateTo({ url: '/pages/staff/staff-inspection/staff-inspection' }) },
  goScheduling: function() { wx.navigateTo({ url: '/pages/staff/staff-scheduling/staff-scheduling' }) },

  // 保留旧导航供其他引用
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
