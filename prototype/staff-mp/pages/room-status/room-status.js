const API = require('../../utils/api')
Page({ data: { rooms: [] }, onShow() { API.getRoomStatusList().then(rooms => this.setData({ rooms })) } })