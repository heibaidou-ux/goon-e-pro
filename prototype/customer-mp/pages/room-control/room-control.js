var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '房间',
    roomStatus: 'idle', roomStatusLabel: '', orderSlot: '',
    countdown: '--:--', endTime: '--:--', orderStart: '',
    balance: 0, hideBottomNav: false,
    devKeys: [], acModeLabel: '',
    acDevice: null, curtainDevices: [], bgmDevice: null,
    lightDevices: [], fanDevices: [],
    _devIdMap: {}, // 本地ID ↔ API真实deviceId映射
    showExtendModal: false, showExtendPayModal: false,
    extendInfo: '', extendOptions: [], selectedExtendIdx: -1,
    extendPayInfo: '', extendPayAmount: 0, extendPayMethod: 'balance'
  },

  onLoad: function(e) {
    var roomId = e.roomId || ''
    var roomName = e.roomName ? decodeURIComponent(e.roomName) : ''
    var duration = parseInt(e.duration) || 120
    var endStr = e.end || ''
    var startStr = e.start || ''
    var self = this
    try { if (wx.getStorageSync('mp_user_role') === 'staff') self.setData({ hideBottomNav: true }) } catch(e) {}

    self.setData({ roomId: roomId, roomName: roomName, orderStart: startStr })

    var todayStr = new Date().getFullYear()+'-'+String(new Date().getMonth()+1).padStart(2,'0')+'-'+String(new Date().getDate()).padStart(2,'0')
    API.getAllOrders().then(function(orders) {
      var curMin = new Date().getHours()*60+new Date().getMinutes()
      var list = orders || []
      var activeOrder = null
      for (var i = 0; i < list.length; i++) {
        var o = list[i]
        if (o.roomId !== roomId) continue
        if (o.status === 'InUse' && o.date === todayStr && o.time) {
          var ep = o.time.split('-')[1].split(':'); var endMin = parseInt(ep[0])*60+parseInt(ep[1])
          if (curMin < endMin) { activeOrder = o; break }
        }
        if (!activeOrder && o.status === 'Booked' && o.date === todayStr && o.time) {
          var sp = o.time.split('-')[0].split(':'); var sm = parseInt(sp[0])*60+parseInt(sp[1])
          if (curMin < sm) { activeOrder = o }
        }
      }

      if (activeOrder && activeOrder.status === 'InUse') {
        var timeStr = activeOrder.time || ''
        var slot = ''
        if (timeStr) {
          var parts = timeStr.split('-')
          if (parts.length >= 2) {
            slot = parts[0] + ' - ' + parts[1]
            self.startCountdown(duration, parts[1])
          }
        }
        self.setData({ roomStatus: 'inuse', roomStatusLabel: '使用中', orderSlot: slot })
      } else if (activeOrder && activeOrder.status === 'Booked') {
        self.setData({ roomStatus: 'booked', roomStatusLabel: '已预订', orderSlot: activeOrder.time || '' })
      } else {
        self.setData({ roomStatus: 'idle', roomStatusLabel: '当前无订单', orderSlot: '' })
      }
    })

    self.loadDevices()
    if (endStr) self.startCountdown(duration, endStr)
    API.getBalance().then(function(b) { self.setData({ balance: b || 0 }) })
  },

  // 按房间类型生成设备清单（RoomType → device list，不按房间ID硬编码）
  _getRoomDevices: function(roomType) {
    // 所有房间都有的基础设备
    var base = [
      { id:'ac', type:'AC', name:'空调' },
      { id:'L1', type:'Light', name:'吊灯' }, { id:'L2', type:'Light', name:'筒灯' }, { id:'L3', type:'Light', name:'背景灯' },
      { id:'F1', type:'Fan', name:'风扇' },
      { id:'bgm', type:'Speaker', name:'音响' },
    ]
    if (roomType === 'MeetingRoom') {
      // 会议室：3个风扇，无窗帘
      return [
        { id:'ac', type:'AC', name:'空调' },
        { id:'L1', type:'Light', name:'筒灯1' }, { id:'L2', type:'Light', name:'筒灯2' }, { id:'L3', type:'Light', name:'吊灯' },
        { id:'F1', type:'Fan', name:'风扇1' }, { id:'F2', type:'Fan', name:'风扇2' }, { id:'F3', type:'Fan', name:'风扇3' },
        { id:'bgm', type:'Speaker', name:'音响' },
      ]
    }
    // 茶室默认：3窗帘
    return base.concat([
      { id:'C1', type:'Curtain', name:'窗帘(1)' }, { id:'C2', type:'Curtain', name:'窗帘(2)' }, { id:'C3', type:'Curtain', name:'窗帘(3)' },
    ])
  },

  loadDevices: function() {
    var self = this
    var roomId = self.data.roomId
    // 先从API获取房间信息确定类型，失败则默认TeaRoom
    var roomType = 'TeaRoom'
    API.getRooms(true).then(function(list) {
      for (var i = 0; i < list.length; i++) {
        if (list[i].roomId === roomId) { roomType = list[i].type || 'TeaRoom'; break }
      }
    }).catch(function() {})

    var devices = self._getRoomDevices(roomType)
    var ac = null, curtains = [], bgm = null

    // 先用本地清单构建设备UI（物理设备一直存在，不受HA连接影响）
    var devKeys = [{ key: 'light_all_on', label: '灯全开', icon: '🔆', type: 'virtual', active: false },
                   { key: 'light_all_off', label: '灯全关', icon: '🔅', type: 'virtual', active: false }]
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i]
      if (d.type === 'AC') { ac = { deviceId: roomId+'_ac', name: d.name, mode: 'off', temperature: 24 }; continue }
      if (d.type === 'Curtain') { curtains.push({ deviceId: d.id, name: d.name, positionNum: 0 }); continue }
      if (d.type === 'Speaker') { bgm = { deviceId: d.id, playing: false, volume: 30 }; continue }
      if (d.type === 'Light') { devKeys.push({ key: d.id, label: d.name, icon: '💡', type: 'Light', active: false }) }
      if (d.type === 'Fan' || d.type === 'ExhaustFan') { devKeys.push({ key: d.id, label: d.name, icon: '⏣', type: d.type, active: false }) }
    }
    self.setData({
      devKeys: devKeys, lightDevices: [], fanDevices: [],
      acDevice: ac, acModeLabel: self._acModeLabel(ac ? ac.mode : 'off'),
      curtainDevices: curtains, bgmDevice: bgm
    })

    // 异步获取真实设备状态（更新状态，不阻塞展示）
    API.getRoomDevices(roomId).then(function(apiDevices) {
      if (!apiDevices || apiDevices.length === 0) return
      var devIdMap = {}
      // 建立本地设备ID到API真实deviceId的映射
      var apiAC = null, apiCurtains = [], apiBGM = null
      for (var i = 0; i < apiDevices.length; i++) {
        var d = apiDevices[i]; var a = d.attributes || {}
        devIdMap[d.deviceId] = d.deviceId
        if (d.type === 'AC') apiAC = d
        else if (d.type === 'Curtain') apiCurtains.push(d)
        else if (d.type === 'BGM' || d.type === 'Speaker') apiBGM = d
      }
      // 尝试按房间映射本地ID → API ID
      // 通过比较设备类型和通道号来匹配
      var apiByType = {}
      for (var i = 0; i < apiDevices.length; i++) {
        var d = apiDevices[i]; var a = d.attributes || {}
        var ch = a.channel || ''
        if (d.type === 'AC') apiByType['ac'] = d.deviceId
        else if (d.type === 'Curtain') { if (!apiByType['curtain']) apiByType['curtain'] = []; apiByType['curtain'].push(d.deviceId) }
        else if (d.type === 'BGM' || d.type === 'Speaker') apiByType['bgm'] = d.deviceId
        else if (d.type === 'Light') { var key = 'L' + (parseInt(ch) || (apiByType['light']||[]).length + 1); if (!apiByType['light']) apiByType['light'] = []; apiByType['light'].push({id:d.deviceId, ch:ch}) }
        else if (d.type === 'Fan' || d.type === 'ExhaustFan') { var fkey = d.type === 'ExhaustFan' ? 'EF' : 'F'; if (!apiByType['fan']) apiByType['fan'] = []; apiByType['fan'].push({id:d.deviceId, type:d.type}) }
      }
      // 构建devIdMap
      if (apiByType['ac']) devIdMap[roomId+'_ac'] = apiByType['ac']
      if (apiByType['bgm']) { devIdMap['bgm'] = apiByType['bgm']; devIdMap['bgm1'] = apiByType['bgm']; devIdMap['bgm2'] = apiByType['bgm'] }
      if (apiByType['curtain']) { for (var j=0; j<apiByType['curtain'].length && j<curtains.length; j++) { devIdMap[curtains[j].deviceId] = apiByType['curtain'][j]; curtains[j].deviceId = apiByType['curtain'][j] } }
      if (apiByType['light']) { for (var j=0; j<apiByType['light'].length && j<3; j++) { var lid = 'L'+(j+1); devIdMap[lid] = apiByType['light'][j].id } }
      if (apiByType['fan']) { for (var j=0; j<apiByType['fan'].length; j++) { var fid = (apiByType['fan'][j].type==='ExhaustFan'?'EF':'F')+(j+1); devIdMap[fid] = apiByType['fan'][j].id } }
      self.setData({ _devIdMap: devIdMap })

      // 更新AC状态
      if (apiAC) { var aa = apiAC.attributes || {}; ac.mode = aa.mode || 'off'; ac.temperature = aa.target_temperature || 24; ac.deviceId = apiAC.deviceId }
      // 更新窗帘状态
      for (var j = 0; j < apiCurtains.length && j < curtains.length; j++) { curtains[j].deviceId = apiCurtains[j].deviceId; curtains[j].positionNum = (apiCurtains[j].attributes||{}).current_position || 0 }
      // 更新音响状态
      if (apiBGM) { var ba = apiBGM.attributes || {}; bgm.playing = ba.playing || false; bgm.volume = ba.volume || 30; bgm.deviceId = apiBGM.deviceId }
      // 更新灯光/风扇状态
      for (var i = 0; i < apiDevices.length; i++) {
        var d = apiDevices[i], a = d.attributes || {}
        var isOn = !!(a.power || a.brightness > 0 || (a.speed || 0) > 0)
        for (var j = 0; j < devKeys.length; j++) {
          if (devKeys[j].key === d.deviceId) { devKeys[j].active = isOn; break }
        }
      }
      self.setData({ devKeys: devKeys, acDevice: ac, curtainDevices: curtains, bgmDevice: bgm })
    }).catch(function() {})
  },

  // 解析设备ID：本地ID → API真实deviceId
  _resolveId: function(localId) {
    return this.data._devIdMap[localId] || localId
  },

  onKeyTap: function(e) {
    var key = e.currentTarget.dataset.key
    var type = e.currentTarget.dataset.type
    if (key === 'light_all_on') { this._setAllLights(true); return }
    if (key === 'light_all_off') { this._setAllLights(false); return }
    var currentOn = false
    var keys = this.data.devKeys
    for (var i = 0; i < keys.length; i++) { if (keys[i].key === key) { currentOn = keys[i].active; break } }
    this._toggleDevice(key, type, !currentOn)
  },

  _setAllLights: function(on) {
    var self = this
    // 从devKeys中找出所有灯光按键
    var keys = self.data.devKeys
    var lightKeys = []
    for (var i = 0; i < keys.length; i++) {
      if (keys[i].type === 'Light') { lightKeys.push(keys[i].key); keys[i].active = on }
      else if (keys[i].key === 'light_all_on') keys[i].active = on
      else if (keys[i].key === 'light_all_off') keys[i].active = false
    }
    self.setData({ devKeys: keys })
    if (lightKeys.length === 0) return
    wx.showLoading({ title: on ? '全开中...' : '全关中...' })
    var done = 0
    for (var i = 0; i < lightKeys.length; i++) {
      API.controlDevice(self._resolveId(lightKeys[i]), { brightness: on ? 80 : 0 }).then(function() {
        done++; if (done >= lightKeys.length) { wx.hideLoading() }
      }).catch(function(err) {
        done++; if (done >= lightKeys.length) { wx.hideLoading() }
        if (err && err.message) wx.showToast({ title: '灯控失败: ' + err.message, icon: 'none' })
      })
    }
  },

  _toggleDevice: function(deviceId, type, newState) {
    var self = this
    var realId = self._resolveId(deviceId)
    var keys = self.data.devKeys
    for (var i = 0; i < keys.length; i++) { if (keys[i].key === deviceId) { keys[i].active = newState; break } }
    self.setData({ devKeys: keys })
    var cmd = {}
    if (type === 'Light') cmd = { brightness: newState ? 80 : 0 }
    else if (type === 'Fan' || type === 'ExhaustFan') cmd = { speed: newState ? 3 : 0 }
    API.controlDevice(realId, cmd).catch(function(err) {
      // 失败则回滚状态
      for (var i = 0; i < keys.length; i++) { if (keys[i].key === deviceId) { keys[i].active = !newState; break } }
      self.setData({ devKeys: keys })
      wx.showToast({ title: '控制失败: ' + ((err && err.message) || '设备无响应'), icon: 'none' })
    })
  },

  toggleAC: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), ac = self.data.acDevice
    if (!ac) return
    ac.mode = ac.mode === 'off' ? 'cool' : 'off'
    self.setData({ acDevice: ac, acModeLabel: self._acModeLabel(ac.mode) })
    API.controlDevice(id, { mode: ac.mode }).catch(function(err){
      wx.showToast({ title: '空调控制失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },
  setACMode: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), mode = e.currentTarget.dataset.mode, ac = self.data.acDevice
    if (!ac) return; ac.mode = mode
    this.setData({ acDevice: ac, acModeLabel: this._acModeLabel(mode) })
    API.controlDevice(id, { mode: mode }).catch(function(err){
      wx.showToast({ title: '空调控制失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },
  acTempUp: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), ac = self.data.acDevice
    if (!ac) return; ac.temperature = Math.min(30, (ac.temperature || 24) + 1)
    self.setData({ acDevice: ac }); API.controlDevice(id, { temperature: ac.temperature }).catch(function(err){
      wx.showToast({ title: '调温失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },
  acTempDown: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), ac = self.data.acDevice
    if (!ac) return; ac.temperature = Math.max(16, (ac.temperature || 24) - 1)
    self.setData({ acDevice: ac }); API.controlDevice(id, { temperature: ac.temperature }).catch(function(err){
      wx.showToast({ title: '调温失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },
  _acModeLabel: function(mode) {
    if (mode === 'cool') return '制冷中'
    if (mode === 'heat') return '制热中'
    if (mode === 'fan') return '送风中'
    return '已关机'
  },

  onCurtainChange: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), val = parseInt(e.detail.value)
    var position = val >= 80 ? 'open' : (val <= 20 ? 'closed' : val + '%')
    var devs = self.data.curtainDevices
    for (var i = 0; i < devs.length; i++) { if (devs[i].deviceId === id || devs[i].deviceId === e.currentTarget.dataset.id) { devs[i].positionNum = val; devs[i].position = position; break } }
    self.setData({ curtainDevices: devs }); API.controlDevice(id, { position: position }).catch(function(err){
      wx.showToast({ title: '窗帘控制失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },

  toggleBGM: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), bgm = self.data.bgmDevice
    if (!bgm) return; bgm.playing = !bgm.playing
    self.setData({ bgmDevice: bgm }); API.controlDevice(id, { playing: bgm.playing }).catch(function(err){
      wx.showToast({ title: '音响控制失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },
  onBGMVolumeChange: function(e) {
    var self = this
    var id = self._resolveId(e.currentTarget.dataset.id), val = parseInt(e.detail.value), bgm = self.data.bgmDevice
    if (!bgm) return; bgm.volume = val; self.setData({ bgmDevice: bgm })
    API.controlDevice(id, { volume: val }).catch(function(err){
      wx.showToast({ title: '音量调节失败: ' + ((err&&err.message)||'无响应'), icon: 'none' })
    })
  },

  startCountdown: function(durationMin, endStr) {
    var self = this; durationMin = durationMin || 120; var now = new Date()
    if (endStr) {
      var ep = endStr.split(':')
      if (ep.length >= 2) {
        var eh = parseInt(ep[0]), em = parseInt(ep[1])
        var endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), eh, em)
        if (endDate <= now) endDate.setDate(endDate.getDate() + 1)
        var totalSec = Math.max(0, Math.round((endDate - now) / 1000))
        self.setData({ endTime: endStr }); self._countdownTotal = totalSec; self._endDate = endDate
        if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
        self.setData({ countdown: self._fmtCountdown(totalSec) }); self._startTimer(); self._updateSlot(); return
      }
    }
    var endH = (now.getHours() + Math.floor((now.getMinutes() + durationMin) / 60)) % 24
    var endM = (now.getMinutes() + durationMin) % 60
    self._endDate = new Date(now.getFullYear(), now.getMonth(), now.getDate(), endH, endM)
    self.setData({ endTime: String(endH).padStart(2,'0') + ':' + String(endM).padStart(2,'0') })
    var totalSec = durationMin * 60; self._countdownTotal = totalSec
    if (totalSec <= 0) { self.setData({ countdown: '00:00' }); return }
    self.setData({ countdown: self._fmtCountdown(totalSec) }); self._startTimer(); self._updateSlot()
  },
  _updateSlot: function() {
    var s = this.data.orderStart, e = this.data.endTime
    if (e) this.setData({ orderSlot: (s || '--:--') + ' - ' + e })
  },
  _startTimer: function() {
    var self = this; if (self._countdownTimer) clearInterval(self._countdownTimer)
    setTimeout(function() {
      self._countdownTimer = setInterval(function() {
        self._countdownTotal = Math.max(0, self._countdownTotal - 1)
        self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      }, 1000)
    }, 300)
  },
  _fmtCountdown: function(s) { if (s <= 0) return '00:00'; var m = Math.floor(s / 60), sec = s % 60; return String(m).padStart(2,'0') + ':' + String(sec).padStart(2,'0') },
  onUnload: function() { if (this._countdownTimer) clearInterval(this._countdownTimer) },
  preventBubble: function() {},
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },

  showExtend: function() {
    var self = this
    var endDate = self._endDate ? new Date(self._endDate) : new Date()
    self.setData({ extendInfo: '当前将于 ' + String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0') + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })
    var options = []
    for (var i = 1; i <= 24; i++) {
      var nd = new Date(endDate.getTime() + i * 30 * 60000)
      options.push({ label: '至 ' + String(nd.getHours()).padStart(2,'0') + ':' + String(nd.getMinutes()).padStart(2,'0'), minutes: i * 30, price: Math.round(120 * i * 30 / 60) })
    }
    self.setData({ extendOptions: options, showExtendModal: true })
  },
  selectExtend: function(e) { this.setData({ selectedExtendIdx: parseInt(e.currentTarget.dataset.index) }) },
  confirmExtend: function() {
    var idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx], self = this
    API.getBalance().then(function(b) { self.setData({ balance: b || 0, extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''), extendPayAmount: opt.price, extendPayMethod: 'balance', showExtendModal: false, showExtendPayModal: true }) })
  },
  selectExtendPay: function(e) { this.setData({ extendPayMethod: e.currentTarget.dataset.pay }) },
  doExtendPayment: function() {
    var self = this, idx = this.data.selectedExtendIdx
    if (idx < 0 || idx >= this.data.extendOptions.length) return
    var opt = this.data.extendOptions[idx], method = this.data.extendPayMethod
    var p = function() {
      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60
      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })
      if (self._endDate) { self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000); self.setData({ endTime: String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0') }) }
      try { var bk = wx.getStorageSync('mp_bookings') || []; for (var i = 0; i < bk.length; i++) { if (bk[i].roomId === self.data.roomId && bk[i].status === 'InUse') { bk[i].endTime = String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0'); break } }; wx.setStorageSync('mp_bookings', bk) } catch(e) {}
      self._updateSlot(); self.setData({ showExtendPayModal: false }); wx.showToast({ title: '续订成功！已支付 ¥' + opt.price, icon: 'success' })
    }
    if (method === 'balance') {
      API.getBalance().then(function(bal) { if (bal < opt.price) { wx.showToast({ title: '余额不足，请选择其他方式', icon: 'none' }); return }; var u = wx.getStorageSync('mp_user') || {}; u.balance = bal - opt.price; wx.setStorageSync('mp_user', u); self.setData({ balance: u.balance }); p() })
    } else { wx.showLoading({ title: '支付中...' }); setTimeout(function() { wx.hideLoading(); p() }, 800) }
  },
  hideExtend: function() { this.setData({ showExtendModal: false }) },
  cancelExtendPay: function() { this.setData({ showExtendPayModal: false }); wx.showToast({ title: '已取消续订', icon: 'none' }) }
})
