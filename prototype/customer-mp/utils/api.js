/**
 * 高岸ERP 统一API层
 * 支持 Mock(本地) / Live(后端) 双模式
 * USE_MOCK = false 时直连后端 FastAPI
 */
const MOCK = require('./mock-data')

// ── 后端配置 ──
const API_BASE = 'https://erp.highbank.cn'
const USE_MOCK = false  // false = 连后端

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

// ── 验证函数 ──
function validatePhone(phone) {
  if (!phone) return true // 可以为空
  // 手机号11位 或 带区号的座机(区号3-4位+号码7-8位)
  return /^1\d{10}$/.test(phone) || /^0\d{2,3}-?\d{7,8}$/.test(phone)
}

function validateTime(start, end) {
  if (!start || !end) return true
  var sp = start.split(':'), ep = end.split(':')
  var sm = parseInt(sp[0])*60+parseInt(sp[1]), em = parseInt(ep[0])*60+parseInt(ep[1])
  return em > sm
}

function isPastTime(timeStr) {
  if (!timeStr) return false
  var now = new Date()
  var curMin = now.getHours()*60+now.getMinutes()
  var sp = timeStr.split(':')
  return parseInt(sp[0])*60+parseInt(sp[1]) <= curMin
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
          setToken(null)
          lsSet('logged_in', false)
          // 店员端：弹对话框让用户选择是否重新登录
          var role = lsGet('user_role', '')
          if (role === 'staff') {
            wx.showModal({
              title: '登录已过期',
              content: '您的登录已过期，是否重新登录？',
              confirmText: '重新登录',
              cancelText: '留在当前页',
              success: function(m) {
                if (m.confirm) {
                  wx.reLaunch({ url: '/pages/staff/staff-login/staff-login' })
                }
              }
            })
          }
          reject(new Error('登录已过期，请重新登录'))
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

// ── 当前数据版本 ──
const DB_VERSION = '1.9.45'

const API = {
  ROLES,
  validatePhone: validatePhone,
  validateTime: validateTime,
  isPastTime: isPastTime,

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
  // ── 微信一键登录 ──
  async wechatLogin(code, userInfo) {
    if (!USE_MOCK) {
      const data = await request({ url: '/api/auth/wechat-login', method: 'POST', data: { code, nickname: (userInfo && userInfo.nickName) || '', avatar: (userInfo && userInfo.avatarUrl) || '' } })
      setToken(data.access_token)
      lsSet('logged_in', true)
      const user = data.user
      user.role = ROLES.GUEST
      lsSet('user', user)
      lsSet('user_role', ROLES.GUEST)
      return user
    }
    return delay().then(() => {
      var nickname = (userInfo && userInfo.nickName) || '微信用户'
      var openid = 'mock_wx_' + code.slice(-8)
      var users = lsGet('users', {})
      var user = null
      for (var k in users) { if (users[k].wechat_openid === openid) { user = users[k]; break } }
      if (!user) {
        user = {
          phone: '', name: nickname, memberLevel: 'Silver', balance: 280,
          totalSpent: 0, visitCount: 0, wechat_openid: openid,
          wechat_nickname: nickname, wechat_avatar: (userInfo && userInfo.avatarUrl) || '',
          role: ROLES.GUEST, created: new Date().toISOString(), tags: []
        }
        users['wx_' + openid.slice(-6)] = user; lsSet('users', users)
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

  // ── 种子数据（版本升级时清空一次，之后不再动）──
  _ensureSeedData: function() {
    var ver = lsGet('_db_ver', '')
    // 版本号不同则清空旧数据重新播种
    if (ver !== DB_VERSION) {
      lsRemove('bookings'); lsRemove('shop_orders'); lsSet('_db_ver', DB_VERSION)
    }
    var bookings = lsGet('bookings', [])
    if (bookings.length > 0) return
    var now = new Date()
    var ds = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    var h = now.getHours(), m = now.getMinutes()
    var endH = (h + 3) % 24
    lsSet('bookings', [
      { orderId:'ORD001', roomId:'RM004', roomName:'白沙瓦', customerName:'张先生', status:'InUse', date:ds, time:String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+'-'+String(endH).padStart(2,'0')+':00', bookedTime:String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+'-'+String(endH).padStart(2,'0')+':00', amount:180, doorCode:'8264', created: new Date().toISOString() },
      { orderId:'ORD002', roomId:'RM002', roomName:'翡冷翠', customerName:'李女士', status:'Booked', date:ds, time:String((h+1)%24).padStart(2,'0')+':00-'+String(endH).padStart(2,'0')+':00', bookedTime:String((h+1)%24).padStart(2,'0')+':00-'+String(endH).padStart(2,'0')+':00', amount:160, doorCode:'7391', created: new Date().toISOString() },
      { orderId:'ORD003', roomId:'RM003', roomName:'布拉格', customerName:'王先生', status:'Booked', date:ds, time:String((h+2)%24).padStart(2,'0')+':00-'+String(endH+1).padStart(2,'0')+':00', bookedTime:String((h+2)%24).padStart(2,'0')+':00-'+String(endH+1).padStart(2,'0')+':00', amount:120, doorCode:'5123', created: new Date().toISOString() },
      { orderId:'ORD004', roomId:'RM001', roomName:'丰沙里', customerName:'赵先生', status:'Booked', date:ds, time:'23:30-01:30', bookedTime:'23:30-01:30', amount:200, doorCode:'6688', created: new Date().toISOString() },
    ])
  },

  // ── 房间 ──
  getRooms(bookableOnly) {
    if (!USE_MOCK) {
      return request({ url: '/api/rooms' }).then(function(data) {
        var list = data || []
        if (!Array.isArray(list)) list = []
        var result = []
        for (var i = 0; i < list.length; i++) {
          var r = list[i]
          result.push({
            roomId: r.room_id || r.roomId || '',
            name: r.name || '',
            type: r.type || '',
            capacity: r.capacity || 0,
            area: r.area || 0,
            floor: r.floor || '',
            description: r.description || '',
            facilities: r.facilities || [],
            pricePerHour: r.price_per_hour || r.pricePerHour || 120,
            pricePerHalfHour: r.price_per_half_hour || r.pricePerHalfHour || 60,
            status: (r.status === false || r.is_active === false) ? 'Inactive' : 'Active',
            bookable: r.bookable !== false,
          })
        }
        return result
      })
    }
    return delay().then(() => {
      let list = MOCK.rooms.slice()
      if (bookableOnly) list = list.filter(r => r.bookable !== false)
      return list
    })
  },

  getRoomById(roomId) {
    if (!USE_MOCK) return request({ url: '/api/rooms/' + roomId }).then(function(r) {
      if (!r) return null
      return {
        roomId: r.room_id || r.roomId || '',
        name: r.name || '',
        type: r.type || '',
        capacity: r.capacity || 0,
        area: r.area || 0,
        floor: r.floor || '',
        description: r.description || '',
        facilities: r.facilities || [],
        pricePerHour: r.price_per_hour || r.pricePerHour || 120,
        pricePerHalfHour: r.price_per_half_hour || r.pricePerHalfHour || 60,
        status: (r.status === false || r.is_active === false) ? 'Inactive' : 'Active',
        bookable: r.bookable !== false,
      }
    })
    return delay().then(() => {
      for (var i = 0; i < MOCK.rooms.length; i++) {
        if (MOCK.rooms[i].roomId === roomId) return JSON.parse(JSON.stringify(MOCK.rooms[i]))
      }
      throw new Error('房间不存在')
    })
  },

  getRoomBookings(roomId, date) {
    if (!USE_MOCK) return request({ url: '/api/orders/active' })
    this._cleanExpiredOrders()
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

  // ── 订单到期自动清理（每次读订单前调用，同步全局状态）──
  // 辅助：解析时间段，返回 {startMin, endMin, crossDay}，跨日时endMin+1440
  _parseTimeSlot: function(timeStr) {
    if (!timeStr) return null
    var parts = timeStr.split('-')
    if (parts.length < 2) return null
    var sp = parts[0].split(':'), ep = parts[1].split(':')
    if (sp.length < 2 || ep.length < 2) return null
    var sm = parseInt(sp[0])*60+parseInt(sp[1])
    var em = parseInt(ep[0])*60+parseInt(ep[1])
    var crossDay = em <= sm
    if (crossDay) em += 1440
    return { startMin: sm, endMin: em, crossDay: crossDay }
  },

  _cleanExpiredOrders: function() {
    var bookings = lsGet('bookings', [])
    var now = new Date()
    var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    var yesterday = new Date(now); yesterday.setDate(now.getDate()-1)
    var yesterdayStr = yesterday.getFullYear()+'-'+String(yesterday.getMonth()+1).padStart(2,'0')+'-'+String(yesterday.getDate()).padStart(2,'0')
    var curMin = now.getHours()*60+now.getMinutes()
    var changed = false

    for (var i = 0; i < bookings.length; i++) {
      var b = bookings[i]
      if (b.status === 'Cancelled' || b.status === 'Completed' || b.status === 'Expired') continue
      if (!b.date || !b.time) continue

      var t = this._parseTimeSlot(b.time)
      if (!t) continue

      var isToday = b.date === todayStr
      var isYesterday = b.date === yesterdayStr

      if (b.status === 'InUse') {
        // InUse：过了结束时间（+15分钟宽限）→ Completed
        // 跨日订单：结束时间在第二天

        // 今天的订单非跨日
        if (isToday && !t.crossDay && curMin >= t.endMin + 15) {
          b.status = 'Completed'; changed = true
        }
        // 今天的订单跨日（结束在次日）
        if (isToday && t.crossDay && curMin >= t.endMin) {  // endMin已+1440
          b.status = 'Completed'; changed = true
        }
        // 昨天的跨日订单（当前时间在第二天）
        if (isYesterday && t.crossDay && curMin >= t.endMin - 1440 + 15) {
          b.status = 'Completed'; changed = true
        }
        // 昨天非跨日订单
        if (isYesterday && !t.crossDay) {
          b.status = 'Completed'; changed = true
        }
        // 更早的日期
        if (b.date && b.date < yesterdayStr) {
          b.status = 'Completed'; changed = true
        }
      } else if (b.status === 'Booked') {
        // Booked：到了结束时间还没签到（没转为InUse）→ Expired
        // 跨日Booked：当前时间过了跨日调整后的结束时间
        if (isToday) {
          if (!t.crossDay && curMin >= t.endMin) {
            b.status = 'Expired'; changed = true
          }
          if (t.crossDay && curMin >= t.endMin) {  // endMin已+1440, curMin不会>=1440除非过了一天
            b.status = 'Expired'; changed = true
          }
        }
        // 昨天的跨日订单
        if (isYesterday && t.crossDay && curMin >= t.endMin - 1440) {
          b.status = 'Expired'; changed = true
        }
        // 昨天非跨日
        if (isYesterday && !t.crossDay) {
          b.status = 'Expired'; changed = true
        }
        // 更早日期
        if (b.date && b.date < yesterdayStr) {
          b.status = 'Expired'; changed = true
        }
      }
    }

    if (changed) lsSet('bookings', bookings)
    return bookings
  },

  // ── 订单 ──
  createBooking(booking) {
    if (!USE_MOCK) {
      var startTime = '', endTime = ''
      var timeStr = booking.time || booking.slot || ''
      var parts = timeStr.split('-')
      if (parts.length >= 2) {
        startTime = booking.date + 'T' + parts[0].trim() + ':00'
        endTime = booking.date + 'T' + parts[1].trim() + ':00'
      }
      return request({ url: '/api/operations/room-appointments', method: 'POST', data: {
        orderId: booking.orderId || ('ORD' + String(Date.now()).slice(-6)),
        roomId: booking.roomId,
        customerId: '',
        startTime: startTime,
        endTime: endTime,
        doorPassword: ''
      } })
    }
    return delay(500).then(() => {
      var bookings = lsGet('bookings', [])
      var id = 'ORD' + String(Date.now()).slice(-6)
      var b = Object.assign({
        orderId: id, status: 'Booked', doorCode: String(Math.floor(1000 + Math.random() * 9000)),
        bookedTime: booking.time || '', created: new Date().toISOString(),
        phone: (lsGet('user', {}) || {}).phone || ''
      }, booking)
      b.bookedTime = booking.time || b.time || ''
      bookings.push(b); lsSet('bookings', bookings)
      var user = lsGet('user', {})
      if (booking.paymentMethod === 'Balance' && user.balance !== undefined) {
        user.balance -= (booking.amount || 0); lsSet('user', user)
      }
      return b
    })
  },

  // ── 给订单添加跨日标注 ──
  _annotateOrder: function(order) {
    if (!order.time) return order
    var parts = order.time.split('-')
    if (parts.length < 2) return order
    var sp = parts[0].split(':'), ep = parts[1].split(':')
    if (sp.length < 2 || ep.length < 2) return order
    var sm = parseInt(sp[0])*60+parseInt(sp[1])
    var em = parseInt(ep[0])*60+parseInt(ep[1])
    var crossDay = em <= sm
    if (crossDay) {
      order.crossDay = true
      // 计算结束日期
      if (order.date) {
        var d = new Date(order.date)
        d.setDate(d.getDate() + 1)
        var m = String(d.getMonth()+1).padStart(2,'0'), dd = String(d.getDate()).padStart(2,'0')
        order.endDate = d.getFullYear()+'-'+m+'-'+dd
        order._timeDisplay = order.date.slice(5) + ' ' + parts[0] + ' → ' + order.endDate.slice(5) + ' ' + parts[1]
      }
    }
    return order
  },

  getAllOrders() {
    this._ensureSeedData()
    this._cleanExpiredOrders()
    return delay().then(() => {
      var bookings = lsGet('bookings', [])
      var nameMap = {'中茶室A':'翡冷翠','中茶室B':'布拉格','大茶室C':'白沙瓦','大会议室':'丰沙里'}
      for (var i = 0; i < bookings.length; i++) {
        if (nameMap[bookings[i].roomName]) bookings[i].roomName = nameMap[bookings[i].roomName]
        this._annotateOrder(bookings[i])
      }
      return bookings
    })
  },

  getUserOrders() {
    this._cleanExpiredOrders()
    return delay().then(() => {
      var bookings = lsGet('bookings', [])
      var user = lsGet('user', null)
      for (var i = 0; i < bookings.length; i++) this._annotateOrder(bookings[i])
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
    if (!USE_MOCK) {
      return request({ url: '/api/products' + (category ? '?categoryId=' + category : '') }).then(function(data) {
        var items = (data && data.items) || (Array.isArray(data) ? data : [])
        var result = []
        for (var i = 0; i < items.length; i++) {
          var p = items[i]
          result.push({
            productId: p.productId || p.product_id || '',
            name: p.name || '',
            desc: p.description || p.desc || '',
            price: p.retailPrice || p.price || p.retail_price || 0,
            category: p.categoryId || p.category || '',
            spec: p.spec || '',
            origin: p.origin || '',
            story: p.story || '',
            brewingTips: p.brewingTips || '',
            isActive: p.isActive !== false,
          })
        }
        return result
      })
    }
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
    if (!USE_MOCK) {
      var user = lsGet('user', {})
      var userId = user.phone || user.username || ''
      var roomId = (deliveryInfo && deliveryInfo.roomId) || ''
      // 余额支付：先扣款
      if (paymentMethod === 'Balance') {
        return request({ url: '/api/auth/balance/deduct', method: 'POST', data: { amount: total, order_id: 'SHP' + String(Date.now()).slice(-6) } }).then(function() {
          return request({ url: '/api/shop/orders', method: 'POST', data: {
            customer_name: user.display_name || user.name || '',
            customer_phone: user.phone || '',
            room_id: roomId,
            payment_method: paymentMethod,
            total_amount: total,
            items: (items || []).map(function(i) { return { product_id: i.productId, quantity: i.qty || 1, unit_price: i.price || 0 } })
          } }).then(function(r) { lsSet('tea_cart', []); return r })
        })
      }
      // 微信支付：直接下单
      return request({ url: '/api/shop/orders', method: 'POST', data: {
        customer_name: user.display_name || user.name || '',
        customer_phone: user.phone || '',
        room_id: roomId,
        payment_method: paymentMethod,
        total_amount: total,
        items: (items || []).map(function(i) { return { product_id: i.productId, quantity: i.qty || 1, unit_price: i.price || 0 } })
      } }).then(function(r) { lsSet('tea_cart', []); return r })
    }
    return delay(400).then(function() {
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
        var u = lsGet('user', {})
        u.balance = (u.balance || 0) - total; lsSet('user', u)
      }
      return order
    })
  },

  getShopOrders() { return delay().then(() => lsGet('shop_orders', [])) },

  // ── 余额 ──
  getBalance() {
    if (!USE_MOCK) return request({ url: '/api/auth/balance' }).then(function(d) { return d.balance || 0 }).catch(function() { return (lsGet('user', {})).balance || 0 })
    return delay(100).then(() => (lsGet('user', {})).balance || 0)
  },

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
      return { roomId, roomName: room.name, storeId: 'ST001', storeName: '盈隆店', status: 'Active', hasActiveOrder: true, activeOrderId: 'ORD001', message: '欢迎使用 ' + room.name }
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
  getLogistics(orderId) { return delay().then(() => null) },

  wechatPay(totalFee, body) {
    if (!USE_MOCK) {
      // 优先使用已存储的wechat_openid（微信登录后已保存）
      var user = lsGet('user', null)
      var openid = user ? (user.wechat_openid || '') : ''
      if (openid) {
        return request({ url: '/api/payment/wxpay/unified-order', method: 'POST', data: { total_fee: totalFee, body: body, openid: openid } }).then(function(data) {
          if (!data || !data.pay_params) throw new Error('统一下单失败')
          return new Promise(function(resolve, reject) {
            wx.requestPayment({
              timeStamp: data.pay_params.timeStamp,
              nonceStr: data.pay_params.nonceStr,
              package: data.pay_params.package,
              signType: data.pay_params.signType,
              paySign: data.pay_params.paySign,
              success: function() { resolve(data) },
              fail: function(err) { reject(new Error(err.errMsg || '支付失败')) }
            })
          })
        })
      }
      // 没有openid则用wx.login获取code交给后端处理
      var self = this
      return new Promise(function(resolve, reject) {
        wx.login({
          success: function(r) {
            if (!r.code) { reject(new Error('获取微信登录态失败')); return }
            request({ url: '/api/payment/wxpay/unified-order', method: 'POST', data: { total_fee: totalFee, body: body, wx_code: r.code } }).then(function(data) {
              if (!data || !data.pay_params) { reject(new Error('统一下单失败')); return }
              wx.requestPayment({
                timeStamp: data.pay_params.timeStamp,
                nonceStr: data.pay_params.nonceStr,
                package: data.pay_params.package,
                signType: data.pay_params.signType,
                paySign: data.pay_params.paySign,
                success: function() { resolve(data) },
                fail: function(err) { reject(new Error(err.errMsg || '支付失败')) }
              })
            }).catch(function(err) { reject(err) })
          },
          fail: function() { reject(new Error('微信登录失败')) }
        })
      })
    }
    return delay(500).then(function() {
      return { success: true, out_trade_no: 'MOCK' + String(Date.now()).slice(-10), prepay_id: 'mock' }
    })
  },
}
module.exports = API
