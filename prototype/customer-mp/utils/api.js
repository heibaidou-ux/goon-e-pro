/**
 * 高岸ERP 客人端 SDK — 微信小程序版
 * 统一数据层，支持 Mock / 真实API 切换
 * 设计原则：与HTML原型 sdk.js API签名一致，底层适配 wx 环境
 */
const MOCK = require('./mock-data')

// ── 存储封装（使用小程序Sync存储） ──
const LS_PREFIX = 'mp_'

function lsGet(key, fallback) {
  try {
    const val = wx.getStorageSync(LS_PREFIX + key)
    return val || fallback
  } catch (e) { return fallback }
}

function lsSet(key, val) {
  try { wx.setStorageSync(LS_PREFIX + key, val) } catch (e) { }
}

function lsRemove(key) {
  try { wx.removeStorageSync(LS_PREFIX + key) } catch (e) { }
}

// ── 模拟网络延迟（Mock模式使用） ──
const USE_MOCK = true  // 切换为 false 后走真实API

function delay(ms) {
  ms = ms || (200 + Math.random() * 300)
  return new Promise(resolve => setTimeout(resolve, ms))
}

// ── 通用请求封装（为真实API预留） ──
function request(options) {
  return new Promise((resolve, reject) => {
    if (USE_MOCK) return reject(new Error('MOCK_MODE'))
    wx.request({
      url: options.url,
      method: options.method || 'GET',
      data: options.data,
      header: { 'Content-Type': 'application/json' },
      success: res => resolve(res.data),
      fail: err => reject(err)
    })
  })
}

// ═══════════════════════════════════════════
//  API 接口（与HTML原型 sdk.js API 签名一致）
// ═══════════════════════════════════════════

