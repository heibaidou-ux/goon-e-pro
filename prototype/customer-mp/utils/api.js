/**
 * 高岸ERP 统一API层
 * 支持 Mock(本地) / Live(后端) 双模式
 * USE_MOCK = false 时直连后端 FastAPI
 */
const MOCK = require('./mock-data')

// ── 后端配置 ──
const API_BASE = 'http://localhost:8000'
const USE_MOCK = true  // false = 连后端

// ── 通用HTTP请求（带认证）──
const LS_PREFIX = 'mp_'

function lsGet(key, fallback) {
  try { const val = wx.getStorageSync(LS_PREFIX + key); return val || fallback } catch (e) { return fallback }
}
function lsSet(key, val) { try { wx.setStorageSync(LS_PREFIX + key, val) } catch (e) { } }
function lsRemove(key) { try { wx.removeStorageSync(LS_PREFIX + key) } catch (e) { } }

function delay(ms) {
  ms = ms || (200 + Math.random() * 300)
  return new Promise(resolve => setTimeout(resolve, ms))
}

function getToken() {
  return lsGet('token', null)
}

function setToken(token) {
  if (token) lsSet('token', token)
  else lsRemove('token')
}

async function request(options) {
  if (USE_MOCK) return Promise.reject(new Error('MOCK_MODE'))

  const token = getToken()
  const header = { 'Content-Type': 'application/json' }
  if (token) header['Authorization'] = 'Bearer ' + token

  return new Promise((resolve, reject) => {
    wx.request({
      url: API_BASE + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: header,
      success: res => {
        if (res.statusCode === 401) {
          // Token过期，清除登录态
          setToken(null)
          lsSet('logged_in', false)
          wx.reLaunch({ url: '/pages/home/home?showLogin=1' })
          reject(new Error('登录已过期'))
          return
        }
        if (res.statusCode >= 400) {
          reject(new Error((res.data && res.data.detail) || '请求失败: ' + res.statusCode))
          return
        }
        resolve(res.data)
      },
      fail: err => reject(new Error('网络请求失败: ' + (err.errMsg || '')))
    })
  })
}

// ── 角色定义 ──
const ROLES = { GUEST: 'guest', STAFF: 'staff', SHAREHOLDER: 'shareholder' }

// ── Mock 角色账号 ──
const MOCK_ACCOUNTS = {
  '138****8888': { name: '张先生', role: ROLES.GUEST, memberLevel: 'Gold', balance: 280, phone: '138****8888' },
  staff: {
    'admin': { name: '管理员', role: ROLES.STAFF, storeId: 'ST001', storeName: '盈隆店', userId: 'E001' },
    'staff': { name: '店员小张', role: ROLES.STAFF, storeId: 'ST001', storeName: '盈隆店', userId: 'E002' },
  },
  shareholder: {
    'shareholder': { name: '王股东', role: ROLES.SHAREHOLDER, shares: 30, storeId: 'ST001' },
  }
}

