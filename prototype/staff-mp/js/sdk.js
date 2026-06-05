/**
 * 高岸ERP 店员端 SDK — Mock数据层 + API接口
 * 与客人端(customer-mp/js/sdk.js)共享同一数据模型和localStorage前缀，
 * 确保两端数据互通。
 *
 * 切换为真实API: localStorage.setItem('staff_use_api', 'true')
 */
(function(win) {
  'use strict';

  // ── 桌面端手机模拟样式：限制宽度+居中 ──
  if (win.innerWidth > 640) {
    var ds = document.createElement('style');
    ds.textContent = 'body{background:#e8e8e8!important;display:flex;justify-content:center}.phone{' +
      'max-width:430px!important;margin:0 auto;box-shadow:0 0 32px rgba(0,0,0,.15);min-height:100vh;' +
      'border-radius:0}@media(min-height:700px){.phone{margin:24px auto;min-height:calc(100vh - 48px);' +
      'border-radius:20px;overflow:hidden}}';
    document.head.appendChild(ds);
  }

  // ═══════════════════════════════════════════
  //  1. 内嵌Mock数据（与customer-mp一致）
  // ═══════════════════════════════════════════

  var MOCK = {};

  MOCK.stores = [{
    storeId: "ST001", name: "盈隆店", address: "广州珠江新城盈隆广场",
    phone: "020-88888888", status: "Active"
  }];

  MOCK.rooms = [
    { roomId: "RM001", name: "大会议室", type: "MeetingRoom", capacity: 10, area: 30,
      facilities: ["投影","会议桌","K歌设备","落地窗"], pricePerHour: 200, pricePerHalfHour: 120, status: "Active", bookable: true },
    { roomId: "RM002", name: "中茶室A", type: "TeaRoom", capacity: 4, area: 18,
      facilities: ["茶台","落地窗","茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
    { roomId: "RM003", name: "中茶室B", type: "TeaRoom", capacity: 4, area: 18,
      facilities: ["茶台","落地窗","茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
    { roomId: "RM004", name: "大茶室C", type: "TeaRoom", capacity: 6, area: 25,
      facilities: ["茶台","K歌","投影","落地窗"], pricePerHour: 120, pricePerHalfHour: 75, status: "Active", bookable: true },
    { roomId: "RM005", name: "展厅", type: "Exhibition", capacity: 20, area: 40,
      facilities: ["前台","收银","茶具展示","休闲区"], status: "Active", bookable: false },
    { roomId: "RM006", name: "工作间", type: "Workspace", capacity: 2, area: 12,
      facilities: ["储物","机柜"], status: "Active", bookable: false }
  ];

  MOCK.devices = [
    { deviceId:"DEV001", roomId:"RM001", type:"Lock",     protocol:"Zigbee", status:"Online", batteryLevel:85 },
    { deviceId:"DEV002", roomId:"RM001", type:"AC",       protocol:"RS485",  status:"Online", temperature:24, mode:"cool" },
    { deviceId:"DEV003", roomId:"RM001", type:"Light",    protocol:"RS485",  status:"Online", brightness:80, colorTemp:4000 },
    { deviceId:"DEV004", roomId:"RM001", type:"Light",    protocol:"RS485",  status:"Online", brightness:80, colorTemp:4000 },
    { deviceId:"DEV005", roomId:"RM001", type:"Curtain",  protocol:"RS485",  status:"Online", position:"closed" },
    { deviceId:"DEV006", roomId:"RM001", type:"Speaker",  protocol:"IP",     status:"Online", volume:70, playing:true, source:"bgm" },
    { deviceId:"DEV007", roomId:"RM001", type:"Speaker",  protocol:"IP",     status:"Online", volume:70, playing:true, source:"bgm" },
    { deviceId:"DEV008", roomId:"RM002", type:"Lock",     protocol:"Zigbee", status:"Offline", batteryLevel:0 },
    { deviceId:"DEV009", roomId:"RM002", type:"AC",       protocol:"RS485",  status:"Online", temperature:26, mode:"cool" },
    { deviceId:"DEV010", roomId:"RM002", type:"Light",    protocol:"RS485",  status:"Online", brightness:60, colorTemp:3000 },
    { deviceId:"DEV011", roomId:"RM002", type:"Light",    protocol:"RS485",  status:"Online", brightness:60, colorTemp:3000 },
    { deviceId:"DEV012", roomId:"RM002", type:"Curtain",  protocol:"RS485",  status:"Online", position:"closed" },
    { deviceId:"DEV013", roomId:"RM002", type:"Speaker",  protocol:"IP",     status:"Online", volume:50, playing:false, source:"bgm" },
    { deviceId:"DEV014", roomId:"RM003", type:"Lock",     protocol:"Zigbee", status:"Online", batteryLevel:92 },
    { deviceId:"DEV015", roomId:"RM003", type:"AC",       protocol:"RS485",  status:"Online", temperature:26, mode:"off" },
    { deviceId:"DEV016", roomId:"RM003", type:"Light",    protocol:"RS485",  status:"Online", brightness:0, colorTemp:3000 },
    { deviceId:"DEV017", roomId:"RM003", type:"Light",    protocol:"RS485",  status:"Online", brightness:0, colorTemp:3000 },
    { deviceId:"DEV018", roomId:"RM003", type:"Curtain",  protocol:"RS485",  status:"Online", position:"open" },
    { deviceId:"DEV019", roomId:"RM003", type:"Speaker",  protocol:"IP",     status:"Online", volume:0, playing:false, source:"bgm" },
    { deviceId:"DEV020", roomId:"RM004", type:"Lock",     protocol:"Zigbee", status:"Online", batteryLevel:73 },
    { deviceId:"DEV021", roomId:"RM004", type:"AC",       protocol:"RS485",  status:"Online", temperature:24, mode:"cool" },
    { deviceId:"DEV022", roomId:"RM004", type:"Light",    protocol:"RS485",  status:"Online", brightness:80, colorTemp:3000 },
    { deviceId:"DEV023", roomId:"RM004", type:"Light",    protocol:"RS485",  status:"Online", brightness:80, colorTemp:3000 },
    { deviceId:"DEV024", roomId:"RM004", type:"Light",    protocol:"RS485",  status:"Online", brightness:80, colorTemp:3000 },
    { deviceId:"DEV025", roomId:"RM004", type:"Curtain",  protocol:"RS485",  status:"Online", position:"open" },
    { deviceId:"DEV026", roomId:"RM004", type:"Speaker",  protocol:"IP",     status:"Online", volume:70, playing:true, source:"bgm" },
    { deviceId:"DEV027", roomId:"RM005", type:"AC",       protocol:"RS485",  status:"Online", temperature:26, mode:"cool" },
    { deviceId:"DEV028", roomId:"RM005", type:"Light",    protocol:"RS485",  status:"Online", brightness:90, colorTemp:4000 },
    { deviceId:"DEV029", roomId:"RM005", type:"Light",    protocol:"RS485",  status:"Online", brightness:90, colorTemp:4000 },
    { deviceId:"DEV030", roomId:"RM005", type:"Light",    protocol:"RS485",  status:"Online", brightness:90, colorTemp:4000 },
    { deviceId:"DEV031", roomId:"RM005", type:"Light",    protocol:"RS485",  status:"Online", brightness:90, colorTemp:4000 },
    { deviceId:"DEV032", roomId:"RM005", type:"Speaker",  protocol:"IP",     status:"Online", volume:50, playing:true, source:"bgm" },
    { deviceId:"DEV033", roomId:"RM005", type:"Speaker",  protocol:"IP",     status:"Online", volume:50, playing:true, source:"bgm" },
    { deviceId:"DEV034", roomId:"RM006", type:"Light",    protocol:"RS485",  status:"Online", brightness:50, colorTemp:4000 }
  ];

  MOCK.deviceTypes = {
    Lock:    { label:"门锁",   icon:"🔒" },
    AC:      { label:"空调",   icon:"❄️" },
    Light:   { label:"灯光",   icon:"💡" },
    Curtain: { label:"窗帘",   icon:"🪟" },
    Speaker: { label:"音响",   icon:"🔊" },
    Sensor:  { label:"传感器", icon:"📡" }
  };

  MOCK.scenes = [
    { sceneId:"SC001", name:"迎宾模式",   icon:"👋", color:"#07c160",
      params:{ curtain:"open", lights:{ on:true, brightness:90, colorTemp:4000 }, ac:{ on:true, temp:24 }, music:{ on:true, track:"bgm_welcome" }}},
    { sceneId:"SC002", name:"茶艺模式",   icon:"🍵", color:"#e37318",
      params:{ curtain:"open", lights:{ on:true, brightness:70, colorTemp:3000 }, ac:{ on:true, temp:26 }, music:{ on:true, track:"bgm_tea" }}},
    { sceneId:"SC003", name:"会议模式",   icon:"💼", color:"#0052d9",
      params:{ curtain:"closed", lights:{ on:true, brightness:100, colorTemp:5000 }, ac:{ on:true, temp:22 }}},
    { sceneId:"SC004", name:"娱乐模式",   icon:"🎤", color:"#9c27b0",
      params:{ curtain:"closed", lights:{ on:true, brightness:60, colorTemp:2500 }, ac:{ on:true, temp:24 }, music:{ on:true, track:"bgm_karaoke" }}},
    { sceneId:"SC005", name:"节能模式",   icon:"💚", color:"#607d8b",
      params:{ curtain:"closed", lights:{ on:false, brightness:0 }, ac:{ on:false }}},
    { sceneId:"SC006", name:"营业前准备", icon:"🔧", color:"#ff5722",
      params:{ curtain:"open", lights:{ on:true, brightness:100, colorTemp:5000 }, ac:{ on:true, temp:24 }, music:{ on:true, track:"bgm_preopen" }}}
  ];

  MOCK.cleaningTasks = {
    pending: [
      { taskId:"CL001", roomId:"RM003", roomName:"中茶室B", type:"FullClean",
        priority:"High", created:"2026-05-16T09:00:00",
        checklist:["擦拭桌面","拖地","清洗茶具","更换垃圾袋","检查设备"] }
    ],
    inProgress: [
      { taskId:"CL002", roomId:"RM002", roomName:"中茶室A", type:"QuickClean",
        priority:"Normal", created:"2026-05-16T08:30:00",
        checklist:["擦拭桌面","拖地","清洗茶具","更换垃圾袋"],
        progress:["擦拭桌面","拖地"] }
    ],
    completed: [
      { taskId:"CL003", roomId:"RM001", roomName:"大会议室", type:"FullClean",
        priority:"Normal", created:"2026-05-16T07:00:00",
        checklist:["擦拭桌面","拖地","清洗茶具","更换垃圾袋","检查设备","消毒"] }
    ]
  };

  MOCK.inspections = [
    { planId:"INSP001", date:"2026-05-16", type:"Daily", status:"InProgress",
      progress:{ total:12, completed:3 },
      items:[
        { category:"设备间", items:[
          { name:"机柜温度", status:"normal", note:"" },
          { name:"交换机指示灯", status:"normal", note:"" },
          { name:"485集线器状态", status:"normal", note:"" },
          { name:"功放运行状态", status:"abnormal", note:"T-6715 RM003 指示灯异常" }
        ]},
        { category:"公共区域", items:[
          { name:"走廊照明", status:"normal", note:"" },
          { name:"展厅温度", status:"normal", note:"" },
          { name:"前台设备", status:"normal", note:"" }
        ]}
      ]
    }
  ];

  MOCK.alerts = [
    { alertId:"ALT001", level:"warning",  message:"中茶室B T-6715 网络功放通讯超时", time:"10:23", status:"Active" },
    { alertId:"ALT002", level:"error",    message:"大会议室 Speaker L 声道音量异常",  time:"09:45", status:"Active" },
    { alertId:"ALT003", level:"info",     message:"走廊485面板固件更新可用",         time:"08:30", status:"Resolved" }
  ];

  MOCK.couponDB = {
    "MT20260501": { platform:"Meituan",   value:30, type:"discount", used:false, desc:"美团点评 满200减30" },
    "DY20260501": { platform:"Douyin",    value:50, type:"discount", used:false, desc:"抖音团购 满200减50" },
    "DP20260501": { platform:"Dianping",  value:25, type:"discount", used:false, desc:"大众点评 满150减25" },
    "MT20260502": { platform:"Meituan",   value:50, type:"discount", used:true,  desc:"美团点评 满300减50（已使用）" },
    "MT20260503": { platform:"Meituan",   value:80, type:"discount", used:false, desc:"美团点评 满500减80" },
    "SY20260501": { platform:"System",    value:50, type:"voucher",  used:false, desc:"首充赠送 50元代金券" },
    "SY20260502": { platform:"System",    value:50, type:"voucher",  used:false, desc:"首充赠送 50元代金券" }
  };

  // ═══════════════════════════════════════════
  //  2. 本地存储（与customer-mp共用 mp_ 前缀）
  // ═══════════════════════════════════════════

  var LS_PREFIX = "mp_";

  function lsGet(key, fallback) {
    try {
      var val = localStorage.getItem(LS_PREFIX + key);
      return val ? JSON.parse(val) : fallback;
    } catch(e) { return fallback; }
  }

  function lsSet(key, val) {
    try { localStorage.setItem(LS_PREFIX + key, JSON.stringify(val)); } catch(e) {}
  }

  function lsRemove(key) {
    try { localStorage.removeItem(LS_PREFIX + key); } catch(e) {}
  }

  // ═══════════════════════════════════════════
  //  3. 公共UI工具
  // ═══════════════════════════════════════════

  var UI = {};

  UI.toast = function(msg, duration) {
    duration = duration || 2000;
    var el = document.getElementById('sdk-toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'sdk-toast';
      el.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);' +
        'background:rgba(0,0,0,.8);color:#fff;padding:12px 24px;border-radius:8px;' +
        'font-size:14px;z-index:9999;display:none;max-width:300px;text-align:center;' +
        'line-height:1.5;';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.style.display = 'block';
    clearTimeout(el._timer);
    el._timer = setTimeout(function() { el.style.display = 'none'; }, duration);
  };

  UI.showLoading = function(msg) {
    msg = msg || '加载中...';
    var el = document.getElementById('sdk-loading');
    if (!el) {
      el = document.createElement('div');
      el.id = 'sdk-loading';
      el.innerHTML = '<div style="background:rgba(0,0,0,.7);color:#fff;padding:24px 36px;' +
        'border-radius:12px;font-size:15px;text-align:center;">' +
        '<div style="font-size:32px;margin-bottom:8px;">⏳</div><div id="sdk-loading-msg"></div></div>';
      el.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;' +
        'display:none;align-items:center;justify-content:center;z-index:9998;';
      document.body.appendChild(el);
    }
    document.getElementById('sdk-loading-msg').textContent = msg;
    el.style.display = 'flex';
  };

  UI.hideLoading = function() {
    var el = document.getElementById('sdk-loading');
    if (el) el.style.display = 'none';
  };

  UI.confirm = function(title, msg, confirmText, cancelText) {
    return new Promise(function(resolve) {
      var overlay = document.createElement('div');
      overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;' +
        'background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;z-index:9997;';
      overlay.innerHTML =
        '<div style="background:#fff;border-radius:14px;padding:24px;width:300px;text-align:center;">' +
        '<h3 style="font-size:16px;margin:0 0 8px;color:#333;">' + title + '</h3>' +
        '<p style="font-size:14px;color:#666;margin:0 0 20px;">' + msg + '</p>' +
        '<div style="display:flex;gap:10px;">' +
        '<button id="sdk-confirm-cancel" style="flex:1;padding:10px;border-radius:8px;border:none;' +
        'background:#f5f5f5;color:#666;font-size:14px;cursor:pointer;">' + (cancelText || '取消') + '</button>' +
        '<button id="sdk-confirm-ok" style="flex:1;padding:10px;border-radius:8px;border:none;' +
        'background:#07c160;color:#fff;font-size:14px;cursor:pointer;">' + (confirmText || '确定') + '</button>' +
        '</div></div>';
      document.body.appendChild(overlay);
      document.getElementById('sdk-confirm-ok').onclick = function() { document.body.removeChild(overlay); resolve(true); };
      document.getElementById('sdk-confirm-cancel').onclick = function() { document.body.removeChild(overlay); resolve(false); };
    });
  };

  // ═══════════════════════════════════════════
  //  4. 真实API请求支持
  // ═══════════════════════════════════════════

  var API_BASE = localStorage.getItem('erp_api_base') || 'http://localhost:8000';
  var USE_API = localStorage.getItem('staff_use_api') === 'true';

  function apiRequest(method, path, body) {
    var url = API_BASE + path;
    var opts = {
      method: method,
      headers: { 'Content-Type': 'application/json' },
    };
    var token = localStorage.getItem('staff_api_token');
    if (token) opts.headers['Authorization'] = 'Bearer ' + token;
    if (body) opts.body = JSON.stringify(body);
    return fetch(url, opts).then(function(res) {
      if (!res.ok) return res.text().then(function(t) { throw new Error(t); });
      return res.json();
    });
  }

  function delay(ms) {
    ms = ms || (300 + Math.random() * 400);
    return new Promise(function(resolve) { setTimeout(resolve, ms); });
  }

  var API = {};

  // ── 店员认证 ──

  API.staffLogin = function(staffId, password) {
    if (USE_API) {
      return apiRequest('POST', '/api/auth/login', { username: staffId, password: password }).then(function(res) {
        localStorage.setItem('staff_api_token', res.access_token);
        var user = res.user;
        lsSet('staff_logged_in', true);
        lsSet('staff_user', { staffId: user.username, name: user.display_name, role: user.role, phone: user.phone || '' });
        return { staffId: user.username, name: user.display_name, role: user.role, phone: user.phone || '' };
      });
    }
    return delay().then(function() {
      var staffList = lsGet('staff_list', [
        { staffId:'S001', name:'小林', role:'店长',    phone:'13800138001', password:'8888' },
        { staffId:'S002', name:'小芳', role:'店员',    phone:'13800138002', password:'8888' },
        { staffId:'S003', name:'小王', role:'管理员',  phone:'13800138003', password:'8888' },
      ]);
      var found = null;
      staffList.forEach(function(s) { if (s.staffId.toUpperCase() === staffId.toUpperCase() && s.password === password) found = s; });
      if (!found) throw new Error('工号或密码错误');
      lsSet('staff_logged_in', true);
      lsSet('staff_user', { staffId: found.staffId, name: found.name, role: found.role, phone: found.phone });
      return found;
    });
  };

  API.staffLogout = function() {
    lsRemove('staff_logged_in');
    lsRemove('staff_user');
    localStorage.removeItem('staff_api_token');
    return Promise.resolve({ success: true });
  };

  API.getCurrentStaff = function() {
    return delay(100).then(function() { return lsGet('staff_user', null); });
  };

  API.isStaffLoggedIn = function() {
    return !!lsGet('staff_logged_in', false);
  };

  // ── 房间 ──

  API.getRooms = function(bookableOnly) {
    if (USE_API) {
      return apiRequest('GET', '/api/rooms').then(function(rooms) {
        if (bookableOnly) rooms = rooms.filter(function(r) { return r.bookable !== false; });
        return rooms.map(function(r) {
          return {
            roomId: r.roomId, name: r.name, type: r.type || 'TeaRoom',
            capacity: r.capacity, area: r.area || 0,
            facilities: typeof r.facilities === 'string' ? JSON.parse(r.facilities) : (r.facilities || []),
            pricePerHour: r.pricePerHour || 0, pricePerHalfHour: r.pricePerHalfHour || 0,
            status: r.status || 'Active', bookable: r.bookable !== false,
          };
        });
      });
    }
    return delay().then(function() {
      var rooms = MOCK.rooms.slice();
      if (bookableOnly) rooms = rooms.filter(function(r) { return r.bookable !== false; });
      return rooms;
    });
  };

  API.getRoomById = function(roomId) {
    if (USE_API) {
      return apiRequest('GET', '/api/rooms/' + roomId);
    }
    return delay().then(function() {
      var room = null;
      MOCK.rooms.forEach(function(r) { if (r.roomId === roomId) room = r; });
      if (!room) throw new Error('房间不存在');
      return JSON.parse(JSON.stringify(room));
    });
  };

  /**
   * 计算房间实时状态（通过 mp_bookings 动态计算）
   */
  API.computeRoomStatus = function(roomId) {
    var bookings = lsGet('bookings', []);
    var now = new Date();
    var roomBookings = bookings.filter(function(b) {
      return b.roomId === roomId && b.status !== 'Cancelled' && b.status !== 'Completed';
    });
    var inUse = null;
    roomBookings.forEach(function(b) { if (b.status === 'InUse') inUse = b; });
    if (inUse) {
      var end = new Date(inUse.end);
      var remaining = Math.max(0, Math.round((end - now) / 60000));
      return { status: 'InUse', booking: inUse, remaining: remaining };
    }
    var booked = null;
    roomBookings.forEach(function(b) {
      if (b.status === 'Booked') {
        var start = new Date(b.date + 'T' + b.startTime);
        if (start > now) booked = b;
      }
    });
    if (booked) return { status: 'Booked', booking: booked, remaining: 0 };
    var maintenance = lsGet('room_maintenance', {});
    if (maintenance[roomId]) return { status: 'Maintenance', booking: null, remaining: 0 };
    return { status: 'Active', booking: null, remaining: 0 };
  };

  API.getAllRoomStatus = function() {
    var results = [];
    MOCK.rooms.forEach(function(r) {
      var s = API.computeRoomStatus(r.roomId);
      results.push({
        roomId: r.roomId, name: r.name, type: r.type,
        bookable: r.bookable, status: s.status, booking: s.booking,
        remaining: s.remaining
      });
    });
    return results;
  };

  // ── 设备 ──

  API.getRoomDevices = function(roomId) {
    if (USE_API) {
      return apiRequest('GET', '/api/iot/devices?room_id=' + roomId);
    }
    return delay().then(function() {
      return MOCK.devices.filter(function(d) { return d.roomId === roomId; }).map(function(d) {
        var copy = {};
        for (var k in d) copy[k] = d[k];
        return copy;
      });
    });
  };

  API.controlDevice = function(deviceId, command) {
    if (USE_API) {
      return apiRequest('POST', '/api/iot/control', { device_id: deviceId, action: command.action || 'set', params: command });
    }
    return delay(200).then(function() {
      var dev = null;
      MOCK.devices.forEach(function(d) { if (d.deviceId === deviceId) dev = d; });
      if (!dev) throw new Error('设备不存在');
      for (var k in command) dev[k] = command[k];
      UI.toast('✅ 指令已下发 (' + (MOCK.deviceTypes[dev.type] ? MOCK.deviceTypes[dev.type].label : dev.type) + ')');
      return { success: true, deviceId: deviceId, command: command };
    });
  };

  API.executeScene = function(roomId, sceneId) {
    if (USE_API) {
      return apiRequest('POST', '/api/iot/scenes/activate', { room_id: roomId, scene: sceneId });
    }
    return delay(800).then(function() {
      var scene = null;
      MOCK.scenes.forEach(function(s) { if (s.sceneId === sceneId) scene = s; });
      if (!scene) throw new Error('场景不存在');
      var p = scene.params;
      MOCK.devices.forEach(function(d) {
        if (d.roomId === roomId && d.type === 'Curtain' && p.curtain) d.position = p.curtain;
        if (d.roomId === roomId && d.type === 'AC' && p.ac) {
          d.mode = p.ac.on ? 'cool' : 'off';
          if (p.ac.temp) d.temperature = p.ac.temp;
        }
        if (d.roomId === roomId && d.type === 'Light' && p.lights) {
          d.brightness = p.lights.brightness || 0;
          d.colorTemp = p.lights.colorTemp || 4000;
        }
        if (d.roomId === roomId && d.type === 'Speaker' && p.music) d.playing = p.music.on || false;
      });
      return { success: true, sceneId: sceneId, sceneName: scene.name };
    });
  };

  API.getActiveAlerts = function() {
    if (USE_API) {
      return apiRequest('GET', '/api/iot/alerts?status=Active');
    }
    return delay().then(function() {
      return MOCK.alerts.filter(function(a) { return a.status === 'Active'; });
    });
  };

  API.getScenes = function() {
    if (USE_API) {
      return apiRequest('GET', '/api/iot/scenes');
    }
    return delay().then(function() { return JSON.parse(JSON.stringify(MOCK.scenes)); });
  };

  // ── 订单（共用 mp_bookings / 后端API） ──

  API.getAllBookings = function() {
    if (USE_API) {
      return apiRequest('GET', '/api/orders');
    }
    return delay().then(function() {
      var bookings = lsGet('bookings', []);
      return bookings.sort(function(a, b) { return new Date(b.created) - new Date(a.created); });
    });
  };

  API.getBookingById = function(orderId) {
    if (USE_API) {
      return apiRequest('GET', '/api/orders/' + encodeURIComponent(orderId));
    }
    return delay().then(function() {
      var bookings = lsGet('bookings', []);
      var found = null;
      bookings.forEach(function(b) { if (b.orderId === orderId) found = b; });
      if (!found) throw new Error('订单不存在');
      return found;
    });
  };

  API.createStaffBooking = function(booking) {
    if (USE_API) {
      return apiRequest('POST', '/api/orders', booking);
    }
    return delay(500).then(function() {
      var bookings = lsGet('bookings', []);
      var orderId = 'ORD' + String(Date.now()).slice(-6);
      var b = {
        orderId: orderId,
        status: booking.startNow ? 'InUse' : 'Booked',
        doorCode: String(Math.floor(1000 + Math.random() * 9000)),
        created: new Date().toISOString(),
        isStaffBooking: true,
        staffName: (lsGet('staff_user', {}) || {}).name || '店员',
        ...booking
      };
      delete b.startNow;
      bookings.push(b);
      lsSet('bookings', bookings);
      return b;
    });
  };

  API.checkIn = function(orderId) {
    if (USE_API) {
      return apiRequest('POST', '/api/orders/' + encodeURIComponent(orderId) + '/checkin');
    }
    return delay(200).then(function() {
      var bookings = lsGet('bookings', []);
      var found = false;
      bookings.forEach(function(b) {
        if (b.orderId === orderId) { b.status = 'InUse'; found = true; }
      });
      if (!found) throw new Error('订单不存在');
      lsSet('bookings', bookings);
      return { success: true };
    });
  };

  API.checkOut = function(orderId) {
    if (USE_API) {
      return apiRequest('POST', '/api/orders/' + encodeURIComponent(orderId) + '/checkout');
    }
    return delay(200).then(function() {
      var bookings = lsGet('bookings', []);
      var found = false;
      bookings.forEach(function(b) {
        if (b.orderId === orderId) { b.status = 'Completed'; found = true; }
      });
      if (!found) throw new Error('订单不存在');
      lsSet('bookings', bookings);
      return { success: true };
    });
  };

  API.cancelBooking = function(orderId) {
    if (USE_API) {
      return apiRequest('POST', '/api/orders/' + encodeURIComponent(orderId) + '/cancel');
    }
    return delay(200).then(function() {
      var bookings = lsGet('bookings', []);
      bookings.forEach(function(b) { if (b.orderId === orderId) b.status = 'Cancelled'; });
      lsSet('bookings', bookings);
      return { success: true };
    });
  };

  API.setMaintenance = function(roomId, reason, restoreTime) {
    return delay(200).then(function() {
      var maintenance = lsGet('room_maintenance', {});
      maintenance[roomId] = { reason: reason, restoreTime: restoreTime || '', setAt: new Date().toISOString() };
      lsSet('room_maintenance', maintenance);
      API.addAuditLog(roomId, 'setMaintenance', reason);
      return { success: true };
    });
  };

  API.clearMaintenance = function(roomId) {
    return delay(200).then(function() {
      var maintenance = lsGet('room_maintenance', {});
      delete maintenance[roomId];
      lsSet('room_maintenance', maintenance);
      return { success: true };
    });
  };

  // ── 监控告警 ──

  API.resolveAlert = function(alertId) {
    return delay(200).then(function() {
      MOCK.alerts.forEach(function(a) { if (a.alertId === alertId) a.status = 'Resolved'; });
      return { success: true };
    });
  };

  // ── 清洁/巡检 ──

  API.getCleaningTasks = function() {
    return delay().then(function() { return JSON.parse(JSON.stringify(MOCK.cleaningTasks)); });
  };

  API.getInspections = function() {
    return delay().then(function() { return JSON.parse(JSON.stringify(MOCK.inspections)); });
  };

  // ── 对账工单 ──

  API.getReconciliationOrders = function() {
    return delay().then(function() {
      return [
        { recId: "REC001", platform: "美团", orderRef: "ORD003", roomName: "中茶室A",
          systemAmount: 160, platformAmount: 152, diff: 8, reason: "平台服务费未对齐",
          status: "Pending", date: "2026-05-16", customerPhone: "139****6666" },
        { recId: "REC002", platform: "抖音", orderRef: "ORD004", roomName: "大会议室",
          systemAmount: 400, platformAmount: 380, diff: 20, reason: "抖音团购折扣",
          status: "Pending", date: "2026-05-15", customerPhone: "136****7777" },
      ];
    });
  };

  API.resolveReconciliation = function(recId, resolution) {
    return delay(300).then(function() {
      return { success: true, recId: recId, resolution: resolution, resolvedAt: new Date().toISOString() };
    });
  };

  // ── 审核工单 ──

  API.getAuditLogs = function() {
    return delay().then(function() {
      var logs = lsGet('audit_logs', []);
      return logs.sort(function(a, b) { return new Date(b.time) - new Date(a.time); });
    });
  };

  API.addAuditLog = function(roomId, action, reason) {
    var logs = lsGet('audit_logs', []);
    var staff = lsGet('staff_user', {});
    logs.push({
      logId: 'AUD' + Date.now(),
      staffName: staff.name || '未知',
      staffRole: staff.role || '',
      roomId: roomId,
      action: action,
      reason: reason || '',
      time: new Date().toISOString()
    });
    lsSet('audit_logs', logs);
  };

  API.approveAuditLog = function(logId) {
    return delay(200).then(function() {
      var logs = lsGet('audit_logs', []);
      logs.forEach(function(l) { if (l.logId === logId) l.approved = true; });
      lsSet('audit_logs', logs);
      return { success: true };
    });
  };

  // ── 会员（共用 mp_users） ──

  API.getMemberByPhone = function(phone) {
    return delay().then(function() {
      var users = lsGet('users', {});
      var member = users[phone];
      if (!member) throw new Error('未找到该会员');
      var bookings = lsGet('bookings', []);
      var memberOrders = [];
      bookings.forEach(function(b) { if (b.phone && b.phone.replace(/\D/g,'') === phone.replace(/\D/g,'')) memberOrders.push(b); });
      return {
        member: member,
        orders: memberOrders.sort(function(a, b) { return new Date(b.created) - new Date(a.created); })
      };
    });
  };

  API.topUpMember = function(phone, amount, paymentMethod) {
    return delay(500).then(function() {
      var users = lsGet('users', {});
      var member = users[phone];
      if (!member) throw new Error('会员不存在');
      member.balance = (member.balance || 0) + parseInt(amount);
      member.totalSpent = (member.totalSpent || 0) + parseInt(amount);
      lsSet('users', users);
      return { success: true, newBalance: member.balance, amount: parseInt(amount) };
    });
  };

  // ── 验券 ──

  API.verifyCoupon = function(code) {
    return delay().then(function() {
      var coupon = MOCK.couponDB[code];
      if (!coupon) throw new Error('无效的券码');
      if (coupon.used) throw new Error('该券码已被使用');
      return { valid: true, coupon: coupon, code: code };
    });
  };

  API.useCoupon = function(code) {
    return delay().then(function() {
      var coupon = MOCK.couponDB[code];
      if (!coupon) throw new Error('无效的券码');
      if (coupon.used) throw new Error('该券码已被使用');
      coupon.used = true;
      return { success: true, coupon: coupon, code: code };
    });
  };

  // ── 统计 ──

  API.getTodayStats = function() {
    if (USE_API) {
      return apiRequest('GET', '/api/finance/dashboard?storeId=YINGLONG').then(function(d) {
        return {
          revenue: d.monthRevenue || 0,
          orderCount: 0,
          guestCount: 0,
          alerts: 0,
          pendingCleaning: 0,
          pendingReconciliation: 0,
          pendingAudit: d.pendingExpenses || 0,
        };
      });
    }
    return delay().then(function() {
      var bookings = lsGet('bookings', []);
      var today = new Date();
      var todayStr = today.getFullYear() + '-' +
        String(today.getMonth() + 1).padStart(2,'0') + '-' +
        String(today.getDate()).padStart(2,'0');
      var todayOrders = [];
      bookings.forEach(function(b) {
        if (b.created && b.created.indexOf(todayStr) === 0) todayOrders.push(b);
      });
      var revenue = 0;
      var guestCount = 0;
      todayOrders.forEach(function(o) {
        revenue += (o.amount || 0);
        if (o.status === 'InUse' || o.status === 'Completed') guestCount++;
      });
      return {
        revenue: revenue,
        orderCount: todayOrders.length,
        guestCount: guestCount,
        alerts: MOCK.alerts.filter(function(a) { return a.status === 'Active'; }).length,
        pendingCleaning: 1,
        pendingReconciliation: 2,
        pendingAudit: 3
      };
    });
  };

  // ═══════════════════════════════════════════
  //  5. 导出
  // ═══════════════════════════════════════════

  win.StaffSDK = {
    API: API,
    UI: UI,
    Utils: {
      lsGet: lsGet, lsSet: lsSet, lsRemove: lsRemove,
      formatMoney: function(n) { return '¥' + (n || 0).toFixed(2); },
      getRoomTypeLabel: function(type) {
        var map = { MeetingRoom:'会议室', TeaRoom:'茶室', Exhibition:'展厅', Workspace:'工作间' };
        return map[type] || type;
      },
      getRoomStatusBadge: function(status) {
        var map = { InUse:'使用中', Booked:'已预订', Cleaning:'清洁中', Active:'空闲', Maintenance:'维护中' };
        return map[status] || status;
      },
      todayStr: function() {
        var d = new Date();
        return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
      },
      formatTime: function(iso) {
        if (!iso) return '';
        var d = new Date(iso);
        return String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
      },
      isApiMode: function() { return USE_API; },
      toggleApiMode: function(enable) {
        localStorage.setItem('staff_use_api', enable ? 'true' : 'false');
        location.reload();
      },
    }
  };

})(window);
