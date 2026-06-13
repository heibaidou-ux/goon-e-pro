/**
 * 高岸ERP 店员端 API
 * 提供店员端仪表盘、待办等 Mock 数据
 */
const MOCK = require('./mock-data')

function delay(ms) {
  ms = ms || (150 + Math.random() * 200)
  return new Promise(resolve => setTimeout(resolve, ms))
}

const STAFF_API = {
  // 店员端仪表盘统计
  getDashboardStats() {
    return delay().then(() => {
      // 从 mock 数据计算今日营收
      var today = new Date()
      var dateStr = today.getFullYear() + '-' + String(today.getMonth()+1).padStart(2,'0') + '-' + String(today.getDate()).padStart(2,'0')
      var todayOrders = MOCK.orders.filter(function(o) {
        return o.start && o.start.indexOf(dateStr) === 0
      })
      var revenue = 0
      for (var i = 0; i < todayOrders.length; i++) { revenue += todayOrders[i].amount || 0 }

      var inUseRooms = MOCK.rooms.filter(function(r) { return r.status === 'Active' }).length
      var pendingOrders = MOCK.orders.filter(function(o) { return o.status === 'Booked' || o.status === 'InUse' }).length

      return {
        roomCount: { inUse: inUseRooms },
        todayRevenue: revenue,
        todayOrders: todayOrders.length,
        pendingTasks: pendingOrders,
        orderStatus: pendingOrders,
        alerts: Math.max(0, 3 - inUseRooms)  // 离线设备较多的房间作为告警
      }
    })
  },

  // 待办事项列表
  getTodos() {
    return delay().then(function() {
      return [
        { id: 'TD001', title: '保洁 — 大茶室C', type: 'cleaning', priority: 'high', deadline: '10:30', status: 'pending' },
        { id: 'TD002', title: '巡检 — 中茶室A智能设备', type: 'inspection', priority: 'normal', deadline: '11:00', status: 'pending' },
        { id: 'TD003', title: '确认 — 下午会议接待', type: 'order', priority: 'high', deadline: '12:00', status: 'pending' },
        { id: 'TD004', title: '补货 — 茶品展示柜', type: 'restock', priority: 'normal', deadline: '14:00', status: 'pending' },
        { id: 'TD005', title: '对账 — 昨日营收', type: 'finance', priority: 'normal', deadline: '18:00', status: 'pending' }
      ]
    })
  },

  // ── 对账 ──
  getReconciliationData(dateStr) {
    return delay().then(function() {
      if (!dateStr) {
        var d = new Date()
        dateStr = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0')
      }
      var dayOrders = MOCK.orders.filter(function(o) { return o.start && o.start.indexOf(dateStr) === 0 })
      var totalRevenue = 0, roomRev = 0, productRev = 0
      var payBreakdown = {}
      for (var i = 0; i < dayOrders.length; i++) {
        var o = dayOrders[i]
        totalRevenue += o.amount || 0
        roomRev += o.amount || 0
        var pm = o.paymentMethod || 'Other'
        payBreakdown[pm] = (payBreakdown[pm] || 0) + (o.amount || 0)
      }
      return {
        date: dateStr,
        totalRevenue: totalRevenue,
        roomRevenue: roomRev,
        productRevenue: productRev,
        orderCount: dayOrders.length,
        paymentBreakdown: payBreakdown,
        // 模拟数据补充
        couponDiscount: 30,
        pendingPayment: 156
      }
    })
  },

  // ── 考勤 ──
  getAttendance() {
    return delay().then(function() {
      var now = new Date()
      var h = now.getHours(), m = now.getMinutes()
      var timeStr = String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0')
      return {
        checkedIn: h >= 8 && h < 9,
        checkInTime: h >= 8 && h < 9 ? '08:' + String(m).padStart(2,'0') : '—',
        checkOutTime: '',
        todayStatus: h < 9 ? '未打卡' : (h < 18 ? '在岗' : '已下班'),
        workHours: Math.min(h - 8, 8),
        records: [
          { date: '2026-06-11', checkIn: '08:32', checkOut: '—', status: '在岗' },
          { date: '2026-06-10', checkIn: '08:25', checkOut: '18:10', status: '正常' },
          { date: '2026-06-09', checkIn: '08:40', checkOut: '17:55', status: '正常' },
          { date: '2026-06-08', checkIn: '08:15', checkOut: '18:20', status: '正常' },
          { date: '2026-06-07', checkIn: '—', checkOut: '—', status: '休息' }
        ]
      }
    })
  },

  checkIn() {
    return delay(300).then(function() {
      var now = new Date()
      var h = String(now.getHours()).padStart(2,'0'), m = String(now.getMinutes()).padStart(2,'0')
      return { success: true, time: h + ':' + m, status: '在岗' }
    })
  },

  checkOut() {
    return delay(300).then(function() {
      var now = new Date()
      var h = String(now.getHours()).padStart(2,'0'), m = String(now.getMinutes()).padStart(2,'0')
      return { success: true, time: h + ':' + m, status: '已下班' }
    })
  },

  // ── 巡检 ──
  getInspectionRooms() {
    return delay().then(function() {
      return MOCK.rooms.filter(function(r) { return r.bookable !== false }).map(function(r) {
        return {
          roomId: r.roomId,
          name: r.name,
          status: r.status || 'Active',
          lastInspection: '2026-06-10',
          items: [
            { name: '门锁', ok: true },
            { name: '空调', ok: true },
            { name: '灯光', ok: r.roomId !== 'RM003' },
            { name: '窗帘', ok: true },
            { name: '音响', ok: r.roomId !== 'RM002' },
            { name: '卫生', ok: true }
          ]
        }
      })
    })
  },

  submitInspection(roomId, results) {
    return delay(300).then(function() {
      return { success: true, message: '巡检记录已保存' }
    })
  },

  // ── 保洁任务 ──
  getCleaningTasks() {
    return delay().then(function() {
      return {
        pending: [
          { taskId:'CT001', roomName:'大茶室C', type:'FullClean', priority:'High', deadline:'10:30' },
          { taskId:'CT002', roomName:'中茶室A', type:'QuickClean', priority:'Normal', deadline:'11:00' }
        ],
        inProgress: [
          { taskId:'CT003', roomName:'大会议室', type:'FullClean', priority:'Normal', deadline:'10:00' }
        ]
      }
    })
  },

  acceptCleaningTask(taskId) {
    return delay(200).then(function() { return { success: true } })
  },

  completeCleaningTask(taskId) {
    return delay(200).then(function() { return { success: true } })
  },

  getRoomStatusList() {
    return delay().then(function() {
      return MOCK.rooms.map(function(r) {
        return {
          roomId: r.roomId, name: r.name, type: r.type, capacity: r.capacity,
          statusColor: r.status === 'Active' ? '#00A870' : '#999',
          statusLabel: r.status === 'Active' ? '在线' : '离线',
          currentOrder: null
        }
      })
    })
  },

  // ── 排班 ──
  getSchedule(weekOffset) {
    return delay().then(function() {
      return {
        weekStart: '2026-06-08',
        weekEnd: '2026-06-14',
        staff: [
          { name: '店员小张', role: '店员', schedule: ['早班', '早班', '晚班', '晚班', '早班', '休息', '休息'] },
          { name: '保洁员', role: '保洁', schedule: ['早班', '早班', '早班', '休息', '早班', '早班', '休息'] },
          { name: '管理员', role: '店长', schedule: ['全天', '全天', '全天', '全天', '全天', '休息', '休息'] },
          { name: '兼职A', role: '兼职', schedule: ['休息', '休息', '晚班', '晚班', '休息', '晚班', '晚班'] }
        ]
      }
    })
  }
}

module.exports = STAFF_API
