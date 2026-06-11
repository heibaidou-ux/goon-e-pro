var API = require('../../utils/api')

Page({
  data: {
    topPadding: 88, loading: false, errorMsg: '',
    showDetail: false, detailProduct: {},
    hasActiveOrder: false,
    activeOrder: { roomName: '', timeStr: '', roomId: '' },
    currentSlide: 0,
    carousels: [
      { title: '高岸茶室', desc: '城市中的静谧茶空间', img: '/images/中英文标题LOGO-蓝天白云-16比9-A.jpg', url: '' },
      { title: '会员首充特惠', desc: '首充享7折 + 赠送优惠券包', img: '/images/头图四-店面招牌.jpg', url: '../member-center/index.html?action=topup' },
      { title: '精选包间', desc: '大茶室 · 会议室 · 中茶室', img: '/images/茶荟头图-空间-诗梳风大茶室.jpg', url: '../home/index.html' },
      { title: '优惠券大放送', desc: '领取专属优惠券，到店享更多折扣', img: '/images/金德大诗梳风004.jpg', url: '../coupon-verify/index.html' }
    ],
    rooms: [], teaProducts: [], cartCount: 0,
    balance: 0, balanceDisplay: '', balanceVisible: true,
    qrRoomId: '', qrRoomName: '', qrTableId: '',
    showStoreModal: false, showParkingModal: false, showLoginModal: false,
    showBillModal: false, showQrWarning: false, qrWarningText: '',
    loginMode: 'login', loginPhone: '138****8888', loginCode: '8888',
    regPhone: '', regName: '', regCode: '',
    billItems: [], billTotal: 0, pendingAction: null, isLoggedIn: false
  },

  onLoad: function() {
    var self = this
    // 角色重定向
    var role = API.getUserRole()
    if (role === 'staff') { wx.reLaunch({ url: '/pages/staff-dashboard/staff-dashboard' }); return }
    if (role === 'shareholder') { wx.reLaunch({ url: '/pages/investor-workbench/investor-workbench' }); return }
    try { var sys = wx.getSystemInfoSync(); self.setData({ topPadding: (sys.statusBarHeight || 44) + 44 }) } catch(e) {}
    self.loadData(); self.checkActiveOrder()
  },
  onShow: function() { this.loadData(); this.checkActiveOrder() },

  loadData: function() {
    var self = this
    try { var v = wx.getStorageSync('balance_visible'); if (v !== '') self.data.balanceVisible = v } catch(e) {}
    self.setData({ loading: true, errorMsg: '' })
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    var visualMap = { 'T001': { icon: '🍃', bg: '#e8f5e9' }, 'T002': { icon: '🪵', bg: '#fce4ec' }, 'T003': { icon: '🏔️', bg: '#fff3e0' }, 'T004': { icon: '🌿', bg: '#efebe9' }, 'T005': { icon: '🏵️', bg: '#f1f8e9' }, 'T006': { icon: '🏔️', bg: '#efebe9' }, 'T007': { icon: '🏺', bg: '#f3e5f5' }, 'T008': { icon: '🥃', bg: '#e0f7fa' } }
    Promise.all([API.getRooms(true), API.getProducts(), API.getCurrentUser(), API.getBalance(), API.getCart()]).then(function(results) {
      var roomsData = results[0] || [], productsData = results[1] || [], user = results[2], balance = results[3] || 0, cart = results[4] || []
      var rooms = []
      for (var i = 0; i < roomsData.length; i++) { var r = roomsData[i]; if (r.bookable === false) continue; rooms.push({ roomId: r.roomId, name: r.name, capacity: r.capacity, area: r.area, pricePerHour: r.pricePerHour || 120, icon: icons[r.type] || '🏠', bgColor: colors[r.type] || '#f0f0f0' }) }
      var qtyMap = {}
      for (var i = 0; i < cart.length; i++) { qtyMap[cart[i].productId] = cart[i].qty || 1 }
      var teas = []
      for (var i = 0; i < productsData.length; i++) { var t = productsData[i], vis = visualMap[t.productId] || { icon: '🍵', bg: '#f0f0f0' }; teas.push({ productId: t.productId, name: t.name, desc: t.desc || '', price: t.price, icon: vis.icon, bg: vis.bg, _qty: qtyMap[t.productId] || 0 }) }
      self.setData({ rooms: rooms, teaProducts: teas, balance: balance, isLoggedIn: !!user })
      self.setData({ balanceDisplay: self.data.balanceVisible ? '¥' + balance : '****' })
      self.loadCartCount()
      self.setData({ loading: false })
    }).catch(function() { self.setData({ loading: false, errorMsg: '加载失败' }) })
  },

  checkActiveOrder: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var active = null
      for (var i = 0; i < orders.length; i++) { if (orders[i].status === 'InUse' || orders[i].status === 'Booked') { active = orders[i]; break } }
      if (active) { self.setData({ hasActiveOrder: true, activeOrder: { roomName: active.roomName || '大茶室C', roomId: active.roomId || '', timeStr: (active.date||'')+' '+(active.time||'') } }) }
      else { self.setData({ hasActiveOrder: false }) }
    })
  },

  onSwiperChange: function(e) { this.setData({ currentSlide: e.detail.current }) },
  goSlide: function(e) { this.setData({ currentSlide: parseInt(e.currentTarget.dataset.idx) }) },
  onCarouselTap: function(e) { var urls = ['/pages/room-list/room-list', '/pages/member-center/member-center?action=topup', '/pages/room-list/room-list', '/pages/coupon-verify/coupon-verify']; var idx = e.currentTarget.dataset.index; if (idx >= 0 && idx < urls.length && urls[idx]) wx.navigateTo({ url: urls[idx] }) },

  handleBalanceClick: function() { if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'profile', showLoginModal: true }); return } wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  handleCouponClick: function() { if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'coupon', showLoginModal: true }); return } wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }) },
  goProfile: function() { if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'profile', showLoginModal: true }); return } wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goRoom: function(e) { if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'room-'+e.currentTarget.dataset.roomid, showLoginModal: true }); return } wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId='+e.currentTarget.dataset.roomid }) },
  incQty: function(e) { var pid = e.currentTarget.dataset.pid, name = e.currentTarget.dataset.name, price = parseFloat(e.currentTarget.dataset.price), p = this.data.teaProducts; for (var i = 0; i < p.length; i++) { if (p[i].productId === pid) { p[i]._qty = (p[i]._qty||0)+1; break } } this.setData({ teaProducts: p }); API.addToCart({ productId: pid, name: name, price: price }).then(this.loadCartCount.bind(this)) },
  decQty: function(e) { var pid = e.currentTarget.dataset.pid, p = this.data.teaProducts; for (var i = 0; i < p.length; i++) { if (p[i].productId === pid && p[i]._qty > 0) { p[i]._qty--; break } } this.setData({ teaProducts: p }); API.removeFromCart(pid).then(this.loadCartCount.bind(this)) },
  loadCartCount: function() { var self = this; API.getCart().then(function(cart) { var c = 0; for (var i = 0; i < cart.length; i++) { c += cart[i].qty||1 } self.setData({ cartCount: c }) }) },

  showProductDetail: function(e) {
    var pid = e.currentTarget.dataset.pid, name = e.currentTarget.dataset.name || '', desc = e.currentTarget.dataset.desc || '', price = e.currentTarget.dataset.price || 0
    var p = this.data.teaProducts, product = null
    for (var i = 0; i < p.length; i++) { if (p[i].productId === pid) { product = p[i]; break } }
    if (!product) return
    this.setData({ detailProduct: product, showDetail: true })
  },
  hideDetail: function() { this.setData({ showDetail: false }) },
  addFromDetail: function() {
    var p = this.data.detailProduct
    if (!p) return
    this.incQty({ currentTarget: { dataset: { pid: p.productId, name: p.name, price: p.price } } })
    this.hideDetail()
  },

  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff-login/staff-login' }) },
  goCartPage: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' }) },

  goSmartControl: function() { var order = this.data.activeOrder; var roomId = order.roomId || '', roomName = order.roomName || ''; wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+roomId+'&roomName='+encodeURIComponent(roomName) }) },
  openDoor: function() { var order = this.data.activeOrder; var roomId = order.roomId || '', roomName = order.roomName || ''; wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+roomId+'&roomName='+encodeURIComponent(roomName) }) },
  callService: function() { wx.showToast({ title: '📞 已通知店员', icon: 'none' }) },
  callPhone: function() { wx.makePhoneCall({ phoneNumber: '020-8888-8888' }) },
  openNavigation: function() { wx.showToast({ title: '🗺 导航中...', icon: 'none' }) },
  showStoreSelector: function() { this.setData({ showStoreModal: true }) }, hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  showParkingInfo: function() { this.setData({ showParkingModal: true }) }, hideParkingInfo: function() { this.setData({ showParkingModal: false }) },
  toastComing: function() { wx.showToast({ title: '即将上线', icon: 'none' }) },
  closeQrContext: function() { this.setData({ qrRoomId: '', qrRoomName: '', qrTableId: '' }) },
  goCartWithRoom: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?room_id='+this.data.qrRoomId }) },
  switchLoginTab: function(e) { this.setData({ loginMode: e.currentTarget.dataset.mode }) },
  onLoginPhone: function(e) { this.setData({ loginPhone: e.detail.value }) }, onLoginCode: function(e) { this.setData({ loginCode: e.detail.value }) },
  onRegPhone: function(e) { this.setData({ regPhone: e.detail.value }) }, onRegName: function(e) { this.setData({ regName: e.detail.value }) },
  getVerifyCode: function() { wx.showToast({ title: '验证码已发送: 8888', icon: 'none' }) },
  doLogin: function() { var self = this; wx.showLoading({ title: '登录中...' }); API.login(self.data.loginPhone, self.data.loginCode).then(function(u) { wx.hideLoading(); self.setData({ isLoggedIn: true, showLoginModal: false }); wx.showToast({ title: '登录成功', icon: 'none' }); self.handlePendingAction() }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'登录失败', icon: 'none' }) }) },
  doRegister: function() { var self = this; wx.showLoading({ title: '注册中...' }); API.login(self.data.regPhone||'130****0000', '8888').then(function(u) { wx.hideLoading(); self.setData({ isLoggedIn: true, showLoginModal: false }); wx.showToast({ title: '注册成功', icon: 'none' }); self.handlePendingAction() }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'注册失败', icon: 'none' }) }) },
  handlePendingAction: function() {
    var a = this.data.pendingAction; if (!a) return; this.setData({ pendingAction: null })
    if (a.indexOf('room-')===0) { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId='+a.replace('room-','') }); return }
    if (a === 'profile') { wx.navigateTo({ url: '/pages/member-center/member-center' }); return }
    if (a === 'coupon') { wx.navigateTo({ url: '/pages/my-coupons/my-coupons' }); return }
  },
  clearError: function() { this.setData({ errorMsg: '' }) },


  // 轮播图加载失败时显示占位
  onImageError: function(e) {
    var idx = e.currentTarget.dataset.index
    if (idx === undefined) return
    var key = 'carousels[' + idx + '].img'
    this.setData({ __cached: {} })
    // fallback: use a placeholder
    var carousels = this.data.carousels
    if (carousels[idx] && carousels[idx].img.indexOf('data:') !== 0) {
      carousels[idx].img = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="375" height="200" viewBox="0 0 375 200"><rect fill="#e8f5e9" width="375" height="200"/><text x="50%" y="50%" fill="#5D8A6B" font-size="16" text-anchor="middle" dy=".3em">' + (carousels[idx].title || '图片加载失败') + '</text></svg>')
      this.setData({ carousels: carousels })
    }
  },

  toggleBalanceVis: function() {
    var visible = !this.data.balanceVisible
    this.setData({ balanceVisible: visible, balanceDisplay: visible ? '¥' + this.data.balance : '****' })
    try { wx.setStorageSync('balance_visible', visible) } catch(e) {}
  }
})
