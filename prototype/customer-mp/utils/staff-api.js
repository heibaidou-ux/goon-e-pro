/**
 * 高岸ERP 店员端 API — 真工具版
 * 支持 Mock(本地) / Live(后端) 双模式
 * USE_MOCK = false 时直连后端 FastAPI
 */
const MOCK = require('./mock-data')

const API_BASE = 'http://localhost:8000'
const USE_MOCK = true  // false = 连后端

function lsGet(key, fallback) {
  try { const val = wx.getStorageSync('mp_' + key); return val || fallback } catch (e) { return fallback }
}
function lsSet(key, val) { try { wx.setStorageSync('mp_' + key, val) } catch (e) { } }

function getToken() { return lsGet('token', null) }

function delay(ms) { ms = ms || (150 + Math.random() * 200); return new Promise(resolve => setTimeout(resolve, ms)) }

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
        if (res.statusCode === 401) { wx.reLaunch({ url: '/pages/staff/staff-login/staff-login' }); return }
        if (res.statusCode >= 400) { reject(new Error((res.data && res.data.detail) || '请求失败')); return }
        resolve(res.data)
      },
      fail: err => reject(new Error('网络请求失败'))
    })
  })
}

const STAFF_API = {
  getDashboardStats() {
    if (!USE_MOCK) return request({ url: '/api/operations/dashboard' }).catch(() => this._mockDashboard())
    return this._mockDashboard()
  },

  _mockDashboard() {
    return delay().then(() => {
      var today = new Date()
      var dateStr = today.getFullYear()+'-'+String(today.getMonth()+1).padStart(2,'0')+'-'+String(today.getDate()).padStart(2,'0')
      var todayOrders = MOCK.orders.filter(o => o.start && o.start.indexOf(dateStr) === 0)
      var revenue = 0; for (var i = 0; i < todayOrders.length; i++) revenue += todayOrders[i].amount || 0
      var inUseRooms = MOCK.rooms.filter(r => r.status === 'Active').length
      var pendingOrders = MOCK.orders.filter(o => o.status === 'Booked' || o.status === 'InUse').length
      return { roomCount: { inUse: inUseRooms }, todayRevenue: revenue, todayOrders: todayOrders.length, pendingTasks: pendingOrders, orderStatus: pendingOrders, alerts: Math.max(0, 3 - inUseRooms) }
    })
  },

  getTodos() {
    return delay().then(() => [
      { id:'TD001', title:'保洁 — 大茶室C', type:'cleaning', priority:'high', deadline:'10:30', status:'pending' },
      { id:'TD002', title:'巡检 — 中茶室A智能设备', type:'inspection', priority:'normal', deadline:'11:00', status:'pending' },
      { id:'TD003', title:'确认 — 下午会议接待', type:'order', priority:'high', deadline:'12:00', status:'pending' },
      { id:'TD004', title:'补货 — 茶品展示柜', type:'restock', priority:'normal', deadline:'14:00', status:'pending' },
      { id:'TD005', title:'对账 — 昨日营收', type:'finance', priority:'normal', deadline:'18:00', status:'pending' }
    ])
  },

  // ── 对账 ──
  getReconciliationData(dateStr) {
    return delay().then(() => {
      if (!dateStr) { var d = new Date(); dateStr = d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0') }
      var dayOrders = MOCK.orders.filter(o => o.start && o.start.indexOf(dateStr) === 0)
      var totalRevenue = 0, roomRev = 0, productRev = 0, payBreakdown = {}
      for (var i = 0; i < dayOrders.length; i++) { var o = dayOrders[i]; totalRevenue += o.amount||0; roomRev += o.amount||0; var pm = o.paymentMethod||'Other'; payBreakdown[pm] = (payBreakdown[pm]||0) + (o.amount||0) }
      return { date: dateStr, totalRevenue: totalRevenue, roomRevenue: roomRev, productRevenue: productRev, orderCount: dayOrders.length, paymentBreakdown: payBreakdown, couponDiscount: 30, pendingPayment: 156, anomalies: totalRevenue > 500 ? [{ type:'大额订单', desc:'RM004 金额¥'+totalRevenue, time:'14:30' }] : [] }
    })
  },

  resolveAnomaly(anomalyId) { return delay(200).then(() => ({ success: true })) },

  // ── 考勤 ──
  getAttendance() {
    return delay().then(() => {
      var now = new Date(), h = now.getHours(), m = now.getMinutes()
      return {
        checkedIn: h >= 8, checkInTime: h >= 8 ? '08:'+String(m).padStart(2,'0') : '—', checkOutTime: h >= 18 ? '18:'+String(m).padStart(2,'0') : '',
        todayStatus: h < 8 ? '未打卡' : (h < 18 ? '在岗' : '已下班'), workHours: Math.min(h - 8, 8),
        records: [
          { date:'2026-06-13', checkIn:'08:32', checkOut:'18:10', status:'正常' },
          { date:'2026-06-12', checkIn:'08:25', checkOut:'17:55', status:'正常' },
          { date:'2026-06-11', checkIn:'08:40', checkOut:'18:20', status:'正常' },
          { date:'2026-06-10', checkIn:'08:15', checkOut:'18:30', status:'正常' },
          { date:'2026-06-09', checkIn:'08:50', checkOut:'17:40', status:'迟到' }
        ]
      }
    })
  },
  checkIn() { return delay(300).then(() => { var n=new Date(); return { success:true, time:String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0'), status:'在岗' } }) },
  checkOut() { return delay(300).then(() => { var n=new Date(); return { success:true, time:String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0'), status:'已下班' } }) },

  // ── 巡检 ──
  getInspectionRooms() {
    return delay().then(() => MOCK.rooms.filter(r => r.bookable !== false).map(r => ({
      roomId: r.roomId, name: r.name, status: r.status||'Active', lastInspection: '2026-06-10',
      items: [{ name:'门锁',ok:true },{ name:'空调',ok:true },{ name:'灯光',ok:r.roomId!=='RM003' },{ name:'窗帘',ok:true },{ name:'音响',ok:r.roomId!=='RM002' },{ name:'卫生',ok:true }]
    })))
  },
  submitInspection(roomId, results) {
    return delay(300).then(() => {
      var reports = []; try { reports = wx.getStorageSync('mp_inspection_reports') || [] } catch(e) {}
      reports.unshift({ id:'IR'+String(Date.now()).slice(-6), roomId: roomId, items: results, inspector: '店员小张', time: new Date().toLocaleString(), status: '待复核' })
      try { wx.setStorageSync('mp_inspection_reports', reports) } catch(e) {}
      return { success: true, message: '巡检记录已保存，等待店长复核' }
    })
  },
  getInspectionReports() {
    return delay().then(() => { try { return wx.getStorageSync('mp_inspection_reports') || [] } catch(e) { return [] } })
  },
  confirmInspectionReport(reportId) {
    return delay(200).then(() => {
      try { var reports = wx.getStorageSync('mp_inspection_reports') || []; for (var i=0;i<reports.length;i++) { if (reports[i].id===reportId) { reports[i].status='已复核'; break } }; wx.setStorageSync('mp_inspection_reports', reports) } catch(e) {}
      return { success: true }
    })
  },

  // ── 排班 ──
  getSchedule(weekOffset) {
    return delay().then(() => ({
      weekStart: '2026-06-08', weekEnd: '2026-06-14',
      staff: [
        { name:'店员小张', role:'店员', schedule:['早班','早班','晚班','晚班','早班','休息','休息'] },
        { name:'保洁员', role:'保洁', schedule:['早班','早班','早班','休息','早班','早班','休息'] },
        { name:'管理员', role:'店长', schedule:['全天','全天','全天','全天','全天','休息','休息'] },
        { name:'兼职A', role:'兼职', schedule:['休息','休息','晚班','晚班','休息','晚班','晚班'] }
      ]
    }))
  },
  saveSchedule(staffName, dayIndex, shift) { return delay(200).then(() => ({ success: true })) },

  // ── 保洁 ──
  getCleaningTasks() {
    if (!USE_MOCK) return request({ url: '/api/operations/cleaning-tasks/today' }).catch(() => this._mockCleaning())
    return this._mockCleaning()
  },
  _mockCleaning() {
    return delay().then(() => ({
      pending: [{taskId:'CT001',roomName:'大茶室C',roomId:'RM004',type:'FullClean',priority:'High',deadline:'10:30'},{taskId:'CT002',roomName:'中茶室A',roomId:'RM002',type:'QuickClean',priority:'Normal',deadline:'11:00'}],
      inProgress: [{taskId:'CT003',roomName:'大会议室',roomId:'RM001',type:'FullClean',priority:'Normal',deadline:'10:00'}]
    }))
  },
  acceptCleaningTask(taskId) { return delay(200).then(() => ({ success:true })) },
  completeCleaningTask(taskId) { return delay(200).then(() => ({ success:true })) },

  // ── 房态 ──
  getRoomStatusList() {
    if (!USE_MOCK) return request({ url: '/api/iot/devices' })  // Will adapt later
    return delay().then(() => MOCK.rooms.map(r => ({
      roomId: r.roomId, name: r.name, type: r.type, capacity: r.capacity,
      statusColor: r.status==='Active'?'#00A870':'#999', statusLabel: r.status==='Active'?'在线':'离线', currentOrder: null
    })))
  },

  // ── IoT ──
  getDeviceStats() {
    if (!USE_MOCK) return request({ url: '/api/iot/stats' })
    return delay().then(() => {
      var total = MOCK.devices.length
      var online = MOCK.devices.filter(d => d.status === 'Online').length
      return { total, online, offline: total - online, rate: Math.round(online/total*100)+'%' }
    })
  },

  getInspections() {
    return delay().then(() => [])
  },
}

module.exports = STAFF_API
