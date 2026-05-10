/**
 * Data sync bridge between customer-mp (localStorage) and admin-web (mock data).
 * Admin-web reads static JSON mock data, merged with any dynamic data
 * created by customer-mp in localStorage.
 */

// Read customer-mp orders from localStorage and merge with mock data
export function getMpOrders(): any[] {
  try {
    const raw = localStorage.getItem('mp_orders')
    if (raw) {
      const orders = JSON.parse(raw)
      return orders.map((o: any) => ({
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
        status: mapMpStatus(o.status),
        doorCode: o.doorCode || '',
        scene: o.scene || null,
        createdAt: o.createdAt || new Date().toISOString(),
        checkInTime: o.checkInTime || null,
        checkOutTime: null,
        paymentStatus: o.paymentStatus || 'Paid',
      }))
    }
  } catch (e) { /* ignore parse errors */ }
  return []
}

// Read customer-mp shop orders
export function getMpShopOrders(): any[] {
  try {
    const raw = localStorage.getItem('mp_shop_orders')
    if (raw) return JSON.parse(raw)
  } catch (e) { /* ignore */ }
  return []
}

// Read customer-mp balance
export function getMpBalance(): number {
  try {
    const user = JSON.parse(localStorage.getItem('mp_user') || 'null')
    return user?.balance || 0
  } catch (e) { /* ignore */ }
  return 0
}

// Read customer-mp user info
export function getMpUser(): any {
  try {
    return JSON.parse(localStorage.getItem('mp_user') || 'null')
  } catch (e) { /* ignore */ }
  return null
}

function mapMpStatus(status: string): string {
  if (status === 'InUse' || status === 'in_use') return 'InUse'
  if (status === 'Booked' || status === 'booked' || status === 'paid') return 'Booked'
  if (status === 'Completed' || status === 'completed') return 'Completed'
  if (status === 'Cancelled' || status === 'cancelled') return 'Cancelled'
  return 'Booked'
}
