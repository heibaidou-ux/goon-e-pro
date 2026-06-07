const API = require('../../utils/staff-api')
Page({ data: { rooms: [] }, onShow() { API.getRoomStatusList().then(rooms => this.setData({ rooms })) } })
