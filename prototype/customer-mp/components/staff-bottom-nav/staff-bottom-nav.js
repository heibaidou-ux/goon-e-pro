Component({
  properties: {
    active: { type: String, value: 'dashboard' }
  },
  data: {
    tabs: [
      { key: 'dashboard', label: '工作台', icon: '📊' },
      { key: 'orders',    label: '订单',   icon: '📋' },
      { key: 'device',    label: '设备',   icon: '📱' },
      { key: 'todo',  label: '待办',   icon: '✅' }
    ]
  },
  methods: {
    onTabTap(e) {
      var key = e.currentTarget.dataset.key
      if (key === this.properties.active) return
      var urls = {
        dashboard: '/pages/staff/staff-dashboard/staff-dashboard',
        orders: '/pages/staff/staff-order-management/staff-order-management',
        device: '/pages/staff/staff-device-monitor/staff-device-monitor',
        todo: '/pages/staff/staff-todo/staff-todo'
      }
      var url = urls[key]
      if (url) wx.switchTab ? wx.navigateTo({ url: url }) : wx.navigateTo({ url: url })
    }
  }
})
