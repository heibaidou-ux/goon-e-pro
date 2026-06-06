/**
 * 高岸ERP 店员端 SDK — 微信小程序版
 */
const MOCK = require('./mock-data')

const LS_PREFIX = 'staff_'

function lsGet(key, fallback) {
  try { const val = wx.getStorageSync(LS_PREFIX + key); return val || fallback } catch (e) { return fallback }
}
function lsSet(key, val) { try { wx.setStorageSync(LS_PREFIX + key, val) } catch (e) { } }
function lsRemove(key) { try { wx.removeStorageSync(LS_PREFIX + key) } catch (e) { } }

const USE_MOCK = true

function delay(ms) {
  ms = ms || (150 + Math.random() * 250)
  return new Promise(resolve => setTimeout(resolve, ms))
}

const API = {
  // ── 认证 ──
  login(username, password) {
    return delay().then(() => {
      if (password !== '8888') throw new Error('密码错误')
      const user = { userId: 'E001', username, displayName: '店员小张', role: 'staff', storeId: 'ST001', storeName: '盈隆店' }
      lsSet('logged_in', true)
      lsSet('user', user)
      return user
    })
  },
  logout() { lsRemove('logged_in'); lsRemove('user'); return Promise.resolve({ success: true }) },
  getCurrentUser() { return Promise.resolve(lsGet('user', null)) },
  isLoggedIn() { return !!lsGet('logged_in', false) },

  // ── Dashboard ──
  getDashboardStats() {
    return delay().then(() => ({
      roomCount: { total: 6, inUse: 2, booked: 1, free: 3 },
      todayRevenue: 3860,
      todayOrders: 12,
      pendingTasks: 5,
      deviceOnlineRate: '94%',
      alerts: 2
    }))
  },

  // ── 房间状态 ──
  getRoomStatusList() {
    return delay().then(() => MOCK.rooms.map(r => ({
      ...r,
      currentOrder: r.roomId === 'RM004' ? { orderId: 'ORD001', customerName: '张先生', start: '10:00', end: '11:30' }
        : r.roomId === 'RM002' ? { orderId: 'ORD002', customerName: '李女士', start: '14:00', end: '16:00' } : null,
      statusLabel: r.roomId === 'RM004' ? '使用中' : r.roomId === 'RM002' ? '已预订' : '空闲',
      statusColor: r.roomId === 'RM004' ? '#366EF4' : r.roomId === 'RM002' ? '#9C27B0' : '#00A870'
    }))
  },

  // ── 设备 ──
  getDeviceList(roomId) {
    return delay().then(() => {
      let list = MOCK.devices
      if (roomId) list = list.filter(d => d.roomId === roomId)
      return list.map(d => ({ ...d, typeLabel: MOCK.deviceTypes[d.type]?.label || d.type, typeIcon: MOCK.deviceTypes[d.type]?.icon || '📡' }))
    })
  },
  getDeviceStats() {
    return delay().then(() => {
      const total = MOCK.devices.length
      const online = MOCK.devices.filter(d => d.status === 'Online').length
      return { total, online, offline: total - online, rate: Math.round(online / total * 100) + '%' }
    })
  },
  controlDevice(deviceId, command) {
    return delay(200).then(() => {
      const dev = MOCK.devices.find(d => d.deviceId === deviceId)
      if (!dev) throw new Error('设备不存在')
      Object.assign(dev, command)
      return { success: true, deviceId, command }
    })
  },
  executeScene(roomId, sceneId) {
    return delay(600).then(() => {
      const scene = MOCK.scenes.find(s => s.sceneId === sceneId)
      if (!scene) throw new Error('场景不存在')
      return { success: true, sceneId, sceneName: scene.name, sceneIcon: scene.icon }
    })
  },

  // ── 清洁任务 ──
  getCleaningTasks() {
    return delay().then(() => ({
      pending: [
        { taskId: 'CL001', roomId: 'RM003', roomName: '中茶室B', type: 'FullClean', priority: 'High', created: '2026-06-06T09:00:00', deadline: '2026-06-06T10:30:00' }
      ],
      inProgress: [
        { taskId: 'CL002', roomId: 'RM002', roomName: '中茶室A', type: 'QuickClean', priority: 'Normal', created: '2026-06-06T08:30:00', deadline: '2026-06-06T09:30:00' }
      ],
      completed: [
        { taskId: 'CL003', roomId: 'RM001', roomName: '大会议室', type: 'FullClean', priority: 'Normal', created: '2026-06-06T07:00:00', deadline: '2026-06-06T08:00:00' }
      ]
    }))
  },
  acceptCleaningTask(taskId) { return delay().then(() => ({ success: true })) },
  completeCleaningTask(taskId) { return delay().then(() => ({ success: true })) },

  // ── 巡检 ──
  getInspections() {
    return delay().then(() => [{
      planId: 'INSP001', date: '2026-06-06', type: 'Daily', status: 'InProgress',
      progress: { total: 12, completed: 3 },
      items: [
        { category: '设备间', items: [{ name: '机柜温度', status: 'normal' }, { name: '交换机指示灯', status: 'normal' }] },
        { category: '公共区域', items: [{ name: '走廊照明', status: 'normal' }, { name: '前台设备', status: 'normal' }] }
      ]
    }])
  },

  // ── 订单管理 ──
  getTodayOrders() {
    return delay().then(() => MOCK.orders.map(o => ({
      ...o,
      statusLabel: o.status === 'InUse' ? '使用中' : o.status === 'Booked' ? '已预订' : '已完成'
    })))
  },
  getActiveOrders() {
    return delay().then(() => MOCK.orders.filter(o => o.status === 'InUse' || o.status === 'Booked'))
  },

  // ── 商品管理 ──
  getProducts() { return delay().then(() => MOCK.products.slice()) },
  updateProduct(productId, data) { return delay().then(() => ({ success: true })) },

  // ── 考勤 ──
  getAttendance(date) { return delay().then(() => []) },
  clockIn() { return delay().then(() => ({ success: true, time: new Date().toISOString() })) },
  clockOut() { return delay().then(() => ({ success: true, time: new Date().toISOString() })) },

  // ── 排班 ──
  getSchedule(date) { return delay().then(() => []) },

  // ── 待办 ──
  getTodos() {
    return delay().then(() => [
      { id: 'T001', type: 'cleaning', title: '中茶室B 退房清洁', priority: 'high', deadline: '10:30' },
      { id: 'T002', type: 'inspection', title: '完成今日设备巡检', priority: 'normal', deadline: '今日' },
      { id: 'T003', type: 'order', title: '大会议室 赵总 即将到店（14:00）', priority: 'normal' }
    ])
  },

  // ── 应收 ──
  getReceivables() {
    return delay().then(() => [
      { orderId: 'ORD002', customerName: '李女士', roomName: '中茶室A', amount: 160, status: 'unpaid', dueDate: '2026-06-06' }
    ])
  },

  // ── 对账 ──
  getReconciliation(date) { return delay().then(() => ({ date, revenue: 3860, expense: 1200, net: 2660, status: 'balanced' })) }
}

module.exports = API
