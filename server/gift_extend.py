# 赠送时长功能 — 在续订页面加"店员赠送"选项
f = 'C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/prototype/customer-mp/pages/room-control/room-control.js'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

# 1. 修改showExtend — 加赠送选项
old_show = "showExtend: function() {\n    var self = this\n    var endDate = self._endDate ? new Date(self._endDate) : new Date()\n    self.setData({ extendInfo: '当前将于 ' + String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0') + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })\n    var options = []\n    for (var i = 1; i <= 24; i++) {\n      var nd = new Date(endDate.getTime() + i * 30 * 60000)\n      options.push({ label: '至 ' + String(nd.getHours()).padStart(2,'0') + ':' + String(nd.getMinutes()).padStart(2,'0'), minutes: i * 30, price: Math.round(120 * i * 30 / 60) })\n    }\n    self.setData({ extendOptions: options, showExtendModal: true })\n  },"

new_show = "showExtend: function() {\n    var self = this\n    var endDate = self._endDate ? new Date(self._endDate) : new Date()\n    self.setData({ extendInfo: '当前将于 ' + String(endDate.getHours()).padStart(2,'0') + ':' + String(endDate.getMinutes()).padStart(2,'0') + ' 结束。请选择续订时长：', selectedExtendIdx: -1 })\n    var options = []\n    options.push({ label: '🎁 店员赠送(30分)', minutes: 30, price: 0, isGift: true })\n    options.push({ label: '🎁 店员赠送(1小时)', minutes: 60, price: 0, isGift: true })\n    options.push({ label: '🎁 店员赠送(2小时)', minutes: 120, price: 0, isGift: true })\n    for (var i = 1; i <= 24; i++) {\n      var nd = new Date(endDate.getTime() + i * 30 * 60000)\n      options.push({ label: '至 ' + String(nd.getHours()).padStart(2,'0') + ':' + String(nd.getMinutes()).padStart(2,'0'), minutes: i * 30, price: Math.round(120 * i * 30 / 60) })\n    }\n    self.setData({ extendOptions: options, showExtendModal: true })\n  },"

if old_show in c:
    c = c.replace(old_show, new_show)
    print('OK: showExtend updated')
else:
    print('ERROR: showExtend not found')

# 2. 修改confirmExtend — 赠送跳过支付
old_confirm = "confirmExtend: function() {\n    var idx = this.data.selectedExtendIdx\n    if (idx < 0 || idx >= this.data.extendOptions.length) return\n    var opt = this.data.extendOptions[idx], self = this\n    API.getBalance().then(function(b) { self.setData({ balance: b || 0, extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''), extendPayAmount: opt.price, extendPayMethod: 'balance', showExtendModal: false, showExtendPayModal: true }) })\n  },"

new_confirm = "confirmExtend: function() {\n    var idx = this.data.selectedExtendIdx\n    if (idx < 0 || idx >= this.data.extendOptions.length) return\n    var opt = this.data.extendOptions[idx], self = this\n    if (opt.price === 0) {\n      wx.showModal({ title: '赠送确认', content: '确认为客人赠送' + opt.minutes + '分钟？', success: function(r) { if (r.confirm) self._applyExtend(opt, 'gift') } })\n      return\n    }\n    API.getBalance().then(function(b) { self.setData({ balance: b || 0, extendPayInfo: '续订' + opt.minutes + '分钟至 ' + opt.label.replace('至 ',''), extendPayAmount: opt.price, extendPayMethod: 'balance', showExtendModal: false, showExtendPayModal: true }) })\n  },"

if old_confirm in c:
    c = c.replace(old_confirm, new_confirm)
    print('OK: confirmExtend updated')
else:
    print('ERROR: confirmExtend not found')

