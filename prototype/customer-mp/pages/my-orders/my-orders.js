const API = require('../../utils/api')
Page({
  data: { orders: [], filteredOrders: [], filter: 'all' },
  onShow() { this.loadOrders() },
  loadOrders() {
    API.getUserOrders().then(orders => {
      const mapped = orders.map(o => ({ ...o, statusLabel: { InUse:'使用中', Booked:'已预订', Completed:'已完成', Cancelled:'已取消' }[o.status] || o.status }))
      this.setData({ orders: mapped }, () => this.applyFilter())
    })
  },
  setFilter(e) { this.setData({ filter: e.currentTarget.dataset.filter }, () => this.applyFilter()) },
  applyFilter() {
    const f = this.data.filter
    const list = f === 'all' ? this.data.orders : this.data.orders.filter(o => o.status === f)
    this.setData({ filteredOrders: list })
  }
})