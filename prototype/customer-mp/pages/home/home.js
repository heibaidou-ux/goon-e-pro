var API = require('../../utils/api')
var app = getApp()

Page({
  data: {
    hasActiveOrder: false,
    activeOrder: { roomName: '', timeStr: '', roomId: '' },
    balance: 0,
    balanceVisible: true,
    balanceDisplay: '¥0',
    carousels: [
      { title: '高岸茶室', desc: '城市中的静谧茶空间 · 商务社交新选择', img: '../../images/中英文标题LOGO-蓝天白云-16比9-A.jpg', color1: '#5D8A6B', color2: '#7BA88E' },
      { title: '会员首充特惠', desc: '首充享7折 + 赠送优惠券包，锁定超值体验', img: '../../images/头图四-店面招牌.jpg', color1: '#B8860B', color2: '#D4A84B' },
      { title: '精选包间', desc: '大茶室 · 会议室 · 中茶室 · 满足不同需求', img: '../../images/茶荟头图-空间-诗梳风大茶室.jpg', color1: '#5D8A6B', color2: '#7BA88E' },
      { title: '优惠券大放送', desc: '领取专属优惠券，到店享更多折扣', img: '../../images/金德大诗梳风004.jpg', color1: '#B8860B', color2: '#D4A84B' }
    ],
    rooms: [],
    teaProducts: [],
    cartCount: 0,
    showStoreModal: false,
    showParkingModal: false,
    showProductModal: false,
    productDetail: {}
  },

  onLoad: function() {
    this.initPage()
  },

  onShow: function() {
    this.loadCartCount()
    this.loadBalance()
    this.checkActiveOrder()
  },

  initPage: function() {
    this.loadRooms()
    this.loadTeaProducts()
    this.loadBalance()
    this.checkActiveOrder()
    this.loadCartCount()
  },

  loadRooms: function() {
    var self = this
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    API.getRooms(true).then(function(roomsData) {
      var rooms = []
      for (var i = 0; i < roomsData.length; i++) {
        var r = roomsData[i]
        if (r.bookable === false) continue
        rooms.push({
          roomId: r.roomId, name: r.name,
          capacity: r.capacity, area: r.area,
          facilities: (r.facilities || []).join(' · '),
          pricePerHour: r.pricePerHour || 120,
          icon: icons[r.type] || '🏠',
          bgColor: colors[r.type] || '#f0f0f0'
        })
      }
      self.setData({ rooms: rooms })
    })
  },

  loadTeaProducts: function() {
    var self = this
    var visualMap = {
      'T001': { icon: '🍃', bg: '#e8f5e9' }, 'T002': { icon: '🪵', bg: '#fce4ec' },
      'T003': { icon: '🏔️', bg: '#fff3e0' }, 'T004': { icon: '🌿', bg: '#efebe9' },
      'T005': { icon: '🏵️', bg: '#f1f8e9' }, 'T006': { icon: '🏔️', bg: '#efebe9' },
      'T007': { icon: '🏺', bg: '#f3e5f5' }, 'T008': { icon: '🥃', bg: '#e0f7fa' }
    }
    API.getProducts().then(function(productsData) {
      var teas = []
      for (var i = 0; i < productsData.length; i++) {
        var t = productsData[i]
        var vis = visualMap[t.productId] || { icon: '🍵', bg: '#f0f0f0' }
        teas.push({
          productId: t.productId, name: t.name, desc: t.desc || '',
          price: t.price, icon: vis.icon, bg: vis.bg, _qty: 0
        })
      }
      self.setData({ teaProducts: teas })
    })
  },

  checkActiveOrder: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var active = null
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].status === 'InUse' || orders[i].status === 'Booked') {
          active = orders[i]; break
        }
      }
      if (active) {
        self.setData({
          hasActiveOrder: true,
          activeOrder: {
            roomName: active.roomName || '大茶室C',
            roomId: active.roomId || '',
            timeStr: (active.date || '') + ' ' + (active.time || '')
          }
        })
      }
    })
  },

  loadBalance: function() {
    var self = this
    API.getBalance().then(function(b) {
      var bal = b || 0
      if (bal !== self.data.balance) {
        self.setData({ balance: bal })
        self.updateBalanceDisplay()
      }
    })
  },

  updateBalanceDisplay: function() {
    var bal = this.data.balance
    if (this.data.balanceVisible) {
      this.setData({ balanceDisplay: '¥' + bal })
    } else {
      this.setData({ balanceDisplay: '****' })
    }
  },

  toggleBalance: function(e) {
    if (e) e.stopPropagation ? e.stopPropagation() : null
    this.setData({ balanceVisible: !this.data.balanceVisible })
    this.updateBalanceDisplay()
  },

  loadCartCount: function() {
    var self = this
    API.getCart().then(function(cart) {
      var count = 0
      for (var i = 0; i < cart.length; i++) { count += cart[i].qty || 1 }
      self.setData({ cartCount: count })
    })
  },

  // 轮播点击（第5条）
  onCarouselTap: function(e) {
    var idx = e.currentTarget.dataset.index
    var urls = ['', '/pages/member-center/member-center?action=topup', '/pages/room-list/room-list', '/pages/coupon-verify/coupon-verify']
    if (idx >= 0 && idx < urls.length && urls[idx]) {
      wx.navigateTo({ url: urls[idx] })
    }
  },

  // 商品详情弹窗（第31条）
  showProductDetail: function(e) {
    var dataset = e.currentTarget.dataset
    this.setData({
      showProductModal: true,
      productDetail: { productId: dataset.pid, name: dataset.name, desc: dataset.desc, price: dataset.price }
    })
  },

  hideProductDetail: function() {
    this.setData({ showProductModal: false })
  },

  incQtyFromModal: function(e) {
    this.hideProductDetail()
    this.incQty(e)
  },

  // 茶品加减
  incQty: function(e) {
    var pid = e.currentTarget.dataset.pid
    var name = e.currentTarget.dataset.name
    var price = parseFloat(e.currentTarget.dataset.price)
    var products = this.data.teaProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === pid) {
        products[i]._qty = (products[i]._qty || 0) + 1
        break
      }
    }
    this.setData({ teaProducts: products })
    API.addToCart({ productId: pid, name: name, price: price }).then(this.loadCartCount.bind(this))
  },

  decQty: function(e) {
    var pid = e.currentTarget.dataset.pid
    var products = this.data.teaProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === pid && products[i]._qty > 0) {
        products[i]._qty = products[i]._qty - 1
        break
      }
    }
    this.setData({ teaProducts: products })
    API.removeFromCart(pid).then(this.loadCartCount.bind(this))
  },

  // 导航
  goRoom: function(e) { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + e.currentTarget.dataset.roomid }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff-login/staff-login' }) },
  goCartPage: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' }) },
  goSmartControl: function() { wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + this.data.activeOrder.roomId }) },

  handleBalanceClick: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  handleCouponClick: function() { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },
  goProfile: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },

  openDoor: function() { wx.showToast({ title: '🚪 门已开', icon: 'none' }) },
  callService: function() { wx.showToast({ title: '📞 已通知店员', icon: 'none' }) },
  callPhone: function() { wx.makePhoneCall({ phoneNumber: '020-8888-8888' }) },

  openNavigation: function() { wx.showToast({ title: '🗺 正在打开导航...', icon: 'none' }) },
  showStoreSelector: function() { this.setData({ showStoreModal: true }) },
  hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  showParkingInfo: function() { this.setData({ showParkingModal: true }) },
  hideParkingInfo: function() { this.setData({ showParkingModal: false }) }
})
