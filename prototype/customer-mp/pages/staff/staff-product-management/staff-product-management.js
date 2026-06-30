var API = require('../../../utils/api')

Page({
  data: {
    selectedCat: '',
    isLowFilter: false,
    allProducts: [],
    products: [],
    stats: { total: 0, onShelf: 0, lowStock: 0 },
    showStockModal: false, stockProduct: null, stockQty: 0,
    showTransferModal: false, transferProduct: null,
    transferReason: '', transferQty: 1,
    transferLog: [],
    showShelfModal: false, shelfProduct: null, shelfQty: 1,
    showDiscrepancyModal: false, discrepancyInfo: ''
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
          status: Math.random() > 0.3 ? '上架' : '下架',
          stock: Math.floor(Math.random() * 50) + 1,
          lowStock: Math.floor(Math.random() * 5) === 0,
          unit: '件'
        })
      })
      var onShelf = 0, lowStock = 0, totalQty = 0
      for (var i = 0; i < list.length; i++) {
        if (list[i].status === '上架') onShelf++
        if (list[i].lowStock) lowStock++
        totalQty += list[i].stock || 0
      }
      self.setData({
        allProducts: list, products: list,
        stats: { total: list.length, onShelf: onShelf, lowStock: lowStock, totalQty: totalQty, onShelfQty: totalQty }
      })
    })
  },

  loadTransferLog: function() {
    try { var log = wx.getStorageSync('mp_stock_transfers') || []; this.setData({ transferLog: log }) } catch(e) {}
  },

  filterCat: function(e) {
    var cat = e.currentTarget.dataset.cat
    this.setData({ selectedCat: cat, isLowFilter: false })
    this._applyFilters()
  },

  filterLowStock: function() {
    this.setData({ isLowFilter: !this.data.isLowFilter, selectedCat: '' })
    this._applyFilters()
  },

  _applyFilters: function() {
    var list = this.data.allProducts
    if (this.data.selectedCat) list = list.filter(function(p) { return p.category === this.data.selectedCat }.bind(this))
    if (this.data.isLowFilter) list = list.filter(function(p) { return p.lowStock })
    this.setData({ products: list })
  },

  // ── 上架（强制输入数量）──
  showShelfForm: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.allProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === id || products[i].id === id) {
        this.setData({ showShelfModal: true, shelfProduct: products[i], shelfQty: 1 })
        break
      }
    }
  },
  onShelfQty: function(e) { this.setData({ shelfQty: parseInt(e.detail.value) || 1 }) },
  confirmShelf: function() {
    var self = this
    var p = self.data.shelfProduct; if (!p || !self.data.shelfQty) return
    var products = self.data.allProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === p.productId || products[i].id === p.id) {
        products[i].status = '上架'; products[i].stock = (products[i].stock || 0) + self.data.shelfQty; break
      }
    }
    self.setData({ allProducts: products, showShelfModal: false }); self._applyFilters()
    wx.showToast({ title: '已上架 +' + self.data.shelfQty, icon: 'success' })
  },
  hideShelfModal: function() { this.setData({ showShelfModal: false }) },
  // ── 下架 ──
  unshelf: function(e) {
    var id = e.currentTarget.dataset.id; var products = this.data.allProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === id || products[i].id === id) { products[i].status = '下架'; break }
    }
    this.setData({ allProducts: products }); this._applyFilters()
    wx.showToast({ title: '已下架', icon: 'success' })
  },

  // ── 盘点 ──
  showStock: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.allProducts
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
    var oldStock = p.stock
    var newStock = self.data.stockQty

    if (oldStock !== newStock) {
      // 生成对账工单
      var discrepancy = {
        type: '盘点差异',
        productName: p.name,
        oldQty: oldStock, newQty: newStock,
        diff: newStock - oldStock,
        reason: '',
        status: '待审核', time: new Date().toLocaleString()
      }
      var discList = []
      try { discList = wx.getStorageSync('mp_stock_discrepancies') || [] } catch(e) {}
      discList.unshift(discrepancy)
      try { wx.setStorageSync('mp_stock_discrepancies', discList) } catch(e) {}
      self.setData({ discrepancyInfo: '盘点差异：' + oldStock + '→' + newStock + '，差异' + (newStock - oldStock > 0 ? '+' : '') + (newStock - oldStock) + '，已生成对账工单，待店长审核',
      showDiscrepancyModal: true })
    }

    var products = self.data.allProducts
    for (var i = 0; i < products.length; i++) {
      if (products[i].productId === p.productId || products[i].id === p.id) {
        products[i].stock = newStock
        products[i].lowStock = newStock < 10
        break
      }
    }
    self.setData({ allProducts: products, showStockModal: false })
    self._applyFilters()
    wx.showToast({ title: '盘点完成', icon: 'success' })
  },

  hideStockModal: function() { this.setData({ showStockModal: false }) },

  // ── 调货申请 ──
  showTransfer: function(e) {
    var id = e.currentTarget.dataset.id
    var products = this.data.allProducts
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
      productName: p.name, qty: self.data.transferQty,
      reason: self.data.transferReason,
      from: '总部仓库', status: '待总部确认', to: '盈隆店',
      time: new Date().toLocaleString()
    })
    try { wx.setStorageSync('mp_stock_transfers', log) } catch(e) {}
    self.setData({ showTransferModal: false, transferLog: log })
    wx.showToast({ title: '调货申请已提交，等待总部确认', icon: 'success' })
  },

  hideTransferModal: function() { this.setData({ showTransferModal: false }) },
  closeDiscrepancy: function() { this.setData({ showDiscrepancyModal: false }) },

  goBack: function() { wx.navigateBack() }
})
