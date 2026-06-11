var STAFF_API = require('../../utils/staff-api')

var PAY_LABELS = { WeChat: '微信支付', Alipay: '支付宝', Balance: '会员余额', Coupon: '验券', Other: '其他' }

Page({
  data: {
    dateStr: '',
    data: { totalRevenue: 0, roomRevenue: 0, productRevenue: 0, orderCount: 0, couponDiscount: 0, pendingPayment: 0, paymentBreakdown: {} },
    payBreakdownList: []
  },

  onLoad: function() {
    var now = new Date()
    var dateStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
    this.setData({ dateStr: dateStr })
    this.loadData(dateStr)
  },

  loadData: function(dateStr) {
    var self = this
    STAFF_API.getReconciliationData(dateStr).then(function(data) {
      var list = []
      for (var key in data.paymentBreakdown) {
        list.push({ key: key, label: PAY_LABELS[key] || key, amount: data.paymentBreakdown[key] })
      }
      self.setData({ data: data, payBreakdownList: list })
    })
  },

  pickDate: function(e) {
    var dateStr = e.detail.value
    this.setData({ dateStr: dateStr })
    this.loadData(dateStr)
  },

  goBack: function() { wx.navigateBack() }
})
