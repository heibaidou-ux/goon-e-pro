var API = require('../../utils/api')

Page({
  data: { rooms: [] },

  onLoad: function() {
    var self = this
    // 强制重置滚动位置，防止前页残影
    wx.pageScrollTo({ scrollTop: 0, duration: 0 })
    // 原型内置4间房，优先展示
    var embedded = [
      { roomId:'RM001', name:'丰沙里', type:'MeetingRoom', capacity:10, area:30, facilities:['投影','会议桌','K歌设备','落地窗'], pricePerHour:200 },
      { roomId:'RM002', name:'翡冷翠', type:'TeaRoom', capacity:4, area:18, facilities:['茶台','落地窗','茶具套装'], pricePerHour:80 },
      { roomId:'RM003', name:'布拉格', type:'TeaRoom', capacity:4, area:18, facilities:['茶台','落地窗','茶具套装'], pricePerHour:80 },
      { roomId:'RM004', name:'白沙瓦', type:'TeaRoom', capacity:6, area:25, facilities:['茶台','K歌','投影','落地窗'], pricePerHour:120 },
    ]
    self.renderRooms(embedded)

    // 异步刷新(原型逻辑)
    API.getRooms(true).then(function(roomsData) {
      if (roomsData && roomsData.length) self.renderRooms(roomsData)
    })
  },

  // 原型 renderRoomList
  renderRooms: function(list) {
    var colors = { MeetingRoom:'#e3f2fd', TeaRoom:'#e8f5e9', Exhibition:'#fff3e0', Workspace:'#f5f5f5' }
    var icons = { MeetingRoom:'💼', TeaRoom:'🍵', Exhibition:'🏛️', Workspace:'🔧' }
    var rooms = []
    for (var i = 0; i < list.length; i++) {
      var r = list[i]
      if (r.bookable === false) continue
      var facilities = (r.facilities || []).join(' · ')
      var price = r.pricePerHour || (r.pricePerHalfHour || 60) * 2 || 120
      rooms.push({
        roomId: r.roomId, name: r.name,
        metaLine: (r.capacity || '—') + '人 · ' + (r.area || '—') + '㎡ · ' + facilities,
        pricePerHour: price,
        icon: icons[r.type] || '🏠',
        bgColor: colors[r.type] || '#f0f0f0'
      })
    }
    this.setData({ rooms: rooms })
  },

  // 原型 goRoom
  goRoom: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + roomId })
  },

  // 导航
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
