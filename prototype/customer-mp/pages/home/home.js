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
    currentStore: 'huachengguangchang', storeName: '花城广场店', showStoreModal: false, showAllStores: false, showLoginModal: false,
    showBillModal: false, showQrWarning: false, qrWarningText: '',
    phoneLoginView: false, loginMode: 'login', loginType: 'code', loginPhone: '', loginCode: '', loginPassword: '',
    regPhone: '', regCode: '',
    billItems: [], billTotal: 0, pendingAction: null, isLoggedIn: false
  },

  onLoad: function(e) {
    var self = this
    this.setData({ _checkingRole: true })
    // 角色重定向（在渲染任何UI前完成）
    var role = API.getUserRole()
    if (role === 'staff') { wx.reLaunch({ url: '/pages/staff/staff-dashboard/staff-dashboard' }); return }
    // 从"我的"跳转过来时自动弹出登录框
    if (e && e.showLogin == '1') {
      self.setData({ showLoginModal: true, pendingAction: 'profile' })
    }
    if (role === 'shareholder') { wx.reLaunch({ url: '/pages/workbench/investor-workbench/investor-workbench' }); return }
    try { self.setData({ topPadding: (wx.getWindowInfo().statusBarHeight || 44) + 44 }) } catch(e) {}
    self.setData({ _checkingRole: false })
    self.loadData(); self.checkActiveOrder()
  },
  onShow: function() { this.loadData(); this.checkActiveOrder() },

  loadData: function() {
    var self = this
    // 立即展示上一次缓存数据（如有）
    self.setData({ loading: false, errorMsg: '' })
    // 同步会员中心的余额显隐设置
    try { var v = wx.getStorageSync('balance_visible'); if (v !== '') self.data.balanceVisible = v } catch(e) {}
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    var visualMap = { 'T001': { icon: '🍃', bg: '#e8f5e9' }, 'T002': { icon: '🪵', bg: '#fce4ec' }, 'T003': { icon: '🏔️', bg: '#fff3e0' }, 'T004': { icon: '🌿', bg: '#efebe9' }, 'T005': { icon: '🏵️', bg: '#f1f8e9' }, 'T006': { icon: '🏔️', bg: '#efebe9' }, 'T007': { icon: '🏺', bg: '#f3e5f5' }, 'T008': { icon: '🥃', bg: '#e0f7fa' }, 'T01': { icon: '🍃', bg: '#e8f5e9' }, 'T02': { icon: '🪵', bg: '#fce4ec' }, 'T03': { icon: '🏔️', bg: '#fff3e0' }, 'T04': { icon: '🏺', bg: '#f3e5f5' }, 'T05': { icon: '🏔️', bg: '#efebe9' }, 'T06': { icon: '🌿', bg: '#e0f7fa' }, 'T07': { icon: '🏵️', bg: '#f1f8e9' }, 'T08': { icon: '🥃', bg: '#fce4ec' } }
    Promise.all([API.getRooms(true), API.getProducts(), API.getCurrentUser(), API.getBalance(), API.getCart()]).then(function(results) {
      var roomsData = results[0] || [], productsData = results[1] || [], user = results[2], balance = results[3] || 0, cart = results[4] || []
      // 后端数据为空时自动使用内置演示数据（VPS未部署/空数据库时仍可展示）
      if (!roomsData.length || !productsData.length) {
        self.renderFallbackData()
        self.setData({ loading: false, isLoggedIn: !!user, balance: balance })
        self.setData({ balanceDisplay: self.data.balanceVisible ? '¥' + balance : '****' })
        return
      }
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
    }).catch(function() {
      self.renderFallbackData()
      self.setData({ loading: false })
    })
  },

  isOrderActiveNow: function(order) {
    if (!order.date || !order.time) return false
    var now = new Date()
    var todayStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
    if (order.date !== todayStr) return false
    var parts = order.time.split('-')
    if (parts.length < 2) return false
    var sp = parts[0].split(':'), ep = parts[1].split(':')
    if (sp.length < 2 || ep.length < 2) return false
    var curMin = now.getHours() * 60 + now.getMinutes()
    var startMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
    var endMin = parseInt(ep[0]) * 60 + parseInt(ep[1])
    return curMin >= startMin && curMin < endMin
  },

  checkActiveOrder: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var active = null
      for (var i = 0; i < orders.length; i++) { if (orders[i].status === 'InUse' || (orders[i].status === 'Booked' && self.isOrderActiveNow(orders[i]))) { active = orders[i]; break } }
      if (active) {
        var timeParts = (active.time || '').split('-')
        var startStr = timeParts.length >= 1 ? timeParts[0].trim() : ''
        var endStr = timeParts.length >= 2 ? timeParts[1].trim() : ''
        self.setData({ hasActiveOrder: true, activeOrder: {
          roomName: active.roomName || active.roomId || '',
          roomId: active.roomId || '',
          timeStr: (active.date||'')+' '+(active.time||''),
          start: startStr, end: endStr,
          duration: active.duration || 120
        } })
      }
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
  // ── 门店选择 ──
  showStoreSelector: function() { this.setData({ showStoreModal: true }) },
  hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  selectStore: function(e) {
    var store = e.currentTarget.dataset.store
    var name = e.currentTarget.dataset.name
    this.setData({ currentStore: store, storeName: name, showStoreModal: false })
    if (store === 'huachengguangchang') {
      wx.showToast({ title: '已切换至 ' + name, icon: 'success' })
    } else {
      wx.showToast({ title: name + ' 即将上线，敬请期待', icon: 'none' })
    }
  },

  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  showPhoneLoginForm: function() { this.setData({ phoneLoginView: true, loginMode: 'login', loginType: 'code' }) },
  hidePhoneLoginForm: function() { this.setData({ phoneLoginView: false }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff/staff-login/staff-login' }) },
  goCartPage: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' }) },

  goSmartControl: function() { var order = this.data.activeOrder; var roomId = order.roomId || '', roomName = order.roomName || '', s = order.start || '', e = order.end || '', dur = order.duration || ''; if (roomId) { API.executeScene(roomId, 'Welcome').catch(function() {}) }; wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+roomId+'&roomName='+encodeURIComponent(roomName)+'&start='+s+'&end='+e+'&duration='+dur }) },
  openDoor: function() { var order = this.data.activeOrder; var roomId = order.roomId || '', roomName = order.roomName || '', s = order.start || '', e = order.end || '', dur = order.duration || ''; if (roomId) { API.executeScene(roomId, 'Welcome').catch(function() {}) }; wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+roomId+'&roomName='+encodeURIComponent(roomName)+'&start='+s+'&end='+e+'&duration='+dur }) },
  callService: function() {
    var calls = []; try { calls = JSON.parse(wx.getStorageSync('mp_service_calls') || '[]') } catch(e) {}
    calls.push({ id:'SV'+String(Date.now()).slice(-6), roomName: this.data.activeOrder.roomName || '', roomId: this.data.activeOrder.roomId || '', time: new Date().toLocaleString(), status: 'pending' })
    try { wx.setStorageSync('mp_service_calls', JSON.stringify(calls)) } catch(e) {}
    wx.showToast({ title: '📞 已通知店员', icon: 'none' })
  },
  callPhone: function() {
    var self = this
    wx.showActionSheet({
      itemList: ['拨打 18011821388', '复制号码'],
      success: function(res) {
        if (res.tapIndex === 0) {
          wx.makePhoneCall({ phoneNumber: '18011821388' })
        } else {
          wx.setClipboardData({ data: '18011821388', success: function() { wx.showToast({ title: '号码已复制', icon: 'none' }) } })
        }
      }
    })
  },
  copyAddress: function() {
    wx.setClipboardData({ data: '广州市天河区珠江新城富力盈隆广场3801', success: function() { wx.showToast({ title: '地址已复制', icon: 'none' }) } })
  },
  openNavigation: function() {
    wx.openLocation({
      latitude: 23.1275,
      longitude: 113.3220,
      name: '高岸·花城广场店',
      address: '广州市天河区珠江新城富力盈隆广场3801',
      scale: 18
    })
  },
  showParkingInfo: function() { wx.navigateTo({ url: '/pages/parking-guide/parking-guide' }) },
  toastComing: function() { wx.showToast({ title: '即将上线', icon: 'none' }) },
  closeQrContext: function() { this.setData({ qrRoomId: '', qrRoomName: '', qrTableId: '' }) },
  goCartWithRoom: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?room_id='+this.data.qrRoomId }) },
  switchLoginTab: function(e) { this.setData({ loginMode: e.currentTarget.dataset.mode }) },
  switchLoginType: function(e) { this.setData({ loginType: e.currentTarget.dataset.type }) },
  // ── 微信一键登录 ──
  onWechatLogin: function(e) {
    if (e.detail && e.detail.errMsg && e.detail.errMsg.indexOf('fail') >= 0) {
      // 用户拒绝授权
      wx.showToast({ title: '已取消微信登录', icon: 'none' })
      return
    }
    var self = this
    var userInfo = e.detail.userInfo || {}
    wx.showLoading({ title: '微信登录中...' })
    wx.login({
      success: function(r) {
        if (!r.code) {
          wx.hideLoading()
          wx.showToast({ title: '微信登录失败', icon: 'none' })
          return
        }
        API.wechatLogin(r.code, userInfo).then(function(u) {
          wx.hideLoading()
          self.setData({ isLoggedIn: true, showLoginModal: false })
          wx.showToast({ title: '登录成功', icon: 'success' })
          self.loadData()
          self.handlePendingAction()
        }).catch(function(err) {
          wx.hideLoading()
          wx.showToast({ title: err.message || '微信登录失败', icon: 'none' })
        })
      },
      fail: function() {
        wx.hideLoading()
        wx.showToast({ title: '微信登录失败', icon: 'none' })
      }
    })
  },
  onLoginPhone: function(e) { this.setData({ loginPhone: e.detail.value }) }, onLoginCode: function(e) { this.setData({ loginCode: e.detail.value }) },
  onLoginPassword: function(e) { this.setData({ loginPassword: e.detail.value }) },
  onRegPhone: function(e) { this.setData({ regPhone: e.detail.value }) },
  getVerifyCode: function() { wx.showToast({ title: '验证码已发送: 8888', icon: 'none' }) },
  doLogin: function() {
    var self = this; wx.showLoading({ title: '登录中...' })
    if (self.data.loginType === 'pwd') {
      // 密码登录
      var phone = self.data.loginPhone
      var pwd = self.data.loginPassword
      if (!pwd) { wx.hideLoading(); wx.showToast({ title: '请输入密码', icon: 'none' }); return }
      try {
        var users = wx.getStorageSync('mp_users') || {}
        var user = users[phone]
        if (!user || user.password !== pwd) {
          wx.hideLoading(); wx.showToast({ title: '手机号或密码错误', icon: 'none' }); return
        }
        user.phone = phone
        wx.setStorageSync('mp_user', user)
        wx.setStorageSync('mp_logged_in', true)
        wx.setStorageSync('mp_user_role', 'guest')
        wx.hideLoading()
        self.setData({ isLoggedIn: true, showLoginModal: false })
        wx.showToast({ title: '登录成功', icon: 'none' })
        self.handlePendingAction()
      } catch(e) { wx.hideLoading(); wx.showToast({ title: '登录失败', icon: 'none' }) }
    } else {
      API.login(self.data.loginPhone, self.data.loginCode).then(function(u) {
        wx.hideLoading(); self.setData({ isLoggedIn: true, showLoginModal: false })
        wx.showToast({ title: '登录成功', icon: 'none' }); self.handlePendingAction()
      }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'登录失败', icon: 'none' }) })
    }
  },
  doRegister: function() {
    var self = this
    var phone = self.data.regPhone || '130****0000'
    wx.showLoading({ title: '注册中...' })
    API.login(phone, '8888').then(function(u) {
      try {
        var users = wx.getStorageSync('mp_users') || {}
        if (!users[phone]) { users[phone] = { name: phone, role: 'guest' } }
        wx.setStorageSync('mp_users', users)
      } catch(e) {}
      wx.hideLoading(); self.setData({ isLoggedIn: true, showLoginModal: false, loginPhone: phone })
      wx.showToast({ title: '注册成功', icon: 'success' }); self.handlePendingAction()
    }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'注册失败', icon: 'none' }) })
  },
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
    var carousels = this.data.carousels
    if (carousels[idx] && carousels[idx].img.indexOf('data:') !== 0) {
      carousels[idx].img = 'data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="375" height="200" viewBox="0 0 375 200"><rect fill="#e8f5e9" width="375" height="200"/><text x="50%" y="50%" fill="#5D8A6B" font-size="16" text-anchor="middle" dy=".3em">' + (carousels[idx].title || '图片加载失败') + '</text></svg>')
      this.setData({ carousels: carousels })
    }
  },

  // API不通或数据为空时展示内置演示数据
  renderFallbackData: function() {
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    var fbRooms = [
      { roomId:'RM001', name:'丰沙里', type:'MeetingRoom', capacity:10, area:30, pricePerHour:200 },
      { roomId:'RM002', name:'翡冷翠', type:'TeaRoom', capacity:4, area:18, pricePerHour:80 },
      { roomId:'RM003', name:'布拉格', type:'TeaRoom', capacity:4, area:18, pricePerHour:80 },
      { roomId:'RM004', name:'白沙瓦', type:'TeaRoom', capacity:6, area:25, pricePerHour:120 },
    ]
    var rooms = []
    for (var i = 0; i < fbRooms.length; i++) {
      var r = fbRooms[i]
      rooms.push({ roomId: r.roomId, name: r.name, capacity: r.capacity, area: r.area, pricePerHour: r.pricePerHour || 120, icon: icons[r.type] || '🏠', bgColor: colors[r.type] || '#f0f0f0' })
    }
    var fbTeas = [
      { productId:'T01', name:'明前龙井', desc:'西湖核心产区 · 清香甘醇', price:168, icon:'🍃', bg:'#e8f5e9', _qty:0 },
      { productId:'T02', name:'金骏眉', desc:'武夷山桐木关 · 蜜香甘醇', price:258, icon:'🪵', bg:'#fce4ec', _qty:0 },
      { productId:'T03', name:'铁观音', desc:'安溪高山 · 七泡有余香', price:138, icon:'🏔️', bg:'#fff3e0', _qty:0 },
      { productId:'T04', name:'普洱茶饼', desc:'云南勐海古树 · 越陈越香', price:198, icon:'🏺', bg:'#f3e5f5', _qty:0 },
      { productId:'T05', name:'正山小种', desc:'传统烟熏 · 桂圆汤味', price:98, icon:'🏔️', bg:'#efebe9', _qty:0 },
      { productId:'T06', name:'白毫银针', desc:'福鼎高山 · 毫香蜜韵', price:228, icon:'🌿', bg:'#e0f7fa', _qty:0 },
      { productId:'T07', name:'大红袍', desc:'武夷岩茶 · 岩骨花香', price:298, icon:'🏵️', bg:'#f1f8e9', _qty:0 },
      { productId:'T08', name:'小青柑', desc:'新会柑+普洱 · 果香馥郁', price:88, icon:'🥃', bg:'#fce4ec', _qty:0 },
    ]
    this.setData({ rooms: rooms, teaProducts: fbTeas })
  },

})
