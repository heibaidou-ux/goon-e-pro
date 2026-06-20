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
      { id:'TD001', title:'保洁 — 白沙瓦', type:'cleaning', priority:'high', deadline:'10:30', status:'pending' },
      { id:'TD002', title:'巡检 — 翡冷翠智能设备', type:'inspection', priority:'normal', deadline:'11:00', status:'pending' },
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

  // ── 考勤（从localStorage读写真实状态）──
  getAttendance() {
    return delay().then(() => {
      var now = new Date(), h = now.getHours(), m = now.getMinutes()
      var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
      var curTime = String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')

      // 从localStorage读今日签到记录
      var today = lsGet('attendance_'+todayStr, {})
      var checkInTime = today.checkInTime || ''
      var checkOutTime = today.checkOutTime || ''
      var checkedIn = !!checkInTime
      var checkedOut = !!checkOutTime

      // 读历史记录
      var allHistory = []
      try { allHistory = JSON.parse(wx.getStorageSync('mp_attendance_history') || '[]') } catch(e) {}
      // 如果今日有记录但不在历史里，补进去
      if (checkedIn) {
        var found = false
        for (var i = 0; i < allHistory.length; i++) {
          if (allHistory[i].date === todayStr) { found = true; break }
        }
        if (!found) {
          allHistory.unshift({
            date: todayStr,
            checkIn: checkInTime,
            checkOut: checkOutTime || '',
            status: checkedOut ? (h < 9 ? '正常' : '迟到') : '在岗'
          })
          try { wx.setStorageSync('mp_attendance_history', JSON.stringify(allHistory)) } catch(e) {}
        }
      }

      // 没有历史mock记录时注入默认数据
      if (allHistory.length === 0) {
        allHistory = [
    { date:'2026-06-19', checkIn:'08:15', checkOut:'', status:'在岗' },
    { date:'2026-06-18', checkIn:'08:05', checkOut:'17:39', status:'正常' },
    { date:'2026-06-17', checkIn:'09:03', checkOut:'18:04', status:'迟到' },
    { date:'2026-06-16', checkIn:'08:07', checkOut:'17:50', status:'正常' },
    { date:'2026-06-15', checkIn:'09:04', checkOut:'18:11', status:'迟到' },
    { date:'2026-06-12', checkIn:'08:22', checkOut:'17:55', status:'正常' },
    { date:'2026-06-11', checkIn:'09:13', checkOut:'18:13', status:'迟到' },
    { date:'2026-06-10', checkIn:'08:21', checkOut:'18:18', status:'正常' },
    { date:'2026-06-09', checkIn:'08:16', checkOut:'17:37', status:'正常' },
    { date:'2026-06-08', checkIn:'08:24', checkOut:'17:40', status:'正常' },
    { date:'2026-06-05', checkIn:'08:19', checkOut:'17:52', status:'正常' },
    { date:'2026-06-04', checkIn:'08:19', checkOut:'18:17', status:'正常' },
    { date:'2026-06-03', checkIn:'08:11', checkOut:'17:47', status:'正常' },
    { date:'2026-06-02', checkIn:'09:12', checkOut:'17:49', status:'迟到' },
    { date:'2026-06-01', checkIn:'09:03', checkOut:'17:30', status:'迟到' },
    { date:'2026-05-29', checkIn:'09:07', checkOut:'17:42', status:'迟到' },
    { date:'2026-05-28', checkIn:'08:12', checkOut:'17:40', status:'正常' },
    { date:'2026-05-27', checkIn:'08:12', checkOut:'18:00', status:'正常' },
    { date:'2026-05-26', checkIn:'08:07', checkOut:'17:41', status:'正常' },
    { date:'2026-05-25', checkIn:'09:06', checkOut:'17:34', status:'迟到' },
    { date:'2026-05-22', checkIn:'08:08', checkOut:'18:10', status:'正常' },
    { date:'2026-05-21', checkIn:'09:06', checkOut:'18:02', status:'迟到' },
    { date:'2026-05-20', checkIn:'08:14', checkOut:'17:51', status:'正常' },
    { date:'2026-05-19', checkIn:'08:20', checkOut:'18:02', status:'正常' },
    { date:'2026-05-18', checkIn:'08:20', checkOut:'18:16', status:'正常' },
    { date:'2026-05-15', checkIn:'08:18', checkOut:'18:06', status:'正常' },
    { date:'2026-05-14', checkIn:'08:22', checkOut:'17:44', status:'正常' },
    { date:'2026-05-13', checkIn:'08:16', checkOut:'17:50', status:'正常' },
    { date:'2026-05-12', checkIn:'08:20', checkOut:'18:01', status:'正常' },
    { date:'2026-05-11', checkIn:'09:08', checkOut:'18:03', status:'迟到' },
    { date:'2026-05-08', checkIn:'08:22', checkOut:'18:15', status:'正常' },
    { date:'2026-05-07', checkIn:'08:17', checkOut:'18:11', status:'正常' },
    { date:'2026-05-06', checkIn:'08:08', checkOut:'17:30', status:'正常' }
        ]
      }

      return {
        checkedIn: checkedIn,
        checkInTime: checkInTime || '—',
        checkOutTime: checkOutTime || '',
        todayStatus: checkedOut ? '已签退' : (checkedIn ? '在岗' : '未打卡'),
        workHours: checkedIn ? Math.round(((checkedOut ? (parseInt(checkOutTime.split(':')[0])*60+parseInt(checkOutTime.split(':')[1])) : (h*60+m)) - (parseInt(checkInTime.split(':')[0])*60+parseInt(checkInTime.split(':')[1]))) / 60 * 10) / 10 : 0,
        records: allHistory
      }
    })
  },
  checkIn() {
    return delay(300).then(() => {
      var n=new Date(); var time=String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')
      var todayStr = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')
      lsSet('attendance_'+todayStr, { checkInTime: time, checkOutTime: '' })
      return { success:true, time:time, status:'在岗' }
    })
  },
  checkOut() {
    return delay(300).then(() => {
      var n=new Date(); var time=String(n.getHours()).padStart(2,'0')+':'+String(n.getMinutes()).padStart(2,'0')
      var todayStr = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')
      var today = lsGet('attendance_'+todayStr, {})
      today.checkOutTime = time
      lsSet('attendance_'+todayStr, today)
      return { success:true, time:time, status:'已下班' }
    })
  },

  // ── 巡检 ──
  getInspectionRooms: function() {
    return delay().then(function() {
      var filtered = []
      for (var i = 0; i < MOCK.rooms.length; i++) {
        if (MOCK.rooms[i].roomId !== 'RM006') filtered.push(MOCK.rooms[i])
      }
      return filtered.map(function(r) {
        return {
          roomId: r.roomId, name: r.name, status: r.status || 'Active',
          lastInspection: '2026-06-10',
          items: [
            { name:'门锁', ok:true }, { name:'空调', ok:true },
            { name:'灯光', ok:true }, { name:'窗帘', ok:true },
            { name:'音响', ok:true }, { name:'卫生', ok:true }
          ]
        }
      })
    })
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
    var self = this
    return delay().then(function() {
      var now = new Date()
      var todayStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
      var curMin = now.getHours()*60+now.getMinutes()
      var needClean = []
      try {
        var bookings = wx.getStorageSync('mp_bookings') || []
        for (var i = 0; i < bookings.length; i++) {
          var b = bookings[i]
          if (b.date === todayStr && b.time && b.roomId) {
            var ep = b.time.split('-')[1].split(':'); var endMin = parseInt(ep[0])*60+parseInt(ep[1])
            if (curMin >= endMin && (b.status === 'InUse' || b.status === 'Expired' || b.status === 'Completed')) {
              var rmName = b.roomName || '房间'
              var dup = false
              for (var j = 0; j < needClean.length; j++) { if (needClean[j].roomId === b.roomId) { dup = true; break } }
              if (!dup) needClean.push({taskId:'CT'+b.roomId,roomName:rmName,roomId:b.roomId,type:'FullClean',priority:'Normal',deadline:'尽快'})
            }
          }
        }
      } catch(e) {}
      if (needClean.length === 0) {
        needClean = [{taskId:'CT001',roomName:'白沙瓦',roomId:'RM004',type:'FullClean',priority:'High',deadline:'尽快'}]
      }
      return { pending: needClean.slice(0,3), inProgress: [] }
    })
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
  getDeviceList(roomId) {
    if (!USE_MOCK) return request({ url: '/api/iot/devices' + (roomId ? '?room_id=' + roomId : '') })
    return delay().then(function() {
      var list = MOCK.devices
      if (roomId) list = list.filter(function(d) { return d.roomId === roomId })
      var typeLabelMap = {Lock:'门锁',AC:'空调',Light:'灯光',Curtain:'窗帘',Speaker:'音响'}
      var typeIconMap = {Lock:'🔒',AC:'❄️',Light:'💡',Curtain:'🪟',Speaker:'🔊'}
      return list.map(function(d) {
        return { roomId: d.roomId, deviceId: d.deviceId, type: d.type, status: d.status,
          typeLabel: typeLabelMap[d.type] || d.type, typeIcon: typeIconMap[d.type] || '📡' }
      })
    })
  },

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
