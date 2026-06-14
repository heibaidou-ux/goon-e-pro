Component({
  properties: {
    active: { type: String, value: 'dashboard' }
  },
  data: {
    tabs: [
      { key: 'dashboard', label: '工作台', icon: '📊' },
      { key: 'orders',    label: '订单',   icon: '📋' },
      { key: 'device',    label: '设备',   icon: '📱' },
      { key: 'cleaning',  label: '保洁',   icon: '🧹' }
    ]
  },
  methods: {
    onTabTap(e) {
      var key = e.currentTarget.dataset.key
      if (key === this.properties.active) return
      var urls = {
        dashboard: '/pages/staff-dashboard/staff-dashboard',
        orders: '/pages/staff-order-management/staff-order-management',
        device: '/pages/staff-device-monitor/staff-device-monitor',
        cleaning: '/pages/staff-cleaning-task/staff-cleaning-task'
      }
      var url = urls[key]
      if (url) wx.switchTab ? wx.navigateTo({ url: url }) : wx.navigateTo({ url: url })
    }
  }
})
