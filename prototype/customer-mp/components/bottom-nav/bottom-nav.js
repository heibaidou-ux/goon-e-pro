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
            try {
              var role = wx.getStorageSync('mp_user_role')
              if (role === 'staff') { wx.reLaunch({ url: '/pages/staff/staff-dashboard/staff-dashboard' }); return }
              if (role === 'shareholder') { wx.reLaunch({ url: '/pages/workbench/investor-workbench/investor-workbench' }); return }
            } catch(e) {}
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
            // 未登录时跳首页弹出登录框
            try {
              var loggedIn = wx.getStorageSync('mp_logged_in')
              if (!loggedIn) { wx.navigateTo({ url: '/pages/home/home?showLogin=1' }); return }
            } catch(e) {}
            wx.navigateTo({ url: '/pages/member-center/member-center' })
            break
        }
      }
    }
  }
})
