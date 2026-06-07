var API = require('../../utils/api')

Page({
  data: {
    statusBarHeight: 44,
    loading: true,
    errorMsg: '',
    hasActiveOrder: false,
    activeOrder: { roomName: '', timeStr: '', roomId: '' },
    currentSlide: 0,
    carousels: [
      { title: '高岸茶室', desc: '城市中的静谧茶空间 · 商务社交新选择', img: '../../images/中英文标题LOGO-蓝天白云-16比9-A.jpg', url: '' },
      { title: '会员首充特惠', desc: '首充享7折 + 赠送优惠券包，锁定超值体验', img: '../../images/头图四-店面招牌.jpg', url: '../member-center/index.html?action=topup' },
      { title: '精选包间', desc: '大茶室 · 会议室 · 中茶室 · 满足不同需求', img: '../../images/茶荟头图-空间-诗梳风大茶室.jpg', url: '../home/index.html' },
      { title: '优惠券大放送', desc: '领取专属优惠券，到店享更多折扣', img: '../../images/金德大诗梳风004.jpg', url: '../coupon-verify/index.html' }
    ],
    rooms: [],
    teaProducts: [],
    cartCount: 0,
    balance: 0,
    balanceDisplay: '',
    balanceIcon: '💰',
    qrRoomId: '', qrRoomName: '', qrTableId: '',
    showStoreModal: false, showParkingModal: false, showLoginModal: false,
    showBillModal: false, showQrWarning: false, qrWarningText: '',
    loginMode: 'login', loginPhone: '138****8888', loginCode: '8888',
    regPhone: '', regName: '', regCode: '',
    billItems: [], billTotal: 0,
    pendingAction: null, isLoggedIn: false
  },

  onLoad: function() {
    var self = this
    try {
      var sys = wx.getSystemInfoSync()
      self.setData({ statusBarHeight: sys.statusBarHeight || 44 })
    } catch(e) {}
    try {
      var v = wx.getStorageSync('balance_visible')
      if (v !== '') self.setData({ balanceVisible: v })
    } catch(e) {}
    self.initPage()
  },

  onShow: function() {
    this.loadData()
    this.checkActiveOrder()
  },

  initPage: function() {
    this.loadData()
    this.checkActiveOrder()
  },

  loadData: function() {
    var self = this
    self.setData({ loading: true, errorMsg: '' })
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    var visualMap = {
      'T001': { icon: '🍃', bg: '#e8f5e9' }, 'T002': { icon: '🪵', bg: '#fce4ec' },
      'T003': { icon: '🏔️', bg: '#fff3e0' }, 'T004': { icon: '🌿', bg: '#efebe9' },
      'T005': { icon: '🏵️', bg: '#f1f8e9' }, 'T006': { icon: '🏔️', bg: '#efebe9' },
      'T007': { icon: '🏺', bg: '#f3e5f5' }, 'T008': { icon: '🥃', bg: '#e0f7fa' }
    }

    Promise.all([
      API.getRooms(true),
      API.getProducts(),
      API.getCurrentUser(),
      API.getBalance()
    ]).then(function(results) {
      var roomsData = results[0] || []
      var productsData = results[1] || []
      var user = results[2]
      var balance = results[3] || 0

      var rooms = []
      for (var i = 0; i < roomsData.length; i++) {
        var r = roomsData[i]
        if (r.bookable === false) continue
        rooms.push({
          roomId: r.roomId, name: r.name,
          capacity: r.capacity, area: r.area,
          metaLine: (r.capacity || '—') + '人 · ' + (r.area || '—') + '㎡ · ' + (r.facilities || []).join(' · '),
          pricePerHour: r.pricePerHour || 120,
          icon: icons[r.type] || '🏠', bgColor: colors[r.type] || '#f0f0f0'
        })
      }
      var teas = []
      for (var i = 0; i < productsData.length; i++) {
        var t = productsData[i]
        var vis = visualMap[t.productId] || { icon: '🍵', bg: '#f0f0f0' }
        teas.push({ productId: t.productId, name: t.name, desc: t.desc || '', price: t.price, icon: vis.icon, bg: vis.bg, _qty: 0 })
      }

      self.setData({ rooms: rooms, teaProducts: teas, balance: balance, isLoggedIn: !!user })
      self.updateBalanceDisplay()
      if (user) {
        var levels = { Gold: '💎', Silver: '💰', Bronze: '👛', Diamond: '💳' }
        self.setData({ balanceIcon: levels[user.memberLevel] || '💰' })
      }
      self.setData({ loading: false })
    }).catch(function(err) {
      self.setData({ loading: false, errorMsg: '数据加载失败，点击重试' })
    })
  },

  checkActiveOrder: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var active = null
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].status === 'InUse' || orders[i].status === 'Booked') { active = orders[i]; break }
      }
      if (active) {
        self.setData({
          hasActiveOrder: true,
          activeOrder: { roomName: active.roomName || '大茶室C', roomId: active.roomId || '', timeStr: (active.date || '') + ' ' + (active.time || '') }
        })
      } else { self.setData({ hasActiveOrder: false }) }
    })
  },

  updateBalanceDisplay: function() { this.setData({ balanceDisplay: '¥' + this.data.balance }) },

  onSwiperChange: function(e) { this.setData({ currentSlide: e.detail.current }) },
  goSlide: function(e) { this.setData({ currentSlide: parseInt(e.currentTarget.dataset.idx) }) },
  onCarouselTap: function(e) {
    var urls = ['', '/pages/member-center/member-center?action=topup', '/pages/room-list/room-list', '/pages/coupon-verify/coupon-verify']
    var idx = e.currentTarget.dataset.index
    if (idx >= 0 && idx < urls.length && urls[idx]) wx.navigateTo({ url: urls[idx] })
  },

  handleBalanceClick: function() {
    if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'profile', showLoginModal: true }); return }
    wx.navigateTo({ url: '/pages/member-center/member-center' })
  },
  handleCouponClick: function() {
    if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'coupon', showLoginModal: true }); return }
    wx.navigateTo({ url: '/pages/my-coupons/my-coupons' })
  },
  goProfile: function() {
    if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'profile', showLoginModal: true }); return }
    wx.navigateTo({ url: '/pages/member-center/member-center' })
  },
  goRoom: function(e) {
    if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'room-' + e.currentTarget.dataset.roomid, showLoginModal: true }); return }
    wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + e.currentTarget.dataset.roomid })
  },

  showProductDetail: function(e) { wx.showModal({ title: e.currentTarget.dataset.name, content: e.currentTarget.dataset.desc + '\n¥' + e.currentTarget.dataset.price }) },
  incQty: function(e) {
    var pid = e.currentTarget.dataset.pid, name = e.currentTarget.dataset.name, price = parseFloat(e.currentTarget.dataset.price)
    var products = this.data.teaProducts
    for (var i = 0; i < products.length; i++) { if (products[i].productId === pid) { products[i]._qty = (products[i]._qty || 0) + 1; break } }
    this.setData({ teaProducts: products })
    API.addToCart({ productId: pid, name: name, price: price }).then(this.loadCartCount.bind(this))
  },
  decQty: function(e) {
    var pid = e.currentTarget.dataset.pid
    var products = this.data.teaProducts
    for (var i = 0; i < products.length; i++) { if (products[i].productId === pid && products[i]._qty > 0) { products[i]._qty--; break } }
    this.setData({ teaProducts: products })
    API.removeFromCart(pid).then(this.loadCartCount.bind(this))
  },
  loadCartCount: function() {
    var self = this
    API.getCart().then(function(cart) { var count = 0; for (var i = 0; i < cart.length; i++) { count += cart[i].qty || 1 } self.setData({ cartCount: count }) })
  },

  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff-login/staff-login' }) },
  goCartPage: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' }) },
  goSmartControl: function() { wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + this.data.activeOrder.roomId }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },

  openDoor: function() { wx.showToast({ title: '🚪 门已开，请进入', icon: 'none' }) },
  callService: function() { wx.showToast({ title: '📞 已通知店员，请稍候', icon: 'none' }) },
  callPhone: function() { wx.makePhoneCall({ phoneNumber: '020-8888-8888' }) },
  openNavigation: function() { wx.showToast({ title: '🗺 正在打开导航...', icon: 'none' }) },

  showStoreSelector: function() { this.setData({ showStoreModal: true }) },
  hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  showParkingInfo: function() { this.setData({ showParkingModal: true }) },
  hideParkingInfo: function() { this.setData({ showParkingModal: false }) },
  toastComing: function() { wx.showToast({ title: '即将上线', icon: 'none' }) },
  showRoomBill: function() { this.setData({ showBillModal: true }) },
  hideRoomBill: function() { this.setData({ showBillModal: false }) },
  closeQrContext: function() { this.setData({ qrRoomId: '', qrRoomName: '', qrTableId: '' }) },
  goCartWithRoom: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?room_id=' + this.data.qrRoomId }) },

  switchLoginTab: function(e) { this.setData({ loginMode: e.currentTarget.dataset.mode }) },
  onLoginPhone: function(e) { this.setData({ loginPhone: e.detail.value }) },
  onLoginCode: function(e) { this.setData({ loginCode: e.detail.value }) },
  onRegPhone: function(e) { this.setData({ regPhone: e.detail.value }) },
  onRegName: function(e) { this.setData({ regName: e.detail.value }) },
  getVerifyCode: function() { wx.showToast({ title: '验证码已发送: 8888', icon: 'none' }) },
  doLogin: function() {
    var self = this
    wx.showLoading({ title: '登录中...' })
    API.login(self.data.loginPhone, self.data.loginCode).then(function(user) {
      wx.hideLoading()
      self.setData({ isLoggedIn: true, showLoginModal: false, balance: user.balance || 0 })
      wx.showToast({ title: '登录成功', icon: 'none' })
      self.handlePendingAction()
    }).catch(function(err) { wx.hideLoading(); wx.showToast({ title: err.message || '登录失败', icon: 'none' }) })
  },
  doRegister: function() {
    var self = this
    wx.showLoading({ title: '注册中...' })
    API.login(self.data.regPhone || '130****0000', '8888').then(function(user) {
      wx.hideLoading()
      self.setData({ isLoggedIn: true, showLoginModal: false, balance: user.balance || 0 })
      wx.showToast({ title: '注册成功', icon: 'none' })
      self.handlePendingAction()
    }).catch(function(err) { wx.hideLoading(); wx.showToast({ title: err.message || '注册失败', icon: 'none' }) })
  },
  handlePendingAction: function() {
    var action = this.data.pendingAction
    if (!action) return
    this.setData({ pendingAction: null })
    if (action.indexOf('room-') === 0) { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + action.replace('room-', '') }) }
    else if (action === 'profile') { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
  },
  clearError: function() { this.setData({ errorMsg: '' }) }
})
