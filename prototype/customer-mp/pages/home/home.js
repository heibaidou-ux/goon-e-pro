var API = require('../../utils/api')

Page({
  data: {
    topPadding: 88, loading: true, errorMsg: '',
    hasActiveOrder: false,
    activeOrder: { roomName: '', timeStr: '', roomId: '' },
    currentSlide: 0,
    carousels: [
      { title: '高岸茶室', desc: '城市中的静谧茶空间', img: '../../images/中英文标题LOGO-蓝天白云-16比9-A.jpg', url: '' },
      { title: '会员首充特惠', desc: '首充享7折 + 赠送优惠券包', img: '../../images/头图四-店面招牌.jpg', url: '../member-center/index.html?action=topup' },
      { title: '精选包间', desc: '大茶室 · 会议室 · 中茶室', img: '../../images/茶荟头图-空间-诗梳风大茶室.jpg', url: '../home/index.html' },
      { title: '优惠券大放送', desc: '领取专属优惠券，到店享更多折扣', img: '../../images/金德大诗梳风004.jpg', url: '../coupon-verify/index.html' }
    ],
    rooms: [], teaProducts: [], cartCount: 0,
    balance: 0, balanceVisible: true, balanceIcon: '💰',
    qrRoomId: '', qrRoomName: '', qrTableId: '',
    showStoreModal: false, showParkingModal: false, showLoginModal: false,
    showBillModal: false, showQrWarning: false, qrWarningText: '',
    showDebug: false, debugRoomId: 'RM004', debugTableId: '1',
    loginMode: 'login', loginPhone: '138****8888', loginCode: '8888',
    regPhone: '', regName: '', regCode: '',
    billItems: [], billTotal: 0,
    pendingAction: null, isLoggedIn: false
  },

  onLoad: function() {
    var self = this
    try { var sys = wx.getSystemInfoSync(); self.setData({ topPadding: (sys.statusBarHeight || 44) + 44 }) } catch(e) {}
    // QR scan detection from URL params
    self.checkQrScan()
    // Debug panel from URL param
    self.checkDebugMode()
    self.loadData()
    self.checkActiveOrder()
  },

  onShow: function() {
    this.loadData()
    this.checkActiveOrder()
  },

  // ── QR Scan Detection ──
  checkQrScan: function() {
    var self = this
    var pages = getCurrentPages()
    var page = pages[pages.length - 1]
    if (!page) return
    var options = page.options || {}
    var qrRoomId = options.room_id || ''
    var qrTableId = options.table_id || ''

    if (qrRoomId) {
      var orders = wx.getStorageSync('mp_orders') || []
      var activeOrder = null
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].roomId === qrRoomId && (orders[i].status === 'InUse' || orders[i].status === 'in_use')) {
          activeOrder = orders[i]; break
        }
      }
      if (!activeOrder) {
        self.setData({ qrRoomId: qrRoomId, qrTableId: qrTableId })
        setTimeout(function() {
          self.showQrWarning('该房间暂未开启使用，请联系店员开启房间')
        }, 500)
      } else {
        API.getRoomById(qrRoomId).then(function(room) {
          self.showQrContextCard(room.name, qrRoomId, qrTableId)
        }).catch(function() {
          self.showQrContextCard(qrRoomId, qrRoomId, qrTableId)
        })
      }
    }
  },

  showQrContextCard: function(roomName, roomId, tableId) {
    this.setData({ qrRoomId: roomId, qrRoomName: roomName, qrTableId: tableId })
    wx.setStorageSync('erp_qr_context', JSON.stringify({ roomId: roomId, roomName: roomName, tableId: tableId }))
  },

  closeQrContext: function() {
    this.setData({ qrRoomId: '', qrRoomName: '', qrTableId: '' })
    wx.removeStorageSync('erp_qr_context')
  },

  goCartWithRoom: function() {
    var ctx = wx.getStorageSync('erp_qr_context')
    var url = '/pages/tea-shop/tea-shop'
    if (ctx) {
      try { var c = JSON.parse(ctx); url += '?room_id=' + c.roomId + '&room_name=' + encodeURIComponent(c.roomName) + '&table_id=' + c.tableId } catch(e) {}
    }
    wx.navigateTo({ url: url })
  },

  // ── Room Bill ──
  showRoomBill: function() {
    var self = this
    var ctx = wx.getStorageSync('erp_qr_context')
    if (!ctx) { wx.showToast({ title: '未检测到房间信息', icon: 'none' }); return }
    try { var c = JSON.parse(ctx) } catch(e) { wx.showToast({ title: '未检测到房间信息', icon: 'none' }); return }
    var roomBills = wx.getStorageSync('erp_room_bills') || {}
    var bill = roomBills[c.roomId]
    if (!bill || !bill.items || bill.items.length === 0) {
      self.setData({ billItems: [], billTotal: 0, showBillModal: true })
    } else {
      var items = []
      var total = 0
      for (var i = 0; i < bill.items.length; i++) {
        var item = bill.items[i]
        var amt = item.amount || (item.price * item.qty)
        total += amt
        items.push({ name: item.productName || item.name, qty: item.qty || 1, amount: '¥' + amt })
      }
      self.setData({ billItems: items, billTotal: total, showBillModal: true })
    }
  },

  hideRoomBill: function() { this.setData({ showBillModal: false }) },

  // ── QR Warning ──
  showQrWarning: function(msg) {
    this.setData({ showQrWarning: true, qrWarningText: msg })
  },

  hideQrWarning: function() {
    this.setData({ showQrWarning: false, qrWarningText: '', qrRoomId: '', qrRoomName: '', qrTableId: '' })
  },

  // ── Debug Panel ──
  checkDebugMode: function() {
    var pages = getCurrentPages()
    var page = pages[pages.length - 1]
    if (!page) return
    var options = page.options || {}
    if (options.debug === '1' || wx.getStorageSync('erp_debug_mode') === 'true') {
      this.setData({ showDebug: true })
    }
  },

  onDebugRoomId: function(e) { this.setData({ debugRoomId: e.detail.value }) },
  onDebugTableId: function(e) { this.setData({ debugTableId: e.detail.value }) },

  debugQrScan: function() {
    var roomId = this.data.debugRoomId
    var tableId = this.data.debugTableId
    wx.navigateTo({
      url: '/pages/home/home?room_id=' + roomId + '&table_id=' + tableId + '&debug=1'
    })
  },

  closeDebug: function() { this.setData({ showDebug: false }) },

  // ── Data Loading ──
  loadData: function() {
    var self = this
    try { var v = wx.getStorageSync('balance_visible'); if (v !== '') self.setData({ balanceVisible: v }) } catch(e) {}
    self.setData({ loading: true, errorMsg: '' })
    var colors = { MeetingRoom: '#e3f2fd', TeaRoom: '#e8f5e9', Exhibition: '#fff3e0', Workspace: '#f5f5f5' }
    var icons = { MeetingRoom: '💼', TeaRoom: '🍵', Exhibition: '🏛️', Workspace: '🔧' }
    var visualMap = {
      'T001': { icon: '🍃', bg: '#e8f5e9' }, 'T002': { icon: '🪵', bg: '#fce4ec' },
      'T003': { icon: '🏔️', bg: '#fff3e0' }, 'T004': { icon: '🌿', bg: '#efebe9' },
      'T005': { icon: '🏵️', bg: '#f1f8e9' }, 'T006': { icon: '🏔️', bg: '#efebe9' },
      'T007': { icon: '🏺', bg: '#f3e5f5' }, 'T008': { icon: '🥃', bg: '#e0f7fa' }
    }
    Promise.all([API.getRooms(true), API.getProducts(), API.getCurrentUser(), API.getBalance()]).then(function(results) {
      var roomsData = results[0] || [], productsData = results[1] || [], user = results[2], balance = results[3] || 0
      var rooms = []
      for (var i = 0; i < roomsData.length; i++) {
        var r = roomsData[i]
        if (r.bookable === false) continue
        var facilities = (r.facilities || []).join(' · ')
        rooms.push({
          roomId: r.roomId, name: r.name, capacity: r.capacity, area: r.area,
          facilities: facilities, pricePerHour: r.pricePerHour || 120,
          icon: icons[r.type] || '🏠', bgColor: colors[r.type] || '#f0f0f0'
        })
      }
      var teas = []
      for (var i = 0; i < productsData.length; i++) {
        var t = productsData[i], vis = visualMap[t.productId] || { icon: '🍵', bg: '#f0f0f0' }
        teas.push({ productId: t.productId, name: t.name, desc: t.desc || '', price: t.price, icon: vis.icon, bg: vis.bg, _qty: 0 })
      }
      self.setData({ rooms: rooms, teaProducts: teas, balance: balance, isLoggedIn: !!user })
      if (user) { self.setData({ balanceIcon: {Gold:'💎',Silver:'💰',Bronze:'👛',Diamond:'💳'}[user.memberLevel] || '💰' }) }
      self.setData({ loading: false })
    }).catch(function() { self.setData({ loading: false, errorMsg: '加载失败' }) })
  },

  // ── Active Order ──
  checkActiveOrder: function() {
    var self = this
    API.getUserOrders().then(function(orders) {
      var active = null
      for (var i = 0; i < orders.length; i++) {
        if (orders[i].status === 'InUse' || orders[i].status === 'in_use') { active = orders[i]; break }
      }
      // Fallback: check Booked orders for today
      if (!active) {
        var now = new Date()
        var dateStr = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0')
        var curMin = now.getHours() * 60 + now.getMinutes()
        for (var i = 0; i < orders.length; i++) {
          var b = orders[i]
          if (b.status === 'Booked' && b.date === dateStr && b.time) {
            var parts = b.time.split('-')
            if (parts.length >= 2) {
              var st = parseInt(parts[0].split(':')[0])*60 + parseInt(parts[0].split(':')[1])
              var en = parseInt(parts[1].split(':')[0])*60 + parseInt(parts[1].split(':')[1])
              if (curMin >= st && curMin < en) { active = b; break }
            }
          }
        }
      }
      // Demo fallback so banner is always visible
      if (!active) {
        var now = new Date()
        active = {
          roomId: 'RM004', roomName: '大茶室C',
          date: now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0'),
          time: String(now.getHours()).padStart(2,'0') + ':00-' + String(now.getHours()+1).padStart(2,'0') + ':00'
        }
      }
      if (active) {
        self.setData({
          hasActiveOrder: true,
          activeOrder: {
            roomName: active.roomName || '—',
            roomId: active.roomId || '',
            timeStr: (active.date||'') + ' ' + (active.time||'')
          }
        })
      }
    }).catch(function() {
      // Demo fallback on error
      var now = new Date()
      self.setData({
        hasActiveOrder: true,
        activeOrder: {
          roomName: '大茶室C', roomId: 'RM004',
          timeStr: String(now.getHours()).padStart(2,'0') + ':00-' + String(now.getHours()+1).padStart(2,'0') + ':00'
        }
      })
    })
  },

  // ── Carousel ──
  onSwiperChange: function(e) { this.setData({ currentSlide: e.detail.current }) },
  goSlide: function(e) { this.setData({ currentSlide: parseInt(e.currentTarget.dataset.idx) }) },
  onCarouselTap: function(e) {
    var urls = ['', '/pages/member-center/member-center?action=topup', '/pages/room-list/room-list', '/pages/coupon-verify/coupon-verify']
    var idx = e.currentTarget.dataset.index
    if (idx >= 0 && idx < urls.length && urls[idx]) wx.navigateTo({ url: urls[idx] })
  },

  // ── Quick Actions ──
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
    if (!this.data.isLoggedIn) { this.setData({ pendingAction: 'room-'+e.currentTarget.dataset.roomid, showLoginModal: true }); return }
    wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId='+e.currentTarget.dataset.roomid })
  },

  // ── Tea / Cart ──
  showProductDetail: function(e) {
    wx.showModal({ title: e.currentTarget.dataset.name, content: e.currentTarget.dataset.desc+'\n¥'+e.currentTarget.dataset.price })
  },
  incQty: function(e) {
    var pid = e.currentTarget.dataset.pid, name = e.currentTarget.dataset.name, price = parseFloat(e.currentTarget.dataset.price), p = this.data.teaProducts
    for (var i = 0; i < p.length; i++) { if (p[i].productId === pid) { p[i]._qty = (p[i]._qty||0)+1; break } }
    this.setData({ teaProducts: p })
    API.addToCart({ productId: pid, name: name, price: price }).then(this.loadCartCount.bind(this))
  },
  decQty: function(e) {
    var pid = e.currentTarget.dataset.pid, p = this.data.teaProducts
    for (var i = 0; i < p.length; i++) { if (p[i].productId === pid && p[i]._qty > 0) { p[i]._qty--; break } }
    this.setData({ teaProducts: p })
    API.removeFromCart(pid).then(this.loadCartCount.bind(this))
  },
  loadCartCount: function() {
    var self = this
    API.getCart().then(function(cart) { var c = 0; for (var i = 0; i < cart.length; i++) { c += cart[i].qty||1 } self.setData({ cartCount: c }) })
  },

  // ── Navigation ──
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goMyOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMemberCenter: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) },
  goCouponVerify: function() { wx.navigateTo({ url: '/pages/coupon-verify/coupon-verify' }) },
  goStaffLogin: function() { wx.navigateTo({ url: '/pages/staff-login/staff-login' }) },
  goCartPage: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop?tab=cart' }) },

  // ── Active Order Actions ──
  openDoor: function() {
    var order = this.data.activeOrder
    if (!order.roomId && !order.roomName) { wx.showToast({ title: '没有进行中的订单', icon: 'none' }); return }
    wx.navigateTo({ url: '/pages/room-control/room-control?roomId='+order.roomId+'&roomName='+encodeURIComponent(order.roomName) })
  },

  callService: function() {
    var order = this.data.activeOrder
    var now = new Date()
    var ts = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0') + '-' + String(now.getDate()).padStart(2,'0') + ' ' + String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0')
    var notification = {
      id: 'SRV' + Date.now(),
      type: 'customer_call',
      roomId: order.roomId || '',
      roomName: order.roomName || '—',
      time: ts,
      message: '客人呼叫服务'
    }
    var notifications = wx.getStorageSync('mp_staff_notifications') || []
    notifications.unshift(notification)
    wx.setStorageSync('mp_staff_notifications', JSON.stringify(notifications))
    wx.showToast({ title: '📞 已通知店员，请稍候', icon: 'success' })
  },

  // ── Store Info ──
  callPhone: function() { wx.makePhoneCall({ phoneNumber: '020-8888-8888' }) },
  openNavigation: function() {
    wx.showToast({ title: '🗺 导航中...', icon: 'none' })
  },

  // ── Modals ──
  showStoreSelector: function() { this.setData({ showStoreModal: true }) },
  hideStoreSelector: function() { this.setData({ showStoreModal: false }) },
  showParkingInfo: function() { this.setData({ showParkingModal: true }) },
  hideParkingInfo: function() { this.setData({ showParkingModal: false }) },
  hideLogin: function() { this.setData({ showLoginModal: false }) },
  toastComing: function() { wx.showToast({ title: '即将上线', icon: 'none' }) },

  // ── Login ──
  switchLoginTab: function(e) { this.setData({ loginMode: e.currentTarget.dataset.mode }) },
  onLoginPhone: function(e) { this.setData({ loginPhone: e.detail.value }) },
  onLoginCode: function(e) { this.setData({ loginCode: e.detail.value }) },
  onRegPhone: function(e) { this.setData({ regPhone: e.detail.value }) },
  onRegName: function(e) { this.setData({ regName: e.detail.value }) },
  getVerifyCode: function() { wx.showToast({ title: '验证码已发送: 8888', icon: 'none' }) },

  doLogin: function() {
    var self = this
    wx.showLoading({ title: '登录中...' })
    API.login(self.data.loginPhone, self.data.loginCode).then(function(u) {
      wx.hideLoading()
      self.setData({ isLoggedIn: true, showLoginModal: false })
      wx.showToast({ title: '登录成功', icon: 'none' })
      self.handlePendingAction()
    }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'登录失败', icon: 'none' }) })
  },

  doRegister: function() {
    var self = this
    wx.showLoading({ title: '注册中...' })
    API.login(self.data.regPhone||'130****0000', '8888').then(function(u) {
      wx.hideLoading()
      self.setData({ isLoggedIn: true, showLoginModal: false })
      wx.showToast({ title: '注册成功', icon: 'none' })
      self.handlePendingAction()
    }).catch(function(e) { wx.hideLoading(); wx.showToast({ title: e.message||'注册失败', icon: 'none' }) })
  },

  handlePendingAction: function() {
    var a = this.data.pendingAction
    if (!a) return
    this.setData({ pendingAction: null })
    if (a.indexOf('room-')===0) { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId='+a.replace('room-','') }) }
    else if (a==='profile') { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
  },

  clearError: function() { this.setData({ errorMsg: '' }) }
})
