var API = require('../../utils/api')

Page({
  data: {
    roomId: '', loading: true, error: false, errorMsg: '',
    billData: { roomName: '', roomCharge: 0, scanTotal: 0, pendingPayment: 0, orders: [], activeOrderId: '' },
    showSettleSheet: false,
    settlePaymentIndex: 0,
    settlePaymentList: ['微信支付', '会员余额']
  },

  onLoad: function(e) {
    var roomId = e.room_id || ''
    this.setData({ roomId: roomId })
    this.loadBill()
  },

  loadBill: function() {
    var self = this
    this.setData({ loading: true, error: false })
    API.getScanBill(this.data.roomId).then(function(bill) {
      self.setData({
        loading: false,
        billData: {
          roomName: bill.roomName || bill.roomName || '',
          roomCharge: bill.billSummary ? bill.billSummary.roomCharge : (bill.roomCharge || 0),
          scanTotal: bill.billSummary ? bill.billSummary.scanTotal : (bill.scanTotal || 0),
          pendingPayment: bill.billSummary ? bill.billSummary.pendingPayment : (bill.pendingPayment || 0),
          activeOrderId: bill.activeOrderId || '',
          orders: bill.scanOrders ? bill.scanOrders.map(function(o) {
            return {
              orderId: o.orderId,
              time: o.createdAt ? o.createdAt.replace('T', ' ').slice(0, 16) : '',
              status: o.status || '挂账中',
              statusClass: o.status === '已撤销' ? 'cancelled' : '',
              items: (o.items || []).map(function(i) {
                return { name: i.productName || i.name, qty: i.quantity || i.qty || 1, subtotal: (i.subtotal || i.unitPrice * i.quantity || 0).toFixed(2) }
              }),
              totalAmount: o.totalAmount.toFixed(2),
              canCancel: o.canCancel !== false
            }
          }) : []
        }
      })
    }).catch(function(err) {
      self.setData({ loading: false, error: true, errorMsg: err.message || '加载账单失败' })
    })
  },

  cancelOrder: function(e) {
    var id = e.currentTarget.dataset.id
    var self = this
    wx.showModal({ title: '确认撤销', content: '撤销后商品将从挂账中移除，库存自动回滚。', success: function(res) {
      if (res.confirm) {
        API.cancelScanOrder(id).then(function() {
          wx.showToast({ title: '✅ 已撤销', icon: 'success' })
          self.loadBill()
        }).catch(function(err) {
          wx.showToast({ title: err.message || '撤销失败', icon: 'none' })
        })
      }
    }})
  },

  showSettle: function() {
    this.setData({ showSettleSheet: true })
  },

  hideSettle: function() {
    this.setData({ showSettleSheet: false })
  },

  preventBubble: function() {},

  onSettlePaymentChange: function(e) {
    this.setData({ settlePaymentIndex: e.detail.value })
  },

  doSettle: function() {
    var methods = ['WxPay', 'AliPay', 'MemberBalance']
    var paymentMethod = methods[this.data.settlePaymentIndex]
    var self = this
    wx.showLoading({ title: '结算中...' })
    API.settleScanBill(this.data.roomId, { paymentMethod: paymentMethod }).then(function(r) {
      wx.hideLoading()
      self.setData({ showSettleSheet: false })
      wx.showToast({ title: '✅ 结算成功 ¥' + (r.totalAmount || r.paymentAmount || 0).toFixed(2), icon: 'none', duration: 2000 })
      self.loadBill()
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '结算失败', icon: 'none' })
    })
  }
})
