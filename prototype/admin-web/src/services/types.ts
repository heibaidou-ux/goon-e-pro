/**
 * API type definitions matching backend schemas.
 */
export interface LoginResult {
  access_token: string
  token_type: string
  user: UserInfo
}

export interface UserInfo {
  id: number
  username: string
  display_name: string
  role: string
  phone?: string
  is_active: bool
}

export interface ProductCategory {
  id: number
  name: string
  subcategories: string[]
  sort_order: number
}

export interface ProductImage {
  id: number
  product_id: number
  url_original: string
  url_thumbnail?: string
  url_medium?: string
  url_large?: string
  is_cover: bool
  sort_order: number
}

export interface Product {
  id: number
  code: string
  name: string
  brand?: string
  category: string
  sub_category?: string
  spec?: string
  unit?: string
  internal_price: number
  retail_price: number
  market_price: number
  is_food: bool
  shelf_life?: number
  is_active: bool
  status: string
  story?: string
  origin?: string
  brewing_tips?: string
  description?: string
  default_supplier?: string
  lead_time: number
  safe_stock: number
  max_stock: number
  current_stock: number
  images: ProductImage[]
}

export interface ProductListResult {
  total: number
  items: Product[]
  page: number
  page_size: number
}

export interface Store {
  id: number
  store_id: string
  name: string
  address?: string
  phone?: string
  is_active: bool
  rooms: Room[]
}

export interface Room {
  id: number
  room_id: string
  store_id?: string
  name: string
  type?: string
  capacity: number
  floor?: string
  price_per_hour: number
  price_per_half_hour: number
  facilities: string[]
  description?: string
  is_active: bool
}

export interface RoomOrder {
  id: number
  order_id: string
  room_id: string
  customer_name?: string
  customer_phone?: string
  date?: string
  start_time?: string
  end_time?: string
  duration?: number
  total_amount?: number
  status: string
  scene?: string
  door_code?: string
  source?: string
  payment_status?: string
  check_in_time?: string
  check_out_time?: string
  room?: Room
}

export interface IoTDevice {
  device_id: string
  room_id: string
  type: string
  name: string
  ha_entity_id: string
  protocol: string
  slave_id?: number
  sub_address?: number
  status: string
  attributes: Record<string, any>
}

export interface IoTStats {
  total: number
  online: number
  offline: number
  fault: number
  online_rate: number
  unresolved_alerts: number
  total_alerts: number
}

export interface IoTScene {
  scene_id: string
  name: string
  label: string
  trigger_type: string
  applicable_room_types: string[]
  rules: IoTSceneRule[]
}

export interface IoTSceneRule {
  sequence: number
  device_type: string
  action: string
  params: Record<string, any>
}

export interface IoTAlert {
  alert_id: string
  device_id: string
  room_id: string
  room_name: string
  device_type: string
  device_code: string
  severity: string
  type: string
  message: string
  detail: string
  status: string
  assigned_role: string
  assigned_name: string
  created_at: string
}

export interface IoTControlResult {
  success: boolean
  message: string
  device_id: string
  action?: string
  old_state?: Record<string, any>
  new_state?: Record<string, any>
}

export interface ShopOrderItem {
  product_id: number
  product_name: string
  spec?: string
  quantity: number
  unit_price: number
}

export interface ShopOrder {
  id: number
  order_no: string
  customer_name?: string
  customer_phone?: string
  room_id?: string
  table_id?: string
  total_amount: number
  status: string
  payment_method?: string
  note?: string
  items: ShopOrderItem[]
}
