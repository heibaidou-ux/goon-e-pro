/**
 * 高岸ERP API Service
 *
 * Centralized API client. All requests go through this module.
 * Toggle `useMock` to switch between mock data and real backend.
 */
import type {
  Product, ProductListResult, ProductCategory,
  Store, Room, RoomOrder, ShopOrder,
  LoginResult, UserInfo,
  IoTDevice, IoTStats, IoTScene, IoTAlert, IoTControlResult,
} from './types'

// ── Config ──
const API_BASE = localStorage.getItem('erp_api_base') || 'http://localhost:8000'
const USE_MOCK = localStorage.getItem('erp_use_mock') !== 'false' // default: mock

// ── Token management ──
function getToken(): string | null {
  return localStorage.getItem('erp_api_token')
}

function setToken(token: string) {
  localStorage.setItem('erp_api_token', token)
}

function clearToken() {
  localStorage.removeItem('erp_api_token')
}

// ── Generic request helper ──
async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  opts?: { noAuth?: boolean; formData?: FormData },
): Promise<T> {
  const headers: Record<string, string> = {}
  if (!opts?.formData) {
    headers['Content-Type'] = 'application/json'
  }
  if (!opts?.noAuth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: opts?.formData ?? (body ? JSON.stringify(body) : undefined),
  })

  if (!res.ok) {
    const text = await res.text().catch(() => 'Unknown error')
    throw new Error(`API ${method} ${path}: ${res.status} ${text}`)
  }

  return res.json()
}

// ── Auth ──
export const authApi = {
  async login(username: string, password: string): Promise<LoginResult> {
    const result = await request<LoginResult>('POST', '/api/auth/login', { username, password }, { noAuth: true })
    setToken(result.access_token)
    return result
  },

  async me(): Promise<UserInfo> {
    return request<UserInfo>('GET', '/api/auth/me')
  },

  logout() {
    clearToken()
  },

  isLoggedIn(): boolean {
    return !!getToken()
  },
}

// ── Products ──
export const productApi = {
  async list(params?: {
    page?: number; page_size?: number; search?: string; category?: string; status?: string
  }): Promise<ProductListResult> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.search) q.set('search', params.search)
    if (params?.category) q.set('category', params.category)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<ProductListResult>('GET', `/api/products${qs ? '?' + qs : ''}`)
  },

  async get(id: number): Promise<Product> {
    return request<Product>('GET', `/api/products/${id}`)
  },

  async create(data: Partial<Product>): Promise<Product> {
    return request<Product>('POST', '/api/products', data)
  },

  async update(id: number, data: Partial<Product>): Promise<Product> {
    return request<Product>('PUT', `/api/products/${id}`, data)
  },

  async delete(id: number): Promise<void> {
    return request('DELETE', `/api/products/${id}`)
  },

  async uploadImages(id: number, files: File[]): Promise<any[]> {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    return request<any[]>('POST', `/api/products/${id}/images`, undefined, { formData })
  },

  async categories(): Promise<ProductCategory[]> {
    return request<ProductCategory[]>('GET', '/api/products/categories')
  },
}

// ── Stores & Rooms ──
export const storeApi = {
  async list(): Promise<Store[]> {
    return request<Store[]>('GET', '/api/stores')
  },
}

export const roomApi = {
  async list(params?: { store_id?: string; type?: string }): Promise<Room[]> {
    const q = new URLSearchParams()
    if (params?.store_id) q.set('store_id', params.store_id)
    if (params?.type) q.set('type', params.type)
    const qs = q.toString()
    return request<Room[]>('GET', `/api/rooms${qs ? '?' + qs : ''}`)
  },

  async get(roomId: string): Promise<Room> {
    return request<Room>('GET', `/api/rooms/${roomId}`)
  },
}

// ── Orders ──
export const orderApi = {
  async list(status?: string): Promise<RoomOrder[]> {
    const q = status ? `?status=${status}` : ''
    return request<RoomOrder[]>('GET', `/api/orders${q}`)
  },

  async active(): Promise<RoomOrder[]> {
    return request<RoomOrder[]>('GET', '/api/orders/active')
  },

  async create(data: Partial<RoomOrder>): Promise<RoomOrder> {
    return request<RoomOrder>('POST', '/api/orders', data)
  },
}

// ── Shop Orders ──
export const shopApi = {
  async list(status?: string): Promise<ShopOrder[]> {
    const q = status ? `?status=${status}` : ''
    return request<ShopOrder[]>('GET', `/api/shop/orders${q}`)
  },

  async create(data: Partial<ShopOrder>): Promise<ShopOrder> {
    return request<ShopOrder>('POST', '/api/shop/orders', data)
  },
}

// ── IoT ──
export const iotApi = {
  async health(): Promise<{ status: string; mode: string }> {
    return request('GET', '/api/iot/health')
  },

  async devices(params?: {
    room_id?: string; type?: string; status?: string
  }): Promise<IoTDevice[]> {
    const q = new URLSearchParams()
    if (params?.room_id) q.set('room_id', params.room_id)
    if (params?.type) q.set('type', params.type)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<IoTDevice[]>('GET', `/api/iot/devices${qs ? '?' + qs : ''}`)
  },

  async getDevice(deviceId: string): Promise<IoTDevice> {
    return request<IoTDevice>('GET', `/api/iot/devices/${deviceId}`)
  },

  async control(deviceId: string, action: string, params?: Record<string, any>): Promise<IoTControlResult> {
    return request<IoTControlResult>('POST', '/api/iot/control', { device_id: deviceId, action, params: params || {} })
  },

  async scenes(): Promise<IoTScene[]> {
    return request<IoTScene[]>('GET', '/api/iot/scenes')
  },

  async activateScene(roomId: string, scene: string): Promise<any> {
    return request('POST', '/api/iot/scenes/activate', { room_id: roomId, scene })
  },

  async alerts(params?: {
    room_id?: string; severity?: string; status?: string
  }): Promise<IoTAlert[]> {
    const q = new URLSearchParams()
    if (params?.room_id) q.set('room_id', params.room_id)
    if (params?.severity) q.set('severity', params.severity)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<IoTAlert[]>('GET', `/api/iot/alerts${qs ? '?' + qs : ''}`)
  },

  async stats(): Promise<IoTStats> {
    return request<IoTStats>('GET', '/api/iot/stats')
  },
}

// ── Mode switch ──
export function useApiMode(): boolean {
  return !USE_MOCK
}

export function setApiMode(useApi: boolean) {
  localStorage.setItem('erp_use_mock', useApi ? 'false' : 'true')
}

export function setApiBase(url: string) {
  localStorage.setItem('erp_api_base', url)
}
