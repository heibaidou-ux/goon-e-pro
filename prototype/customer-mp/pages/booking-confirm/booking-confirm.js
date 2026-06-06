const API = require('../../utils/api')
Page({
  data: { roomId: '', roomName: '', dateStr: '', startTime: '10:00', endTime: '12:00', duration: 2, totalAmount: '0.00', paymentMethod: 'WeChat', balance: 0 },
  onLoad(e) {
    const d = this.data
    this.setData({ roomId: e.roomId || '', dateStr: e.date || '', startTime: e.start || '10:00', endTime: e.end || '12:00', totalAmount: e.total || '0.00', duration: ((parseFloat(e.end || '12') - parseFloat(e.start || '10')) || 2).toString() })
    if (e.roomId) API.getRoomById(e.roomId).then(r => this.setData({ roomName: r.name })).catch(() => {})
    API.getBalance().then(b => this.setData({ balance: b }))
  },
  setPayment(e) { this.setData({ paymentMethod: e.currentTarget.dataset.method }) },
  submitBooking() {
    const d = this.data
    API.createBooking({ roomId: d.roomId, roomName: d.roomName, date: d.dateStr, start: d.startTime, end: d.endTime, duration: parseFloat(d.duration), amount: parseFloat(d.totalAmount), paymentMethod: d.paymentMethod }).then(() => {
      wx.showToast({ title: '✅ 预约成功！', icon: 'success', duration: 2000 })
      setTimeout(() => wx.switchTab({ url: '/pages/my-orders/my-orders' }), 2000)
    }).catch(err => wx.showToast({ title: '❌ ' + (err.message || '预约失败'), icon: 'none' }))
  }
})