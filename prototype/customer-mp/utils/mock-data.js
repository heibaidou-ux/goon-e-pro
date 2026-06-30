/**
 * 高岸ERP 客人端 Mock 数据
 * 与 prototype/shared-mock/ 保持数据格局一致
 */

// 门店
const stores = [{
  storeId: "ST001", name: "盈隆店", address: "广州市天河区珠江新城富力盈隆广场3801",
  phone: "020-88888888", status: "Active"
}]

// 房间
const rooms = [
  { roomId: "RM001", name: "丰沙里", type: "MeetingRoom", capacity: 10, area: 30,
    facilities: ["投影", "会议桌", "K歌设备", "落地窗"], pricePerHour: 200, pricePerHalfHour: 120, status: "Active", bookable: true },
  { roomId: "RM002", name: "翡冷翠", type: "TeaRoom", capacity: 4, area: 18,
    facilities: ["茶台", "落地窗", "茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
  { roomId: "RM003", name: "布拉格", type: "TeaRoom", capacity: 4, area: 18,
    facilities: ["茶台", "落地窗", "茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
  { roomId: "RM004", name: "白沙瓦", type: "TeaRoom", capacity: 6, area: 25,
    facilities: ["茶台", "K歌", "投影", "落地窗"], pricePerHour: 120, pricePerHalfHour: 75, status: "Active", bookable: true },
  { roomId: "RM005", name: "展厅", type: "Exhibition", capacity: 20, area: 40,
    facilities: ["前台", "收银", "茶具展示", "休闲区"], status: "Active", bookable: false },
  { roomId: "RM006", name: "工作间", type: "Workspace", capacity: 2, area: 12,
    facilities: ["储物", "机柜"], status: "Active", bookable: false }
]

// 设备（客人端可见设备，隐藏继电器等基础设施）
const devices = [
  // ── 丰沙里 RM001 ──
  { deviceId: "DEV001", roomId: "RM001", type: "Light", label: "筒灯1", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV002", roomId: "RM001", type: "Light", label: "筒灯2", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV003", roomId: "RM001", type: "Light", label: "吊灯", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV004", roomId: "RM001", type: "Fan", label: "风扇1", protocol: "RS485", status: "Online", speed: 3 },
  { deviceId: "DEV005", roomId: "RM001", type: "Fan", label: "风扇2", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV006", roomId: "RM001", type: "Fan", label: "风扇3", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV007", roomId: "RM001", type: "AC", label: "空调", protocol: "RS485", status: "Online", temperature: 24, mode: "cool" },
  { deviceId: "DEV008", roomId: "RM001", type: "BGM", label: "背景音乐", protocol: "RS485", status: "Online", playing: false, volume: 50 },
  // ── 翡冷翠 RM002 ──
  { deviceId: "DEV009", roomId: "RM002", type: "Light", label: "吊灯", protocol: "RS485", status: "Online", brightness: 60 },
  { deviceId: "DEV010", roomId: "RM002", type: "Light", label: "筒灯", protocol: "RS485", status: "Online", brightness: 60 },
  { deviceId: "DEV011", roomId: "RM002", type: "ExhaustFan", label: "换气扇", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV012", roomId: "RM002", type: "Fan", label: "风扇", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV013", roomId: "RM002", type: "Curtain", label: "窗帘", protocol: "RS485", status: "Online", position: "closed" },
  { deviceId: "DEV014", roomId: "RM002", type: "BGM", label: "背景音乐", protocol: "RS485", status: "Online", playing: false, volume: 50 },
  // ── 翡冷翠 RM003 ──
  { deviceId: "DEV016", roomId: "RM003", type: "Light", label: "吊灯", protocol: "RS485", status: "Online", brightness: 0 },
  { deviceId: "DEV017", roomId: "RM003", type: "Light", label: "筒灯", protocol: "RS485", status: "Online", brightness: 0 },
  { deviceId: "DEV018", roomId: "RM003", type: "Light", label: "背景灯", protocol: "RS485", status: "Online", brightness: 0 },
  { deviceId: "DEV019", roomId: "RM003", type: "Fan", label: "风扇", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV020", roomId: "RM003", type: "Curtain", label: "窗帘", protocol: "RS485", status: "Online", position: "closed" },
  { deviceId: "DEV024", roomId: "RM003", type: "BGM", label: "背景音乐", protocol: "RS485", status: "Online", playing: false, volume: 50 },
  // ── 白沙瓦 RM004 ──
  { deviceId: "DEV025", roomId: "RM004", type: "Light", label: "吊灯", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV026", roomId: "RM004", type: "Light", label: "筒灯", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV027", roomId: "RM004", type: "Light", label: "背景灯", protocol: "RS485", status: "Online", brightness: 80 },
  { deviceId: "DEV028", roomId: "RM004", type: "Fan", label: "风扇", protocol: "RS485", status: "Online", speed: 0 },
  { deviceId: "DEV029", roomId: "RM004", type: "AC", label: "空调", protocol: "RS485", status: "Online", temperature: 24, mode: "cool" },
  { deviceId: "DEV030", roomId: "RM004", type: "Curtain", label: "窗帘左", protocol: "RS485", status: "Online", position: "open" },
  { deviceId: "DEV031", roomId: "RM004", type: "Curtain", label: "窗帘中", protocol: "RS485", status: "Online", position: "open" },
  { deviceId: "DEV032", roomId: "RM004", type: "Curtain", label: "窗帘右", protocol: "RS485", status: "Online", position: "closed" },
  { deviceId: "DEV033", roomId: "RM004", type: "BGM", label: "背景音乐", protocol: "RS485", status: "Online", playing: true, volume: 70 },
  // ── 展厅 RM005 ──
  { deviceId: "DEV034", roomId: "RM005", type: "BGM", label: "背景音乐", protocol: "RS485", status: "Online", playing: true, volume: 50 },
]

const deviceTypes = {
  Light: { label: "灯光", icon: "💡" },
  AC: { label: "空调", icon: "❄️" },
  Fan: { label: "风扇", icon: "🌀" },
  ExhaustFan: { label: "换气扇", icon: "🌬️" },
  Curtain: { label: "窗帘", icon: "🪟" },
  BGM: { label: "背景音乐", icon: "🎵" }
}

// 订单
const orders = [
  { orderId: "ORD001", customerName: "张先生", roomId: "RM004", roomName: "白沙瓦",
    status: "InUse", start: "2026-06-06T10:00:00", end: "2026-06-06T11:30:00",
    duration: 90, amount: 180, paymentMethod: "WeChat", phone: "138****8888" },
  { orderId: "ORD002", customerName: "李女士", roomId: "RM002", roomName: "翡冷翠",
    status: "Booked", start: "2026-06-06T14:00:00", end: "2026-06-06T16:00:00",
    duration: 120, amount: 160, paymentMethod: "Balance", phone: "139****6666" },
  { orderId: "ORD003", customerName: "王先生", roomId: "RM003", roomName: "布拉格",
    status: "Completed", start: "2026-06-06T08:00:00", end: "2026-06-06T09:30:00",
    duration: 90, amount: 120, paymentMethod: "WeChat", phone: "137****5555" },
  { orderId: "ORD004", customerName: "赵总", roomId: "RM001", roomName: "丰沙里",
    status: "Completed", start: "2026-06-05T15:00:00", end: "2026-06-05T17:00:00",
    duration: 120, amount: 400, paymentMethod: "Alipay", phone: "136****7777" }
]

// 客户
const customers = [
  { customerId: "C001", name: "张先生", phone: "138****8888", level: "Gold", totalSpent: 3200, visitCount: 12, lastVisit: "2026-06-06" },
  { customerId: "C002", name: "李女士", phone: "139****6666", level: "Silver", totalSpent: 1800, visitCount: 6, lastVisit: "2026-06-04" },
  { customerId: "C003", name: "王先生", phone: "137****5555", level: "Silver", totalSpent: 1500, visitCount: 5, lastVisit: "2026-06-06" },
  { customerId: "C004", name: "赵总", phone: "136****7777", level: "Diamond", totalSpent: 8500, visitCount: 28, lastVisit: "2026-06-05" }
]

// 场景
const scenes = [
  { sceneId: "SC001", name: "迎宾模式", icon: "👋", color: "#07c160",
    params: { curtain: "open", lights: { on: true }, ac: { on: true, temp: 26 }, music: { on: true, track: "bgm_welcome" } } },
  { sceneId: "SC002", name: "茶艺模式", icon: "🍵", color: "#e37318",
    params: { curtain: "open", lights: { on: true }, ac: { on: true, temp: 26 }, music: { on: true, track: "bgm_tea" } } },
  { sceneId: "SC003", name: "会议模式", icon: "💼", color: "#0052d9",
    params: { curtain: "closed", lights: { on: true }, ac: { on: true, temp: 22 } } },
  { sceneId: "SC004", name: "娱乐模式", icon: "🎤", color: "#9c27b0",
    params: { curtain: "closed", lights: { on: true }, ac: { on: true, temp: 24 }, music: { on: true, track: "bgm_karaoke" } } },
  { sceneId: "SC005", name: "节能模式", icon: "💚", color: "#607d8b",
    params: { curtain: "closed", lights: { on: false }, ac: { on: false } } },
  { sceneId: "SC006", name: "营业前准备", icon: "🔧", color: "#ff5722",
    params: { curtain: "open", lights: { on: true }, ac: { on: true, temp: 24 }, music: { on: true, track: "bgm_preopen" } } },
  { sceneId: "SC007", name: "打扫完成", icon: "🧹", color: "#607d8b",
    params: { curtain: "closed", lights: { on: false }, ac: { on: false }, music: { on: false } } },
  { sceneId: "PreOpen", name: "空调预开", icon: "⏰", color: "#5D8A6B",
    params: { ac: { on: true, temp: 26 }, music: { on: true, track: "bgm_light" } } }
]

// 商品
const products = [
  { productId: "T001", name: "安吉白茶", category: "Tea", price: 68, desc: "清香甘甜，明前采摘", image: "🍃" },
  { productId: "T002", name: "正山小种", category: "Tea", price: 88, desc: "松烟香，桂圆味", image: "🌿" },
  { productId: "T003", name: "铁观音", category: "Tea", price: 58, desc: "七泡有余香", image: "🍵" },
  { productId: "T004", name: "手工茶点A", category: "Snack", price: 38, desc: "绿豆糕拼盘", image: "🍪" },
  { productId: "T005", name: "手工茶点B", category: "Snack", price: 48, desc: "坚果四宫格", image: "🥜" },
  { productId: "T006", name: "时令水果盘", category: "Snack", price: 58, desc: "当日新鲜水果", image: "🍉" },
  { productId: "T007", name: "定制茶具A", category: "Ware", price: 288, desc: "手作紫砂壶套装", image: "🏺" },
  { productId: "T008", name: "定制茶具B", category: "Ware", price: 188, desc: "玻璃茶道六君子", image: "🥃" }
]

// 优惠券
const couponDB = {
  "MT20260601": { platform: "Meituan", value: 30, type: "discount", used: false, desc: "美团点评 满200减30", expiry: "2026-07-15" },
  "DY20260601": { platform: "Douyin", value: 50, type: "discount", used: false, desc: "抖音团购 满200减50", expiry: "2026-07-20" },
  "DP20260601": { platform: "Dianping", value: 25, type: "discount", used: true, desc: "大众点评 满150减25", expiry: "2026-06-01" },
  "GD20260601": { platform: "Gaode", value: 30, type: "discount", used: false, desc: "高德地图 满200减30", expiry: "2026-07-31" },
  "SY20260601": { platform: "System", value: 50, type: "voucher", used: true, desc: "首充赠送 50元代金券", expiry: "2026-05-01" },
  "SY20260602": { platform: "System", value: 50, type: "voucher", used: false, desc: "首充赠送 50元代金券", expiry: "2026-08-01" }
}

module.exports = {
  stores, rooms, devices, deviceTypes, orders, customers, scenes, products, couponDB
}
