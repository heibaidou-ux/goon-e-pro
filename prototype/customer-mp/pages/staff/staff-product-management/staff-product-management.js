var API = require('../../../utils/api')

Page({
  data: {
    selectedCat: '',
    allProducts: [],
    products: [],
    stats: { total: 0, onShelf: 0, lowStock: 0 },
    showStockModal: false, stockProduct: null, stockQty: 0,
    showTransferModal: false, transferProduct: null,
    transferReason: '', transferQty: 1,
    transferLog: []
  },

  onShow: function() {
    this.loadProducts()
    this.loadTransferLog()
  },

  loadProducts: function() {
    var self = this
    API.getProducts().then(function(products) {
      var list = products.map(function(p) {
        return Object.assign({}, p, {
          status: '上架',
          stock: Math.floor(Math.random() * 50) + 5,
          lowStock: Math.floor(Math.random() * 10) === 0
        })
      })
      var onShelf = 0, lowStock = 0
      for (var i = 0; i < list.length; i++) {
        if (list[i].status === '上架') onShelf++
        if (list[i].lowStock) lowStock++
      }
      self.setData({
        allProducts: list, products: list,
        stats: { total: list.length, onShelf: onShelf, lowStock: lowStock }
      })
    })
  },

  loadTransferLog: function() {
    try { var log = wx.getStorageSync('mp_stock_transfers') || []; this.setData({ transferLog: log }) } catch(e) {}
  },

  filterCat: function(e) {
    var cat = e.currentTarget.dataset.cat
    this.setData({ selectedCat: cat })
    if (!cat) this.setData({ products: this.data.allProducts })
    else this.setData({ products: this.data.allProducts.filter(function(p) { return p.category === cat }) })
  },

  // ── 上架/下架 ──
  toggleStatus: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.products
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === id || products[i].id === id) {
        products[i].status = products[i].status === '上架' ? '下架' : '上架'
        break
      }
    }
    this.setData({ products: products })
    wx.showToast({ title: '状态已更新', icon: 'success' })
  },

  // ── 盘点 ──
  showStock: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.products
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === id || products[i].id === id) {
        this.setData({ showStockModal: true, stockProduct: products[i], stockQty: products[i].stock || 0 })
        break
      }
    }
  },

  onStockQty: function(e) { this.setData({ stockQty: parseInt(e.detail.value) || 0 }) },

  saveStock: function() {
    var self = this
    var p = self.data.stockProduct
    if (!p) return
    var products = self.data.allProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === p.productId || products[i].id === p.id) {
        products[i].stock = self.data.stockQty
        break
      }
    }
    self.setData({ allProducts: products, showStockModal: false })
    self.filterCat({ currentTarget: { dataset: { cat: self.data.selectedCat } } })
    wx.showToast({ title: '盘点已更新', icon: 'success' })
  },

  hideStockModal: function() { this.setData({ showStockModal: false }) },

  // ── 调货申请 ──
  showTransfer: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.products
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === id || products[i].id === id) {
        this.setData({ showTransferModal: true, transferProduct: products[i], transferQty: 1, transferReason: '' })
        break
      }
    }
  },

  onTransferQty: function(e) { this.setData({ transferQty: parseInt(e.detail.value) || 1 }) },
  onTransferReason: function(e) { this.setData({ transferReason: e.detail.value }) },

  confirmTransfer: function() {
    var self = this
    var p = self.data.transferProduct
    if (!p || !self.data.transferReason) { wx.showToast({ title: '请填写调货原因', icon: 'none' }); return }
    var log = self.data.transferLog
    log.unshift({
      id: 'TR' + String(Date.now()).slice(-6),
      productName: p.name,
      qty: self.data.transferQty,
      reason: self.data.transferReason,
      from: '盈隆店',
      status: '待审批',
      time: new Date().toLocaleString()
    })
    try { wx.setStorageSync('mp_stock_transfers', log) } catch(e) {}
    self.setData({ showTransferModal: false, transferLog: log })
    wx.showToast({ title: '调货申请已提交', icon: 'success' })
  },

  hideTransferModal: function() { this.setData({ showTransferModal: false }) },

  goBack: function() { wx.navigateBack() }
})
