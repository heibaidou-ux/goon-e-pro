var API = require('../../utils/api')

Page({
  data: {
    rooms: [],
    dateOptions: [],
    selectedDateIdx: 0,
    currentDate: ''
  },

  onLoad: function() {
    var self = this
    wx.pageScrollTo({ scrollTop: 0, duration: 0 })
    self.generateDateOptions()

    var embedded = [
      { roomId:'RM001', name:'丰沙里', type:'MeetingRoom', capacity:10, area:30, facilities:['投影','会议桌','K歌设备','落地窗'], pricePerHour:200 },
      { roomId:'RM002', name:'翡冷翠', type:'TeaRoom', capacity:4, area:18, facilities:['茶台','落地窗','茶具套装'], pricePerHour:80 },
      { roomId:'RM003', name:'布拉格', type:'TeaRoom', capacity:4, area:18, facilities:['茶台','落地窗','茶具套装'], pricePerHour:80 },
      { roomId:'RM004', name:'白沙瓦', type:'TeaRoom', capacity:6, area:25, facilities:['茶台','K歌','投影','落地窗'], pricePerHour:120 },
    ]
    self.renderRooms(embedded)
    API.getRooms(true).then(function(roomsData) {
      if (roomsData && roomsData.length) self.renderRooms(roomsData)
    })
  },

  generateDateOptions: function() {
    var options = []
    var weekNames = ['日','一','二','三','四','五','六']
    var today = new Date()
    for (var i = 0; i < 7; i++) {
      var d = new Date(today)
      d.setDate(today.getDate() + i)
      var m = String(d.getMonth() + 1).padStart(2, '0')
      var day = String(d.getDate()).padStart(2, '0')
      var week = i === 0 ? '今天' : weekNames[d.getDay()]
      options.push({
        week: week,
        date: day,
        month: m + '月',
        full: d.getFullYear() + '-' + m + '-' + day,
        isToday: i === 0
      })
    }
    this.setData({
      dateOptions: options,
      selectedDateIdx: 0,
      currentDate: options[0].full
    })
  },

  selectDate: function(e) {
    var idx = parseInt(e.currentTarget.dataset.idx)
    this.setData({
      selectedDateIdx: idx,
      currentDate: this.data.dateOptions[idx].full
    })
  },

  showMoreDates: function() {
    var self = this
    var options = self.data.dateOptions
    var list = []
    for (var i = 0; i < options.length; i++) {
      list.push(options[i].week + ' ' + options[i].month + options[i].date)
    }
    wx.showActionSheet({
      itemList: list,
      success: function(res) {
        if (res.tapIndex !== undefined) {
          self.setData({
            selectedDateIdx: res.tapIndex,
            currentDate: options[res.tapIndex].full
          })
        }
      }
    })
  },

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

  goRoom: function(e) {
    var roomId = e.currentTarget.dataset.roomid
    wx.navigateTo({
      url: '/pages/room-detail/room-detail?roomId=' + roomId + '&date=' + this.data.currentDate
    })
  },

  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
