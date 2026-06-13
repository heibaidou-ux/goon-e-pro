Page({
  data: {
    addresses: [],
    showForm: false, editIdx: -1,
    formName: '', formPhone: '', formDetail: '',
    formProvince: '', formCity: '', formDistrict: '',
    provinceIndex: 0, cityIndex: 0, districtIndex: 0,
    provinces: ['广东省','北京市','上海市','浙江省','江苏省','福建省','四川省','湖北省','湖南省','山东省','河南省','安徽省','河北省','重庆市','陕西省','江西省','辽宁省','天津市','广西区'],
    cities: [], districts: []
  },

  onShow: function() { this.loadAddresses() },

  loadAddresses: function() {
    try { var h = wx.getStorageSync('mp_address_history') || []; this.setData({ addresses: h }) } catch(e) {}
  },

  showAddForm: function() {
    this.setData({
      showForm: true, editIdx: -1,
      formName: '', formPhone: '', formDetail: '',
      formProvince: '', formCity: '', formDistrict: '',
      cities: [], districts: []
    })
  },

  hideForm: function() { this.setData({ showForm: false }) },

  onFormName: function(e) { this.setData({ formName: e.detail.value }) },
  onFormPhone: function(e) { this.setData({ formPhone: e.detail.value }) },
  onFormDetail: function(e) { this.setData({ formDetail: e.detail.value }) },

  _getCities: function(p) {
    var m={'广东省':['广州市','深圳市','珠海市','佛山市','东莞市','中山市'],'北京市':['北京市'],'上海市':['上海市'],'浙江省':['杭州市','宁波市','温州市'],'江苏省':['南京市','苏州市','无锡市'],'福建省':['福州市','厦门市','泉州市'],'四川省':['成都市','绵阳市']}
    return m[p] || ['广州市']
  },

  _getDistricts: function(p, c) {
    if(c==='北京市')return['海淀区','朝阳区','东城区','西城区'];if(c==='上海市')return['浦东新区','静安区','徐汇区'];if(c==='深圳市')return['南山区','福田区','罗湖区'];if(c==='广州市')return['天河区','海珠区','越秀区','荔湾区','白云区','番禺区'];if(c==='杭州市')return['西湖区','上城区','拱墅区']
    return['全区']
  },

  onProvinceChange: function(e) {
    var idx = e.detail.value, p = this.data.provinces[idx]
    var cities = this._getCities(p)
    this.setData({provinceIndex: idx, formProvince: p, cityIndex: 0, districtIndex: 0, cities: cities, districts: [], formCity: '', formDistrict: ''})
    if(cities.length>0){this.setData({formCity: cities[0]}); this.setData({districts: this._getDistricts(p, cities[0]), formDistrict: this._getDistricts(p, cities[0])[0] || ''})}
  },

  onCityChange: function(e) {
    var idx = e.detail.value, c = this.data.cities[idx], d = this._getDistricts(this.data.formProvince, c)
    this.setData({cityIndex: idx, formCity: c, districtIndex: 0, districts: d, formDistrict: d.length>0?d[0]:''})
  },

  onDistrictChange: function(e) {
    this.setData({districtIndex: e.detail.value, formDistrict: this.data.districts[e.detail.value]})
  },

  saveAddr: function() {
    var self = this
    if(!self.data.formName || !self.data.formPhone || !self.data.formProvince || !self.data.formDetail) {
      wx.showToast({ title: '请填写完整信息', icon: 'none' }); return
    }
    var addr = {name: self.data.formName, phone: self.data.formPhone, province: self.data.formProvince, city: self.data.formCity, district: self.data.formDistrict, detail: self.data.formDetail}
    try {
      var h = wx.getStorageSync('mp_address_history') || []
      if(self.data.editIdx >= 0) { h[self.data.editIdx] = addr } else { h.unshift(addr); if(h.length>10) h = h.slice(0,10) }
      wx.setStorageSync('mp_address_history', h)
    } catch(e) {}
    self.setData({ showForm: false })
    self.loadAddresses()
    wx.showToast({ title: '已保存', icon: 'success' })
  },

  deleteAddr: function(e) {
    var self = this, idx = e.currentTarget.dataset.idx
    wx.showModal({
      title: '删除地址', content: '确定删除此地址？',
      success: function(res) { if(res.confirm) {
        try { var h = wx.getStorageSync('mp_address_history') || []; h.splice(idx, 1); wx.setStorageSync('mp_address_history', h); self.loadAddresses() } catch(e) {}
      }}
    })
  },

  goBack: function() { wx.navigateBack() }
})
