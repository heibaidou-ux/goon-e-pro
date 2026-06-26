Page({
  data: {},
  onLoad: function() {},
  goBack: function() { wx.navigateBack() },
  openNavigation: function() {
    wx.openLocation({
      latitude: 23.1275,
      longitude: 113.3220,
      name: '高岸·花城广场店',
      address: '广州市天河区珠江新城富力盈隆广场3801',
      scale: 18
    })
  }
})
