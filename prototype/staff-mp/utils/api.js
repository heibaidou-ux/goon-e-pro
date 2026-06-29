/**
 * 高岸ERP 店员端 SDK — 微信小程序版
 */
var MOCK = require('./mock-data')

var LS_PREFIX = 'staff_'

function lsGet(key, fallback) {
  try { var val = wx.getStorageSync(LS_PREFIX + key); return val || fallback } catch (e) { return fallback }
}
function lsSet(key, val) { try { wx.setStorageSync(LS_PREFIX + key, val) } catch (e) { } }
function lsRemove(key) { try { wx.removeStorageSync(LS_PREFIX + key) } catch (e) { } }

var USE_MOCK = false

function delay(ms) {
  ms = ms || (150 + Math.random() * 250)
  return new Promise(function(resolve) { setTimeout(resolve, ms) })
}

var API = {
  // ── 认证 ──
  login: function(username, password) {
    return delay().then(function() {
      if (password !== '8888') throw new Error('密码错误')
      var user = { userId: 'E001', username: username, displayName: '店员小张', role: 'staff', storeId: 'ST001', storeName: '盈隆店' }
      lsSet('logged_in', true)
      lsSet('user', user)
      return user
    })
  },

  logout: function() { lsRemove('logged_in'); lsRemove('user'); return Promise.resolve({ success: true }) },
  getCurrentUser: function() { return Promise.resolve(lsGet('user', null)) },
  isLoggedIn: function() { return !!lsGet('logged_in', false) },

  // ── Dashboard ──
  getDashboardStats: function() {
    return delay().then(function() {
      return {
        roomCount: { total: 6, inUse: 2, booked: 1, free: 3 },
        todayRevenue: 3860,
        todayOrders: 12,
        pendingTasks: 5,
        deviceOnlineRate: '94%',
        alerts: 2
      }
    })
  },

  // ── 房间状态 ──
  getRoomStatusList: function() {
    return delay().then(function() {
      return MOCK.rooms.map(function(r) {
        var order = null
        if (r.roomId === 'RM004') order = { orderId: 'ORD001', customerName: '张先生', start: '10:00', end: '11:30' }
        if (r.roomId === 'RM002') order = { orderId: 'ORD002', customerName: '李女士', start: '14:00', end: '16:00' }
        return {
          roomId: r.roomId, name: r.name, type: r.type, capacity: r.capacity,
          status: r.status, currentOrder: order,
          statusLabel: r.roomId === 'RM004' ? '使用中' : r.roomId === 'RM002' ? '已预订' : '空闲',
          statusColor: r.roomId === 'RM004' ? '#366EF4' : r.roomId === 'RM002' ? '#9C27B0' : '#00A870'
        }
      })
    })
  },

  // ── 设备 ──
  getDeviceList: function(roomId) {
    return delay().then(function() {
      var list = MOCK.devices
      if (roomId) list = list.filter(function(d) { return d.roomId === roomId })
      var typeLabelMap = {Lock:'门锁',AC:'空调',Light:'灯光',Curtain:'窗帘',Speaker:'音响'}
      var typeIconMap = {Lock:'🔒',AC:'❄️',Light:'💡',Curtain:'🪟',Speaker:'🔊'}
      return list.map(function(d) {
        return { roomId: d.roomId, deviceId: d.deviceId, type: d.type, status: d.status, protocol: d.protocol,
          typeLabel: typeLabelMap[d.type] || d.type, typeIcon: typeIconMap[d.type] || '📡' }
      })
    })
  },

  getDeviceStats: function() {
    return delay().then(function() {
      var total = MOCK.devices.length
      var online = MOCK.devices.filter(function(d) { return d.status === 'Online' }).length
      return { total: total, online: online, offline: total - online, rate: Math.round(online / total * 100) + '%' }
    })
  },

  controlDevice: function(deviceId, command) {
    return delay(200).then(function() {
      var dev = null
      for (var i = 0; i < MOCK.devices.length; i++) {
        if (MOCK.devices[i].deviceId === deviceId) { dev = MOCK.devices[i]; break }
      }
      if (!dev) throw new Error('设备不存在')
      Object.assign(dev, command)
      return { success: true, deviceId: deviceId, command: command }
    })
  },

  executeScene: function(roomId, sceneId) {
    return delay(600).then(function() {
      var scene = null
      for (var i = 0; i < MOCK.scenes.length; i++) {
        if (MOCK.scenes[i].sceneId === sceneId) { scene = MOCK.scenes[i]; break }
      }
      if (!scene) throw new Error('场景不存在')
      return { success: true, sceneId: sceneId, sceneName: scene.name, sceneIcon: scene.icon }
    })
  },

  // ── 清洁任务 ──
  getCleaningTasks: function() {
    return delay().then(function() {
      return {
        pending: [{ taskId: 'CL001', roomId: 'RM003', roomName: '中茶室B', type: 'FullClean', priority: 'High', created: '2026-06-06T09:00:00', deadline: '2026-06-06T10:30:00' }],
        inProgress: [{ taskId: 'CL002', roomId: 'RM002', roomName: '中茶室A', type: 'QuickClean', priority: 'Normal', created: '2026-06-06T08:30:00', deadline: '2026-06-06T09:30:00' }],
        completed: [{ taskId: 'CL003', roomId: 'RM001', roomName: '大会议室', type: 'FullClean', priority: 'Normal', created: '2026-06-06T07:00:00', deadline: '2026-06-06T08:00:00' }]
      }
    })
  },

  acceptCleaningTask: function(taskId) { return delay().then(function() { return { success: true } }) },
  completeCleaningTask: function(taskId) { return delay().then(function() { return { success: true } }) },

  // ── 巡检 ──
  getInspections: function() {
    return delay().then(function() {
      return [{
        planId: 'INSP001', date: '2026-06-06', type: 'Daily', status: 'InProgress',
        progress: { total: 12, completed: 3 },
        items: [
          { category: '设备间', items: [{ name: '机柜温度', status: 'normal' }, { name: '交换机指示灯', status: 'normal' }] },
          { category: '公共区域', items: [{ name: '走廊照明', status: 'normal' }, { name: '前台设备', status: 'normal' }] }
        ]
      }]
    })
  },

  // ── 订单管理 ──
  getTodayOrders: function() {
    return delay().then(function() {
      return MOCK.orders.map(function(o) {
        var labels = { InUse: '使用中', Booked: '已预订', Completed: '已完成' }
        return { orderId: o.orderId, customerName: o.customerName, roomId: o.roomId, roomName: o.roomName,
          status: o.status, statusLabel: labels[o.status] || o.status, start: o.start, end: o.end,
          amount: o.amount, paymentMethod: o.paymentMethod }
      })
    })
  },

  getActiveOrders: function() {
    return delay().then(function() {
      return MOCK.orders.filter(function(o) { return o.status === 'InUse' || o.status === 'Booked' })
    })
  },

  // ── 商品管理 ──
  getProducts: function() { return delay().then(function() { return MOCK.products.slice() }) },
  updateProduct: function(productId, data) { return delay().then(function() { return { success: true } }) },

  // ── 考勤 ──
  getAttendance: function(date) { return delay().then(function() { return [] }) },
  clockIn: function() { return delay().then(function() { return { success: true, time: new Date().toISOString() } }) },
  clockOut: function() { return delay().then(function() { return { success: true, time: new Date().toISOString() } }) },

  // ── 排班 ──
  getSchedule: function(date) { return delay().then(function() { return [] }) },

  // ── 待办 ──
  getTodos: function() {
    return delay().then(function() {
      return [
        { id: 'T001', type: 'cleaning', title: '中茶室B 退房清洁', priority: 'high', deadline: '10:30' },
        { id: 'T002', type: 'inspection', title: '完成今日设备巡检', priority: 'normal', deadline: '今日' },
        { id: 'T003', type: 'order', title: '大会议室 赵总 即将到店（14:00）', priority: 'normal' }
      ]
    })
  },

  // ── 应收 ──
  getReceivables: function() {
    return delay().then(function() {
      return [{ orderId: 'ORD002', customerName: '李女士', roomName: '中茶室A', amount: 160, status: 'unpaid', dueDate: '2026-06-06' }]
    })
  },

  // ── 对账 ──
  getReconciliation: function(date) {
    return delay().then(function() {
      return { date: date, revenue: 3860, expense: 1200, net: 2660, status: 'balanced' }
    })
  }
}

module.exports = API
