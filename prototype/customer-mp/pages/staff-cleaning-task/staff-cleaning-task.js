const API = require('../../utils/staff-api')
Page({
  data: { pending: [], inProgress: [] },
  onShow() { API.getCleaningTasks().then(t => this.setData({ pending: t.pending, inProgress: t.inProgress })) },
  acceptTask(e) { API.acceptCleaningTask(e.currentTarget.dataset.id).then(() => this.onShow()) },
  completeTask(e) { API.completeCleaningTask(e.currentTarget.dataset.id).then(() => this.onShow()) }
})
