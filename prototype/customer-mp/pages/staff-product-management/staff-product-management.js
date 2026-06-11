var API = require('../../utils/api')

Page({
  data: {
    selectedCat: '',
    allProducts: [],
    products: []
  },

  onShow: function() {
    var self = this
    API.getProducts().then(function(products) {
      var list = products.map(function(p) { return Object.assign({}, p, { status: '上架' }) })
      self.setData({ allProducts: list, products: list })
    })
  },

  filterCat: function(e) {
    var cat = e.currentTarget.dataset.cat
    this.setData({ selectedCat: cat })
    if (!cat) {
      this.setData({ products: this.data.allProducts })
    } else {
      this.setData({ products: this.data.allProducts.filter(function(p) { return p.category === cat }) })
    }
  },

  goBack: function() { wx.navigateBack() }
})
