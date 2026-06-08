/**
 * 高岸ERP 客人端 Mock 数据
 * 与 prototype/shared-mock/ 保持数据格局一致
 */

// 门店
const stores = [{
  storeId: "ST001", name: "盈隆店", address: "广州珠江新城盈隆广场",
  phone: "020-88888888", status: "Active"
}]

// 房间
const rooms = [
  { roomId: "RM001", name: "大会议室", type: "MeetingRoom", capacity: 10, area: 30,
    facilities: ["投影", "会议桌", "K歌设备", "落地窗"], pricePerHour: 200, pricePerHalfHour: 120, status: "Active", bookable: true },
  { roomId: "RM002", name: "中茶室A", type: "TeaRoom", capacity: 4, area: 18,
    facilities: ["茶台", "落地窗", "茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
  { roomId: "RM003", name: "中茶室B", type: "TeaRoom", capacity: 4, area: 18,
    facilities: ["茶台", "落地窗", "茶具套装"], pricePerHour: 80, pricePerHalfHour: 50, status: "Active", bookable: true },
  { roomId: "RM004", name: "大茶室C", type: "TeaRoom", capacity: 6, area: 25,
    facilities: ["茶台", "K歌", "投影", "落地窗"], pricePerHour: 120, pricePerHalfHour: 75, status: "Active", bookable: true },
  { roomId: "RM005", name: "展厅", type: "Exhibition", capacity: 20, area: 40,
    facilities: ["前台", "收银", "茶具展示", "休闲区"], status: "Active", bookable: false },
  { roomId: "RM006", name: "工作间", type: "Workspace", capacity: 2, area: 12,
    facilities: ["储物", "机柜"], status: "Active", bookable: false }
]

// 设备
const devices = [
  { deviceId: "DEV001", roomId: "RM001", type: "Lock", protocol: "Zigbee", status: "Online", batteryLevel: 85 },
  { deviceId: "DEV002", roomId: "RM001", type: "AC", protocol: "RS485", status: "Online", temperature: 24, mode: "cool" },
  { deviceId: "DEV003", roomId: "RM001", type: "Light", protocol: "RS485", status: "Online", brightness: 80, colorTemp: 4000 },
  { deviceId: "DEV004", roomId: "RM001", type: "Light", protocol: "RS485", status: "Online", brightness: 80, colorTemp: 4000 },
  { deviceId: "DEV005", roomId: "RM001", type: "Curtain", protocol: "RS485", status: "Online", position: "closed" },
  { deviceId: "DEV006", roomId: "RM001", type: "Speaker", protocol: "IP", status: "Online", volume: 70, playing: true, source: "bgm" },
  { deviceId: "DEV007", roomId: "RM001", type: "Speaker", protocol: "IP", status: "Online", volume: 70, playing: true, source: "bgm" },
  { deviceId: "DEV008", roomId: "RM002", type: "Lock", protocol: "Zigbee", status: "Offline", batteryLevel: 0 },
  { deviceId: "DEV009", roomId: "RM002", type: "AC", protocol: "RS485", status: "Online", temperature: 26, mode: "cool" },
  { deviceId: "DEV010", roomId: "RM002", type: "Light", protocol: "RS485", status: "Online", brightness: 60, colorTemp: 3000 },
  { deviceId: "DEV011", roomId: "RM002", type: "Light", protocol: "RS485", status: "Online", brightness: 60, colorTemp: 3000 },
  { deviceId: "DEV012", roomId: "RM002", type: "Curtain", protocol: "RS485", status: "Online", position: "closed" },
  { deviceId: "DEV013", roomId: "RM002", type: "Speaker", protocol: "IP", status: "Online", volume: 50, playing: false, source: "bgm" },
  { deviceId: "DEV014", roomId: "RM003", type: "Lock", protocol: "Zigbee", status: "Online", batteryLevel: 92 },
  { deviceId: "DEV015", roomId: "RM003", type: "AC", protocol: "RS485", status: "Online", temperature: 26, mode: "off" },
  { deviceId: "DEV016", roomId: "RM003", type: "Light", protocol: "RS485", status: "Online", brightness: 0, colorTemp: 3000 },
  { deviceId: "DEV017", roomId: "RM003", type: "Light", protocol: "RS485", status: "Online", brightness: 0, colorTemp: 3000 },
  { deviceId: "DEV018", roomId: "RM003", type: "Curtain", protocol: "RS485", status: "Online", position: "open" },
  { deviceId: "DEV019", roomId: "RM003", type: "Speaker", protocol: "IP", status: "Online", volume: 0, playing: false, source: "bgm" },
  { deviceId: "DEV020", roomId: "RM004", type: "Lock", protocol: "Zigbee", status: "Online", batteryLevel: 73 },
  { deviceId: "DEV021", roomId: "RM004", type: "AC", protocol: "RS485", status: "Online", temperature: 24, mode: "cool" },
  { deviceId: "DEV022", roomId: "RM004", type: "Light", protocol: "RS485", status: "Online", brightness: 80, colorTemp: 3000 },
  { deviceId: "DEV023", roomId: "RM004", type: "Light", protocol: "RS485", status: "Online", brightness: 80, colorTemp: 3000 },
  { deviceId: "DEV024", roomId: "RM004", type: "Light", protocol: "RS485", status: "Online", brightness: 80, colorTemp: 3000 },
  { deviceId: "DEV025", roomId: "RM004", type: "Curtain", protocol: "RS485", status: "Online", position: "open" },
  { deviceId: "DEV026", roomId: "RM004", type: "Speaker", protocol: "IP", status: "Online", volume: 70, playing: true, source: "bgm" },
  { deviceId: "DEV027", roomId: "RM005", type: "AC", protocol: "RS485", status: "Online", temperature: 26, mode: "cool" },
  { deviceId: "DEV028", roomId: "RM005", type: "Light", protocol: "RS485", status: "Online", brightness: 90, colorTemp: 4000 },
  { deviceId: "DEV029", roomId: "RM005", type: "Light", protocol: "RS485", status: "Online", brightness: 90, colorTemp: 4000 },
  { deviceId: "DEV030", roomId: "RM005", type: "Light", protocol: "RS485", status: "Online", brightness: 90, colorTemp: 4000 },
  { deviceId: "DEV031", roomId: "RM005", type: "Light", protocol: "RS485", status: "Online", brightness: 90, colorTemp: 4000 },
  { deviceId: "DEV032", roomId: "RM005", type: "Speaker", protocol: "IP", status: "Online", volume: 50, playing: true, source: "bgm" },
  { deviceId: "DEV033", roomId: "RM005", type: "Speaker", protocol: "IP", status: "Online", volume: 50, playing: true, source: "bgm" },
  { deviceId: "DEV034", roomId: "RM006", type: "Light", protocol: "RS485", status: "Online", brightness: 50, colorTemp: 4000 }
]

const deviceTypes = {
  Lock: { label: "门锁", icon: "🔒" },
  AC: { label: "空调", icon: "❄️" },
  Light: { label: "灯光", icon: "💡" },
  Curtain: { label: "窗帘", icon: "🪟" },
  Speaker: { label: "音响", icon: "🔊" },
  Sensor: { label: "传感器", icon: "📡" }
}

// 订单
const orders = [
  { orderId: "ORD001", customerName: "张先生", roomId: "RM004", roomName: "大茶室C",
    status: "InUse", start: "2026-06-06T10:00:00", end: "2026-06-06T11:30:00",
    duration: 90, amount: 180, paymentMethod: "WeChat", phone: "138****8888" },
  { orderId: "ORD002", customerName: "李女士", roomId: "RM002", roomName: "中茶室A",
    status: "Booked", start: "2026-06-06T14:00:00", end: "2026-06-06T16:00:00",
    duration: 120, amount: 160, paymentMethod: "Balance", phone: "139****6666" },
  { orderId: "ORD003", customerName: "王先生", roomId: "RM003", roomName: "中茶室B",
    status: "Completed", start: "2026-06-06T08:00:00", end: "2026-06-06T09:30:00",
    duration: 90, amount: 120, paymentMethod: "WeChat", phone: "137****5555" },
  { orderId: "ORD004", customerName: "赵总", roomId: "RM001", roomName: "大会议室",
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
    params: { curtain: "open", lights: { on: true, brightness: 90, colorTemp: 4000 }, ac: { on: true, temp: 24 }, music: { on: true, track: "bgm_welcome" } } },
  { sceneId: "SC002", name: "茶艺模式", icon: "🍵", color: "#e37318",
    params: { curtain: "open", lights: { on: true, brightness: 70, colorTemp: 3000 }, ac: { on: true, temp: 26 }, music: { on: true, track: "bgm_tea" } } },
  { sceneId: "SC003", name: "会议模式", icon: "💼", color: "#0052d9",
    params: { curtain: "closed", lights: { on: true, brightness: 100, colorTemp: 5000 }, ac: { on: true, temp: 22 } } },
  { sceneId: "SC004", name: "娱乐模式", icon: "🎤", color: "#9c27b0",
    params: { curtain: "closed", lights: { on: true, brightness: 60, colorTemp: 2500 }, ac: { on: true, temp: 24 }, music: { on: true, track: "bgm_karaoke" } } },
  { sceneId: "SC005", name: "节能模式", icon: "💚", color: "#607d8b",
    params: { curtain: "closed", lights: { on: false, brightness: 0 }, ac: { on: false } } },
  { sceneId: "SC006", name: "营业前准备", icon: "🔧", color: "#ff5722",
    params: { curtain: "open", lights: { on: true, brightness: 100, colorTemp: 5000 }, ac: { on: true, temp: 24 }, music: { on: true, track: "bgm_preopen" } } }
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
