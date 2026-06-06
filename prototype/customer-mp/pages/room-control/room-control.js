const API = require('../../utils/api')
Page({
  data: { roomId: '', roomName: '房间', devices: [], scenes: [] },
  onLoad(e) {
    const roomId = e.roomId || 'RM004'
    this.setData({ roomId })
    Promise.all([
      API.getRoomDevices(roomId),
      Promise.resolve([{sceneId:'SC001',name:'迎宾模式',icon:'👋',color:'#07c160'},{sceneId:'SC002',name:'茶艺模式',icon:'🍵',color:'#e37318'},{sceneId:'SC003',name:'会议模式',icon:'💼',color:'#0052d9'}])
    ]).then(([devices, scenes]) => {
      this.setData({ devices: devices.map(d => ({ ...d, typeLabel: {Lock:'门锁',AC:'空调',Light:'灯光',Curtain:'窗帘',Speaker:'音响'}[d.type] || d.type, typeIcon: {Lock:'🔒',AC:'❄️',Light:'💡',Curtain:'🪟',Speaker:'🔊'}[d.type] || '📡' })), scenes })
    })
  },
  activateScene(e) { API.executeScene(this.data.roomId, e.currentTarget.dataset.id).then(() => wx.showToast({ title: '场景已执行', icon: 'none' })) },
  onLightChange(e) { API.controlDevice(e.currentTarget.dataset.id, { brightness: e.detail.value }).catch(() => {}) },
  onAcToggle(e) { API.controlDevice(e.currentTarget.dataset.id, { mode: e.detail.value ? 'cool' : 'off' }).catch(() => {}) },
  onSpeakerToggle(e) { API.controlDevice(e.currentTarget.dataset.id, { playing: e.detail.value }).catch(() => {}) },
  onCurtainToggle(e) { API.controlDevice(e.currentTarget.dataset.id, { position: e.detail.value ? 'open' : 'closed' }).catch(() => {}) }
})