const STAFF_API = require('../../../utils/staff-api')
const API = require('../../../utils/api')
Page({
  data: { pending: [], inProgress: [] },
  onShow() { STAFF_API.getCleaningTasks().then(t => this.setData({ pending: t.pending, inProgress: t.inProgress })) },
  acceptTask(e) {
    var self = this
    var taskId = e.currentTarget.dataset.id
    var task = null
    for (var i = 0; i < self.data.pending.length; i++) {
      if (self.data.pending[i].taskId === taskId) { task = self.data.pending[i]; break }
    }
    if (!task) return
    STAFF_API.acceptCleaningTask(taskId).then(function() {
      var p = self.data.pending.filter(function(t) { return t.taskId !== taskId })
      task.status = 'inProgress'
      var ip = self.data.inProgress
      ip.push(task)
      self.setData({ pending: p, inProgress: ip })
      wx.showToast({ title: '已接单', icon: 'none' })
    })
  },
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
