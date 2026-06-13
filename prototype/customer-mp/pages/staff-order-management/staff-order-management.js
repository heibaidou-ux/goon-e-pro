var API = require('../../utils/api')

Page({
  data: {
    tabIndex: 0,
    orders: [], filteredOrders: [],
    showDetail: false, detailOrder: null, editSource: '',
    showShipModal: false, shipOrder: null,
    shipName: '', shipAddress: '', shipCarrier: '', shipTrackingNum: '',
    sourceOptions: ['到店','美团','抖音','大众点评','高德地图','小红书','会小二','老客户','电话预约','其他']
  },

  onShow: function() {
    this.loadOrders()
  },

  loadOrders: function() {
    var self = this
    Promise.all([API.getUserOrders(), API.getShopOrders?API.getShopOrders():Promise.resolve([])]).then(function(results) {
      var orders = results[0]||[], shopOrders = results[1]||[]
      var now = new Date()
      var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours()*60+now.getMinutes()

      // 房间订单
      var roomOrders = orders.map(function(o) {
        var status = o.status||'Booked'
        if(status==='Booked'&&o.date===todayStr&&o.time){
          var p=o.time.split('-')
          if(p.length===2){var sm=parseInt(p[0].split(':')[0])*60+parseInt(p[0].split(':')[1]),em=parseInt(p[1].split(':')[0])*60+parseInt(p[1].split(':')[1]);if(curMin>=sm&&curMin<em)status='InUse';else if(curMin>=em)status='Completed'}
        }
        return{
          orderId:o.orderId,roomName:o.roomName||'房间',roomId:o.roomId||'',status:status,
          date:o.date||'',time:o.time||'',amount:o.amount||0,customerName:o.customerName||'',
          phone:o.phone||'',customerSource:o.customerSource||'',isRoomOrder:true,isTeaOrder:false,
          statusClass:status==='InUse'?'status-inuse':(status==='Booked'?'status-booked':'status-completed'),
          statusLabel:status==='InUse'?'进行中':(status==='Booked'?'已预订':'已完成')
        }
      })

      // 茶品订单
      for(var si=0;si<shopOrders.length;si++){
        var so=shopOrders[si]
        var shopStatus='PendingDelivery'
        if(so.deliveryMethod==='inroom'||so.deliveryMethod==='pickup')shopStatus='PendingDelivery'
        else if(so.deliveryMethod==='express')shopStatus='PendingDelivery'
        roomOrders.push({
          orderId:so.orderId,roomName:'茶品订单',roomId:'',status:shopStatus,isRoomOrder:false,isTeaOrder:true,
          date:so.created?so.created.slice(0,10):'',time:so.created?so.created.slice(11,16):'',
          amount:so.total||0,customerName:'',phone:'',customerSource:'',
          deliveryMethod:so.deliveryMethod||'',deliveryLabel:so.deliveryMethod==='inroom'?'配送中':(so.deliveryMethod==='express'?'待发货':(so.deliveryMethod==='pickup'?'待取货':'')),
          trackingNum:so.trackingNum||'',statusClass:'status-inuse',statusLabel:'待处理'
        })
      }

      self.setData({orders:roomOrders})
      self.filterOrders()
    })
  },

  filterOrders: function() {
    var tab = this.data.tabIndex
    var list = this.data.orders
    if(tab===0)list=list.filter(function(o){return o.status==='InUse'||o.status==='PendingDelivery'})
    else if(tab===1)list=list.filter(function(o){return o.status==='Booked'})
    else if(tab===2)list=list.filter(function(o){return o.status==='Completed'})
    this.setData({filteredOrders:list})
  },

  switchTab: function(e) {
    this.setData({tabIndex:parseInt(e.currentTarget.dataset.tab)})
    this.filterOrders()
  },

  showOrderDetail: function(e) {
    var id=e.currentTarget.dataset.id,orders=this.data.orders
    for(var i=0;i<orders.length;i++){if(orders[i].orderId===id){this.setData({showDetail:true,detailOrder:orders[i],editSource:orders[i].customerSource||''});break}}
  },

  onSourceChange: function(e) {this.setData({editSource:this.data.sourceOptions[e.detail.value]})},

  saveSource: function() {
    var order=this.data.detailOrder,source=this.data.editSource
    if(!order||!source){wx.showToast({title:'请选择客户来源',icon:'none'});return}
    try{var bk=wx.getStorageSync('mp_bookings')||[];for(var i=0;i<bk.length;i++){if(bk[i].orderId===order.orderId){bk[i].customerSource=source;break}};wx.setStorageSync('mp_bookings',bk)}catch(e){}
    wx.showToast({title:'已保存',icon:'success'})
    this.setData({showDetail:false})
    this.loadOrders()
  },

  hideDetail: function(){this.setData({showDetail:false})},

  // ── 发货 ──
  shipOrder: function(e) {
    var id=e.currentTarget.dataset.id
    var orders=this.data.orders
    for(var i=0;i<orders.length;i++){
      if(orders[i].orderId===id){
        this.setData({
          showShipModal:true,shipOrder:orders[i],
          shipCarrier:'',shipTrackingNum:'',
          shipName:'',shipAddress:''
        })
        break
      }
    }
  },

  onShipCarrier: function(e){this.setData({shipCarrier:e.detail.value})},
  onShipTrackingNum: function(e){this.setData({shipTrackingNum:e.detail.value})},

  confirmShip: function() {
    var self=this,order=self.data.shipOrder
    var carrier=self.data.shipCarrier||'顺丰速运'
    var tracking=self.data.shipTrackingNum||('SF'+String(Date.now()).slice(-8))
    if(!tracking){wx.showToast({title:'请输入运单号',icon:'none'});return}
    try{
      var shop=wx.getStorageSync('mp_shop_orders')||[]
      for(var i=0;i<shop.length;i++){if(shop[i].orderId===order.orderId){shop[i].trackingNum=tracking;shop[i].carrier=carrier;shop[i].status='Shipped';break}}
      wx.setStorageSync('mp_shop_orders',shop)
    }catch(e){}
    wx.showToast({title:'✅ 已发货 运单号:'+tracking,icon:'success'})
    this.setData({showShipModal:false})
    this.loadOrders()
  },

  hideShipModal: function(){this.setData({showShipModal:false})},

  // ── 配送完成 ──
  completeDelivery: function(e) {
    var self=this,id=e.currentTarget.dataset.id
    wx.showModal({
      title:'确认配送完成',content:'确认已完成配送/取货？',
      success:function(res){if(res.confirm){
        try{var shop=wx.getStorageSync('mp_shop_orders')||[];for(var i=0;i<shop.length;i++){if(shop[i].orderId===id){shop[i].status='Completed';break}};wx.setStorageSync('mp_shop_orders',shop)}catch(e){}
        wx.showToast({title:'配送已完成',icon:'success'});self.loadOrders()
      }}
    })
  },

  checkIn: function(e){wx.showToast({title:'已办理入住',icon:'success'})},
  completeOrder: function(e){wx.showToast({title:'订单已完成',icon:'success'})}
})
