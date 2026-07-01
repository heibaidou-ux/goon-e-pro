import re

f = 'C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/prototype/customer-mp/pages/room-control/room-control.js'
with open(f, encoding='utf-8') as fh:
    c = fh.read()

old_marker = "loadDevices: function() {"
idx = c.find(old_marker)
if idx < 0:
    print("ERROR: loadDevices not found")
    exit(1)

rest = c[idx:]
match = re.search(r'\n  },\n\s+\w+', rest)
if not match:
    print("ERROR: end boundary not found")
    exit(1)

end_pos = idx + match.start() + 1
old_func = c[idx:end_pos]
print(f"Found loadDevices, length={len(old_func)}")

new_func = """loadDevices: function() {
    var self = this
    var roomId = self.data.roomId

    API.getRoomDevices(roomId).then(function(apiDevices) {
      if (!apiDevices || apiDevices.length === 0) {
        self._renderLocalDevices(roomId)
        return
      }
      var ac = null, curtains = [], bgm = null
      var devKeys = [{ key: 'light_all_on', label: '灯全开', icon: '\\U0001f506', type: 'virtual', active: false },
                     { key: 'light_all_off', label: '灯全关', icon: '\\U0001f505', type: 'virtual', active: false }]
      for (var i = 0; i < apiDevices.length; i++) {
        var d = apiDevices[i], a = d.attributes || {}
        if (d.type === 'AC') {
          ac = { deviceId: d.deviceId, name: d.name, mode: a.mode || 'off', temperature: a.target_temperature || a.temperature || 24 }
        } else if (d.type === 'Curtain') {
          var pos = a.current_position !== undefined ? a.current_position : (a.position === 'open' ? 100 : 0)
          curtains.push({ deviceId: d.deviceId, name: d.name || '\\u7a97\\u5e18', positionNum: pos })
        } else if (d.type === 'Light') {
          devKeys.push({ key: d.deviceId, label: d.name || '\\u706f\\u5149', icon: '\\U0001f4a1', type: 'Light', active: !!(a.power || a.brightness > 0), deviceId: d.deviceId })
        } else if (d.type === 'Fan' || d.type === 'ExhaustFan') {
          devKeys.push({ key: d.deviceId, label: d.name || '\\u98ce\\u6247', icon: '\\u23e3', type: d.type, active: !!(a.speed > 0 || a.power), deviceId: d.deviceId })
        } else if (d.type === 'Speaker' || d.type === 'BGM') {
          bgm = { deviceId: d.deviceId, playing: a.playing || false, volume: a.volume || 30 }
        }
      }
      self.setData({ devKeys: devKeys, acDevice: ac, acModeLabel: ac ? self._acModeLabel(ac.mode) : '\\u5df2\\u5173\\u673a', curtainDevices: curtains, bgmDevice: bgm })
      try { wx.setStorageSync('room_devices_' + roomId, { devKeys: devKeys, acDevice: ac, curtains: curtains, bgm: bgm }) } catch(e) {}
    }).catch(function() {
      self._renderLocalDevices(roomId)
    })
  },

  _renderLocalDevices: function(roomId) {
    var self = this
    try {
      var cached = wx.getStorageSync('room_devices_' + roomId)
      if (cached && cached.devKeys) {
        self.setData({ devKeys: cached.devKeys, acDevice: cached.acDevice, acModeLabel: cached.acDevice ? self._acModeLabel(cached.acDevice.mode) : '\\u5df2\\u5173\\u673a', curtainDevices: cached.curtains || [], bgmDevice: cached.bgm || null })
        return
      }
    } catch(e) {}
    var devices = self._getRoomDevices('TeaRoom')
    var ac = null, curtains = [], bgm = null
    var devKeys = [{ key: 'light_all_on', label: '\\u706f\\u5168\\u5f00', icon: '\\U0001f506', type: 'virtual', active: false },
                   { key: 'light_all_off', label: '\\u706f\\u5168\\u5173', icon: '\\U0001f505', type: 'virtual', active: false }]
    for (var i = 0; i < devices.length; i++) {
      var d = devices[i]
      if (d.type === 'AC') { ac = { deviceId: roomId+'_ac', name: d.name, mode: 'off', temperature: 24 }; continue }
      if (d.type === 'Curtain') { curtains.push({ deviceId: d.id, name: d.name, positionNum: 0 }); continue }
      if (d.type === 'Speaker') { bgm = { deviceId: d.id, playing: false, volume: 30 }; continue }
      if (d.type === 'Light') { devKeys.push({ key: d.id, label: d.name, icon: '\\U0001f4a1', type: 'Light', active: false }) }
      if (d.type === 'Fan' || d.type === 'ExhaustFan') { devKeys.push({ key: d.id, label: d.name, icon: '\\u23e3', type: d.type, active: false }) }
    }
    self.setData({ devKeys: devKeys, acDevice: ac, acModeLabel: ac ? self._acModeLabel(ac.mode) : '\\u5df2\\u5173\\u673a', curtainDevices: curtains, bgmDevice: bgm })
  },"""

c = c[:idx] + new_func + c[end_pos:]
with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print("OK: loadDevices rewritten")
