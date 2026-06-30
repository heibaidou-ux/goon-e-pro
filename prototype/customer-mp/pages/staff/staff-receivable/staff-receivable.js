Page({
  data: { totalReceivable: 0, totalSettled: 0, totalPending: 0, orderCount: 0, bills: [] },
  onShow: function() { this.loadData() },
  loadData: function() {
    var API = require('../../../utils/api')
    var self = this
    (API.getAllOrders ? API.getAllOrders() : API.getUserOrders()).then(function(orders) {
      var total=0,pending=0,settled=0
      for(var i=0;i<orders.length;i++){total+=orders[i].amount||0;if(orders[i].status==='Booked'||orders[i].status==='InUse')pending+=orders[i].amount||0;else settled+=orders[i].amount||0}
      var bills=orders.filter(function(o){return o.status==='InUse'||o.status==='Booked'}).slice(0,10).map(function(o){
        return{billId:o.orderId,roomName:o.roomName||'房间',amount:o.amount||0,date:o.date||'',time:o.time||'',status:'pending',statusLabel:o.status==='InUse'?'使用中':'待入住'}
      })
      self.setData({totalReceivable:total,totalSettled:settled,totalPending: pending,orderCount:orders.length,bills:bills})
    })
  },
  settleBill:function(e){wx.showToast({title:'结算成功',icon:'success'})},
  showBillDetail:function(e){wx.showToast({title:'查看详情',icon:'none'})}
})
