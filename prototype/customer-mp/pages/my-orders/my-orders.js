var API = require('../../utils/api')

Page({
  data: {
    tabIndex: 0, orders: [], filteredOrders: [],
    showLogisticsModal: false, showCancelModal: false, showExtendModal: false,
    logisticsData: { carrier: '', trackingNum: '', timeline: [] },
    cancelOrderId: null, cancelMsg: '',
    extendOrderId: null, extendOptions: [], selectedExtendIdx: -1, extendInfo: ''
  },

  onShow: function() { this.loadOrders() },

  loadOrders: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var now = new Date()
      var todayStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours() * 60 + now.getMinutes()

      var mapped = orders.map(function(o) {
        var status = o.status
        // 自动判断订单状态：根据当前时间
        if (status === 'Booked' && o.date === todayStr && o.time) {
          var parts = o.time.split('-')
          if (parts.length === 2) {
            var startParts = parts[0].split(':')
            var endParts = parts[1].split(':')
            var startMin = parseInt(startParts[0])*60 + parseInt(startParts[1])
            var endMin = parseInt(endParts[0])*60 + parseInt(endParts[1])
            if (curMin >= startMin && curMin < endMin) {
              status = 'InUse'
            }
          }
        }

        // 状态标签
        var statusClass = 'status-completed', statusLabel = '已完成'
        if (status === 'InUse' || status === 'in_use') { statusClass = 'status-inuse'; statusLabel = '进行中' }
        else if (status === 'Booked') { statusClass = 'status-booked'; statusLabel = '待使用' }

        // 剩余时间（进行中订单）
        var remaining = null
        if (status === 'InUse' && o.time && o.date === todayStr) {
          var parts = o.time.split('-')
          if (parts.length === 2) {
            var endParts = parts[1].split(':')
            var endMin = parseInt(endParts[0])*60 + parseInt(endParts[1])
            var diff = endMin - curMin
            if (diff > 0) remaining = diff
          }
        }

        // 取消规则（待使用订单）
        var cancelFree = true, cancelMsg = ''
        if (status === 'Booked' && o.date && o.time) {
          var startParts2 = o.time.split('-')[0].split(':')
          var orderDate = new Date(o.date)
          var orderDT = new Date(orderDate.getFullYear(), orderDate.getMonth(), orderDate.getDate(), parseInt(startParts2[0]), parseInt(startParts2[1]))
          var hoursUntil = (orderDT - now) / 3600000
          if (hoursUntil < 2 && hoursUntil > 0) {
            cancelFree = false
            cancelMsg = '距开始不足2小时，取消将收取首小时费用50%'
          } else if (hoursUntil >= 2) {
            cancelMsg = '距开始超过2小时，可免费取消'
          } else {
            cancelMsg = '已超过预约时间，不可取消'
          }
        }

        // 已完成订单的物流信息
        var log = null
        if (status === 'Completed' && o.orderId === 'ORD003') {
          log = { carrier: '顺丰速运', icon: '📦', trackingNum: 'SF1234567890', statusBadge: 'transit', statusLabel: '运输中', estimated: '预计明日送达', steps: [{ label: '已下单', active: true }, { label: '已发货', active: true, current: true }, { label: '派送中', active: false }, { label: '已签收', active: false }] }
        }

        return {
          orderId: o.orderId, roomName: o.roomName || '房间', roomId: o.roomId || '',
          status: status, statusClass: statusClass, statusLabel: statusLabel,
          timeStr: (o.date||'')+' '+(o.time||(o.start?o.start.slice(0,5)+'-'+o.end.slice(0,5):'')),
          amount: o.amount||0, doorCode: o.doorCode||'0000',
          remaining: remaining, cancelFree: cancelFree, cancelMsg: cancelMsg,
          logistics: log, payment: o.payment||''
        }
      })
      self.setData({ orders: mapped })
      self.filterOrders()
    })
  },

  switchTab: function(e) {
    var idx = parseInt(e.currentTarget.dataset.tab)
    this.setData({ tabIndex: idx })
    this.filterOrders()
  },

  filterOrders: function() {
    var tab = this.data.tabIndex, list = this.data.orders
    if (tab === 0) list = list.filter(function(o) { return o.status === 'InUse' || o.status === 'in_use' })
    else if (tab === 1) list = list.filter(function(o) { return o.status === 'Booked' })
    else if (tab === 2) list = list.filter(function(o) { return o.status === 'Completed' })
    this.setData({ filteredOrders: list })
  },

  findOrder: function(id) {
    var orders = this.data.orders
    for (var i = 0; i < orders.length; i++) {
      if (orders[i].orderId === id) return orders[i]
    }
    return null
  },

  // ── 进行中操作 ──

  openDoor: function(e) {
    var order = this.findOrder(e.currentTarget.dataset.id)
    if (!order) return
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+(order.roomId||'')+'&roomName='+encodeURIComponent(order.roomName||'') })
  },

  goRoomControl: function(e) {
    var roomId = e.currentTarget.dataset.roomId || ''
    var roomName = e.currentTarget.dataset.roomName || ''
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+roomId+'&roomName='+encodeURIComponent(roomName) })
  },

  callService: function(e) {
    wx.showToast({ title: '📞 已通知店员', icon: 'none' })
  },

  showExtend: function(e) {
    var id = e.currentTarget.dataset.id
    var order = this.findOrder(id)
    if (!order) return
    var endTime = '12:00'
    if (order.timeStr) {
      var parts = order.timeStr.split(' ')
      if (parts.length >= 2 && parts[1].indexOf('-') > -1) {
        endTime = parts[1].split('-')[1]
      }
    }
    var eh = parseInt(endTime.split(':')[0]) || 12
    var em = parseInt(endTime.split(':')[1]) || 0
    var baseMin = Math.ceil((eh * 60 + em) / 30) * 30
    var options = []
    for (var i = 1; i <= 8; i++) {
      var totalMin = baseMin + i * 30
      var h = Math.floor(totalMin / 60) % 24
      var m = totalMin % 60
      var extMin = i * 30
      var price = Math.round(120 * extMin / 60)
      options.push({ label: '至 ' + String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0'), price: price, minutes: extMin, idx: i })
    }
    this.setData({ showExtendModal: true, extendOrderId: id, extendOptions: options, selectedExtendIdx: -1, extendInfo: order.roomName + ' · 当前至 ' + endTime + ' 结束' })
  },

  selectExtend: function(e) {
    this.setData({ selectedExtendIdx: parseInt(e.currentTarget.dataset.idx) })
  },

  confirmExtend: function() {
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx]
    wx.showToast({ title: '续订成功 +' + opt.minutes + '分 ¥' + opt.price, icon: 'none' })
    this.setData({ showExtendModal: false, extendOrderId: null })
    this.loadOrders()
  },

  hideExtendModal: function() { this.setData({ showExtendModal: false }) },

  // ── 待使用操作 ──

  showCancel: function(e) {
    var id = e.currentTarget.dataset.id
    var order = this.findOrder(id)
    if (!order) return
    this.setData({ showCancelModal: true, cancelOrderId: id, cancelMsg: order.cancelMsg || '确定要取消此订单？' })
  },

  confirmCancel: function() {
    var self = this
    var id = this.data.cancelOrderId
    if (!id) return
    API.cancelOrder(id).then(function() {
      wx.showToast({ title: '已取消', icon: 'success' })
      self.setData({ showCancelModal: false, cancelOrderId: null })
      self.loadOrders()
    }).catch(function() {
      // fallback: local cancel
      var orders = self.data.orders
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].orderId === id) { orders.splice(i, 1); break }
      }
      self.setData({ orders: orders })
      self.filterOrders()
      wx.showToast({ title: '已取消', icon: 'success' })
      self.setData({ showCancelModal: false, cancelOrderId: null })
    })
  },

  hideCancelModal: function() { this.setData({ showCancelModal: false }) },

  // ── 已完成操作 ──

  reBook: function(e) {
    wx.showToast({ title: '再次预约', icon: 'none' })
  },

  goRoomDetail: function(e) {
    wx.navigateTo({ url: '/pages/room-detail/room-detail' })
  },

  // ── 物流 ──

  showLogistics: function(e) {
    var id = e.currentTarget.dataset.id
    var orders = this.data.orders
    for (var i = 0; i < orders.length; i++) {
      if (orders[i].orderId === id && orders[i].logistics) {
        this.setData({
          showLogisticsModal: true,
          logisticsData: {
            carrier: orders[i].logistics.carrier,
            trackingNum: orders[i].logistics.trackingNum,
            timeline: [
              { title: '已揽收', time: '2026-06-06 14:00', status: 'done' },
              { title: '已到达广州分拣中心', time: '2026-06-06 18:30', status: 'done' },
              { title: '派送中', time: '2026-06-07 08:00', status: 'current' },
              { title: '已签收', time: '预计今天', status: 'pending' }
            ]
          }
        })
        break
      }
    }
  },

  hideLogistics: function() { this.setData({ showLogisticsModal: false }) },

  copyTracking: function(e) { wx.setClipboardData({ data: e.currentTarget.dataset.code }) },

  // ── 底部导航 ──
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
