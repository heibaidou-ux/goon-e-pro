const API = require('../../utils/api')
Page({
  data: { rooms: [], devices: [], stats: { total: 0, online: 0, rate: '0%' }, selectedRoomId: '', selectedRoomName: '全部房间', roomOptions: ['全部房间'] },
  onShow() {
    Promise.all([API.getRoomStatusList(), API.getDeviceList(), API.getDeviceStats()]).then(([rooms, devices, stats]) => {
      const names = rooms.map(r => r.name)
      this.setData({ rooms, devices, stats, roomOptions: ['全部房间', ...names] })
    })
  },
  onRoomChange(e) {
    const idx = e.detail.value
    const name = this.data.roomOptions[idx]
    if (idx === 0) {
      API.getDeviceList().then(devices => this.setData({ devices, selectedRoomId: '', selectedRoomName: name }))
    } else {
      const room = this.data.rooms[idx - 1]
      API.getDeviceList(room.roomId).then(devices => this.setData({ devices, selectedRoomId: room.roomId, selectedRoomName: name }))
    }
  }
})