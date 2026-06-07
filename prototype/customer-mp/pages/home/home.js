var API = require('../../utils/api')

Page({
  data: {
    // 14.4 加载状态
    loading: true,
    // 14.5 错误提示
    errorMsg: '',
    // 当前消费
    hasActiveOrder: false,
    activeOrder: { roomName: '', timeStr: '', roomId: '' },
    // 轮播
    currentSlide: 0,
    carousels: [
      { title: '高岸茶室', desc: '城市中的静谧茶空间 · 商务社交新选择', img: '../../images/中英文标题LOGO-蓝天白云-16比9-A.jpg', url: '' },
      { title: '会员首充特惠', desc: '首充享7折 + 赠送优惠券包，锁定超值体验', img: '../../images/头图四-店面招牌.jpg', url: '../member-center/index.html?action=topup' },
      { title: '精选包间', desc: '大茶室 · 会议室 · 中茶室 · 满足不同需求', img: '../../images/茶荟头图-空间-诗梳风大茶室.jpg', url: '../home/index.html' },
      { title: '优惠券大放送', desc: '领取专属优惠券，到店享更多折扣', img: '../../images/金德大诗梳风004.jpg', url: '../coupon-verify/index.html' }
    ],
    // 房间
    rooms: [],
    // 茶品
    teaProducts: [],
    // 购物车
    cartCount: 0,
    // 会员余额（直接显示金额，不添加图标）
    balance: 0,
    balanceDisplay: '',
    // QR扫码状态
    qrRoomId: '',
    qrRoomName: '',
    qrTableId: '',
    // 弹窗
    showStoreModal: false,
    showParkingModal: false,
    showLoginModal: false,
    showBillModal: false,
    showQrWarning: false,
    qrWarningText: '',
    // 登录
    loginMode: 'login',
    loginPhone: '138****8888',
    loginCode: '8888',
    regPhone: '',
    regName: '',
    regCode: '',
    // 挂账
    billItems: [],
    billTotal: 0,
    // 待处理操作（登录后跳转）
    pendingAction: null,
    // 登录状态
    isLoggedIn: false
  },

  onLoad: function() {
    this.initPage()
    // 从全局读取余额显隐设置
    try {
      var v = wx.getStorageSync('balance_visible')
      if (v !== '') this.setData({ balanceVisible: v })
    } catch(e) {}
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

      // 房间列表 — 原型渲染方式
      var rooms = []
      for (var i = 0; i < roomsData.length; i++) {
        var r = roomsData[i]
        if (r.bookable === false) continue
        var facilities = (r.facilities || []).join(' · ')
        rooms.push({
          roomId: r.roomId, name: r.name,
          capacity: r.capacity, area: r.area,
          metaLine: (r.capacity || '—') + '人 · ' + (r.area || '—') + '㎡ · ' + facilities,
          pricePerHour: r.pricePerHour || 120,
          icon: icons[r.type] || '🏠',
          bgColor: colors[r.type] || '#f0f0f0'
        })
      }
      // 茶品 — 原型渲染方式
      var teas = []
      for (var i = 0; i < productsData.length; i++) {
        var t = productsData[i]
        var vis = visualMap[t.productId] || { icon: '🍵', bg: '#f0f0f0' }
        teas.push({
          productId: t.productId, name: t.name, desc: t.desc || '',
          price: t.price, icon: vis.icon, bg: vis.bg, _qty: 0
        })
      }

      self.setData({
        rooms: rooms,
        teaProducts: teas,
        balance: balance,
        isLoggedIn: !!user
      })
      self.updateBalanceDisplay()

      // 更新会员等级图标（原型updateQuickIcons）
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
      } else {
        self.setData({ hasActiveOrder: false })
      }
    })
  },

  updateBalanceDisplay: function() {
    this.setData({ balanceDisplay: '¥' + this.data.balance })
  },

  // ── 轮播 ──
  onSwiperChange: function(e) {
    this.setData({ currentSlide: e.detail.current })
  },

  goSlide: function(e) {
    this.setData({ currentSlide: parseInt(e.currentTarget.dataset.idx) })
  },

  onCarouselTap: function(e) {
    var idx = e.currentTarget.dataset.index
    var url = this.data.carousels[idx].url
    if (url) {
      var pageMap = {
        '../member-center/index.html?action=topup': '/pages/member-center/member-center?action=topup',
        '../home/index.html': '/pages/home/home',
        '../coupon-verify/index.html': '/pages/coupon-verify/coupon-verify'
      }
      var target = pageMap[url]
      if (target) wx.navigateTo({ url: target })
    }
  },

  // ── 快捷入口 ──
  handleBalanceClick: function() {
    if (!this.data.isLoggedIn) {
      this.setData({ pendingAction: 'profile', showLoginModal: true })
      return
    }
    wx.navigateTo({ url: '/pages/member-center/member-center' })
  },

  handleCouponClick: function() {
    if (!this.data.isLoggedIn) {
      this.setData({ pendingAction: 'coupon', showLoginModal: true })
      return
    }
    wx.navigateTo({ url: '/pages/my-coupons/my-coupons' })
  },

  goProfile: function() {
    if (!this.data.isLoggedIn) {
      this.setData({ pendingAction: 'profile', showLoginModal: true })
      return
    }
    wx.navigateTo({ url: '/pages/member-center/member-center' })
  },

  goRoom: function(e) {
    if (!this.data.isLoggedIn) {
      this.setData({ pendingAction: 'room-' + e.currentTarget.dataset.roomid, showLoginModal: true })
      return
    }
    wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + e.currentTarget.dataset.roomid })
  },

  // ── 茶品 ──
  showProductDetail: function(e) {
    wx.showModal({
      title: e.currentTarget.dataset.name,
      content: e.currentTarget.dataset.desc + '\n¥' + e.currentTarget.dataset.price,
      showCancel: true,
      cancelText: '关闭',
      confirmText: '加入购物车',
      success: function(res) {
        if (res.confirm) {
          // 调用addToCart
        }
      }
    })
    // 实际原型是跳转到tea-shop详情页
  },

  addToCart: function(e) {
    var pid = e.currentTarget.dataset.pid
    var name = e.currentTarget.dataset.name
    var price = parseFloat(e.currentTarget.dataset.price)
    var self = this
    API.addToCart({ productId: pid, name: name, price: price }).then(function(cart) {
      var count = 0
      for (var i = 0; i < cart.length; i++) { count += cart[i].qty || 1 }
      self.setData({ cartCount: count })
    })
  },

  goCartPage: function() {
    var self = this
    API.getCart().then(function(cart) {
      if (cart.length === 0) { wx.showToast({ title: '购物车为空', icon: 'none' }); return }
      wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' })
    })
  },

  // ── 导航 ──
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff-login/staff-login' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },

  // ── 当前消费 ──
  openDoor: function() { wx.showToast({ title: '🚪 门已开，请进入', icon: 'none' }) },

  callService: function() {
    wx.showToast({ title: '📞 已通知店员，请稍候', icon: 'none' })
  },

  // ── 门店信息 ──
  openNavigation: function() {
    wx.showToast({ title: '🗺 正在打开导航...', icon: 'none' })
  },

  callPhone: function() {
    wx.makePhoneCall({ phoneNumber: '020-8888-8888' })
  },

  // ── 门店选择 ──
  showStoreSelector: function() { this.setData({ showStoreModal: true }) },
  hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  toastComing: function() { wx.showToast({ title: '即将上线', icon: 'none' }) },

  // ── 停车 ──
  showParkingInfo: function() { this.setData({ showParkingModal: true }) },
  hideParkingInfo: function() { this.setData({ showParkingModal: false }) },

  // ── 挂账 ──
  showRoomBill: function() {
    if (!this.data.qrRoomId) { wx.showToast({ title: '未检测到房间信息', icon: 'none' }); return }
    this.setData({ showBillModal: true })
  },
  hideRoomBill: function() { this.setData({ showBillModal: false }) },

  // ── QR未启用 ──
  showQrWarning: function(msg) { this.setData({ showQrWarning: true, qrWarningText: msg }) },
  hideQrWarning: function() { this.setData({ showQrWarning: false }) },

  // ── QR上下文 ──
  closeQrContext: function() { this.setData({ qrRoomId: '', qrRoomName: '', qrTableId: '' }) },
  goCartWithRoom: function() {
    var q = '?room_id=' + this.data.qrRoomId + '&room_name=' + encodeURIComponent(this.data.qrRoomName) + '&table_id=' + this.data.qrTableId
    wx.navigateTo({ url: '/pages/tea-shop/tea-shop' + q })
  },

  // ── 登录 ──
  switchLoginTab: function(e) {
    this.setData({ loginMode: e.currentTarget.dataset.mode })
  },
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
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '登录失败', icon: 'none' })
    })
  },

  doRegister: function() {
    var self = this
    wx.showLoading({ title: '注册中...' })
    API.login(self.data.regPhone || '130****0000', '8888').then(function(user) {
      wx.hideLoading()
      self.setData({ isLoggedIn: true, showLoginModal: false, balance: user.balance || 0 })
      wx.showToast({ title: '注册成功', icon: 'none' })
      self.handlePendingAction()
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: err.message || '注册失败', icon: 'none' })
    })
  },

  handlePendingAction: function() {
    var action = this.data.pendingAction
    if (!action) return
    this.setData({ pendingAction: null })
    var self = this
    if (action.indexOf('room-') === 0) {
      var roomId = action.replace('room-', '')
      setTimeout(function() { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + roomId }) }, 300)
    } else if (action === 'profile') {
      setTimeout(function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }, 300)
    }
  },

  // 14.4 加载/错误
  clearError: function() { this.setData({ errorMsg: '' }) },

  // 第3条/第24条 智控
  goSmartControl: function() {
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId=' + this.data.activeOrder.roomId })
  }
})