# 3. 抽离_applyExtend方法
old_do = "doExtendPayment: function() {\n    var self = this, idx = this.data.selectedExtendIdx\n    if (idx < 0 || idx >= this.data.extendOptions.length) return\n    var opt = this.data.extendOptions[idx], method = this.data.extendPayMethod\n    var p = function() {\n      self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60\n      self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })\n      if (self._endDate) { self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000); self.setData({ endTime: String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0') }) }\n      try { var bk = wx.getStorageSync('mp_bookings') || []; for (var i = 0; i < bk.length; i++) { if (bk[i].roomId === self.data.roomId && bk[i].status === 'InUse') { bk[i].endTime = String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0'); break } }; wx.setStorageSync('mp_bookings', bk) } catch(e) {}\n      self._updateSlot(); self.setData({ showExtendPayModal: false }); wx.showToast({ title: '续订成功！已支付 ¥' + opt.price, icon: 'success' })\n    }\n    if (method === 'balance') {\n      API.getBalance().then(function(bal) { if (bal < opt.price) { wx.showToast({ title: '余额不足，请选择其他方式', icon: 'none' }); return }; var u = wx.getStorageSync('mp_user') || {}; u.balance = bal - opt.price; wx.setStorageSync('mp_user', u); self.setData({ balance: u.balance }); p() })\n    } else { wx.showLoading({ title: '支付中...' }); setTimeout(function() { wx.hideLoading(); p() }, 800) }\n  },"

new_do = "doExtendPayment: function() {\n    var self = this, idx = this.data.selectedExtendIdx\n    if (idx < 0 || idx >= this.data.extendOptions.length) return\n    var opt = this.data.extendOptions[idx], method = this.data.extendPayMethod\n    self._applyExtend(opt, method)\n  },\n\n  _applyExtend: function(opt, method) {\n    var self = this\n    var isGift = (opt.price === 0)\n    if (!isGift && method === 'balance') {\n      API.getBalance().then(function(bal) {\n        if (bal < opt.price) { wx.showToast({ title: '余额不足', icon: 'none' }); return }\n        var u = wx.getStorageSync('mp_user') || {}; u.balance = bal - opt.price; wx.setStorageSync('mp_user', u); self.setData({ balance: u.balance })\n        self._extendCountdown(opt, method)\n      })\n      return\n    }\n    if (!isGift && method !== 'gift') {\n      wx.showLoading({ title: '支付中...' })\n      setTimeout(function() { wx.hideLoading(); self._extendCountdown(opt, method) }, 800)\n      return\n    }\n    self._extendCountdown(opt, 'gift')\n  },\n\n  _extendCountdown: function(opt, method) {\n    var self = this\n    self._countdownTotal = (self._countdownTotal || 0) + opt.minutes * 60\n    self.setData({ countdown: self._fmtCountdown(self._countdownTotal) })\n    if (self._endDate) {\n      self._endDate = new Date(self._endDate.getTime() + opt.minutes * 60000)\n      self.setData({ endTime: String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0') })\n    }\n    try {\n      var bk = wx.getStorageSync('mp_bookings') || []\n      for (var i = 0; i < bk.length; i++) {\n        if (bk[i].roomId === self.data.roomId && bk[i].status === 'InUse') {\n          bk[i].endTime = String(self._endDate.getHours()).padStart(2,'0') + ':' + String(self._endDate.getMinutes()).padStart(2,'0')\n          break\n        }\n      }\n      wx.setStorageSync('mp_bookings', bk)\n    } catch(e) {}\n    self._updateSlot()\n    self.setData({ showExtendPayModal: false })\n    var title = method === 'gift' ? '🎁 赠送成功！已延长' + opt.minutes + '分钟' : '续订成功！¥' + opt.price\n    wx.showToast({ title: title, icon: 'success' })\n  },"

if old_do in c:
    c = c.replace(old_do, new_do)
    print('OK: _applyExtend and _extendCountdown added')
else:
    print('ERROR: doExtendPayment not found')

open(f, 'w', encoding='utf-8').write(c)
print('Done')
