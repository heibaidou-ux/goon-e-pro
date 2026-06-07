var API = require('../../utils/api')

Page({
  data: {
    tabIndex: 0, orders: [], filteredOrders: [],
    showLogisticsModal: false,
    logisticsData: { carrier: '', trackingNum: '', timeline: [] }
  },

  onShow: function() { this.loadOrders() },

  loadOrders: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var mapped = orders.map(function(o) {
        var statusClass = 'status-completed', statusLabel = '已完成'
        if (o.status === 'InUse' || o.status === 'in_use') { statusClass = 'status-inuse'; statusLabel = '使用中' }
        else if (o.status === 'Booked') { statusClass = 'status-booked'; statusLabel = '已预订' }

        var log = null
        if (o.status === 'Completed' && o.orderId === 'ORD003') {
          log = { carrier: '顺丰速运', icon: '📦', trackingNum: 'SF1234567890', statusBadge: 'transit', statusLabel: '运输中', estimated: '预计明日送达', steps: [{ label: '已下单', active: true }, { label: '已发货', active: true, current: true }, { label: '派送中', active: false }, { label: '已签收', active: false }] }
        }
        return { orderId: o.orderId, roomName: o.roomName || '房间', status: o.status, statusClass: statusClass, statusLabel: statusLabel, timeStr: (o.date||'')+' '+(o.time||(o.start?o.start.slice(0,5)+'-'+o.end.slice(0,5):'')), amount: o.amount||0, doorCode: o.doorCode||'0000', logistics: log }
      })
      self.setData({ orders: mapped })
      self.filterOrders()
    })
  },

  switchTab: function(e) { var idx = parseInt(e.currentTarget.dataset.tab); this.setData({ tabIndex: idx }); this.filterOrders() },

  filterOrders: function() {
    var tab = this.data.tabIndex, list = this.data.orders
    if (tab === 1) list = list.filter(function(o) { return o.status === 'InUse' || o.status === 'Booked' || o.status === 'in_use' })
    else if (tab === 2) list = list.filter(function(o) { return o.status === 'Completed' })
    this.setData({ filteredOrders: list })
  },

  openDoor: function(e) { wx.showToast({ title: '🚪 门已开', icon: 'none' }) },
  callService: function(e) { wx.showToast({ title: '📞 已通知店员', icon: 'none' }) },

  cancelOrEndOrder: function(e) {
    var id = e.currentTarget.dataset.id, self = this, orders = self.data.orders, order = null
    for (var i = 0; i < orders.length; i++) { if (orders[i].orderId === id) { order = orders[i]; break } }
    if (!order) return
    if (order.status === 'InUse' || order.status === 'in_use') {
      wx.showModal({ title: '结束订单', content: '确定要结束此订单吗？', success: function(res) {
        if (res.confirm) {
          for (var i = 0; i < orders.length; i++) { if (orders[i].orderId === id) { orders[i].status = 'Completed'; orders[i].statusClass = 'status-completed'; orders[i].statusLabel = '已完成'; break } }
          self.setData({ orders: orders }); self.filterOrders(); wx.showToast({ title: '订单已结束', icon: 'success' })
        }
      }})
    } else {
      wx.showModal({ title: '取消订单', content: '确定要取消此订单？', success: function(res) {
        if (res.confirm) { API.cancelOrder(id).then(function() { wx.showToast({ title: '已取消', icon: 'success' }); self.loadOrders() }) }
      }})
    }
  },

  reBook: function(e) { wx.showToast({ title: '再次预约', icon: 'none' }) },
  goRoomControl: function(e) { wx.navigateTo({ url: '/pages/room-control/room-control' }) },
  goRoomDetail: function(e) { wx.navigateTo({ url: '/pages/room-detail/room-detail' }) },

  showLogistics: function(e) {
    var id = e.currentTarget.dataset.id, orders = this.data.orders
    for (var i = 0; i < orders.length; i++) { if (orders[i].orderId === id && orders[i].logistics) {
      this.setData({ showLogisticsModal: true, logisticsData: { carrier: orders[i].logistics.carrier, trackingNum: orders[i].logistics.trackingNum, timeline: [{ title: '已揽收', time: '2026-06-06 14:00', status: 'done', active: true }, { title: '已到达广州分拣中心', time: '2026-06-06 18:30', status: 'done', active: true }, { title: '派送中', time: '2026-06-07 08:00', status: 'current', active: true }, { title: '已签收', time: '预计今天', status: 'pending', active: false }] } }); break
    }}
  },
  hideLogistics: function() { this.setData({ showLogisticsModal: false }) },
  copyTracking: function(e) { wx.setClipboardData({ data: e.currentTarget.dataset.code }) },

  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
