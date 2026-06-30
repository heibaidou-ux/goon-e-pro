/**
 * 高岸ERP 客户端SDK — Mock数据层 + API接口
 * 设计原则：
 *   1. 所有API返回Promise，模拟异步调用，后续可无缝替换为真实HTTP请求
 *   2. 数据格局与shared-mock/ JSON文件一致
 *   3. localStorage作为本地持久化层
 *   4. 模拟500-800ms网络延迟以呈现真实加载态
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
  //  1. 内嵌Mock数据（与shared-mock/ 一一对应）
  // ═══════════════════════════════════════════

  var MOCK = {};

  // ── 门店 ──
  MOCK.stores = [{
    storeId: "ST001", name: "盈隆店", address: "广州市天河区珠江新城富力盈隆广场3801",
    phone: "18011821388", status: "Active"
  }];

  // ── 房间 ──
  MOCK.rooms = [
    { roomId: "RM001", name: "丰沙里", type: "MeetingRoom", capacity: 10, area: 30,
      facilities: ["投影","会议桌","K歌设备","落地窗"], pricePerHour: 200, pricePerHalfHour: 120, status: "Active", bookable: true },
    { roomId: "RM002", name: "翡冷翠", type: "TeaRoom", capacity: 4, area: 18,
      facilities: ["茶台","落地窗","茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
    { roomId: "RM003", name: "布拉格", type: "TeaRoom", capacity: 4, area: 18,
      facilities: ["茶台","落地窗","茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
    { roomId: "RM004", name: "白沙瓦", type: "TeaRoom", capacity: 6, area: 25,
      facilities: ["茶台","K歌","投影","落地窗"], pricePerHour: 120, pricePerHalfHour: 75, status: "Active", bookable: true },
    { roomId: "RM005", name: "展厅", type: "Exhibition", capacity: 20, area: 40,
      facilities: ["前台","收银","茶具展示","休闲区"], status: "Active", bookable: false },
    { roomId: "RM006", name: "工作间", type: "Workspace", capacity: 2, area: 12,
      facilities: ["储物","机柜"], status: "Active", bookable: false }
  ];

  // ── 设备 ──
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

  // ── 订单 ──
  MOCK.orders = [
    { orderId:"ORD001", customerName:"张先生", roomId:"RM004", roomName:"白沙瓦",
      status:"InUse", start:"2026-05-16T10:00:00", end:"2026-05-16T11:30:00",
      duration:90, amount:180, paymentMethod:"WeChat", phone:"138****8888" },
    { orderId:"ORD002", customerName:"李女士", roomId:"RM002", roomName:"翡冷翠",
      status:"Booked", start:"2026-05-16T14:00:00", end:"2026-05-16T16:00:00",
      duration:120, amount:160, paymentMethod:"Balance", phone:"139****6666" },
    { orderId:"ORD003", customerName:"王先生", roomId:"RM003", roomName:"布拉格",
      status:"Completed", start:"2026-05-16T08:00:00", end:"2026-05-16T09:30:00",
      duration:90, amount:120, paymentMethod:"WeChat", phone:"137****5555" },
    { orderId:"ORD004", customerName:"赵总", roomId:"RM001", roomName:"丰沙里",
      status:"Completed", start:"2026-05-15T15:00:00", end:"2026-05-15T17:00:00",
      duration:120, amount:400, paymentMethod:"Alipay", phone:"136****7777" }
  ];

  // ── 客户 ──
  MOCK.customers = [
    { customerId:"C001", name:"张先生", phone:"138****8888", level:"Gold",
      totalSpent:3200, visitCount:12, lastVisit:"2026-05-16" },
    { customerId:"C002", name:"李女士", phone:"139****6666", level:"Silver",
      totalSpent:1800, visitCount:6, lastVisit:"2026-05-14" },
    { customerId:"C003", name:"王先生", phone:"137****5555", level:"Silver",
      totalSpent:1500, visitCount:5, lastVisit:"2026-05-16" },
    { customerId:"C004", name:"赵总", phone:"136****7777", level:"Diamond",
      totalSpent:8500, visitCount:28, lastVisit:"2026-05-15" }
  ];

  // ── 场景 ──
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

  // ── 茶品 ──
  MOCK.products = [
    { productId:"T001", name:"安吉白茶",   category:"Tea",   price:68,  desc:"清香甘甜，明前采摘", image:"🍃" },
    { productId:"T002", name:"正山小种",   category:"Tea",   price:88,  desc:"松烟香，桂圆味",   image:"🌿" },
    { productId:"T003", name:"铁观音",     category:"Tea",   price:58,  desc:"七泡有余香",       image:"🍵" },
    { productId:"T004", name:"手工茶点A",  category:"Snack", price:38,  desc:"绿豆糕拼盘",       image:"🍪" },
    { productId:"T005", name:"手工茶点B",  category:"Snack", price:48,  desc:"坚果四宫格",       image:"🥜" },
    { productId:"T006", name:"时令水果盘", category:"Snack", price:58,  desc:"当日新鲜水果",     image:"🍉" },
    { productId:"T007", name:"定制茶具A",  category:"Ware",  price:288, desc:"手作紫砂壶套装",   image:"🏺" },
    { productId:"T008", name:"定制茶具B",  category:"Ware",  price:188, desc:"玻璃茶道六君子",   image:"🥃" }
  ];

  // ── 优惠券 ──
  MOCK.couponDB = {
    "MT20260501": { platform:"Meituan",   value:30, type:"discount", used:false, desc:"美团点评 满200减30" },
    "DY20260501": { platform:"Douyin",    value:50, type:"discount", used:false, desc:"抖音团购 满200减50" },
    "DP20260501": { platform:"Dianping",  value:25, type:"discount", used:false, desc:"大众点评 满150减25" },
    "MT20260502": { platform:"Meituan",   value:50, type:"discount", used:true,  desc:"美团点评 满300减50（已使用）" },
    "MT20260503": { platform:"Meituan",   value:80, type:"discount", used:false, desc:"美团点评 满500减80" },
    "SY20260501": { platform:"System",    value:50, type:"voucher",  used:false, desc:"首充赠送 50元代金券" },
    "SY20260502": { platform:"System",    value:50, type:"voucher",  used:false, desc:"首充赠送 50元代金券" }
  };

  // ── 清洁/巡检/告警 ──
  MOCK.cleaningTasks = {
    pending: [
      { taskId:"CL001", roomId:"RM003", roomName:"布拉格", type:"FullClean",
        priority:"High", created:"2026-05-16T09:00:00",
        checklist:["擦拭桌面","拖地","清洗茶具","更换垃圾袋","检查设备"] }
    ],
    inProgress: [
      { taskId:"CL002", roomId:"RM002", roomName:"翡冷翠", type:"QuickClean",
        priority:"Normal", created:"2026-05-16T08:30:00",
        checklist:["擦拭桌面","拖地","清洗茶具","更换垃圾袋"],
        progress:["擦拭桌面","拖地"] }
    ],
    completed: [
      { taskId:"CL003", roomId:"RM001", roomName:"丰沙里", type:"FullClean",
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
    { alertId:"ALT001", level:"warning",  message:"布拉格 T-6715 网络功放通讯超时", time:"10:23", status:"Active" },
    { alertId:"ALT002", level:"error",    message:"丰沙里 Speaker L 声道音量异常",  time:"09:45", status:"Active" },
    { alertId:"ALT003", level:"info",     message:"走廊485面板固件更新可用",         time:"08:30", status:"Resolved" }
  ];

  // ═══════════════════════════════════════════
  //  2. 本地存储（localStorage封装）
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

  /** Toast提示 */
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

  /** Loading遮罩 */
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

  /** 确认对话框 */
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
        'background:#5D8A6B;color:#fff;font-size:14px;cursor:pointer;">' + (confirmText || '确定') + '</button>' +
        '</div></div>';
      document.body.appendChild(overlay);
      document.getElementById('sdk-confirm-ok').onclick = function() { document.body.removeChild(overlay); resolve(true); };
      document.getElementById('sdk-confirm-cancel').onclick = function() { document.body.removeChild(overlay); resolve(false); };
    });
  };

  // ═══════════════════════════════════════════
  //  4. API接口（全部返回Promise）
  // ═══════════════════════════════════════════

  /** 模拟网络延迟 */
  function delay(ms) {
    ms = ms || (300 + Math.random() * 400);
    return new Promise(function(resolve) { setTimeout(resolve, ms); });
  }

  var API = {};

  // ── 认证 ──

  /** 登录（任意手机号 + 验证码"8888"即通过） */
  API.login = function(phone, code) {
    return delay().then(function() {
      if (code !== '8888') throw new Error('验证码错误');
      // 查询或新建用户
      var users = lsGet('users', {});
      var user = users[phone];
      if (!user) {
        user = { phone: phone, name: phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
          memberLevel: 'Silver', balance: 280, totalSpent: 0, visitCount: 0, created: new Date().toISOString(), tags: [] };
        users[phone] = user;
        lsSet('users', users);
      }
      lsSet('logged_in', true);
      lsSet('user', user);
      return user;
    });
  };

  API.logout = function() {
    lsRemove('logged_in');
    lsRemove('user');
    return Promise.resolve({ success: true });
  };

  API.getCurrentUser = function() {
    return delay(100).then(function() {
      return lsGet('user', null);
    });
  };

  API.isLoggedIn = function() {
    return !!lsGet('logged_in', false);
  };

  // ── 房间 ──

  API.getRooms = function(bookableOnly) {
    return delay().then(function() {
      var rooms = MOCK.rooms.slice();
      if (bookableOnly) rooms = rooms.filter(function(r) { return r.bookable !== false; });
      return rooms;
    });
  };

  API.getRoomById = function(roomId) {
    return delay().then(function() {
      var room = null;
      MOCK.rooms.forEach(function(r) { if (r.roomId === roomId) room = r; });
      if (!room) throw new Error('房间不存在');
      return room;
    });
  };

  /** 查询某房间某日期的已有预订，用于冲突检测 */
  API.getRoomBookings = function(roomId, date) {
    return delay().then(function() {
      var bookings = lsGet('bookings', []);
      return bookings.filter(function(b) {
        return b.roomId === roomId && b.date === date && b.status !== 'Cancelled';
      });
    });
  };

  // ── 设备 ──

  API.getRoomDevices = function(roomId) {
    return delay().then(function() {
      return MOCK.devices.filter(function(d) { return d.roomId === roomId; }).map(function(d) {
        var copy = {};
        for (var k in d) copy[k] = d[k];
        return copy;
      });
    });
  };

  /** 控制设备（模拟485/IP指令下发） */
  API.controlDevice = function(deviceId, command) {
    return delay(200).then(function() {
      var dev = null;
      MOCK.devices.forEach(function(d) { if (d.deviceId === deviceId) dev = d; });
      if (!dev) throw new Error('设备不存在');
      for (var k in command) dev[k] = command[k];
      UI.toast('✅ 指令已下发 (' + (MOCK.deviceTypes[dev.type] ? MOCK.deviceTypes[dev.type].label : dev.type) + ')');
      return { success: true, deviceId: deviceId, command: command };
    });
  };

  /** 批量控制同房间设备（场景联动） */
  API.executeScene = function(roomId, sceneId) {
    return delay(800).then(function() {
      var scene = null;
      MOCK.scenes.forEach(function(s) { if (s.sceneId === sceneId) scene = s; });
      if (!scene) throw new Error('场景不存在');
      var p = scene.params;
      var cmds = [];
      // 窗帘
      MOCK.devices.forEach(function(d) {
        if (d.roomId === roomId && d.type === 'Curtain' && p.curtain) {
          d.position = p.curtain;
          cmds.push({ deviceId: d.deviceId, action: 'curtain_' + p.curtain });
        }
        if (d.roomId === roomId && d.type === 'AC' && p.ac) {
          d.mode = p.ac.on ? 'cool' : 'off';
          if (p.ac.temp) d.temperature = p.ac.temp;
          cmds.push({ deviceId: d.deviceId, action: 'ac_' + (p.ac.on ? 'on_' + p.ac.temp : 'off') });
        }
        if (d.roomId === roomId && d.type === 'Light' && p.lights) {
          d.brightness = p.lights.brightness || 0;
          d.colorTemp = p.lights.colorTemp || 4000;
          cmds.push({ deviceId: d.deviceId, action: 'light_' + d.brightness });
        }
        if (d.roomId === roomId && d.type === 'Speaker' && p.music) {
          d.playing = p.music.on || false;
          cmds.push({ deviceId: d.deviceId, action: 'music_' + (p.music.on ? 'play' : 'stop') });
        }
      });
      return { success: true, sceneId: sceneId, sceneName: scene.name, commands: cmds };
    });
  };

  /** 获取设备告警 */
  API.getActiveAlerts = function() {
    return delay().then(function() {
      return MOCK.alerts.filter(function(a) { return a.status === 'Active'; });
    });
  };

  // ── 音频系统（对接V1.2分布式IP音频架构） ──

  /** 获取房间T-6715状态 */
  API.getAudioStatus = function(roomId) {
    return delay().then(function() {
      var speakers = MOCK.devices.filter(function(d) { return d.roomId === roomId && d.type === 'Speaker'; });
      if (speakers.length === 0) return null;
      // 模拟T-6715状态
      return {
        roomId: roomId,
        online: speakers.some(function(s) { return s.status === 'Online'; }),
        speakers: speakers,
        volume: speakers.length > 0 ? speakers[0].volume : 0,
        playing: speakers.length > 0 ? speakers[0].playing : false,
        source: speakers.length > 0 ? speakers[0].source : 'none',
        // 以下为T-6715特有属性
        ipAddress: '192.168.10.' + (10 + parseInt(roomId.slice(-1))),
        firmware: 'v2.3.1',
        signalQuality: (85 + Math.floor(Math.random() * 15)) + '%',
        availableSources: [
          { id: 'bluetooth', label: '蓝牙音频', icon: '🔵' },
          { id: 'bgm',       label: '背景音乐', icon: '🎵' },
          { id: 'ha_push',   label: 'HA提示音', icon: '🔔' }
        ]
      };
    });
  };

  /** 控制T-6715音量 */
  API.setVolume = function(roomId, volume) {
    return delay(150).then(function() {
      MOCK.devices.forEach(function(d) {
        if (d.roomId === roomId && d.type === 'Speaker') d.volume = volume;
      });
      UI.toast('音量已设为 ' + volume + '%');
      return { success: true, roomId: roomId, volume: volume };
    });
  };

  /** 切换音频源（蓝牙/背景音乐/HA提示音） */
  API.switchAudioSource = function(roomId, source) {
    return delay(200).then(function() {
      MOCK.devices.forEach(function(d) {
        if (d.roomId === roomId && d.type === 'Speaker') d.source = source;
      });
      var labels = { bluetooth:'蓝牙音频', bgm:'背景音乐', ha_push:'HA提示音' };
      UI.toast('音频源切换为：' + (labels[source] || source));
      return { success: true, roomId: roomId, source: source };
    });
  };

  /** HA发送提示音到指定房间 */
  API.sendAlertAudio = function(roomId, alertType) {
    return delay(300).then(function() {
      var messages = {
        timeout:    '⏰ 您的订单即将结束，请及时续订',
        service:    '🔔 您有新的服务通知',
        welcome:    '👋 欢迎光临，祝您有一个愉快的茶室体验',
        custom:     '📢 前台通知'
      };
      UI.toast('🔔 ' + (messages[alertType] || '提示音') + ' (' + roomId + ')');
      return { success: true, roomId: roomId, alertType: alertType, message: messages[alertType] || '' };
    });
  };

  // ── 订单 ──

  /** 创建预订 */
  API.createBooking = function(booking) {
    return delay(500).then(function() {
      var bookings = lsGet('bookings', []);
      var id = 'ORD' + String(Date.now()).slice(-6);
      var b = {
        orderId: id, status: 'Booked', doorCode: String(Math.floor(1000 + Math.random() * 9000)),
        created: new Date().toISOString(), phone: (lsGet('user', {}) || {}).phone || '',
        ...booking
      };
      bookings.push(b);
      lsSet('bookings', bookings);
      // 扣余额
      var user = lsGet('user', {});
      if (booking.paymentMethod === 'Balance' && user.balance !== undefined) {
        user.balance -= (booking.amount || 0);
        lsSet('user', user);
      }
      return b;
    });
  };

  API.getUserOrders = function() {
    return delay().then(function() {
      var bookings = lsGet('bookings', []);
      var orders = [];
      var user = lsGet('user', null);
      if (user) {
        bookings.forEach(function(b) {
          if (b.phone === user.phone) orders.push(b);
        });
      }
      return orders.sort(function(a, b) { return new Date(b.created) - new Date(a.created); });
    });
  };

  API.cancelOrder = function(orderId) {
    return delay(200).then(function() {
      var bookings = lsGet('bookings', []);
      bookings.forEach(function(b) { if (b.orderId === orderId) b.status = 'Cancelled'; });
      lsSet('bookings', bookings);
      return { success: true };
    });
  };

  // ── 茶品商城 ──

  API.getProducts = function(category) {
    return delay().then(function() {
      if (category) return MOCK.products.filter(function(p) { return p.category === category; });
      return MOCK.products.slice();
    });
  };

  /** 购物车 */
  API.getCart = function() {
    return Promise.resolve(lsGet('tea_cart', []));
  };

  API.addToCart = function(product) {
    var cart = lsGet('tea_cart', []);
    var found = false;
    cart.forEach(function(item) {
      if (item.productId === product.productId) { item.qty = (item.qty || 1) + 1; found = true; }
    });
    if (!found) { product.qty = 1; cart.push(product); }
    lsSet('tea_cart', cart);
    return Promise.resolve(cart);
  };

  API.removeFromCart = function(productId) {
    var cart = lsGet('tea_cart', []);
    for (var i = 0; i < cart.length; i++) {
      if (cart[i].productId === productId) {
        if (cart[i].qty > 1) { cart[i].qty--; } else { cart.splice(i, 1); }
        break;
      }
    }
    lsSet('tea_cart', cart);
    return Promise.resolve(cart);
  };

  API.createShopOrder = function(items, paymentMethod, total) {
    return delay(400).then(function() {
      var order = {
        orderId: 'SHP' + String(Date.now()).slice(-6),
        items: items, total: total, paymentMethod: paymentMethod,
        status: 'Paid', created: new Date().toISOString()
      };
      var shopOrders = lsGet('shop_orders', []);
      shopOrders.push(order);
      lsSet('shop_orders', shopOrders);
      lsSet('tea_cart', []);
      // 扣余额
      if (paymentMethod === 'Balance') {
        var user = lsGet('user', {});
        user.balance = (user.balance || 0) - total;
        lsSet('user', user);
      }
      return order;
    });
  };

  // ── 余额与充值 ──

  API.getBalance = function() {
    return delay(100).then(function() {
      var user = lsGet('user', {});
      return user.balance || 0;
    });
  };

  API.topUp = function(amount, paymentMethod) {
    return delay(500).then(function() {
      var user = lsGet('user', {});
      var bonus = 0;
      // 首充奖励
      if (!user._firstRecharge) {
        bonus = Math.round(amount * 0.3);
        user._firstRecharge = true;
      }
      user.balance = (user.balance || 0) + amount + bonus;
      lsSet('user', user);
      return { success: true, amount: amount, bonus: bonus, newBalance: user.balance };
    });
  };

  // ── 优惠券 ──

  API.verifyCoupon = function(code) {
    return delay(300).then(function() {
      var c = MOCK.couponDB[code];
      if (!c) throw new Error('券码不存在');
      if (c.used) throw new Error('该券已被使用');
      return { code: code, value: c.value, type: c.type, desc: c.desc, platform: c.platform };
    });
  };

  API.getUserCoupons = function() {
    return delay().then(function() {
      var r = [];
      for (var code in MOCK.couponDB) {
        var c = MOCK.couponDB[code];
        r.push({ code: code, value: c.value, type: c.type, desc: c.desc, platform: c.platform, used: c.used });
      }
      return r;
    });
  };

  // ── 清洁/巡检 ──

  API.getCleaningTasks = function() {
    return delay().then(function() { return JSON.parse(JSON.stringify(MOCK.cleaningTasks)); });
  };

  API.getInspections = function() {
    return delay().then(function() { return JSON.parse(JSON.stringify(MOCK.inspections)); });
  };

  // ── 扫码消费（V1.1）──

  /** 扫码验证房间状态（防误扫） */
  API.scanRoomStatus = function(roomId) {
    return delay().then(function() {
      var room = null;
      MOCK.rooms.forEach(function(r) { if (r.roomId === roomId) room = r; });
      if (!room) throw new Error('房间不存在');
      // 模拟有进行中的订单
      var activeOrder = {
        orderId: "ORD001", status: "InUse",
        start: "2026-06-06T10:00:00", end: "2026-06-06T12:00:00"
      };
      return {
        roomId: roomId,
        roomName: room.name,
        storeId: "ST001",
        storeName: "盈隆店",
        status: room.status === 'Active' ? 'Active' : 'Inactive',
        hasActiveOrder: roomId === 'RM004' || roomId === 'RM002',
        activeOrderId: activeOrder.orderId,
        message: '欢迎使用 ' + room.name + '，可扫码加购'
      };
    });
  };

  /** 获取房间扫码账单 */
  API.getScanBill = function(roomId) {
    return delay().then(function() {
      return {
        roomId: roomId,
        roomName: roomId === 'RM004' ? '白沙瓦' : '翡冷翠',
        activeOrderId: 'ORD001',
        billId: 'BILL001',
        billStatus: 'Active',
        billSummary: {
          roomCharge: 180,
          scanTotal: 156,
          pendingPayment: 156,
          totalPaid: 180
        },
        scanOrders: [
          {
            orderId: 'SCAN001', orderNumber: 'SCAN20260606001',
            createdAt: new Date().toISOString(),
            items: [{ productName: '安吉白茶', quantity: 1, subtotal: 68 }],
            totalAmount: 68, status: '挂账中', canCancel: true
          },
          {
            orderId: 'SCAN002', orderNumber: 'SCAN20260606002',
            createdAt: new Date().toISOString(),
            items: [{ productName: '手工茶点A', quantity: 2, subtotal: 76 }],
            totalAmount: 76, status: '挂账中', canCancel: true
          },
          {
            orderId: 'SCAN003', orderNumber: 'SCAN20260606003',
            createdAt: new Date().toISOString(),
            items: [{ productName: '定制茶具A', quantity: 1, subtotal: 12 }],
            totalAmount: 12, status: '挂账中', canCancel: false
          }
        ]
      };
    });
  };

  /** 扫码下单/加购 */
  API.createScanOrder = function(data) {
    return delay(500).then(function() {
      var orderId = 'SCAN' + String(Date.now()).slice(-6);
      return {
        orderId: orderId,
        orderNumber: 'SCAN' + new Date().toISOString().slice(0,10).replace(/-/g,'') + orderId.slice(-4).toUpperCase(),
        roomId: data.roomId,
        storeId: data.storeId,
        totalAmount: data.items.reduce(function(s, i) { return s + (i.unitPrice || 0) * (i.quantity || 1); }, 0),
        itemCount: data.items.length,
        status: 'Completed',
        tags: ['扫码加购'],
        message: '扫码点单成功，已挂入房间账单'
      };
    });
  };

  /** 撤销扫码订单 */
  API.cancelScanOrder = function(orderId) {
    return delay(200).then(function() {
      return {
        success: true,
        orderId: orderId,
        refundStatus: '无需退款（挂账未支付）',
        stockRollback: true,
        cancelledAt: new Date().toISOString(),
        message: '扫码订单已成功撤销'
      };
    });
  };

  /** 结算挂账 */
  API.settleScanBill = function(roomId, data) {
    return delay(500).then(function() {
      return {
        success: true,
        settleId: 'STL' + String(Date.now()).slice(-6),
        roomId: roomId,
        totalAmount: 156,
        memberBalanceUsed: data.useMemberBalance ? 50 : 0,
        paymentAmount: data.useMemberBalance ? 106 : 156,
        paymentMethod: data.paymentMethod || 'WxPay',
        ordersSettled: 3,
        invoiceNumber: data.issueInvoice ? ('INV-20260606-' + String(Date.now()).slice(-4)) : null,
        message: '结算成功，共 3 笔订单'
      };
    });
  };

  // ═══════════════════════════════════════════
  //  5. 导出全局对象
  // ═══════════════════════════════════════════

  win.ERP = {
    SDK: {
      API: API,
      UI: UI,
      Utils: {
        lsGet: lsGet,
        lsSet: lsSet,
        lsRemove: lsRemove,
        formatMoney: function(n) { return '¥' + (n || 0).toFixed(2); },
        getRoomTypeLabel: function(type) {
          var map = { MeetingRoom:'会议室', TeaRoom:'茶室', Exhibition:'展厅', Workspace:'工作间' };
          return map[type] || type;
        },
        getRoomStatusBadge: function(status) {
          var map = { InUse:'使用中', Booked:'已预订', Cleaning:'清洁中', Active:'可用', Maintenance:'维护中' };
          return map[status] || status;
        },
        getDeviceProtocolBadge: function(protocol) {
          var map = { IP:'IP网络', RS485:'485总线', Zigbee:'Zigbee', WiFi:'WiFi' };
          return map[protocol] || protocol;
        },
        todayStr: function() {
          var d = new Date();
          return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
        }
      }
    }
  };

})(window);
