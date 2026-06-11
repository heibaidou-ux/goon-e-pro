/**
 * bottom-nav 自定义底部导航栏组件
 * 5个按钮：首页、预订、茶品、订单、我的
 * 通过 active 属性控制当前高亮页
 */
Component({
  properties: {
    // 当前激活的页面标识: 'home' | 'booking' | 'tea' | 'orders' | 'profile'
    active: {
      type: String,
      value: 'home'
    }
  },

  data: {
    tabs: [
      { key: 'home',    label: '首页', icon: '🏠' },
      { key: 'booking', label: '预订', icon: '📅' },
      { key: 'tea',     label: '茶品', icon: '🍵' },
      { key: 'orders',  label: '订单', icon: '📋' },
      { key: 'profile', label: '我的', icon: '👤' }
    ]
  },

  methods: {
    onTabTap(e) {
      var key = e.currentTarget.dataset.key
      // 如果点击的不是当前页，跳转
      if (key !== this.properties.active) {
        switch (key) {
          case 'home':
            wx.navigateTo({ url: '/pages/home/home' })
            break
          case 'booking':
            wx.navigateTo({ url: '/pages/room-list/room-list' })
            break
          case 'tea':
            wx.navigateTo({ url: '/pages/tea-shop/tea-shop' })
            break
          case 'orders':
            wx.navigateTo({ url: '/pages/my-orders/my-orders' })
            break
          case 'profile':
            wx.navigateTo({ url: '/pages/member-center/member-center' })
            break
        }
      }
    }
  }
})
