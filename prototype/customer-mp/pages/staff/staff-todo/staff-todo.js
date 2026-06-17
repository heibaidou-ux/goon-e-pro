var STAFF_API = require('../../../utils/staff-api')
var API = require('../../../utils/api')

Page({
  data: {
    cleaning: { count: 0, items: [] },
    reconciliation: { count: 0, items: [] },
    alerts: { count: 0, items: [] },
    inspection: { count: 0, items: [] },
    audit: { count: 0, items: [] }
  },

  onShow: function() {
    var self = this

    // 保洁
    STAFF_API.getCleaningTasks().then(function(t) {
      var pending = t.pending || []
      self.setData({ cleaning: { count: pending.length, items: pending } })
    })

    // 告警
    STAFF_API.getDeviceStats().then(function(s) {
      var offline = s.offline || 0
      self.setData({ alerts: { count: offline, items: offline > 0 ? [{ title: offline + '个设备离线', room: '' }] : [] } })
    })

    // 订单角度：待处理
    API.getAllOrders().then(function(orders) {
      if (!orders) return
      var todayStr = new Date().getFullYear() + '-' + String(new Date().getMonth()+1).padStart(2,'0') + '-' + String(new Date().getDate()).padStart(2,'0')
      var today = orders.filter(function(o) { return o.date === todayStr || (o.created && o.created.indexOf(todayStr) === 0) })
      var pendingPay = today.filter(function(o) { return o.status === 'Completed' && o.paymentMethod === 'Pending' })
      var reconCount = pendingPay.length
      self.setData({ reconciliation: { count: reconCount, items: reconCount > 0 ? [{ title: reconCount + '笔待收款' }] : [] } })
    })

    // 巡检
    STAFF_API.getInspections().then(function(insp) {
      var list = insp || []
      var todoInsp = 0
      for (var i = 0; i < list.length; i++) {
        if (list[i].status === 'InProgress' || list[i].status === 'Pending') todoInsp++
      }
      self.setData({ inspection: { count: todoInsp, items: todoInsp > 0 ? [{ title: todoInsp + '个巡检任务' }] : [] } })
    })

    // 客人取消申请
    try {
      var requests = wx.getStorageSync('mp_cancel_requests') || []
      var pendingReqs = []
      for (var i = 0; i < requests.length; i++) {
        if (requests[i].status === 'pending') pendingReqs.push(requests[i])
      }
      if (pendingReqs.length > 0) {
        self.setData({
          audit: { count: pendingReqs.length, items: pendingReqs.map(function(r) { return { title: '📋 取消申请·' + r.orderId, data: r } }) }
        })
      }
    } catch(e) {}
  },

  goTo: function(e) {
    var page = e.currentTarget.dataset.page
    var urls = {
      cleaning: '/pages/staff/staff-cleaning-task/staff-cleaning-task',
      reconciliation: '/pages/staff/staff-reconciliation/staff-reconciliation',
      alerts: '/pages/staff/staff-device-monitor/staff-device-monitor',
      inspection: '/pages/staff/staff-inspection/staff-inspection',
      audit: '/pages/staff/staff-order-management/staff-order-management'
    }
    var url = urls[page]
    if (url) wx.navigateTo({ url: url })
  }
})
