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
    payMethod: 'wechat',
    // Delivery modal
    showDeliveryModal: false,
    deliveryMethod: 'inroom',
    expressName: '', expressPhone: '',
    expressProvince: '', expressCity: '', expressDistrict: '', expressDetail: '',
    expressAddress: '',
    provinceIndex: 0, cityIndex: 0, districtIndex: 0,
    provinces: ['广东省','北京市','上海市','浙江省','江苏省','福建省','四川省','湖北省','湖南省','山东省','河南省','安徽省','河北省','重庆市','陕西省','江西省','辽宁省','天津市','广西区','云南省','贵州省','山西省','吉林省','黑龙江省','海南省','甘肃省','内蒙古','新疆','宁夏','青海省','西藏区'],
    cities: [], districts: [],
    addressHistory: [],
    pendingOrder: null
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
    // 模拟支付，先保存订单数据，然后弹出配送方式选择
    setTimeout(function() {
      wx.hideLoading()
      // 加载地址历史
      try {
        var history = wx.getStorageSync('mp_address_history') || []
        self.setData({ addressHistory: history })
      } catch(e) {}
      self.setData({
        showPayModal: false,
        showDeliveryModal: true,
        deliveryMethod: self.data.roomId ? 'inroom' : 'pickup',
        pendingOrder: { cart: self.data.cart, payMethod: payMethod, total: total }
      })
    }, 800)
  },

  cancelPay: function() { this.setData({ showPayModal: false }) },
  hideInsufficient: function() { this.setData({ showInsufficient: false }) },
  switchPayMethod: function() { this.setData({ showInsufficient: false }) },

  // ── 配送方式 ──
  selectDeliveryMethod: function(e) {
    this.setData({ deliveryMethod: e.currentTarget.dataset.method })
  },

  onExpressName: function(e) { this.setData({ expressName: e.detail.value }) },
  onExpressPhone: function(e) { this.setData({ expressPhone: e.detail.value }) },
  onExpressDetail: function(e) { this.setData({ expressDetail: e.detail.value }) },
  onExpressAddress: function(e) { this.setData({ expressAddress: e.detail.value }) },

  // ── 省市区选择 ──
  onProvinceChange: function(e) {
    var idx = e.detail.value
    var province = this.data.provinces[idx]
    var cities = this._getCities(province)
    this.setData({ provinceIndex: idx, expressProvince: province, cityIndex: 0, districtIndex: 0, cities: cities, districts: [], expressCity: '', expressDistrict: '' })
    if (cities.length > 0) {
      this.setData({ expressCity: cities[0] })
      var districts = this._getDistricts(province, cities[0])
      this.setData({ districts: districts, expressDistrict: districts.length > 0 ? districts[0] : '' })
    }
  },

  onCityChange: function(e) {
    var idx = e.detail.value
    var city = this.data.cities[idx]
    var districts = this._getDistricts(this.data.expressProvince, city)
    this.setData({ cityIndex: idx, expressCity: city, districtIndex: 0, districts: districts, expressDistrict: districts.length > 0 ? districts[0] : '' })
  },

  onDistrictChange: function(e) {
    var idx = e.detail.value
    this.setData({ districtIndex: idx, expressDistrict: this.data.districts[idx] })
  },

  _getCities: function(province) {
    var map = {
      '广东省': ['广州市','深圳市','珠海市','佛山市','东莞市','中山市','惠州市','江门市','汕头市','湛江市','肇庆市','韶关市','茂名市','梅州市','清远市','揭阳市','阳江市','河源市','汕尾市','潮州市','云浮市'],
      '北京市': ['北京市'],
      '上海市': ['上海市'],
      '浙江省': ['杭州市','宁波市','温州市','嘉兴市','绍兴市','金华市','台州市','湖州市','丽水市','衢州市','舟山市'],
      '江苏省': ['南京市','苏州市','无锡市','常州市','南通市','徐州市','扬州市','盐城市','镇江市','泰州市','淮安市','连云港市','宿迁市'],
      '福建省': ['福州市','厦门市','泉州市','漳州市','莆田市','三明市','龙岩市','南平市','宁德市'],
      '四川省': ['成都市','绵阳市','德阳市','宜宾市','南充市','泸州市','达州市','乐山市','自贡市','眉山市','遂宁市','广元市','内江市'],
      '湖北省': ['武汉市','宜昌市','襄阳市','荆州市','黄冈市','十堰市','孝感市','荆门市'],
      '湖南省': ['长沙市','株洲市','湘潭市','衡阳市','岳阳市','常德市','郴州市'],
      '山东省': ['济南市','青岛市','烟台市','潍坊市','临沂市','淄博市','济宁市'],
      '河南省': ['郑州市','洛阳市','新乡市','南阳市','开封市','安阳市','许昌市'],
      '安徽省': ['合肥市','芜湖市','蚌埠市','阜阳市','安庆市','马鞍山市'],
      '河北省': ['石家庄市','唐山市','保定市','邯郸市','廊坊市','秦皇岛市'],
      '重庆市': ['重庆市'],
      '陕西省': ['西安市','咸阳市','宝鸡市'],
      '江西省': ['南昌市','九江市','赣州市'],
      '辽宁省': ['沈阳市','大连市'],
      '天津市': ['天津市'],
      '广西区': ['南宁市','桂林市','柳州市'],
      '云南省': ['昆明市','大理市'],
      '贵州省': ['贵阳市'],
      '山西省': ['太原市'],
      '吉林省': ['长春市'],
      '黑龙江省': ['哈尔滨市'],
      '海南省': ['海口市','三亚市'],
      '甘肃省': ['兰州市'],
      '内蒙古': ['呼和浩特市'],
      '新疆': ['乌鲁木齐市'],
      '宁夏': ['银川市'],
      '青海省': ['西宁市'],
      '西藏区': ['拉萨市']
    }
    return map[province] || ['广州市']
  },

  _getDistricts: function(province, city) {
    // 简化处理，返回常见区
    var common = ['天河区','海珠区','越秀区','荔湾区','白云区','番禺区','黄埔区','花都区','南沙区','从化区','增城区']
    if (city === '北京市') return ['海淀区','朝阳区','东城区','西城区','丰台区','通州区']
    if (city === '上海市') return ['浦东新区','静安区','徐汇区','长宁区','黄浦区','虹口区']
    if (city === '深圳市') return ['南山区','福田区','罗湖区','宝安区','龙岗区','龙华区']
    if (city === '广州市') return common
    if (city === '杭州市') return ['西湖区','上城区','拱墅区','滨江区','余杭区','萧山区']
    if (city === '成都市') return ['武侯区','锦江区','青羊区','金牛区','成华区','高新区']
    if (city === '武汉市') return ['武昌区','江汉区','江岸区','洪山区','硚口区','汉阳区']
    if (city === '南京市') return ['鼓楼区','秦淮区','建邺区','玄武区','栖霞区','雨花台区']
    if (city === '重庆市') return ['渝中区','江北区','渝北区','沙坪坝区','九龙坡区']
    return ['全区']
  },

  // ── 地址历史 ──
  loadAddressHistory: function() {
    try {
      var history = wx.getStorageSync('mp_address_history') || []
      this.setData({ addressHistory: history })
    } catch(e) {}
  },

  selectHistoryAddress: function(e) {
    var idx = e.currentTarget.dataset.idx
    var addr = this.data.addressHistory[idx]
    if (!addr) return
    this.setData({
      expressName: addr.name || '',
      expressPhone: addr.phone || '',
      expressProvince: addr.province || '',
      expressCity: addr.city || '',
      expressDistrict: addr.district || '',
      expressDetail: addr.detail || ''
    })
    wx.showToast({ title: '已填入收货地址', icon: 'none' })
  },

  deleteHistoryAddress: function(e) {
    var self = this
    var idx = e.currentTarget.dataset.idx
    var history = self.data.addressHistory
    if (idx < 0 || idx >= history.length) return
    wx.showModal({
      title: '删除地址',
      content: '确定删除此地址？',
      success: function(res) {
        if (res.confirm) {
          history.splice(idx, 1)
          self.setData({ addressHistory: history })
          try { wx.setStorageSync('mp_address_history', history) } catch(e) {}
        }
      }
    })
  },

  confirmDelivery: function() {
    var self = this
    var order = self.data.pendingOrder
    if (!order) return
    var method = self.data.deliveryMethod

    if (method === 'express') {
      var fullAddr = (self.data.expressProvince || '') + (self.data.expressCity || '') + (self.data.expressDistrict || '') + (self.data.expressDetail || '')
      if (!self.data.expressName || !self.data.expressPhone || !fullAddr) {
        wx.showToast({ title: '请填写完整的收货信息', icon: 'none' })
        return
      }
      // 保存地址到历史
      var history = self.data.addressHistory || []
      var newAddr = { name: self.data.expressName, phone: self.data.expressPhone, province: self.data.expressProvince, city: self.data.expressCity, district: self.data.expressDistrict, detail: self.data.expressDetail }
      // 去重
      for (var i = 0; i < history.length; i++) {
        if (history[i].name === newAddr.name && history[i].phone === newAddr.phone && history[i].detail === newAddr.detail) {
          history.splice(i, 1); break
        }
      }
      history.unshift(newAddr)
      if (history.length > 5) history = history.slice(0, 5)
      try { wx.setStorageSync('mp_address_history', history) } catch(e) {}
    }

    var deliveryInfo = { method: method }
    if (method === 'express') {
      deliveryInfo.expressName = self.data.expressName
      deliveryInfo.expressPhone = self.data.expressPhone
      deliveryInfo.expressAddress = (self.data.expressProvince || '') + (self.data.expressCity || '') + (self.data.expressDistrict || '') + (self.data.expressDetail || '')
    }
    if (method === 'inroom') {
      deliveryInfo.roomName = self.data.roomName || self.data.roomBannerRoomName || ''
      deliveryInfo.roomId = self.data.roomId || ''
    }

    wx.showLoading({ title: '提交订单...' })
    API.createShopOrder(order.cart, order.payMethod, order.total, deliveryInfo).then(function() {
      wx.hideLoading()
      self.setData({
        showDeliveryModal: false, showProductView: true,
        pendingOrder: null
      })
      self.loadCart()
      wx.showToast({ title: '✅ 下单成功！', icon: 'success' })
    }).catch(function(err) {
      wx.hideLoading()
      wx.showToast({ title: '提交失败：' + (err.message || ''), icon: 'none' })
    })
  },

  hideDeliveryModal: function() {
    var self = this
    wx.showModal({
      title: '放弃订单', content: '确定要放弃当前订单吗？',
      success: function(res) {
        if (res.confirm) {
          self.setData({ showDeliveryModal: false, pendingOrder: null })
          self.loadCart()
        }
      }
    })
  },

  closeRoomBanner: function() {
    this.setData({ roomBannerVisible: false })
  },

  // ── 导航 ──
  goHome: function() { wx.navigateTo({ url: '/pages/home/home' }) },
  goRoomList: function() { wx.navigateTo({ url: '/pages/room-list/room-list' }) },
  goOrders: function() { wx.navigateTo({ url: '/pages/my-orders/my-orders' }) },
  goMember: function() { wx.navigateTo({ url: '/pages/member-center/member-center' }) }
})
