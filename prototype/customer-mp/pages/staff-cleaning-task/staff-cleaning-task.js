const STAFF_API = require('../../utils/staff-api')
const API = require('../../utils/api')
Page({
  data: { pending: [], inProgress: [] },
  onShow() { STAFF_API.getCleaningTasks().then(t => this.setData({ pending: t.pending, inProgress: t.inProgress })) },
  acceptTask(e) { STAFF_API.acceptCleaningTask(e.currentTarget.dataset.id).then(() => this.onShow()) },
  completeTask(e) {
    var self = this
    var taskId = e.currentTarget.dataset.id
    var roomId = e.currentTarget.dataset.roomid || ''
    STAFF_API.completeCleaningTask(taskId).then(function() {
      wx.showToast({ title: '🧹 保洁完成，已恢复设备', icon: 'none' })
      // 触发打扫完成场景：关灯 → 关空调 → 关窗帘 → 关音乐
      if (roomId) { API.executeScene(roomId, 'Cleanup').catch(function() {}) }
      self.onShow()
    })
  }
})
