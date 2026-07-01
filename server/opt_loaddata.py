import re

f = r'C:\Users\王晓东\Documents\高岸管理\盈隆\高岸智能管理系统\高岸ERP\prototype\customer-mp\pages\home\home.js'
with open(f, encoding='utf-8') as fh:
    c = fh.read()

# Find the loadData function and replace it
old_marker = "loadData: function() {"
idx = c.find(old_marker)
if idx < 0:
    print("ERROR: loadData not found")
    exit(1)

# Find the next top-level function after loadData
rest = c[idx:]
# Find the position of the next "}," that ends loadData and starts next function
# Look for "}," followed by newline and space and a word character
next_func = re.search(r'\},\n\s+\w+:', rest)
if not next_func:
    print("ERROR: next function not found")
    exit(1)

new_func = """loadData: function() {
    var self = this
    // 立刻展示localStorage缓存（秒开）
    try {
      var cached = wx.getStorageSync('home_cache')
      if (cached && cached.rooms && cached.teas) {
        self.setData({ rooms: cached.rooms, teaProducts: cached.teas })
      }
    } catch(e) {}
    // 读取用户微信信息
    var u = API.getCurrentUser()
    self.setData({ wxNickname: (u&&(u.wechat_nickname||u.display_name||u.name))||'', wxAvatar: (u&&u.wechat_avatar)||'', loading: false, errorMsg: '' })
    try { var v = wx.getStorageSync('balance_visible'); if (v !== '') self.data.balanceVisible = v } catch(e) {}
    var colors = { MeetingRoom:'#e3f2fd', TeaRoom:'#e8f5e9', Exhibition:'#fff3e0', Workspace:'#f5f5f5' }
    var icons = { MeetingRoom:'\\U0001f4bc', TeaRoom:'\\U0001f375', Exhibition:'\\U0001f3db', Workspace:'\\U0001f527' }

    // 第1批：房间列表（最快，1个请求即可渲染首页主体）
    API.getRooms(true).then(function(list) {
      if (!list || !list.length) { self.renderFallbackData(); return }
      var rooms = []
      for (var i = 0; i < list.length; i++) {
        var r = list[i]; if (r.bookable === false) continue
        rooms.push({ roomId:r.roomId, name:r.name, capacity:r.capacity, area:r.area, pricePerHour:r.pricePerHour||120, icon:icons[r.type]||'\\U0001f3e0', bgColor:colors[r.type]||'#f0f0f0' })
      }
      self.setData({ rooms: rooms })
      try { var cache = wx.getStorageSync('home_cache') || {}; cache.rooms = rooms; wx.setStorageSync('home_cache', cache) } catch(e) {}
    }).catch(function() { self.renderFallbackData() })

    // 第2批：茶品列表（不阻塞页面渲染）
    API.getProducts().then(function(productsData) {
      if (!productsData || !productsData.length) return
      var visualMap = { 'T001':{icon:'\\U0001f343',bg:'#e8f5e9'},'T002':{icon:'\\U0001fab5',bg:'#fce4ec'},'T003':{icon:'\\U0001f3d4',bg:'#fff3e0'},'T004':{icon:'\\U0001f33f',bg:'#efebe9'},'T005':{icon:'\\U0001f3f5',bg:'#f1f8e9'},'T006':{icon:'\\U0001f3d4',bg:'#efebe9'},'T007':{icon:'\\U0001f3fa',bg:'#f3e5f5'},'T008':{icon:'\\U0001f943',bg:'#e0f7fa'},'T01':{icon:'\\U0001f343',bg:'#e8f5e9'},'T02':{icon:'\\U0001fab5',bg:'#fce4ec'},'T03':{icon:'\\U0001f3d4',bg:'#fff3e0'},'T04':{icon:'\\U0001f3fa',bg:'#f3e5f5'},'T05':{icon:'\\U0001f3d4',bg:'#efebe9'},'T06':{icon:'\\U0001f33f',bg:'#e0f7fa'},'T07':{icon:'\\U0001f3f5',bg:'#f1f8e9'},'T08':{icon:'\\U0001f943',bg:'#fce4ec'} }
      var qtyMap = {}
      try { var cart = wx.getStorageSync('mp_tea_cart') || []; for (var i = 0; i < cart.length; i++) { qtyMap[cart[i].productId] = cart[i].qty || 1 } } catch(e) {}
      var teas = []
      for (var i = 0; i < productsData.length; i++) {
        var t = productsData[i], vis = visualMap[t.productId] || {icon:'\\U0001f375',bg:'#f0f0f0'}
        teas.push({ productId:t.productId, name:t.name, desc:t.desc||'', price:t.price, icon:vis.icon, bg:vis.bg, _qty:qtyMap[t.productId]||0 })
      }
      self.setData({ teaProducts: teas })
      try { var cache = wx.getStorageSync('home_cache') || {}; cache.teas = teas; wx.setStorageSync('home_cache', cache) } catch(e) {}
    }).catch(function() {})

    // 余额+购物车数量（后台刷新）
    API.getBalance().then(function(b) {
      self.setData({ balance: b || 0 })
      self.setData({ balanceDisplay: self.data.balanceVisible ? '\\U0000a5'+(b||0) : '****' })
    }).catch(function() {})
    API.getCart().then(function(c) {
      var total = 0; for (var i = 0; i < (c||[]).length; i++) { total += (c[i].qty||1) }
      self.setData({ cartCount: total })
    }).catch(function() {})
  },"""

new_str = new_func
c = c[:idx] + new_str + c[idx + next_func.start():]
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print("OK: loadData rewritten for 3-stage loading")
