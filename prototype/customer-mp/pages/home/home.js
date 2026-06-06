const API = require('../../utils/api')

Page({
  data: {
    hasActiveOrder: false,
    activeOrder: { roomName: '', startTime: '', endTime: '' },
    balance: 0,
    rooms: [],
    carousels: [
      { title: '新茶上市 · 明前龙井', desc: '限时尝鲜价 ¥68/份', color1: '#5D8A6B', color2: '00a854' },
      { title: '会员充值赠30%', desc: '新会员首充即享额外赠送', color1: '#B8860B', color2: 'D4A84B' },
      { title: '盈隆店 · 新客专享', desc: '首次预约享8折优惠', color1: '#7A8B8B', color2: 'A3B5B5' }
    ]
  },

  onLoad() {
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  loadData() {
    // 加载推荐房间
    API.getRooms(true).then(rooms => {
      this.setData({ rooms: rooms.filter(r => r.bookable !== false).slice(0, 6) })
    })

    // 加载用户信息
    const user = API.getCurrentUser()
    if (user) {
      API.getBalance().then(balance => this.setData({ balance }))
    }

    // 检查是否有进行中订单
    API.getUserOrders().then(orders => {
      const active = orders.find(o => o.status === 'InUse' || o.status === 'Booked')
      if (active) {
        this.setData({
          hasActiveOrder: true,
          activeOrder: {
            roomName: active.roomName || '',
            startTime: active.start ? active.start.slice(11, 16) : '',
            endTime: active.end ? active.end.slice(11, 16) : ''
          }
        })
      }
    })
  },

  goRoomList() { wx.switchTab({ url: '/pages/room-list/room-list' }) },
  goTeaShop() { wx.switchTab({ url: '/pages/tea-shop/tea-shop' }) },
  goMyCoupons() { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },
  goMember() { wx.switchTab({ url: '/pages/member-center/member-center' }) },

  goRoomDetail(e) {
    const roomId = e.currentTarget.dataset.roomid
    wx.navigateTo({ url: `/pages/room-detail/room-detail?roomId=${roomId}` })
  },

  goRoomControl() {
    const active = this.data.activeOrder
    if (active.roomName) {
      wx.navigateTo({ url: `/pages/room-control/room-control?roomId=${active.roomId || ''}` })
    }
  },

  goScanOrder() {
    wx.navigateTo({ url: '/pages/scan-landing/scan-landing' })
  },

  switchStore() {
    wx.showToast({ title: '当前仅盈隆店', icon: 'none' })
  }
})
