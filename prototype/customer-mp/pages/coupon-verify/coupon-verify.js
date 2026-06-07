var API = require('../../utils/api')

var COUPON_DB = {
  'MT001298': { source:'美团', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'MT002456': { source:'美团', title:'茶室单人品茗券', matchRooms:['RM002','RM003'], price:68, duration:60 },
  'MT003789': { source:'美团', title:'商务会议3小时套餐', matchRooms:['RM001'], price:358, duration:180 },
  'DY003456': { source:'抖音', title:'商务会议3小时套餐', matchRooms:['RM001'], price:358, duration:180 },
  'DY007891': { source:'抖音', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
  'DP007891': { source:'大众点评', title:'中茶室休闲体验', matchRooms:['RM002','RM003'], price:88, duration:120 },
  'GD009876': { source:'高德', title:'茶室双人体验套餐', matchRooms:['RM004','RM002'], price:168, duration:120 },
}

var ROOM_DATA = {
  RM004: { name:'大茶室C', capacity:6, icon:'🍵' },
  RM001: { name:'大会议室', capacity:10, icon:'💼' },
  RM002: { name:'中茶室A', capacity:4, icon:'🍵' },
  RM003: { name:'中茶室B', capacity:4, icon:'🍵' },
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
    availableRooms: [],
    selectedRoom: '',
    timeSlots: [],
    selectedTime: '',
    myCoupons: []
  },

  onLoad: function() {
    this.renderMyCoupons()
    this.generateTimeSlots()
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
    this.setData({ showConfirmModal: false })
    this.doVerify(this.data.pendingCode)
  },

  doVerify: function(code) {
    var info = COUPON_DB[code]
    if (!info) return
    var rooms = []
    for (var i = 0; i < info.matchRooms.length; i++) {
      var rid = info.matchRooms[i]
      if (ROOM_DATA[rid]) rooms.push({ id: rid, name: ROOM_DATA[rid].name, capacity: ROOM_DATA[rid].capacity, icon: ROOM_DATA[rid].icon })
    }
    this.setData({
      matchedCouponInfo: info.title + ' · 价值 ¥' + info.price,
      availableRooms: rooms,
      selectedRoom: rooms.length > 0 ? rooms[0].id : '',
      step: 2
    })
    wx.showToast({ title: '验券成功！', icon: 'none' })
  },

  selectCouponRoom: function(e) {
    this.setData({ selectedRoom: e.currentTarget.dataset.id })
  },

  goToTimeSelect: function() { this.setData({ step: 3 }) },

  // 6.2 时间段限制：当前时间之后的时间段才可选中
  generateTimeSlots: function() {
    var slots = []
    var now = new Date()
    var curMin = now.getHours() * 60 + now.getMinutes()
    for (var h = 9; h < 22; h++) {
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
    var slots = this.data.timeSlots
    for (var i = 0; i < slots.length; i++) {
      if (slots[i].time === ds.time && !slots[i].available) {
        wx.showToast({ title: '该时段已过，请选择其他时段', icon: 'none' })
        return
      }
    }
    this.setData({ selectedTime: ds.time })
  },

  pickNow: function() {
    var now = new Date()
    var curMin = now.getHours() * 60 + now.getMinutes()
    var roundedMin = Math.ceil(curMin / 30) * 30
    var h = Math.floor(roundedMin / 60)
    var m = roundedMin % 60
    if (h >= 22) { wx.showToast({ title: '已过营业时间', icon: 'none' }); return }
    var t = String(h).padStart(2,'0') + ':' + String(m).padStart(2,'0')
    this.setData({ selectedTime: t })
    wx.showToast({ title: '已选择 ' + t + ' 开始', icon: 'none' })
  },

  confirmBooking: function() {
    if (!this.data.selectedRoom || !this.data.selectedTime) { wx.showToast({ title: '请选择时段', icon: 'none' }); return }
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
