const API = require('../../utils/api')
Page({
  data: { rooms: [], filteredRooms: [], filterType: '' },
  onLoad() { API.getRooms(true).then(rooms => this.setData({ rooms, filteredRooms: rooms })) },
  setFilter(e) {
    const type = e.currentTarget.dataset.type
    const list = type ? this.data.rooms.filter(r => r.type === type) : this.data.rooms
    this.setData({ filterType: type, filteredRooms: list })
  },
  goDetail(e) { wx.navigateTo({ url: '/pages/room-detail/room-detail?roomId=' + e.currentTarget.dataset.id }) }
})