var API = require('../../../utils/api')

Page({
  data: {
    orderType: 0, // 0=房间, 1=茶品
    tabIndex: 0,
    orders: [], filteredOrders: [],
    showDetail: false, detailOrder: null, editSource: '',
    showShipModal: false, shipOrder: null,
    shipName: '', shipAddress: '', shipCarrier: '', shipTrackingNum: '',
    sourceOptions: ['到店','美团','抖音','大众点评','高德地图','小红书','会小二','老客户','电话预约','其他'],
    searchKeyword: '', showSearch: false,
    tabCounts: [0,0,0,0]
  },

  onShow: function() { this.loadOrders() },

  loadOrders: function() {
    var self = this
    Promise.all([API.getAllOrders(), API.getShopOrders?API.getShopOrders():Promise.resolve([])]).then(function(results) {
      var orders = results[0]||[], shopOrders = results[1]||[]
      var now = new Date()
      var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours()*60+now.getMinutes()

      // 房间订单
      var roomOrders = orders.map(function(o) {
        var status = o.status||'Booked'
        if(status==='Booked'&&o.date&&o.time){
          var p=o.time.split('-')
          if(p.length===2){
            var sm=parseInt(p[0].split(':')[0])*60+parseInt(p[0].split(':')[1]),em=parseInt(p[1].split(':')[0])*60+parseInt(p[1].split(':')[1])
            if(o.date===todayStr){if(curMin>=em)status='Expired'}
            else if(new Date(o.date)<new Date(todayStr)) status='Expired'
          }
        }
        var sc='status-completed',sl='已完成'
        if(status==='InUse'){sc='status-inuse';sl='进行中'}
        else if(status==='Booked'){sc='status-booked';sl='已预订'}
        else if(status==='Expired'){sc='status-expired';sl='已失效'}
        return{
          orderId:o.orderId,roomName:o.roomName||'房间',roomId:o.roomId||'',status:status,
          date:o.date||'',time:o.time||'',amount:o.amount||0,customerName:o.customerName||'',
          phone:o.phone||'',customerSource:o.customerSource||'',orderType:'room',
          statusClass:sc,statusLabel:sl
        }
      })

      // 茶品订单(按配送方式分类)
      for(var si=0;si<shopOrders.length;si++){
        var so=shopOrders[si]
        var shopStatus = so.status||'PendingDelivery'
        if(shopStatus==='Shipped')shopStatus='Shipped'
        else if(shopStatus==='Completed')shopStatus='Completed'
        else shopStatus='PendingDelivery'
        var method = so.deliveryMethod||'pickup'
        var methodLabel = method==='express'?'快递':(method==='inroom'?'店内消费':'自取')
        roomOrders.push({
          orderId:so.orderId,roomName:'茶品',roomId:'',status:shopStatus,orderType:'tea',
          date:so.created?so.created.slice(0,10):'',time:so.created?so.created.slice(11,16):'',
          amount:so.total||0,customerName:'',phone:'',customerSource:'',
          deliveryMethod:method,deliveryLabel:methodLabel,
          trackingNum:so.trackingNum||'',items:so.items||[],
          statusClass:shopStatus==='Completed'||shopStatus==='Shipped'?'status-completed':'status-inuse',
          statusLabel:shopStatus==='Completed'?'已完成':(shopStatus==='Shipped'?'已发货':'待处理')
        })
      }

      self.setData({orders:roomOrders})
      self.filterOrders()
    })
  },

  switchOrderType: function(e) {
    this.setData({orderType:parseInt(e.currentTarget.dataset.type),tabIndex:0,searchKeyword:''})
    this.filterOrders()
  },

  switchTab: function(e) {
    this.setData({tabIndex:parseInt(e.currentTarget.dataset.tab),searchKeyword:''})
    this.filterOrders()
  },

  filterOrders: function() {
    var type = this.data.orderType, tab = this.data.tabIndex
    var list = this.data.orders.filter(function(o){return type===0 ? o.orderType==='room' : o.orderType==='tea'})

    if(type===0){
      // 房间订单按状态
      if(tab===0)list=list.filter(function(o){return o.status==='InUse'})
      else if(tab===1)list=list.filter(function(o){return o.status==='Booked'})
      else if(tab===2)list=list.filter(function(o){return o.status==='Completed'})
      else if(tab===3)list=list.filter(function(o){return o.status==='Expired'})
    }else{
      // 茶品订单按配送方式
      if(tab===0)list=list.filter(function(o){return o.deliveryMethod==='express'&&o.status!=='Completed'})
      else if(tab===1)list=list.filter(function(o){return o.deliveryMethod==='pickup'&&o.status!=='Completed'})
      else if(tab===2)list=list.filter(function(o){return o.deliveryMethod==='inroom'&&o.status!=='Completed'})
      else if(tab===3)list=list.filter(function(o){return o.status==='Completed'})
    }

    var kw=this.data.searchKeyword.trim()
    if(kw)list=list.filter(function(o){return(o.customerName&&o.customerName.indexOf(kw)>=0)||(o.phone&&o.phone.indexOf(kw)>=0)||(o.date&&o.date.indexOf(kw)>=0)})

    // 计算各Tab统计（用于角标）
    var type = this.data.orderType
    var allList = this.data.orders.filter(function(o){return type===0 ? o.orderType==='room' : o.orderType==='tea'})
    var counts = [0,0,0,0]
    if(type===0){
      for(var i=0;i<allList.length;i++){
        var s=allList[i].status
        if(s==='InUse')counts[0]++;else if(s==='Booked')counts[1]++;else if(s==='Completed')counts[2]++;else if(s==='Expired')counts[3]++
      }
    }else{
      for(var i=0;i<allList.length;i++){
        var m=allList[i].deliveryMethod
        if(allList[i].status==='Completed')counts[3]++
        else if(m==='express')counts[0]++;else if(m==='pickup')counts[1]++;else if(m==='inroom')counts[2]++
      }
    }
    this.setData({filteredOrders:list,tabCounts:counts})
  },

  toggleSearch: function(){this.setData({showSearch:!this.data.showSearch,searchKeyword:''})},
  onSearchInput: function(e){this.setData({searchKeyword:e.detail.value})},
  doSearch: function(){this.filterOrders()},

  showOrderDetail: function(e) {
    var id=e.currentTarget.dataset.id,orders=this.data.orders
    for(var i=0;i<orders.length;i++){if(orders[i].orderId===id){this.setData({showDetail:true,detailOrder:orders[i],editSource:orders[i].customerSource||''});break}}
  },

  onSourceChange: function(e){this.setData({editSource:this.data.sourceOptions[e.detail.value]})},

  saveSource: function() {
    var order=this.data.detailOrder,source=this.data.editSource
    if(!order||!source){wx.showToast({title:'请选择客户来源',icon:'none'});return}
    try{var bk=wx.getStorageSync('mp_bookings')||[];for(var i=0;i<bk.length;i++){if(bk[i].orderId===order.orderId){bk[i].customerSource=source;break}};wx.setStorageSync('mp_bookings',bk)}catch(e){}
    wx.showToast({title:'已保存',icon:'success'});this.setData({showDetail:false});this.loadOrders()
  },

  hideDetail: function(){this.setData({showDetail:false})},

  // ── 发货 ──
  shipOrder: function(e) {
    var id=e.currentTarget.dataset.id;var orders=this.data.orders
    for(var i=0;i<orders.length;i++){if(orders[i].orderId===id){this.setData({showShipModal:true,shipOrder:orders[i],shipCarrier:'',shipTrackingNum:'',shipName:'',shipAddress:''});break}}
  },
  onShipCarrier: function(e){this.setData({shipCarrier:e.detail.value})},
  onShipTrackingNum: function(e){this.setData({shipTrackingNum:e.detail.value})},

  confirmShip: function() {
    var self=this,order=self.data.shipOrder
    var carrier=self.data.shipCarrier||'顺丰速运',tracking=self.data.shipTrackingNum||('SF'+String(Date.now()).slice(-8))
    if(!tracking){wx.showToast({title:'请输入运单号',icon:'none'});return}
    try{var shop=wx.getStorageSync('mp_shop_orders')||[];for(var i=0;i<shop.length;i++){if(shop[i].orderId===order.orderId){shop[i].trackingNum=tracking;shop[i].carrier=carrier;shop[i].status='Shipped';break}};wx.setStorageSync('mp_shop_orders',shop)}catch(e){}
    wx.showToast({title:'✅ 已发货',icon:'success'});this.setData({showShipModal:false});this.loadOrders()
  },
  hideShipModal: function(){this.setData({showShipModal:false})},

  completeDelivery: function(e) {
    var self=this,id=e.currentTarget.dataset.id
    wx.showModal({title:'确认完成',content:'确认已完成？',
      success:function(res){if(res.confirm){
        try{var shop=wx.getStorageSync('mp_shop_orders')||[];for(var i=0;i<shop.length;i++){if(shop[i].orderId===id){shop[i].status='Completed';break}};wx.setStorageSync('mp_shop_orders',shop)}catch(e){}
        wx.showToast({title:'已完成',icon:'success'});self.loadOrders()
      }}
    })
  },

  checkIn: function(e){
    var id=e.currentTarget.dataset.id,orders=this.data.orders,roomId=''
    for(var i=0;i<orders.length;i++){if(orders[i].orderId===id||orders[i].id===id){roomId=orders[i].roomId||'';break}}
    if(roomId){var api=require('../../../utils/api');api.executeScene(roomId,'Welcome').catch(function(){})}
    wx.showToast({title:'已办理入住',icon:'success'})
  },
  completeOrder: function(e){wx.showToast({title:'订单已完成',icon:'success'})}
})
