var API = require('../../utils/api')

Page({
  data: { loading: true, verified: false, roomId: '', roomName: '', errorTitle: '', errorMsg: '',
    billSummary: { roomCharge: 0, scanTotal: 0, pendingPayment: 0 } },

  onLoad: function(e) {
    var roomId = e.room_id || e.roomId || 'RM004'
    this.setData({ roomId: roomId })
    var self = this
    API.scanRoomStatus(roomId).then(function(info) {
      if (info.hasActiveOrder && info.status == 'Active') {
        self.setData({ loading: false, verified: true, roomName: info.roomName })
        API.getScanBill(roomId).then(function(bill) {
          self.setData({ billSummary: bill.billSummary })
        }).catch(function(){})
      } else {
        self.setData({ loading: false, errorTitle: '房间不可用', errorMsg: info.message || '请联系店员开房后再扫码' })
      }
    }).catch(function(err) {
      self.setData({ loading: false, errorTitle: '验证失败', errorMsg: err.message || '网络异常' })
    })
  },

  goOrder: function() { wx.navigateTo({ url: '/pages/scan-order/scan-order?room_id=' + this.data.roomId }) },
  goBill: function() { wx.navigateTo({ url: '/pages/scan-bill/scan-bill?room_id=' + this.data.roomId }) },
  callStaff: function() { wx.showToast({ title: '前台电话：020-88888888', icon: 'none' }) }
})
