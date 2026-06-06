const API = require('../../utils/api')
Page({
  data: { room: {}, roomId: '', selectedDate: '', startTime: '10:00', endTime: '12:00', estimatedTotal: 0 },
  onLoad(e) {
    const roomId = e.roomId || 'RM001'
    const today = new Date().toISOString().slice(0,10)
    this.setData({ roomId, selectedDate: today })
    API.getRoomById(roomId).then(room => this.setData({ room }, () => this.calcTotal()))
  },
  onDateChange(e) { this.setData({ selectedDate: e.detail.value }, () => this.calcTotal()) },
  onStartChange(e) { this.setData({ startTime: e.detail.value }, () => this.calcTotal()) },
  onEndChange(e) { this.setData({ endTime: e.detail.value }, () => this.calcTotal()) },
  calcTotal() {
    const hours = parseFloat(this.data.endTime) - parseFloat(this.data.startTime)
    const total = Math.max(0, hours * (this.data.room.pricePerHour || 0))
    this.setData({ estimatedTotal: total.toFixed(2) })
  },
  goBooking() {
    wx.navigateTo({ url: '/pages/booking-confirm/booking-confirm?roomId=' + this.data.roomId + '&date=' + this.data.selectedDate + '&start=' + this.data.startTime + '&end=' + this.data.endTime + '&total=' + this.data.estimatedTotal })
  }
})