const API = {

  // ── 认证 ──

  login(phone, code) {
    if (!USE_MOCK) return request({ url: '/api/auth/login', method: 'POST', data: { phone, code } })
    return delay().then(() => {
      if (code !== '8888') throw new Error('验证码错误')
      let users = lsGet('users', {})
      let user = users[phone]
      if (!user) {
        user = {
          phone, name: phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
          memberLevel: 'Silver', balance: 280, totalSpent: 0, visitCount: 0,
          created: new Date().toISOString(), tags: []
        }
        users[phone] = user
        lsSet('users', users)
      }
      lsSet('logged_in', true)
      lsSet('user', user)
      return user
    })
  },

  logout() {
    lsRemove('logged_in')
    lsRemove('user')
    return Promise.resolve({ success: true })
  },

  getCurrentUser() {
    return Promise.resolve(lsGet('user', null))
  },

  isLoggedIn() {
    return !!lsGet('logged_in', false)
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
    if (!USE_MOCK) return request({ url: `/api/rooms/${roomId}` })
    return delay().then(() => {
      const room = MOCK.rooms.find(r => r.roomId === roomId)
      if (!room) throw new Error('房间不存在')
      return room
    })
  },

  getRoomBookings(roomId, date) {
    if (!USE_MOCK) return request({ url: `/api/rooms/${roomId}/bookings?date=${date}` })
    return delay().then(() => {
      const bookings = lsGet('bookings', [])
      return bookings.filter(b => b.roomId === roomId && b.date === date && b.status !== 'Cancelled')
    })
  },

  // ── 设备 ──

  getRoomDevices(roomId) {
    if (!USE_MOCK) return request({ url: `/api/iot/devices?room_id=${roomId}` })
    return delay().then(() => MOCK.devices.filter(d => d.roomId === roomId).map(d => ({ ...d })))
  },

  controlDevice(deviceId, command) {
    if (!USE_MOCK) return request({ url: '/api/iot/control', method: 'POST', data: { device_id: deviceId, ...command } })
    return delay(200).then(() => {
      const dev = MOCK.devices.find(d => d.deviceId === deviceId)
      if (!dev) throw new Error('设备不存在')
      Object.assign(dev, command)
      wx.showToast({ title: '✅ 指令已下发', icon: 'none' })
      return { success: true, deviceId, command }
    })
  },

  executeScene(roomId, sceneId) {
    if (!USE_MOCK) return request({ url: '/api/iot/scenes/activate', method: 'POST', data: { room_id: roomId, scene: sceneId } })
    return delay(800).then(() => {
      const scene = MOCK.scenes.find(s => s.sceneId === sceneId)
      if (!scene) throw new Error('场景不存在')
      const p = scene.params
      MOCK.devices.forEach(d => {
        if (d.roomId !== roomId) return
        if (d.type === 'Curtain' && p.curtain) d.position = p.curtain
        if (d.type === 'AC' && p.ac) {
          d.mode = p.ac.on ? 'cool' : 'off'
          if (p.ac.temp) d.temperature = p.ac.temp
        }
        if (d.type === 'Light' && p.lights) {
          d.brightness = p.lights.brightness || 0
          d.colorTemp = p.lights.colorTemp || 4000
        }
        if (d.type === 'Speaker' && p.music) {
          d.playing = p.music.on || false
        }
      })
      return { success: true, sceneId, sceneName: scene.name }
    })
  },

  getActiveAlerts() {
    return delay().then(() => [])
  },

  // ── 音频 ──

  getAudioStatus(roomId) {
    return delay().then(() => {
      const speakers = MOCK.devices.filter(d => d.roomId === roomId && d.type === 'Speaker')
      if (!speakers.length) return null
      return {
        roomId, online: speakers.some(s => s.status === 'Online'),
        speakers, volume: speakers[0]?.volume || 0, playing: speakers[0]?.playing || false,
        source: speakers[0]?.source || 'none'
      }
    })
  },

  setVolume(roomId, volume) {
    return delay(150).then(() => {
      MOCK.devices.forEach(d => { if (d.roomId === roomId && d.type === 'Speaker') d.volume = volume })
      wx.showToast({ title: '音量已设为 ' + volume + '%', icon: 'none' })
      return { success: true, roomId, volume }
    })
  },

  // ── 订单 ──

  createBooking(booking) {
    if (!USE_MOCK) return request({ url: '/api/orders', method: 'POST', data: booking })
    return delay(500).then(() => {
      const bookings = lsGet('bookings', [])
      const id = 'ORD' + String(Date.now()).slice(-6)
      const b = {
        orderId: id, status: 'Booked', doorCode: String(Math.floor(1000 + Math.random() * 9000)),
        created: new Date().toISOString(), phone: (lsGet('user', {}) || {}).phone || '',
        ...booking
      }
      bookings.push(b)
      lsSet('bookings', bookings)
      const user = lsGet('user', {})
      if (booking.paymentMethod === 'Balance' && user.balance !== undefined) {
        user.balance -= (booking.amount || 0)
        lsSet('user', user)
      }
      return b
    })
  },

  getUserOrders() {
    return delay().then(() => {
      const bookings = lsGet('bookings', [])
      const user = lsGet('user', null)
      if (user) return bookings.filter(b => b.phone === user.phone).sort((a, b) => new Date(b.created) - new Date(a.created))
      return []
    })
  },

  cancelOrder(orderId) {
    return delay(200).then(() => {
      const bookings = lsGet('bookings', [])
      bookings.forEach(b => { if (b.orderId === orderId) b.status = 'Cancelled' })
      lsSet('bookings', bookings)
      return { success: true }
    })
  },

  // ── 商品 ──

  getProducts(category) {
    if (!USE_MOCK) return request({ url: `/api/products?category=${category || ''}` })
    return delay().then(() => {
      if (category) return MOCK.products.filter(p => p.category === category)
      return MOCK.products.slice()
    })
  },

  getCart() {
    return Promise.resolve(lsGet('tea_cart', []))
  },

  addToCart(product) {
    const cart = lsGet('tea_cart', [])
    const found = cart.find(item => item.productId === product.productId)
    if (found) { found.qty = (found.qty || 1) + 1 } else { product.qty = 1; cart.push(product) }
    lsSet('tea_cart', cart)
    return Promise.resolve(cart)
  },

  removeFromCart(productId) {
    const cart = lsGet('tea_cart', []).filter(item => item.productId !== productId)
    lsSet('tea_cart', cart)
    return Promise.resolve(cart)
  },

  createShopOrder(items, paymentMethod, total) {
    return delay(400).then(() => {
      const order = {
        orderId: 'SHP' + String(Date.now()).slice(-6),
        items, total, paymentMethod, status: 'Paid', created: new Date().toISOString()
      }
      const shopOrders = lsGet('shop_orders', [])
      shopOrders.push(order)
      lsSet('shop_orders', shopOrders)
      lsSet('tea_cart', [])
      if (paymentMethod === 'Balance') {
        const user = lsGet('user', {})
        user.balance = (user.balance || 0) - total
        lsSet('user', user)
      }
      return order
    })
  },

  // ── 余额 ──

  getBalance() {
    return delay(100).then(() => (lsGet('user', {})).balance || 0)
  },

  topUp(amount, paymentMethod) {
    return delay(500).then(() => {
      const user = lsGet('user', {})
      let bonus = 0
      if (!user._firstRecharge) { bonus = Math.round(amount * 0.3); user._firstRecharge = true }
      user.balance = (user.balance || 0) + amount + bonus
      lsSet('user', user)
      return { success: true, amount, bonus, newBalance: user.balance }
    })
  },

  // ── 优惠券 ──

  verifyCoupon(code) {
    return delay(300).then(() => {
      const c = MOCK.couponDB[code]
      if (!c) throw new Error('券码不存在')
      if (c.used) throw new Error('该券已被使用')
      return { code, value: c.value, type: c.type, desc: c.desc, platform: c.platform }
    })
  },

  getUserCoupons() {
    return delay().then(() => {
      return Object.entries(MOCK.couponDB).map(([code, c]) => ({
        code, value: c.value, type: c.type, desc: c.desc, platform: c.platform, used: c.used, expiry: c.expiry
      }))
    })
  },

  // ── 扫码消费（V1.1） ──

  scanRoomStatus(roomId) {
    return delay().then(() => {
      const room = MOCK.rooms.find(r => r.roomId === roomId)
      if (!room) throw new Error('房间不存在')
      return {
        roomId, roomName: room.name, storeId: 'ST001', storeName: '盈隆店',
        status: room.status === 'Active' ? 'Active' : 'Inactive',
        hasActiveOrder: roomId === 'RM004' || roomId === 'RM002',
        activeOrderId: 'ORD001',
        message: '欢迎使用 ' + room.name + '，可扫码加购'
      }
    })
  },

  getScanBill(roomId) {
    return delay().then(() => ({
      roomId, roomName: roomId === 'RM004' ? '大茶室C' : '中茶室A',
      activeOrderId: 'ORD001', billId: 'BILL001', billStatus: 'Active',
      billSummary: { roomCharge: 180, scanTotal: 156, pendingPayment: 156, totalPaid: 180 },
      scanOrders: [
        { orderId: 'SCAN001', orderNumber: 'SCAN20260606001', createdAt: new Date().toISOString(),
          items: [{ productName: '安吉白茶', quantity: 1, subtotal: 68 }], totalAmount: 68, status: '挂账中', canCancel: true },
        { orderId: 'SCAN002', orderNumber: 'SCAN20260606002', createdAt: new Date().toISOString(),
          items: [{ productName: '手工茶点A', quantity: 2, subtotal: 76 }], totalAmount: 76, status: '挂账中', canCancel: true },
        { orderId: 'SCAN003', orderNumber: 'SCAN20260606003', createdAt: new Date().toISOString(),
          items: [{ productName: '定制茶具A', quantity: 1, subtotal: 12 }], totalAmount: 12, status: '挂账中', canCancel: false }
      ]
    }))
  },

  createScanOrder(data) {
    return delay(500).then(() => {
      const orderId = 'SCAN' + String(Date.now()).slice(-6)
      const total = data.items.reduce((s, i) => s + (i.unitPrice || 0) * (i.quantity || 1), 0)
      return { orderId, orderNumber: 'SCAN' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + orderId.slice(-4).toUpperCase(),
        roomId: data.roomId, storeId: data.storeId, totalAmount: total, itemCount: data.items.length,
        status: 'Completed', tags: ['扫码加购'], message: '扫码点单成功，已挂入房间账单' }
    })
  },

  cancelScanOrder(orderId) {
    return delay(200).then(() => ({
      success: true, orderId, refundStatus: '无需退款（挂账未支付）', stockRollback: true,
      cancelledAt: new Date().toISOString(), message: '扫码订单已成功撤销'
    }))
  },

  settleScanBill(roomId, data) {
    return delay(500).then(() => ({
      success: true, settleId: 'STL' + String(Date.now()).slice(-6), roomId,
      totalAmount: 156, memberBalanceUsed: data.useMemberBalance ? 50 : 0,
      paymentAmount: data.useMemberBalance ? 106 : 156, paymentMethod: data.paymentMethod || 'WxPay',
      ordersSettled: 3, invoiceNumber: data.issueInvoice ? ('INV-20260606-' + String(Date.now()).slice(-4)) : null,
      message: '结算成功，共 3 笔订单'
    }))
  }
}

module.exports = API
