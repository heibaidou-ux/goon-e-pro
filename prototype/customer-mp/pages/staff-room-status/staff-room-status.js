var API = require('../../utils/api')
Page({
  data:{rooms:[]},
  onShow:function(){
    var self=this
    API.getRooms(true).then(function(rooms){
      var icons={MeetingRoom:'💼',TeaRoom:'🍵',Exhibition:'🏛️',Workspace:'🔧'}
      API.getUserOrders().then(function(orders){
        var inuse={}
        for(var i=0;i<orders.length;i++){if(orders[i].status==='InUse')inuse[orders[i].roomId]=orders[i].time||''}
        self.setData({rooms:rooms.map(function(r){
          var iu=!!inuse[r.roomId]
          return{roomId:r.roomId,name:r.name,icon:icons[r.type]||'🏠',statusClass:iu?'inuse':'available',statusLabel:iu?'使用中':'空闲',time:inuse[r.roomId]||''}
        })})
      })
    })
  },
  goRoom:function(e){wx.navigateTo({url:'/pages/room-control/room-control?roomId='+e.currentTarget.dataset.roomid})}
})
