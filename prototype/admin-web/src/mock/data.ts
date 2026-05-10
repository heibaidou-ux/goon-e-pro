import stores from '@mock/stores.json'
import rooms from '@mock/rooms.json'
import devices from '@mock/devices.json'
import scenes from '@mock/scenes.json'
import ordersJson from '@mock/orders.json'
import customers from '@mock/customers.json'
import employees from '@mock/employees.json'
import alerts from '@mock/alerts.json'
import cleaningTasks from '@mock/cleaning-tasks.json'

// Merge static mock orders with customer-mp orders from localStorage
function mergeOrders() {
  try {
    const raw = localStorage.getItem('mp_orders')
    if (raw) {
      const mpOrders = JSON.parse(raw).map((o: any) => ({
        orderId: o.orderId || 'MP' + Date.now(),
        orderNo: o.orderNo || '',
        customerId: o.customerId || '',
        customerName: o.customerName || o.name || '小程序用户',
        customerPhone: o.phone || '',
        roomId: o.roomId || '',
        roomName: o.roomName || '',
        date: o.date || '',
        startTime: o.startTime || '',
        endTime: o.endTime || '',
        duration: o.duration || 0,
        totalAmount: o.totalAmount || o.price || 0,
        status: o.status === 'InUse' || o.status === 'in_use' ? 'InUse'
          : o.status === 'Booked' || o.status === 'booked' || o.status === 'paid' ? 'Booked'
          : o.status === 'Completed' || o.status === 'completed' ? 'Completed'
          : 'Booked',
        doorCode: o.doorCode || '',
        scene: o.scene || null,
        createdAt: o.createdAt || new Date().toISOString(),
        checkInTime: o.checkInTime || null,
        checkOutTime: null,
        paymentStatus: o.paymentStatus || 'Paid',
      }))
      // Deduplicate: remove mock orders that have same orderId as mp orders
      const mpIds = new Set(mpOrders.map((o: any) => o.orderId))
      const filtered = ordersJson.orders.filter((o: any) => !mpIds.has(o.orderId))
      return { orders: [...mpOrders, ...filtered] }
    }
  } catch (e) { /* ignore */ }
  return ordersJson
}

const orders = mergeOrders()

export {
  stores,
  rooms,
  devices,
  scenes,
  orders,
  customers,
  employees,
  alerts,
  cleaningTasks,
}

export function getRoomsByStore(storeId: string) {
  const store = stores.stores.find(s => s.storeId === storeId)
  if (!store) return []
  return rooms.rooms.filter(r => store.rooms.includes(r.roomId))
}

export function getDevicesByRoom(roomId: string) {
  return devices.devices.filter(d => d.roomId === roomId)
}

export function getOrdersByStatus(status: string) {
  return orders.orders.filter(o => o.status === status)
}

export function getActiveOrders() {
  return orders.orders.filter(o => o.status === 'InUse' || o.status === 'Booked')
}

export function getAlertsByStatus(status: string) {
  return alerts.alerts.filter(a => a.status === status)
}

export function getCleaningTasksByStatus(status: string) {
  return cleaningTasks.cleaningTasks.filter(t => t.status === status)
}

export function getRoomStatusColor(status: string): string {
  const map: Record<string, string> = {
    Active: '#00A870',   // 空闲-绿
    Booked: '#9C27B0',   // 已预定-紫
    InUse: '#366EF4',    // 使用中-蓝
    Cleaning: '#D4A017', // 待打扫-黄
    Maintenance: '#D54941', // 维修-红
  }
  return map[status] || '#999'
}

export function getRoomStatusLabel(status: string): string {
  const map: Record<string, string> = {
    Active: '空闲',
    Booked: '已预定',
    InUse: '使用中',
    Cleaning: '待打扫',
    Maintenance: '维修中',
  }
  return map[status] || status
}

export function getDeviceStatusColor(status: string): string {
  const map: Record<string, string> = {
    Online: '#00A870',
    Offline: '#D54941',
    Fault: '#E37318',
    Maintenance: '#366EF4',
  }
  return map[status] || '#999'
}

export function getAlertSeverityColor(severity: string): string {
  const map: Record<string, string> = {
    Error: '#D54941',
    Warning: '#E37318',
    Info: '#366EF4',
  }
  return map[severity] || '#999'
}
