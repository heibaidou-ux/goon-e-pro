var API = require('../../utils/api')

Page({
  data: { roomId: '', billData: { roomName: '', roomCharge: 0, scanTotal: 0, pendingPayment: 0, orders: [] } },

  onLoad: function(e) {
    var roomId = e.room_id || ''
    this.setData({ roomId: roomId })
    var self = this
    API.getScanBill(roomId).then(function(bill) {
      self.setData({ billData: bill })
    }).catch(function() {
      wx.showToast({ title: '加载账单失败', icon: 'none' })
    })
  },

  cancelOrder: function(e) {
    var id = e.currentTarget.dataset.id
    wx.showModal({ title: '确认撤销', content: '确定撤销此订单？商品将从挂账中移除', success: function(res) {
      if (res.confirm) {
        API.cancelScanOrder(id).then(function() {
          wx.showToast({ title: '✅ 已撤销', icon: 'success' })
        }).catch(function() {})
      }
    }})
  },

  settleBill: function() {
    var self = this
    wx.showActionSheet({ itemList: ['微信支付', '支付宝', '会员余额'], success: function(res) {
      var methods = ['WxPay', 'AliPay', 'MemberBalance']
      API.settleScanBill(self.data.roomId, { paymentMethod: methods[res.tapIndex] }).then(function(r) {
        wx.showToast({ title: '✅ 结算成功 ¥' + r.totalAmount.toFixed(2), icon: 'none', duration: 2000 })
      }).catch(function() {
        wx.showToast({ title: '结算失败', icon: 'none' })
      })
    }})
  }
})
