var API = require('../../utils/api')

Page({
  data: {
    roomId: '', roomName: '', products: [], filteredProducts: [], currentCat: '',
    cartCount: 0, total: 0, cartItems: [],
    showConfirm: false, showSuccess: false, successMsg: ''
  },

  onLoad: function(e) {
    var roomId = e.room_id || ''
    this.setData({ roomId: roomId })
    var self = this
    if (roomId) {
      API.scanRoomStatus(roomId).then(function(info) {
        self.setData({ roomName: info.roomName })
      }).catch(function(){})
    }
    API.getProducts().then(function(products) {
      var p = products.map(function(x) {
        return { productId: x.productId, name: x.name, price: x.price, desc: x.desc || '', image: x.image || '', category: x.category || '', _qty: 0 }
      })
      self.setData({ products: p, filteredProducts: p })
    })
  },

  switchCat: function(e) {
    var cat = e.currentTarget.dataset.cat
    var list = cat ? this.data.products.filter(function(p) { return p.category === cat }) : this.data.products
    this.setData({ currentCat: cat, filteredProducts: list })
  },

  incQty: function(e) {
    var id = e.currentTarget.dataset.id
    var p = this.data.products.map(function(x) {
      return x.productId === id ? Object.assign({}, x, { _qty: (x._qty || 0) + 1 }) : Object.assign({}, x)
    })
    this.setData({ products: p }, this.updateTotal)
  },

  decQty: function(e) {
    var id = e.currentTarget.dataset.id
    var p = this.data.products.map(function(x) {
      return x.productId === id && x._qty > 0 ? Object.assign({}, x, { _qty: x._qty - 1 }) : Object.assign({}, x)
    })
    this.setData({ products: p }, this.updateTotal)
  },

  updateTotal: function() {
    var t = 0, count = 0, items = []
    for (var i = 0; i < this.data.products.length; i++) {
      var pr = this.data.products[i]
      if (pr._qty > 0) {
        t += pr._qty * pr.price
        count += pr._qty
        items.push({ productId: pr.productId, name: pr.name, price: pr.price, _qty: pr._qty, _subtotal: (pr._qty * pr.price).toFixed(2) })
      }
    }
    this.setData({ total: t.toFixed(2), cartCount: count, cartItems: items })
  },

  showConfirm: function() {
    if (this.data.cartCount === 0) return
    this.setData({ showConfirm: true })
  },

  hideConfirm: function() {
    this.setData({ showConfirm: false })
  },

  preventBubble: function() {},

  submitOrder: function() {
    var items = []
    for (var i = 0; i < this.data.products.length; i++) {
      if (this.data.products[i]._qty > 0) {
        items.push({ productId: this.data.products[i].productId, quantity: this.data.products[i]._qty, unitPrice: this.data.products[i].price })
      }
    }
    if (items.length == 0) { wx.showToast({ title: '请选择商品', icon: 'none' }); return }
    var self = this
    API.createScanOrder({ roomId: this.data.roomId, storeId: 'ST001', items: items }).then(function(r) {
      self.setData({
        showConfirm: false, showSuccess: true,
        successMsg: '共 ' + r.itemCount + ' 件商品，金额 ¥' + r.totalAmount.toFixed(2) + ' 已挂入房间账单',
        products: self.data.products.map(function(x) { return Object.assign({}, x, { _qty: 0 }) }),
        total: 0, cartCount: 0, cartItems: []
      })
    }).catch(function(err) {
      wx.showToast({ title: err.message || '下单失败', icon: 'none' })
    })
  },

  hideSuccess: function() {
    this.setData({ showSuccess: false })
  },

  continueOrder: function() {
    this.setData({ showSuccess: false })
  },

  goToBill: function() {
    wx.navigateTo({ url: '/pages/scan-bill/scan-bill?room_id=' + this.data.roomId })
  }
})