const API = {
  ROLES,

  // ── 认证 ──
  async login(phone, code) {
    if (!USE_MOCK) {
      const data = await request({ url: '/api/auth/phone-login', method: 'POST', data: { phone, code } })
      setToken(data.access_token)
      lsSet('logged_in', true)
      const user = data.user
      user.role = ROLES.GUEST
      lsSet('user', user)
      lsSet('user_role', ROLES.GUEST)
      return user
    }
    return delay().then(() => {
      if (code !== '8888') throw new Error('验证码错误')
      let users = lsGet('users', {})
      let user = users[phone]
      if (!user) {
        user = {
          phone, name: phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
          memberLevel: 'Silver', balance: 280, totalSpent: 0, visitCount: 0,
          role: ROLES.GUEST, created: new Date().toISOString(), tags: []
        }
        users[phone] = user; lsSet('users', users)
      }
      user.role = ROLES.GUEST
      lsSet('logged_in', true); lsSet('user', user); lsSet('user_role', ROLES.GUEST)
      return user
    })
  },

  loginWithRole(account, password, role) {
    if (!USE_MOCK) {
      return request({ url: '/api/auth/login', method: 'POST', data: { username: account, password } })
        .then(data => {
          setToken(data.access_token)
          lsSet('logged_in', true)
          const user = data.user
          user.role = role
          lsSet('user', user)
          lsSet('user_role', role)
          return user
        })
    }
    return delay().then(() => {
      if (password !== '8888') throw new Error('密码错误')
      var user = null
      if (role === ROLES.STAFF) {
        user = MOCK_ACCOUNTS.staff[account]
        if (!user) throw new Error('员工账号不存在')
        user = Object.assign({}, user, { account, role: ROLES.STAFF })
      } else if (role === ROLES.SHAREHOLDER) {
        user = MOCK_ACCOUNTS.shareholder[account]
        if (!user) throw new Error('股东账号不存在')
        user = Object.assign({}, user, { account, role: ROLES.SHAREHOLDER })
      } else throw new Error('无效的角色类型')
      lsSet('logged_in', true); lsSet('user', user); lsSet('user_role', role)
      return user
    })
  },

  logout() {
    setToken(null)
    lsRemove('logged_in'); lsRemove('user'); lsRemove('user_role')
    return Promise.resolve({ success: true })
  },

  getCurrentUser() { return Promise.resolve(lsGet('user', null)) },
  isLoggedIn() { return !!lsGet('logged_in', false) },
  getUserRole() { return lsGet('user_role', null) },
  hasRole(requiredRoles) {
    var role = this.getUserRole()
    if (!role) return false
    if (Array.isArray(requiredRoles)) return requiredRoles.indexOf(role) >= 0
    return role === requiredRoles
  },

  // ── 房间 ──
  getRooms(bookableOnly) {
    if (!USE_MOCK) return request({ url: '/api/rooms' })
    return delay().then(() => {
      let list = MOCK.rooms.slice()
      if (bookableOnly) list = list.filter(r => r.bookable !== false)
      return list
    })
  },

  getRoomById(roomId) {
    if (!USE_MOCK) return request({ url: '/api/rooms/' + roomId })
    return delay().then(() => {
      for (var i = 0; i < MOCK.rooms.length; i++) {
        if (MOCK.rooms[i].roomId === roomId) return JSON.parse(JSON.stringify(MOCK.rooms[i]))
      }
      throw new Error('房间不存在')
    })
  },

  getRoomBookings(roomId, date) {
    if (!USE_MOCK) return request({ url: '/api/orders/active' })
    return delay().then(() => {
      const bookings = lsGet('bookings', [])
      return bookings.filter(b => b.roomId === roomId && b.date === date && b.status !== 'Cancelled')
    })
  },

  // ── 设备 ──
  getRoomDevices(roomId) {
    if (!USE_MOCK) return request({ url: '/api/iot/devices?room_id=' + roomId })
    return delay().then(() => MOCK.devices.filter(d => d.roomId === roomId).map(d => Object.assign({}, d)))
  },

  controlDevice(deviceId, command) {
    if (!USE_MOCK) return request({ url: '/api/iot/control', method: 'POST', data: { device_id: deviceId, action: command.action || 'toggle', params: command } })
    return delay(200).then(() => {
      for (var i = 0; i < MOCK.devices.length; i++) {
        if (MOCK.devices[i].deviceId === deviceId) { Object.assign(MOCK.devices[i], command); break }
      }
      return { success: true, deviceId, command }
    })
  },

  executeScene(roomId, sceneId) {
    if (!USE_MOCK) return request({ url: '/api/iot/scenes/activate', method: 'POST', data: { room_id: roomId, scene: sceneId } })
    return delay(800).then(() => {
      for (var i = 0; i < MOCK.scenes.length; i++) {
        if (MOCK.scenes[i].sceneId === sceneId) {
          var scene = MOCK.scenes[i]; var p = scene.params
          MOCK.devices.forEach(function(d) {
            if (d.roomId !== roomId) return
            if (d.type === 'Curtain' && p.curtain) d.position = p.curtain
            if (d.type === 'AC' && p.ac) { d.mode = p.ac.on ? 'cool' : 'off'; if (p.ac.temp) d.temperature = p.ac.temp }
            if (d.type === 'Light' && p.lights) { d.brightness = p.lights.brightness || 0; d.colorTemp = p.lights.colorTemp || 4000 }
            if ((d.type === 'BGM' || d.type === 'Speaker') && p.music) d.playing = p.music.on || false
          })
          return { success: true, sceneId, sceneName: scene.name }
        }
      }
      throw new Error('场景不存在')
    })
  },

  getActiveAlerts() { return delay().then(() => []) },
  getAudioStatus(roomId) {
    return delay().then(() => {
      var speakers = MOCK.devices.filter(d => d.roomId === roomId && (d.type === 'BGM' || d.type === 'Speaker'))
      if (!speakers.length) return null
      var s = speakers[0] || {}
      return { roomId, online: speakers.some(sp => sp.status === 'Online'), speakers, volume: s.volume || 0, playing: s.playing || false, source: s.source || 'none' }
    })
  },
  setVolume(roomId, volume) {
    return delay(150).then(() => {
      MOCK.devices.forEach(d => { if (d.roomId === roomId && (d.type === 'BGM' || d.type === 'Speaker')) d.volume = volume })
      return { success: true, roomId, volume }
    })
  },

  // ── 订单 ──
  createBooking(booking) {
    if (!USE_MOCK) return request({ url: '/api/orders', method: 'POST', data: booking })
    return delay(500).then(() => {
      var bookings = lsGet('bookings', [])
      var id = 'ORD' + String(Date.now()).slice(-6)
      var b = Object.assign({
        orderId: id, status: 'Booked', doorCode: String(Math.floor(1000 + Math.random() * 9000)),
        created: new Date().toISOString(), phone: (lsGet('user', {}) || {}).phone || ''
      }, booking)
      bookings.push(b); lsSet('bookings', bookings)
      var user = lsGet('user', {})
      if (booking.paymentMethod === 'Balance' && user.balance !== undefined) {
        user.balance -= (booking.amount || 0); lsSet('user', user)
      }
      return b
    })
  },

  getAllOrders() {
    return delay().then(() => {
      var today = new Date()
      var ds = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0')
      var h = today.getHours(), m = today.getMinutes()
      var startH = (h + 1) % 24, endH = (h + 3) % 24

      var bookings = lsGet('bookings', [])
      var hasRM004 = false, hasRM002 = false, hasRM003 = false
      for (var i = 0; i < bookings.length; i++) {
        if (bookings[i].roomId === 'RM004' && (bookings[i].status === 'InUse' || bookings[i].status === 'Booked')) hasRM004 = true
        if (bookings[i].roomId === 'RM002' && bookings[i].status === 'Booked') hasRM002 = true
        if (bookings[i].roomId === 'RM003' && bookings[i].status === 'Booked') hasRM003 = true
      }
      if (!hasRM004) bookings.push({ orderId:'ORD001', roomId:'RM004', roomName:'白沙瓦', customerName:'张先生', status:'InUse', date:ds, time:String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+'-'+String(endH).padStart(2,'0')+':00', amount:180, doorCode:'8264', created: new Date().toISOString() })
      if (!hasRM002) bookings.push({ orderId:'ORD002', roomId:'RM002', roomName:'翡冷翠', customerName:'李女士', status:'Booked', date:ds, time:String(startH).padStart(2,'0')+':00-'+String(endH).padStart(2,'0')+':00', amount:160, doorCode:'7391', created: new Date().toISOString() })
      if (!hasRM003) bookings.push({ orderId:'ORD003', roomId:'RM003', roomName:'布拉格', customerName:'王先生', status:'Booked', date:ds, time:String(startH+2).padStart(2,'0')+':00-'+String(endH+3).padStart(2,'0')+':00', amount:120, doorCode:'5123', created: new Date().toISOString() })
      return bookings
    })
  },

  getUserOrders() {
    return delay().then(() => {
      var bookings = lsGet('bookings', [])
      var user = lsGet('user', null)
      if (user) return bookings.filter(b => b.phone === user.phone || b.customerName === user.name).sort((a, b) => new Date(b.created) - new Date(a.created))
      return []
    })
  },

  cancelOrder(orderId) {
    return delay(200).then(() => {
      var bookings = lsGet('bookings', [])
      bookings.forEach(b => { if (b.orderId === orderId) b.status = 'Cancelled' })
      lsSet('bookings', bookings)
      return { success: true }
    })
  },

  // ── 商品 ──
  getProducts(category) {
    if (!USE_MOCK) return request({ url: '/api/products?category=' + (category || '') })
    if (!USE_MOCK) return request({ url: '/api/products' + (category ? '?categoryId=' + category : '') })
    return delay().then(() => {
      if (category) return MOCK.products.filter(p => p.category === category)
      return MOCK.products.slice()
    })
  },

  getCart() { return Promise.resolve(lsGet('tea_cart', [])) },

  addToCart(product) {
    var cart = lsGet('tea_cart', [])
    var found = false
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].productId === product.productId) { cart[i].qty = (cart[i].qty || 1) + 1; found = true; break }
    }
    if (!found) { product.qty = 1; cart.push(product) }
    lsSet('tea_cart', cart)
    return Promise.resolve(cart)
  },

  removeFromCart(productId) {
    var cart = lsGet('tea_cart', [])
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].productId === productId) {
        if (cart[i].qty > 1) { cart[i].qty-- } else { cart.splice(i, 1) }
        break
      }
    }
    lsSet('tea_cart', cart)
    return Promise.resolve(cart)
  },

  createShopOrder(items, paymentMethod, total, deliveryInfo) {
    return delay(400).then(() => {
      deliveryInfo = deliveryInfo || {}
      var order = {
        orderId: 'SHP' + String(Date.now()).slice(-6), items, total, paymentMethod,
        status: 'PendingDelivery', created: new Date().toISOString(),
        deliveryMethod: deliveryInfo.method || 'pickup', deliveryStatus: deliveryInfo.method === 'express' ? 'pending' : 'ready'
      }
      if (deliveryInfo.method === 'express') {
        order.expressName = deliveryInfo.expressName || ''
        order.expressPhone = deliveryInfo.expressPhone || ''
        order.expressAddress = deliveryInfo.expressAddress || ''
        order.trackingNum = 'SF' + String(Date.now()).slice(-10)
        order.carrier = '顺丰速运'
      }
      if (deliveryInfo.method === 'inroom') {
        order.roomName = deliveryInfo.roomName || ''
        order.roomId = deliveryInfo.roomId || ''
      }
      var shopOrders = lsGet('shop_orders', [])
      shopOrders.push(order); lsSet('shop_orders', shopOrders)
      lsSet('tea_cart', [])
      if (paymentMethod === 'Balance') {
        var user = lsGet('user', {})
        user.balance = (user.balance || 0) - total; lsSet('user', user)
      }
      return order
    })
  },

  getShopOrders() { return delay().then(() => lsGet('shop_orders', [])) },

  // ── 余额 ──
  getBalance() { return delay(100).then(() => (lsGet('user', {})).balance || 0) },

  topUp(amount, paymentMethod) {
    return delay(500).then(() => {
      var user = lsGet('user', {})
      var bonus = 0
      if (!user._firstRecharge) { bonus = Math.round(amount * 0.3); user._firstRecharge = true }
      user.balance = (user.balance || 0) + amount + bonus; lsSet('user', user)
      return { success: true, amount, bonus, newBalance: user.balance }
    })
  },

  // ── 优惠券 ──
  verifyCoupon(code) {
    return delay(300).then(() => {
      var c = MOCK.couponDB[code]
      if (!c) throw new Error('券码不存在')
      if (c.used) throw new Error('该券已被使用')
      return { code, value: c.value, type: c.type, desc: c.desc, platform: c.platform }
    })
  },

  getUserCoupons() {
    return delay().then(() => {
      var result = []
      for (var code in MOCK.couponDB) {
        var c = MOCK.couponDB[code]
        result.push({ code, value: c.value, type: c.type, desc: c.desc, platform: c.platform, used: c.used })
      }
      return result
    })
  },

  // ── 扫码消费 ──
  scanRoomStatus(roomId) {
    return delay().then(() => {
      var room = null
      for (var i = 0; i < MOCK.rooms.length; i++) { if (MOCK.rooms[i].roomId === roomId) { room = MOCK.rooms[i]; break } }
      if (!room) throw new Error('房间不存在')
      return { roomId, roomName: room.name, storeId: 'ST001', storeName: '盈隆店', status: room.status === 'Active' ? 'Active' : 'Inactive', hasActiveOrder: roomId === 'RM004' || roomId === 'RM002', activeOrderId: 'ORD001', message: '欢迎使用 ' + room.name }
    })
  },

  getScanBill(roomId) {
    return delay().then(() => ({
      roomId, roomName: roomId === 'RM004' ? '白沙瓦' : '翡冷翠',
      activeOrderId: 'ORD001', billId: 'BILL001', billStatus: 'Active',
      billSummary: { roomCharge: 180, scanTotal: 156, pendingPayment: 156, totalPaid: 180 },
      scanOrders: [
        { orderId: 'SCAN001', orderNumber: 'SCAN20260606001', createdAt: new Date().toISOString(), items: [{ productName: '安吉白茶', quantity: 1, subtotal: 68 }], totalAmount: 68, status: '挂账中', canCancel: true },
        { orderId: 'SCAN002', orderNumber: 'SCAN20260606002', createdAt: new Date().toISOString(), items: [{ productName: '手工茶点A', quantity: 2, subtotal: 76 }], totalAmount: 76, status: '挂账中', canCancel: true }
      ]
    }))
  },

  createScanOrder(data) {
    return delay(500).then(() => {
      var orderId = 'SCAN' + String(Date.now()).slice(-6)
      var total = 0
      for (var i = 0; i < data.items.length; i++) { total += (data.items[i].unitPrice || 0) * (data.items[i].quantity || 1) }
      return { orderId, orderNumber: 'SCAN' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + orderId.slice(-4).toUpperCase(), roomId: data.roomId, storeId: data.storeId || 'ST001', totalAmount: total, itemCount: data.items.length, status: 'Completed', tags: ['扫码加购'], message: '扫码点单成功' }
    })
  },

  cancelScanOrder(orderId) { return delay(200).then(() => ({ success: true, orderId, refundStatus: '无需退款（挂账未支付）', stockRollback: true, cancelledAt: new Date().toISOString(), message: '扫码订单已成功撤销' })) },

  settleScanBill(roomId, data) {
    return delay(500).then(() => ({
      success: true, settleId: 'STL' + String(Date.now()).slice(-6), roomId, totalAmount: 156,
      memberBalanceUsed: data.useMemberBalance ? 50 : 0, paymentAmount: data.useMemberBalance ? 106 : 156,
      paymentMethod: data.paymentMethod || 'WxPay', ordersSettled: 3,
      invoiceNumber: data.issueInvoice ? ('INV-20260606-' + String(Date.now()).slice(-4)) : null, message: '结算成功'
    }))
  },

  // ── 物流查询 ──
  getLogistics(orderId) { return delay().then(() => null) }
}

module.exports = API
