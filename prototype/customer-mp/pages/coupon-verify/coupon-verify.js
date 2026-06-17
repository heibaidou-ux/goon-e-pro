var API = require('../../utils/api')

var COUPON_DB = {
  'MT20260601': { source:'美团', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'DY20260601': { source:'抖音', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'DP20260601': { source:'大众点评', title:'中茶室休闲体验', matchRooms:['RM002','RM003'], price:88, duration:120 },
  'GD20260601': { source:'高德', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'SY20260602': { source:'系统赠送', title:'首充赠送代金券', matchRooms:['RM001','RM002','RM003','RM004'], price:50, duration:120 },
  'MT001298': { source:'美团', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'MT002456': { source:'美团', title:'茶室单人品茗券', matchRooms:['RM002','RM003'], price:68, duration:60 },
  'MT003789': { source:'美团', title:'商务会议3小时套餐', matchRooms:['RM001'], price:358, duration:180 },
  'DY003456': { source:'抖音', title:'商务会议3小时套餐', matchRooms:['RM001'], price:358, duration:180 },
  'DY007891': { source:'抖音', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'DP007891': { source:'大众点评', title:'中茶室休闲体验', matchRooms:['RM002','RM003'], price:88, duration:120 },
  'GD009876': { source:'高德', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
}

var ROOM_DATA = {
  RM004: { name:'白沙瓦', capacity:6, icon:'🍵' },
  RM001: { name:'丰沙里', capacity:10, icon:'💼' },
  RM002: { name:'翡冷翠', capacity:4, icon:'🍵' },
  RM003: { name:'布拉格', capacity:4, icon:'🍵' },
}

var PLATFORM_HINTS = {
  meituan:'美团券码格式：MT + 6位数字，如 MT001298',
  douyin:'抖音券码格式：DY + 6位数字，如 DY003456',
  dianping:'大众点评券码格式：DP + 6位数字，如 DP007891',
  gaode:'高德券码格式：GD + 6位数字，如 GD009876'
}

var PLATFORM_PREFIX = { meituan:'MT', douyin:'DY', dianping:'DP', gaode:'GD' }

Page({
  data: {
    step: 1,
    selectedPlatform: 'meituan',
    couponCode: '',
    platformHint: PLATFORM_HINTS.meituan,
    showConfirmModal: false,
    confirmPreview: '',
    pendingCode: '',
    matchedCouponInfo: '',
    couponName: '', couponPlatform: '', couponPrice: 0, couponDuration: 120, selectedTimeSlot: '',
    availableRooms: [],
    selectedRoom: '',
    selectedRoomName: '',
    timeSlots: [],
    selectedTime: '',
    showBookingConfirm: false,
    myCoupons: [],
    verifiedCoupons: [],
    isStaff: false,
    _verifying: false
  },

  onLoad: function(e) {
    // 区分店员端和客人端
    try {
      var role = wx.getStorageSync('mp_user_role')
      if (role === 'staff') {
        this.setData({ isStaff: true })
        this.loadVerifiedCoupons()
      }
    } catch(e) {}

    this.renderMyCoupons()
    this.generateTimeSlots()
    // 从优惠券页跳转过来时自动填入券码
    if (e && e.code) {
      this.setData({ couponCode: e.code, selectedPlatform: '' })
      // 自动识别平台
      var prefix = e.code.substring(0, 2).toUpperCase()
      var platformMap = { MT: 'meituan', DY: 'douyin', DP: 'dianping', GD: 'gaode' }
      var platform = platformMap[prefix] || 'meituan'
      this.setData({ selectedPlatform: platform, platformHint: PLATFORM_HINTS[platform] })
      // 如果券码在数据库中有记录，直接触发确认
      if (COUPON_DB[e.code]) {
        this.setData({ pendingCode: e.code })
        setTimeout(function() { this.setData({ showConfirmModal: true }) }.bind(this), 500)
      }
    }
  },

  selectPlatform: function(e) {
    var p = e.currentTarget.dataset.platform
    this.setData({ selectedPlatform: p, platformHint: PLATFORM_HINTS[p] })
  },

  onCouponInput: function(e) {
    var code = e.detail.value
    this.setData({ couponCode: code })
    if (code.length >= 7 && COUPON_DB[code]) {
      this.setData({ pendingCode: code, showConfirmModal: true })
    }
  },

  verifyCoupon: function() {
    var code = this.data.couponCode
    if (!code) { wx.showToast({ title: '请输入券码', icon: 'none' }); return }
    var prefix = PLATFORM_PREFIX[this.data.selectedPlatform]
    if (code.substring(0,2).toUpperCase() !== prefix) {
      wx.showToast({ title: '券码格式错误：' + PLATFORM_HINTS[this.data.selectedPlatform], icon: 'none' }); return
    }
    if (!COUPON_DB[code]) { wx.showToast({ title: '该券码暂未在系统中登记', icon: 'none' }); return }
    this.setData({ pendingCode: code, showConfirmModal: true })
  },

  scanCouponCode: function() {
    var self = this
    wx.scanCode({ onlyFromCamera: true, success: function(res) {
      self.setData({ couponCode: res.result })
      wx.showToast({ title: '扫码成功', icon: 'none' })
    }})
  },

  hideConfirmModal: function() { this.setData({ showConfirmModal: false, pendingCode: '' }) },

  confirmCouponUse: function() {
    if (this.data._verifying) return
    this.setData({ _verifying: true, showConfirmModal: false })
    var code = this.data.pendingCode
    var info = COUPON_DB[code]
    if (info) {
      try {
        var verified = wx.getStorageSync('mp_verified_coupons') || []
        var dup = false
        for (var i = 0; i < verified.length; i++) { if (verified[i].code === code) { dup = true; break } }
        if (!dup) verified.unshift({
          code: code, platform: info.source, title: info.title, price: info.price,
          time: new Date().toLocaleString(), room: ''
        })
        wx.setStorageSync('mp_verified_coupons', verified)
      } catch(e) {}
    }
    this.doVerify(code)
    var self = this
    setTimeout(function() { self.setData({ _verifying: false }) }, 1000)
  },

  // 店员端：加载已核销记录
  loadVerifiedCoupons: function() {
    try {
      var verified = wx.getStorageSync('mp_verified_coupons') || []
      this.setData({ verifiedCoupons: verified })
    } catch(e) {}
  },

  doVerify: function(code) {
    var info = COUPON_DB[code]
    if (!info) return
    var rooms = []
    for (var i = 0; i < info.matchRooms.length; i++) {
      var rid = info.matchRooms[i]
      if (ROOM_DATA[rid]) rooms.push({ id: rid, name: ROOM_DATA[rid].name, capacity: ROOM_DATA[rid].capacity, icon: ROOM_DATA[rid].icon })
    }
    var firstRoomName = rooms.length > 0 ? rooms[0].name : ''
    this.setData({
      matchedCouponInfo: info.title + ' · 价值 ¥' + info.price,
      couponName: info.title,
      couponPlatform: info.source,
      couponPrice: info.price,
      couponDuration: info.duration || 120,
      availableRooms: rooms,
      selectedRoom: rooms.length > 0 ? rooms[0].id : '',
      selectedRoomName: firstRoomName,
      step: 2
    })
    wx.showToast({ title: '验券成功！', icon: 'none' })
  },

  selectCouponRoom: function(e) {
    var id = e.currentTarget.dataset.id
    var rooms = this.data.availableRooms
    var name = ''
    for (var i = 0; i < rooms.length; i++) { if (rooms[i].id === id) { name = rooms[i].name; break } }
    this.setData({ selectedRoom: id, selectedRoomName: name })
  },

  goToTimeSelect: function() { this.setData({ step: 3 }) },

  // 6.2 时间段限制：当前时间之后的时间段才可选中
  generateTimeSlots: function() {
    var slots = []
    var now = new Date()
    var curMin = now.getHours() * 60 + now.getMinutes()
    for (var h = 0; h < 24; h++) {
      for (var m = 0; m < 60; m += 30) {
        var min = h * 60 + m
        var timeStr = String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0')
        var available = min >= curMin
        slots.push({ time: timeStr, label: timeStr, available: available, min: min })
      }
    }
    this.setData({ timeSlots: slots })
  },

  selectTime: function(e) {
    var ds = e.currentTarget.dataset
    if (ds.available === 'false' || ds.available === false) {
      wx.showToast({ title: '该时段已过，请选择其他时段', icon: 'none' })
      return
    }
    var slot = this._makeSlot(ds.time)
    this.setData({ selectedTime: slot, showBookingConfirm: true })
  },

  pickNow: function() {
    var now = new Date()
    var curMin = now.getHours() * 60 + now.getMinutes()
    var roundedMin = Math.ceil(curMin / 30) * 30
    var h = Math.floor(roundedMin / 60)
    var m = roundedMin % 60
    if (h >= 24) { wx.showToast({ title: '已过营业时间', icon: 'none' }); return }
    var t = String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0')
    var slot = this._makeSlot(t)
    this.setData({ selectedTime: slot, showBookingConfirm: true })
  },

  _makeSlot: function(startTime) {
    var sp = startTime.split(':')
    var startMin = parseInt(sp[0]) * 60 + parseInt(sp[1])
    var dur = this.data.couponDuration || 120
    var endMin = startMin + dur
    var eh = Math.floor(endMin / 60) % 24
    var em = endMin % 60
    var endStr = String(eh).padStart(2,'0') + ':' + String(em).padStart(2,'0')
    return startTime + ' - ' + endStr
  },

  hideBookingConfirm: function() { this.setData({ showBookingConfirm: false }) },

  confirmBooking: function() {
    this.setData({ showBookingConfirm: false })
    var code = this.data.pendingCode
    var info = COUPON_DB[code]
    if (!info) { wx.showToast({ title: '请先验券', icon: 'none' }); return }
    var now = new Date()
    var dateStr = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    var booking = {
      orderId: 'ORD'+String(Date.now()).slice(-6),
      roomId: this.data.selectedRoom, roomName: this.data.selectedRoomName,
      customerName: '', phone: '',
      date: dateStr, time: this.data.selectedTime || '',
      amount: info.price, status: 'Booked',
      created: new Date().toISOString(),
      doorCode: String(Math.floor(1000+Math.random()*9000))
    }
    try { var bookings = wx.getStorageSync('mp_bookings') || []; bookings.push(booking); wx.setStorageSync('mp_bookings', bookings) } catch(e) {}
    wx.showToast({ title: '✅ 预约成功！', icon: 'success' })
    setTimeout(function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) }, 1000)
  },

  selectDemoCoupon: function(e) {
    var code = e.currentTarget.dataset.code
    if (!COUPON_DB[code]) return
    this.setData({ couponCode: code, pendingCode: code, showConfirmModal: true })
  },

  useMyCoupon: function(e) {
    this.setData({ couponCode: 'MT001298', pendingCode: 'MT001298', showConfirmModal: true })
  },

  renderMyCoupons: function() {
    var self = this
    API.getUserCoupons().then(function(coupons) {
      var unused = []
      for (var i = 0; i < coupons.length; i++) {
        if (!coupons[i].used) unused.push({ id: 'c' + i, value: coupons[i].value, source: coupons[i].platform, status: 'unused', expiry: '2026-12-31' })
      }
      self.setData({ myCoupons: unused })
    })
  },

  goBack: function() { wx.navigateBack() },
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goTeaShop: function() { wx.navigateTo({ url: '/pages/tea-shop/tea-shop' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
