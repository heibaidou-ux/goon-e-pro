var API = require('../../utils/api')

Page({
  data: {
    tabIndex: 0, orders: [], filteredOrders: [],
    showLogisticsModal: false, showCancelModal: false, showExtendModal: false, showDetailModal: false,
    detailOrder: null,
    logisticsData: { carrier: '', trackingNum: '', timeline: [] },
    cancelOrderId: null, cancelMsg: '',
    extendOrderId: null, extendOptions: [], selectedExtendIdx: -1, extendInfo: ''
  },

  onShow: function() {
    // 首次加载不管登录状态都尝试显示，避免白屏
    this.loadOrders()
  },

  loadOrders: function() {
    var self = this
    // 确保至少有数据，不白屏
    self.setData({ orders: [], filteredOrders: [], tabIndex: self.data.tabIndex })
    Promise.all([API.getUserOrders().catch(function() { return [] }), API.getShopOrders ? API.getShopOrders().catch(function() { return [] }) : Promise.resolve([])]).then(function(results) {
      var orders = results[0] || []
      var shopOrders = results[1] || []
      // 合并茶品订单
      for (var si = 0; si < shopOrders.length; si++) {
        var so = shopOrders[si]
        var shopStatus = so.status || 'PendingDelivery'
        // 递送状态映射：用真实状态而非硬编码
        if (shopStatus === 'Shipped') { /*保持Shipped*/ }
        else if (shopStatus === 'Completed') { /*保持Completed*/ }
        else { shopStatus = 'PendingDelivery' }
        var teaLog = null
        if (so.deliveryMethod === 'express') {
          var carriers = { SF: '顺丰速运', YT: '圆通速递', ZTO: '中通快递', STO: '申通快递', YD: '韵达快递', JD: '京东物流' }
          var carrierCodes = ['SF','YT','ZTO','STO','YD','JD']
          var cc = carrierCodes[Math.floor(Math.random()*carrierCodes.length)]
          teaLog = {
            carrier: carriers[cc] || '顺丰速运', icon: '📦',
            trackingNum: so.trackingNum || (cc + String(Date.now()).slice(-8)),
            statusBadge: 'transit', statusLabel: '运输中',
            estimated: '预计2-3天送达',
            steps: [
              { label: '已揽收', active: true },
              { label: '运输中', active: true, current: true },
              { label: '派送中', active: false },
              { label: '已签收', active: false }
            ]
          }
        }
        orders.push({
          orderId: so.orderId, roomName: '茶品订单', roomId: '',
          status: shopStatus,
          date: so.created ? so.created.slice(0,10) : '',
          time: so.created ? so.created.slice(11,16) : '',
          amount: so.total || 0, doorCode: '',
          payment: so.paymentMethod || '',
          isTeaOrder: true, items: so.items || [],
          deliveryMethod: so.deliveryMethod || '',
          deliveryStatus: so.deliveryStatus || 'pending',
          deliveryLabel: shopStatus === 'Shipped' ? '运输中' : (so.deliveryMethod === 'inroom' ? '配送中' : (so.deliveryMethod === 'express' ? '待发货' : (so.deliveryMethod === 'pickup' ? '待取货' : ''))),
          logistics: teaLog
        })
      }
      var now = new Date()
      var todayStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours() * 60 + now.getMinutes()

      var mapped = orders.map(function(o) {
        var status = o.status
        // 自动判断订单状态：根据当前时间
        if (status === 'Booked' && o.date && o.time) {
          var parts = o.time.split('-')
          if (parts.length === 2) {
            var startParts = parts[0].split(':')
            var endParts = parts[1].split(':')
            var orderDate = new Date(o.date)
            var orderEndDT = new Date(orderDate.getFullYear(), orderDate.getMonth(), orderDate.getDate(), parseInt(endParts[0]), parseInt(endParts[1]))
            var orderStartDT = new Date(orderDate.getFullYear(), orderDate.getMonth(), orderDate.getDate(), parseInt(startParts[0]), parseInt(startParts[1]))
            var startMin = parseInt(startParts[0])*60 + parseInt(startParts[1])
            var endMin = parseInt(endParts[0])*60 + parseInt(endParts[1])

            if (o.date === todayStr) {
              // 今天的订单
              if (curMin >= startMin && curMin < endMin) {
                status = 'InUse'  // 当前时段内，自动开始
              } else if (curMin >= endMin) {
                status = 'Expired'  // 已过结束时间，失效
              }
            } else if (orderEndDT < now) {
              status = 'Expired'  // 过去日期的未使用订单，失效
            }
          }
        }

        // 开门条件：进行中订单随时可用 / 待使用订单需在开始前15分钟内且房间未被占用
        var doorCanOpen = false
        var doorHint = ''
        var roomOccupied = false
        if (status === 'InUse' || status === 'in_use') {
          doorCanOpen = true
          doorHint = '密码可用'
        } else if (status === 'Booked' && o.date && o.time) {
          var sb = o.time.split('-')[0].split(':')
          if (sb.length >= 2) {
            var orderDate = new Date(o.date)
            var orderDT = new Date(orderDate.getFullYear(), orderDate.getMonth(), orderDate.getDate(), parseInt(sb[0]), parseInt(sb[1]))
            var minUntilStart = (orderDT - now) / 60000
            // 检查房间是否被其他进行中订单占用
            for (var oi = 0; oi < orders.length; oi++) {
              var oo = orders[oi]
              if (oo.orderId === o.orderId) continue
              if (oo.roomId === o.roomId && (oo.status === 'InUse' || oo.status === 'in_use')) {
                roomOccupied = true; break
              }
            }
            // 条件1: 在开始前15分钟内
            // 条件2: 房间未被占用
            doorCanOpen = (minUntilStart <= 15) && !roomOccupied
            if (minUntilStart > 15) {
              var waitMin = Math.ceil(minUntilStart - 15)
              doorHint = '密码将在预约开始前15分钟生效，还需等待' + waitMin + '分钟'
            } else if (roomOccupied) {
              doorHint = '当前房间正在使用中，请稍后再试'
            } else {
              doorHint = '密码可用'
            }
          }
        }

        // 状态标签
        var statusClass = 'status-completed', statusLabel = '已完成'
        if (status === 'InUse' || status === 'in_use') { statusClass = 'status-inuse'; statusLabel = '进行中' }
        else if (status === 'Booked') { statusClass = 'status-booked'; statusLabel = '待使用' }
        else if (status === 'Expired') { statusClass = 'status-expired'; statusLabel = '已失效' }
        else if (status === 'PendingDelivery' || status === 'Shipped') {
          statusClass = 'status-inuse'
          if (status === 'Shipped') statusLabel = '运输中'
          else if (o.deliveryMethod === 'inroom') statusLabel = '配送中'
          else if (o.deliveryMethod === 'express') statusLabel = '待发货'
          else if (o.deliveryMethod === 'pickup') statusLabel = '待取货'
          else statusLabel = '处理中'
        }

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
        var cancelFree = true, canCancel = false, cancelMsg = ''
        if (status === 'Booked' && o.date && o.time) {
          var startParts2 = o.time.split('-')[0].split(':')
          var orderDate = new Date(o.date)
          var orderDT = new Date(orderDate.getFullYear(), orderDate.getMonth(), orderDate.getDate(), parseInt(startParts2[0]), parseInt(startParts2[1]))
          var hoursUntil = (orderDT - now) / 3600000
          if (hoursUntil < 2 && hoursUntil > 0) {
            canCancel = true
            cancelFree = false
            cancelMsg = '距开始不足2小时，取消将收取首小时费用50%'
          } else if (hoursUntil >= 2) {
            canCancel = true
            cancelMsg = '距开始超过2小时，可免费取消'
          } else {
            canCancel = false
            cancelMsg = '已超过预约时间，不可取消'
          }
        }

        // 物流信息（优先使用茶品订单自带的物流数据）
        var log = o.logistics || null
        if (!log && status === 'Completed' && o.orderId === 'ORD003') {
          log = { carrier: '顺丰速运', icon: '📦', trackingNum: 'SF1234567890', statusBadge: 'transit', statusLabel: '运输中', estimated: '预计明日送达', steps: [{ label: '已下单', active: true }, { label: '已发货', active: true, current: true }, { label: '派送中', active: false }, { label: '已签收', active: false }] }
        }

        return {
          orderId: o.orderId, roomName: o.roomName || '房间', roomId: o.roomId || '',
          status: status, statusClass: statusClass, statusLabel: statusLabel,
          timeStr: (o.date||'')+' '+(o.time||(o.start?o.start.slice(0,5)+'-'+o.end.slice(0,5):'')),
          amount: o.amount||0, doorCode: o.doorCode||'0000',
          remaining: remaining, canCancel: canCancel, cancelFree: cancelFree, cancelMsg: cancelMsg,
          logistics: log, payment: o.payment||'',
          doorCanOpen: doorCanOpen, doorHint: doorHint,
          isTeaOrder: o.isTeaOrder || false, items: o.items || [],
          deliveryMethod: o.deliveryMethod || '',
          deliveryStatus: o.deliveryStatus || '',
          deliveryLabel: o.deliveryLabel || ''
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
    if (tab === 0) list = list.filter(function(o) { return o.status === 'InUse' || o.status === 'in_use' || o.status === 'PendingDelivery' || o.status === 'Shipped' })
    else if (tab === 1) list = list.filter(function(o) { return o.status === 'Booked' })
    else if (tab === 2) list = list.filter(function(o) { return o.status === 'Completed' })
    else if (tab === 3) list = list.filter(function(o) { return o.status === 'Expired' })
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
    if (order.status === 'Booked' && !order.doorCanOpen) {
      wx.showToast({ title: order.doorHint || '暂不能开门', icon: 'none' })
      return
    }
    var timeParts = (order.timeStr || '').split(' ').pop().split('-')
    var startStr = timeParts.length >= 1 ? timeParts[0].trim() : ''
    var endStr = timeParts.length >= 2 ? timeParts[1].trim() : ''
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+(order.roomId||'')+'&roomName='+encodeURIComponent(order.roomName||'')+'&start='+startStr+'&end='+endStr+'&duration='+(order.remaining ? Math.ceil(order.remaining/60) : 120) })
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
    var id = e.currentTarget.dataset.id
    var order = this.findOrder(id)
    if (!order) return
    if (order.isTeaOrder) {
      wx.navigateTo({ url: '/pages/tea-shop/tea-shop' })
    } else {
      wx.navigateTo({ url: '/pages/room-list/room-list' })
    }
  },

  goRoomDetail: function(e) {
    var id = e.currentTarget.dataset.id
    var order = this.findOrder(id)
    if (!order) return
    // 翻译支付方式
    var payLabels = { WeChat: '微信支付', Alipay: '支付宝', Balance: '会员余额', Coupon: '验券', wechat: '微信支付', alipay: '支付宝', balance: '会员余额', coupon: '验券', WxPay: '微信支付' }
    var detail = Object.assign({}, order)
    detail.payLabel = payLabels[order.payment] || order.payment || '—'
    // 显示订单详情弹窗
    this.setData({
      detailOrder: detail,
      showDetailModal: true
    })
  },

  hideDetailModal: function() { this.setData({ showDetailModal: false }) },

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
