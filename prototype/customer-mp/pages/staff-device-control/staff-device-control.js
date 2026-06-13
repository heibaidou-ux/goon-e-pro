var API=require('../../utils/api')
Page({
  data:{currentRoomId:'RM001',currentRoomName:'大会议室',roomNames:['大会议室','中茶室A','中茶室B','大茶室C'],devices:[]},
  onShow:function(){this.loadDevices(this.data.currentRoomId)},
  switchRoom:function(e){
    var rooms=['RM001','RM002','RM003','RM004'],names=['大会议室','中茶室A','中茶室B','大茶室C']
    this.setData({currentRoomId:rooms[e.detail.value],currentRoomName:names[e.detail.value]})
    this.loadDevices(rooms[e.detail.value])
  },
  loadDevices:function(roomId){
    var self=this
    API.getRoomDevices(roomId).then(function(devices){
      var labels={Light:'灯光',AC:'空调',Fan:'风扇',ExhaustFan:'换气扇',Curtain:'窗帘',BGM:'背景音乐'}
      var icons={Light:'💡',AC:'❄️',Fan:'🌀',ExhaustFan:'🌬️',Curtain:'🪟',BGM:'🎵'}
      for(var i=0;i<devices.length;i++){
        devices[i].typeLabel=labels[devices[i].type]||devices[i].type;devices[i].typeIcon=icons[devices[i].type]||'📡'
        if(devices[i].type==='Light')devices[i].on=(devices[i].brightness||0)>0
        else if(devices[i].type==='Fan'||devices[i].type==='ExhaustFan')devices[i].on=(devices[i].speed||0)>0
        else if(devices[i].type==='AC')devices[i].on=devices[i].mode==='cool'
        else if(devices[i].type==='BGM')devices[i].on=devices[i].playing
      }
      self.setData({devices:devices})
    })
  },
  toggleDevice:function(e){API.controlDevice(e.currentTarget.dataset.id,{}).catch(function(){})}
})
