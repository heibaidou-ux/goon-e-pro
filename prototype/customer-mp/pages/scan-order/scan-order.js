var API = require('../../utils/api')

Page({
  data: { roomId: '', roomName: '', products: [], filteredProducts: [], currentCat: '', cartCount: 0, cartTotal: 0, total: 0 },

  onLoad: function(e) {
    var roomId = e.room_id || ''
    this.setData({ roomId: roomId })
    var self = this
    if (roomId) {
      API.scanRoomStatus(roomId).then(function(info) { self.setData({ roomName: info.roomName }) }).catch(function(){})
    }
    API.getProducts().then(function(products) {
      var p = products.map(function(x) { return { productId: x.productId, name: x.name, price: x.price, desc: x.desc || '', _qty: 0 } })
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
    var p = this.data.products.map(function(x) { return x.productId === id ? { productId: x.productId, name: x.name, price: x.price, desc: x.desc, _qty: (x._qty || 0) + 1 } : x })
    this.setData({ products: p }, this.updateTotal)
  },

  decQty: function(e) {
    var id = e.currentTarget.dataset.id
    var p = this.data.products.map(function(x) { return x.productId === id && x._qty > 0 ? { productId: x.productId, name: x.name, price: x.price, desc: x.desc, _qty: x._qty - 1 } : x })
    this.setData({ products: p }, this.updateTotal)
  },

  updateTotal: function() {
    var t = 0
    for (var i = 0; i < this.data.products.length; i++) { t += (this.data.products[i]._qty || 0) * this.data.products[i].price }
    this.setData({ total: t.toFixed(2) })
  },

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
      wx.showToast({ title: '✅ 加购成功，已挂入账单', icon: 'success' })
      self.setData({ products: self.data.products.map(function(x) { return { productId: x.productId, name: x.name, price: x.price, desc: x.desc, _qty: 0 } }), total: 0 })
    }).catch(function(err) {
      wx.showToast({ title: err.message || '下单失败', icon: 'none' })
    })
  }
})
