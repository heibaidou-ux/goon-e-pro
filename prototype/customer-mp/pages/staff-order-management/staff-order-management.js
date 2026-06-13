var API = require('../../utils/api')

Page({
  data: {
    tabIndex: 0,
    orders: [], filteredOrders: [],
    showDetail: false, detailOrder: null, editSource: '',
    sourceOptions: ['到店', '美团', '抖音', '大众点评', '高德地图', '小红书', '会小二', '老客户', '电话预约', '其他']
  },

  onShow: function() {
    this.loadOrders()
  },

  loadOrders: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var now = new Date()
      var todayStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours() * 60 + now.getMinutes()

      var mapped = orders.map(function(o) {
        var status = o.status || 'Booked'
        // 自动判断状态
        if (status === 'Booked' && o.date === todayStr && o.time) {
          var parts = o.time.split('-')
          if (parts.length === 2) {
            var sp = parts[0].split(':'), ep = parts[1].split(':')
            var sm = parseInt(sp[0])*60+parseInt(sp[1]), em = parseInt(ep[0])*60+parseInt(ep[1])
            if (curMin >= sm && curMin < em) status = 'InUse'
            else if (curMin >= em) status = 'Completed'
          }
        }
        return {
          orderId: o.orderId, roomName: o.roomName || '房间', roomId: o.roomId || '',
          status: status, date: o.date || '', time: o.time || '',
          amount: o.amount || 0, customerName: o.customerName || '',
          phone: o.phone || '', customerSource: o.customerSource || '',
          statusClass: status === 'InUse' ? 'status-inuse' : (status === 'Booked' ? 'status-booked' : 'status-completed'),
          statusLabel: status === 'InUse' ? '进行中' : (status === 'Booked' ? '已预订' : '已完成')
        }
      })
      self.setData({ orders: mapped })
      self.filterOrders()
    })
  },

  filterOrders: function() {
    var tab = this.data.tabIndex
    var list = this.data.orders
    if (tab === 0) list = list.filter(function(o) { return o.status === 'InUse' })
    else if (tab === 1) list = list.filter(function(o) { return o.status === 'Booked' })
    else if (tab === 2) list = list.filter(function(o) { return o.status === 'Completed' })
    this.setData({ filteredOrders: list })
  },

  switchTab: function(e) {
    this.setData({ tabIndex: parseInt(e.currentTarget.dataset.tab) })
    this.filterOrders()
  },

  // ── 客户来源 ──
  showOrderDetail: function(e) {
    var id = e.currentTarget.dataset.id
    var orders = this.data.orders
    for (var i = 0; i < orders.length; i++) {
      if (orders[i].orderId === id) {
        this.setData({ showDetail: true, detailOrder: orders[i], editSource: orders[i].customerSource || '' })
        break
      }
    }
  },

  onSourceChange: function(e) {
    var idx = e.detail.value
    this.setData({ editSource: this.data.sourceOptions[idx] })
  },

  saveSource: function() {
    var self = this
    var order = self.data.detailOrder
    var source = self.data.editSource
    if (!order || !source) { wx.showToast({ title: '请选择客户来源', icon: 'none' }); return }
    // 保存到订单中
    try {
      var bookings = wx.getStorageSync('mp_bookings') || []
      for (var i = 0; i < bookings.length; i++) {
        if (bookings[i].orderId === order.orderId) {
          bookings[i].customerSource = source
          break
        }
      }
      wx.setStorageSync('mp_bookings', bookings)
    } catch(e) {}
    wx.showToast({ title: '已保存', icon: 'success' })
    self.setData({ showDetail: false })
    self.loadOrders()
  },

  hideDetail: function() { this.setData({ showDetail: false }) },

  // ── 操作 ──
  checkIn: function(e) {
    wx.showToast({ title: '已办理入住', icon: 'success' })
  },

  completeOrder: function(e) {
    wx.showToast({ title: '订单已完成', icon: 'success' })
  }
})
