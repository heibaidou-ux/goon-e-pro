var API = require('../../utils/api')

Page({
  data: {
    showProductView: true,
    currentCat: 'tea',
    products: {},
    cart: [],
    cartTotal: 0,
    cartTotalPrice: '0.00',
    // Room context
    roomBannerVisible: false,
    roomBannerText: '',
    roomBannerRoomName: '',
    roomId: '', roomName: '', tableId: '',
    // Detail modal
    showDetail: false,
    detailProduct: {},
    detailQty: 1,
    // Payment modal
    showPayModal: false,
    showInsufficient: false,
    insufficientMsg: '',
    payMethod: 'balance'
  },

  onLoad: function(e) {
    var self = this
    // 原型12个商品
    var defaultProducts = {
      snack: [
        { id:'S01', name:'坚果拼盘', desc:'精选四种坚果 · 轻盐烘焙', price:38, spec:'200g/份', icon:'🌰', bg:'#fff3e0', story:'精选美国杏仁、新疆核桃、云南松子、东北榛子', origin:'混合产地' },
        { id:'S02', name:'绿豆糕（经典款）', desc:'传统苏式 · 细腻绵密', price:25, spec:'150g/盒', icon:'🥮', bg:'#fff8e1', story:'去皮绿豆蒸制，口感细腻绵密', origin:'江苏苏州' },
      ],
      tea: [
        { id:'T01', name:'明前龙井', desc:'西湖核心产区 · 清香甘醇', price:168, spec:'250g/罐', icon:'🍃', bg:'#e8f5e9', story:'明前采摘于西湖核心产区', origin:'杭州西湖', brewingTips:'85℃水温 · 30-60秒出汤 · 玻璃杯' },
        { id:'T02', name:'金骏眉', desc:'武夷山桐木关 · 蜜香甘醇', price:258, spec:'200g/罐', icon:'🪵', bg:'#fce4ec', story:'全芽头制作金毫显露', origin:'福建武夷山', brewingTips:'90℃水温 · 即刻出汤 · 白瓷盖碗' },
        { id:'T03', name:'铁观音', desc:'安溪高山 · 七泡有余香', price:138, spec:'250g/罐', icon:'🏔️', bg:'#fff3e0', story:'安溪高山生态茶园', origin:'福建安溪', brewingTips:'100℃沸水 · 15-30秒 · 盖碗' },
        { id:'T04', name:'云南普洱（生普）', desc:'勐海古树 · 茶气霸烈', price:198, spec:'357g/饼', icon:'🌿', bg:'#efebe9', story:'古树茶园原料传统石磨压饼', origin:'云南勐海', brewingTips:'100℃沸水 · 5-10秒 · 紫砂壶' },
        { id:'T05', name:'云南普洱（熟普）', desc:'勐海发酵 · 陈香醇厚', price:208, spec:'357g/饼', icon:'🏵️', bg:'#f1f8e9', story:'传统渥堆发酵工艺', origin:'云南勐海', brewingTips:'100℃沸水 · 10-20秒' },
        { id:'T06', name:'武夷岩茶', desc:'大红袍 · 岩骨花香', price:358, spec:'100g/罐', icon:'🪨', bg:'#efebe9', story:'大红袍岩骨花香', origin:'福建武夷山', brewingTips:'100℃沸水 · 5-10秒 · 紫砂壶' },
        { id:'T07', name:'福鼎白茶', desc:'白毫银针 · 清甜回甘', price:198, spec:'50g/罐', icon:'🌸', bg:'#f3e5f5', story:'白毫银针清甜回甘', origin:'福建福鼎', brewingTips:'90℃水温 · 30-60秒 · 盖碗' },
        { id:'T08', name:'碧螺春', desc:'太湖东山 · 花果香韵', price:218, spec:'200g/罐', icon:'🌱', bg:'#e8f5e9', story:'一芽一叶精制白毫显露', origin:'苏州太湖', brewingTips:'80℃水温 · 20-40秒 · 玻璃杯' },
      ],
      ware: [
        { id:'W01', name:'建盏茶杯', desc:'建阳传统工艺 · 铁胎厚釉', price:58, spec:'单只装', icon:'🏺', bg:'#efebe9', story:'福建建阳传统工艺烧制', origin:'福建建阳' },
        { id:'W02', name:'紫砂壶（小号）', desc:'宜兴原矿 · 手工拍打', price:188, spec:'200ml', icon:'🫖', bg:'#f5f5f5', story:'宜兴原矿紫泥手工拍打成型', origin:'江苏宜兴' },
        { id:'W03', name:'双人下午茶套餐', desc:'双人茶聚 · 经典之选', price:168, spec:'1份', icon:'🧁', bg:'#fce4ec', story:'任选2壶茶饮+双色绿豆糕+坚果拼盘', origin:'高岸茶室' },
        { id:'W04', name:'商务洽谈套餐', desc:'商务会谈 · 尊享体验', price:228, spec:'1份', icon:'💼', bg:'#e3f2fd', story:'精选岩茶或金骏眉+茶点四色拼盘', origin:'高岸茶室' },
      ]
    }

    // 处理brewingTips → _tips
    for (var cat in defaultProducts) {
      var list = defaultProducts[cat]
      for (var i = 0; i < list.length; i++) {
        if (list[i].brewingTips) {
          list[i]._tips = list[i].brewingTips.split('·')
        } else {
          list[i]._tips = []
        }
        list[i]._qty = 0
      }
    }

    self.setData({ products: defaultProducts })

    // Room context params
    var roomId = e.room_id || ''
    var roomName = e.room_name || e.roomName || ''
    var tableId = e.table_id || '1'
    if (roomId) {
      self.setData({
        roomId: roomId, roomName: roomName, tableId: tableId,
        roomBannerVisible: true,
        roomBannerRoomName: roomName || '本包间',
        roomBannerText: '正在为 ' + (roomName || '本包间') + ' ' + tableId + '号桌 点单'
      })
    }

    // Load cart
    self.loadCart()

    // Check if ?tab=cart
    if (e.tab === 'cart') self.setData({ showProductView: false })
  },

  // ── 分类切换 ──
  switchCat: function(e) {
    this.setData({ currentCat: e.currentTarget.dataset.cat })
  },

  // ── 购物车 ──
  loadCart: function() {
    var self = this
    API.getCart().then(function(cartData) {
      var cart = cartData || []
      var totalAmt = 0
      var totalQty = 0
      // 给购物车商品附上图标
      var products = self.data.products
      for (var i = 0; i < cart.length; i++) {
        totalAmt += (cart[i].qty || 1) * (cart[i].price || 0)
        totalQty += (cart[i].qty || 1)
        // 从商品数据中查找图标
        for (var cat in products) {
          for (var j = 0; j < products[cat].length; j++) {
            if (products[cat][j].id === cart[i].productId) {
              cart[i].icon = products[cat][j].icon
              break
            }
          }
        }
      }
      self.setData({ cart: cart, cartTotal: totalQty, cartTotalPrice: totalAmt.toFixed(2) })
      // Sync _qty with products
      for (var cat in products) {
        for (var j = 0; j < products[cat].length; j++) {
          products[cat][j]._qty = 0
          for (var k = 0; k < cart.length; k++) {
            if (cart[k].productId === products[cat][j].id) { products[cat][j]._qty = cart[k].qty; break }
          }
        }
      }
      self.setData({ products: products })
    })
  },

  // incQty / decQty (原型 addToCart / removeFromCart)
  incQty: function(e) {
    var id = e.currentTarget.dataset.id
    var self = this
    // Find product
    var p = null
    for (var cat in self.data.products) {
      for (var i = 0; i < self.data.products[cat].length; i++) {
        if (self.data.products[cat][i].id === id) { p = self.data.products[cat][i]; break }
      }
      if (p) break
    }
    if (!p) return
    API.addToCart({ productId: id, name: p.name, price: p.price }).then(function() { self.loadCart() })
  },

  decQty: function(e) {
    var id = e.currentTarget.dataset.id
    var self = this
    API.removeFromCart(id).then(function() { self.loadCart() })
  },

  // ── 购物车视图 ──
  showCart: function() {
    this.setData({ showProductView: false })
  },

  showProducts: function() {
    this.setData({ showProductView: true })
  },

  cartQtyInc: function(e) {
    var id = e.currentTarget.dataset.id
    var self = this
    API.addToCart({ productId: id }).then(function() { self.loadCart() })
  },

  cartQtyDec: function(e) {
    var id = e.currentTarget.dataset.id
    var self = this
    API.removeFromCart(id).then(function() { self.loadCart() })
  },

  clearCart: function() {
    var self = this
    // Clear one by one
    var cart = self.data.cart
    var count = cart.length
    var cleared = 0
    for (var i = 0; i < cart.length; i++) {
      API.removeFromCart(cart[i].productId).then(function() {
        cleared++
        if (cleared >= count) { self.loadCart(); wx.showToast({ title: '购物车已清空', icon: 'none' }) }
      })
    }
    if (count === 0) { self.loadCart(); self.showProducts() }
  },

  // ── 商品详情 ──
  showProductDetail: function(e) {
    var id = e.currentTarget.dataset.id
    var cat = e.currentTarget.dataset.cat
    var list = this.data.products[cat] || []
    for (var i = 0; i < list.length; i++) {
      if (list[i].id === id) {
        this.setData({ showDetail: true, detailProduct: list[i], detailQty: 1 })
        break
      }
    }
  },

  hideDetail: function() { this.setData({ showDetail: false }) },
  detailQtyInc: function() {
    var q = this.data.detailQty + 1
    this.setData({ detailQty: q })
  },
  detailQtyDec: function() {
    if (this.data.detailQty > 1) this.setData({ detailQty: this.data.detailQty - 1 })
  },

  detailAddToCart: function() {
    var p = this.data.detailProduct
    var qty = this.data.detailQty
    if (!p) return
    var self = this
    // Add multiple times
    for (var i = 0; i < qty; i++) {
      API.addToCart({ productId: p.id, name: p.name, price: p.price })
    }
    this.setData({ showDetail: false })
    wx.showToast({ title: p.name + ' ×' + qty + ' 已加入购物车', icon: 'none' })
    setTimeout(function() { self.loadCart() }, 300)
  },

  // ── 结算 ──
  checkout: function() {
    if (this.data.cart.length === 0) { wx.showToast({ title: '购物车为空', icon: 'none' }); return }
    this.setData({ showPayModal: true, payMethod: 'balance' })
  },

  selectPayMethod: function(e) {
    this.setData({ payMethod: e.currentTarget.dataset.method })
  },

  confirmPay: function() {
    var self = this
    var total = parseFloat(self.data.cartTotalPrice)
    var payMethod = self.data.payMethod

    if (payMethod === 'balance') {
      var user = API.getCurrentUser()
      var balance = user ? (user.balance || 0) : 0
      if (balance < total) {
        self.setData({
          showInsufficient: true,
          insufficientMsg: '当前余额 ¥' + balance + '，需支付 ¥' + total + '。请选择其他支付方式或取消支付。'
        })
        return
      }
    }

    wx.showLoading({ title: '支付中...' })
    API.createShopOrder(self.data.cart, payMethod, total).then(function() {
      wx.hideLoading()
      self.setData({ showPayModal: false, showProductView: true })
      self.loadCart()
      wx.showToast({ title: '✅ 支付成功！', icon: 'success' })
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: '支付失败：' + (err.message || ''), icon: 'none' })
    })
  },

  cancelPay: function() { this.setData({ showPayModal: false }) },
  hideInsufficient: function() { this.setData({ showInsufficient: false }) },
  switchPayMethod: function() { this.setData({ showInsufficient: false }) },

  closeRoomBanner: function() {
    this.setData({ roomBannerVisible: false })
  },

  // ── 导航 ──
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
