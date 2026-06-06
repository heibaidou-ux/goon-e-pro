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
  RevenueFlow, RevenueFlowListResult, ExpenseRecord, ExpenseRecordListResult,
  FixedAsset, FixedAssetListResult, DailySettlementOut, MonthlySettlementOut,
  ReconciliationTicketOut, DividendRecordOut, FinanceDashboard,
  Warehouse, InventoryItem, InventoryListResult,
  Organization, BusinessGoal, GoalMetric, BrandAsset, Contract, Shareholder, Investment, Milestone,
  LegalEntity, StoreSiteSelection, StoreConstruction, ConstructionCost, DesignDrawing,
  RoomPricing, RoomPersonPricing, TimeSlotCoefficient, HolidayCalendar, ActivityCalendar,
  DurationDiscountRule, NightPackage,
  Customer, MemberCard, RechargeRecord, RoomAppointment, RoomStatusEntry,
  CleaningTask, InspectionTemplate, InspectionTask, RectificationTask,
  Campaign, CouponTemplate, CouponEntry, Lead, Opportunity, ThirdPartyActivity,
  AccountSubject, JournalEntry, BudgetEntry, AdvanceRequest, ReimbursementEntry,
  PaymentEntry, AccountsPayable, BankAccount, Invoice,
  Department, Position, Employee, ExternalStaff, ScheduleEntry, AttendanceEntry,
  LeaveRequestEntry, PayrollEntry, PerformanceReviewEntry,
  AuditLogEntry, AlertRule, SystemJob, BackupRecord, DeviceEvent, CommandQueueEntry,
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
    page?: number; page_size?: number; search?: string; categoryId?: string; status?: string
  }): Promise<ProductListResult> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.search) q.set('search', params.search)
    if (params?.categoryId) q.set('categoryId', params.categoryId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<ProductListResult>('GET', `/api/products${qs ? '?' + qs : ''}`)
  },

  async get(productId: string): Promise<Product> {
    return request<Product>('GET', `/api/products/${productId}`)
  },

  async create(data: Partial<Product>): Promise<Product> {
    return request<Product>('POST', '/api/products', data)
  },

  async update(productId: string, data: Partial<Product>): Promise<Product> {
    return request<Product>('PUT', `/api/products/${productId}`, data)
  },

  async delete(productId: string): Promise<void> {
    return request('DELETE', `/api/products/${productId}`)
  },

  async uploadImages(productId: string, files: File[]): Promise<any[]> {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    return request<any[]>('POST', `/api/products/${productId}/images`, undefined, { formData })
  },

  async categories(): Promise<ProductCategory[]> {
    return request<ProductCategory[]>('GET', '/api/products/categories')
  },

  // ── Inventory ──
  async warehouses(params?: { storeId?: string }): Promise<Warehouse[]> {
    const q = params?.storeId ? `?storeId=${params.storeId}` : ''
    return request<Warehouse[]>('GET', `/api/products/warehouses${q}`)
  },

  async inventory(params?: {
    page?: number; page_size?: number; warehouseId?: string; productId?: string
  }): Promise<InventoryListResult> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.warehouseId) q.set('warehouseId', params.warehouseId)
    if (params?.productId) q.set('productId', params.productId)
    const qs = q.toString()
    return request<InventoryListResult>('GET', `/api/products/inventory${qs ? '?' + qs : ''}`)
  },

  async adjustInventory(data: { warehouseId: string; productId: string; quantity: number }): Promise<any> {
    return request('PUT', '/api/products/inventory/adjust', data)
  },

  async inventoryLots(params?: {
    page?: number; page_size?: number; warehouseId?: string; productId?: string
  }): Promise<{ total: number; items: any[]; page: number; page_size: number }> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.warehouseId) q.set('warehouseId', params.warehouseId)
    if (params?.productId) q.set('productId', params.productId)
    const qs = q.toString()
    return request('GET', `/api/products/inventory-lots${qs ? '?' + qs : ''}`)
  },

  async stockCounts(params?: {
    page?: number; page_size?: number; status?: string; warehouseId?: string
  }): Promise<any> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.status) q.set('status', params.status)
    if (params?.warehouseId) q.set('warehouseId', params.warehouseId)
    const qs = q.toString()
    return request('GET', `/api/products/stock-counts${qs ? '?' + qs : ''}`)
  },

  async createStockCount(data: any): Promise<any> {
    return request('POST', '/api/products/stock-counts', data)
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

// ── Finance (记账管理) ──
export const financeApi = {
  async listRevenue(params?: {
    storeId?: string; startDate?: string; endDate?: string; type?: string; page?: number; page_size?: number
  }): Promise<RevenueFlowListResult> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.startDate) q.set('startDate', params.startDate)
    if (params?.endDate) q.set('endDate', params.endDate)
    if (params?.type) q.set('type', params.type)
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    const qs = q.toString()
    return request<RevenueFlowListResult>('GET', `/api/finance/revenue${qs ? '?' + qs : ''}`)
  },

  async revenueStats(params?: { storeId?: string; days?: number }): Promise<any> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.days) q.set('days', String(params.days))
    const qs = q.toString()
    return request<any>('GET', `/api/finance/revenue/stats${qs ? '?' + qs : ''}`)
  },

  async createRevenue(data: Partial<RevenueFlow>): Promise<RevenueFlow> {
    return request<RevenueFlow>('POST', '/api/finance/revenue', data)
  },

  async listExpenses(params?: {
    storeId?: string; category?: string; status?: string; startDate?: string; endDate?: string
  }): Promise<ExpenseRecordListResult> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.category) q.set('category', params.category)
    if (params?.status) q.set('status', params.status)
    if (params?.startDate) q.set('startDate', params.startDate)
    if (params?.endDate) q.set('endDate', params.endDate)
    const qs = q.toString()
    return request<ExpenseRecordListResult>('GET', `/api/finance/expenses${qs ? '?' + qs : ''}`)
  },

  async createExpense(data: Partial<ExpenseRecord>): Promise<ExpenseRecord> {
    return request<ExpenseRecord>('POST', '/api/finance/expenses', data)
  },

  async updateExpense(expenseId: string, data: Partial<ExpenseRecord>): Promise<ExpenseRecord> {
    return request<ExpenseRecord>('PUT', `/api/finance/expenses/${expenseId}`, data)
  },

  async listDailySettlements(params?: { storeId?: string; status?: string }): Promise<DailySettlementOut[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<DailySettlementOut[]>('GET', `/api/finance/settlements/daily${qs ? '?' + qs : ''}`)
  },

  async createDailySettlement(storeId: string, settlementDate: string): Promise<DailySettlementOut> {
    return request<DailySettlementOut>('POST', '/api/finance/settlements/daily', { storeId, settlementDate })
  },

  async listMonthlySettlements(storeId?: string): Promise<MonthlySettlementOut[]> {
    const q = storeId ? `?storeId=${storeId}` : ''
    return request<MonthlySettlementOut[]>('GET', `/api/finance/settlements/monthly${q}`)
  },

  async runMonthlySettlement(storeId: string, yearMonth: string): Promise<MonthlySettlementOut> {
    return request<MonthlySettlementOut>('POST', `/api/finance/settlements/monthly/run?storeId=${storeId}&yearMonth=${yearMonth}`)
  },

  async listReconciliationTickets(params?: { storeId?: string; status?: string }): Promise<ReconciliationTicketOut[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<ReconciliationTicketOut[]>('GET', `/api/finance/reconciliation/tickets${qs ? '?' + qs : ''}`)
  },

  async listDividends(params?: { storeId?: string; status?: string }): Promise<DividendRecordOut[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<DividendRecordOut[]>('GET', `/api/finance/dividends${qs ? '?' + qs : ''}`)
  },

  async listAssets(params?: {
    storeId?: string; category?: string; status?: string; search?: string; page?: number; page_size?: number
  }): Promise<FixedAssetListResult> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.category) q.set('category', params.category)
    if (params?.status) q.set('status', params.status)
    if (params?.search) q.set('search', params.search)
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    const qs = q.toString()
    return request<FixedAssetListResult>('GET', `/api/finance/assets${qs ? '?' + qs : ''}`)
  },

  async getAsset(assetId: string): Promise<FixedAsset> {
    return request<FixedAsset>('GET', `/api/finance/assets/${assetId}`)
  },

  async createAsset(data: Partial<FixedAsset>): Promise<FixedAsset> {
    return request<FixedAsset>('POST', '/api/finance/assets', data)
  },

  async updateAsset(assetId: string, data: Partial<FixedAsset>): Promise<FixedAsset> {
    return request<FixedAsset>('PUT', `/api/finance/assets/${assetId}`, data)
  },

  async dashboard(storeId?: string): Promise<FinanceDashboard> {
    const q = storeId ? `?storeId=${storeId}` : ''
    return request<FinanceDashboard>('GET', `/api/finance/dashboard${q}`)
  },
}

// ═══════════════════════════════════════════
// D01 Brand Operations (品牌运营)
// ═══════════════════════════════════════════
export const brandApi = {
  async listOrganizations(): Promise<Organization[]> {
    return request<Organization[]>('GET', '/api/brand/orgs')
  },
  async getOrganization(orgId: string): Promise<Organization> {
    return request<Organization>('GET', `/api/brand/orgs/${orgId}`)
  },
  async createOrganization(data: Partial<Organization>): Promise<Organization> {
    return request<Organization>('POST', '/api/brand/orgs', data)
  },
  async updateOrganization(orgId: string, data: Partial<Organization>): Promise<Organization> {
    return request<Organization>('PUT', `/api/brand/orgs/${orgId}`, data)
  },
  async deleteOrganization(orgId: string): Promise<void> {
    return request('DELETE', `/api/brand/orgs/${orgId}`)
  },
  async organizationTree(): Promise<Organization[]> {
    return request<Organization[]>('GET', '/api/brand/orgs/tree')
  },

  async listBusinessGoals(params?: { orgId?: string; year?: number }): Promise<BusinessGoal[]> {
    const q = new URLSearchParams()
    if (params?.orgId) q.set('orgId', params.orgId)
    if (params?.year) q.set('year', String(params.year))
    const qs = q.toString()
    return request<BusinessGoal[]>('GET', `/api/brand/goals${qs ? '?' + qs : ''}`)
  },
  async createBusinessGoal(data: Partial<BusinessGoal>): Promise<BusinessGoal> {
    return request<BusinessGoal>('POST', '/api/brand/goals', data)
  },
  async updateBusinessGoal(goalId: string, data: Partial<BusinessGoal>): Promise<BusinessGoal> {
    return request<BusinessGoal>('PUT', `/api/brand/goals/${goalId}`, data)
  },

  async listContracts(params?: { orgId?: string; status?: string }): Promise<Contract[]> {
    const q = new URLSearchParams()
    if (params?.orgId) q.set('orgId', params.orgId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<Contract[]>('GET', `/api/brand/contracts${qs ? '?' + qs : ''}`)
  },
  async createContract(data: Partial<Contract>): Promise<Contract> {
    return request<Contract>('POST', '/api/brand/contracts', data)
  },
  async updateContract(contractId: string, data: Partial<Contract>): Promise<Contract> {
    return request<Contract>('PUT', `/api/brand/contracts/${contractId}`, data)
  },

  async listShareholders(params?: { status?: string }): Promise<Shareholder[]> {
    const q = params?.status ? `?status=${params.status}` : ''
    return request<Shareholder[]>('GET', `/api/brand/shareholders${q}`)
  },
  async createShareholder(data: Partial<Shareholder>): Promise<Shareholder> {
    return request<Shareholder>('POST', '/api/brand/shareholders', data)
  },
  async updateShareholder(shareholderId: string, data: Partial<Shareholder>): Promise<Shareholder> {
    return request<Shareholder>('PUT', `/api/brand/shareholders/${shareholderId}`, data)
  },

  async listBrandAssets(orgId?: string): Promise<BrandAsset[]> {
    const q = orgId ? `?orgId=${orgId}` : ''
    return request<BrandAsset[]>('GET', `/api/brand/assets${q}`)
  },
  async createBrandAsset(data: Partial<BrandAsset>): Promise<BrandAsset> {
    return request<BrandAsset>('POST', '/api/brand/assets', data)
  },
}

// ═══════════════════════════════════════════
// D02 Store Development (门店拓展 - 扩展)
// ═══════════════════════════════════════════
export const storeDevApi = {
  async listLegalEntities(): Promise<LegalEntity[]> {
    return request<LegalEntity[]>('GET', '/api/store-dev/legal-entities')
  },
  async createLegalEntity(data: Partial<LegalEntity>): Promise<LegalEntity> {
    return request<LegalEntity>('POST', '/api/store-dev/legal-entities', data)
  },
  async updateLegalEntity(entityId: string, data: Partial<LegalEntity>): Promise<LegalEntity> {
    return request<LegalEntity>('PUT', `/api/store-dev/legal-entities/${entityId}`, data)
  },

  async listSiteSelections(params?: { status?: string }): Promise<StoreSiteSelection[]> {
    const q = params?.status ? `?status=${params.status}` : ''
    return request<StoreSiteSelection[]>('GET', `/api/store-dev/site-selections${q}`)
  },
  async createSiteSelection(data: Partial<StoreSiteSelection>): Promise<StoreSiteSelection> {
    return request<StoreSiteSelection>('POST', '/api/store-dev/site-selections', data)
  },
  async updateSiteSelection(selectionId: string, data: Partial<StoreSiteSelection>): Promise<StoreSiteSelection> {
    return request<StoreSiteSelection>('PUT', `/api/store-dev/site-selections/${selectionId}`, data)
  },

  async listConstructions(storeId?: string): Promise<StoreConstruction[]> {
    const q = storeId ? `?storeId=${storeId}` : ''
    return request<StoreConstruction[]>('GET', `/api/store-dev/constructions${q}`)
  },
  async createConstruction(data: Partial<StoreConstruction>): Promise<StoreConstruction> {
    return request<StoreConstruction>('POST', '/api/store-dev/constructions', data)
  },
  async updateConstruction(constructionId: string, data: Partial<StoreConstruction>): Promise<StoreConstruction> {
    return request<StoreConstruction>('PUT', `/api/store-dev/constructions/${constructionId}`, data)
  },

  async listRoomPricings(roomId: string): Promise<RoomPricing[]> {
    return request<RoomPricing[]>('GET', `/api/store-dev/room-pricings?roomId=${roomId}`)
  },
  async createRoomPricing(data: Partial<RoomPricing>): Promise<RoomPricing> {
    return request<RoomPricing>('POST', '/api/store-dev/room-pricings', data)
  },

  async listTimeSlotCoefficients(storeId: string): Promise<TimeSlotCoefficient[]> {
    return request<TimeSlotCoefficient[]>('GET', `/api/store-dev/time-slot-coefficients?storeId=${storeId}`)
  },
  async createTimeSlotCoefficient(data: Partial<TimeSlotCoefficient>): Promise<TimeSlotCoefficient> {
    return request<TimeSlotCoefficient>('POST', '/api/store-dev/time-slot-coefficients', data)
  },

  async listHolidayCalendars(): Promise<HolidayCalendar[]> {
    return request<HolidayCalendar[]>('GET', '/api/store-dev/holiday-calendars')
  },
  async listActivityCalendars(storeId: string): Promise<ActivityCalendar[]> {
    return request<ActivityCalendar[]>('GET', `/api/store-dev/activity-calendars?storeId=${storeId}`)
  },
  async listDurationDiscountRules(storeId: string): Promise<DurationDiscountRule[]> {
    return request<DurationDiscountRule[]>('GET', `/api/store-dev/duration-discount-rules?storeId=${storeId}`)
  },
  async listNightPackages(storeId: string): Promise<NightPackage[]> {
    return request<NightPackage[]>('GET', `/api/store-dev/night-packages?storeId=${storeId}`)
  },
}

// ═══════════════════════════════════════════
// D03 Operations (门店运营 - 扩展)
// ═══════════════════════════════════════════
export const operationsApi = {
  async searchCustomers(params?: { phone?: string; name?: string; wxOpenId?: string }): Promise<Customer[]> {
    const q = new URLSearchParams()
    if (params?.phone) q.set('phone', params.phone)
    if (params?.name) q.set('name', params.name)
    if (params?.wxOpenId) q.set('wxOpenId', params.wxOpenId)
    const qs = q.toString()
    return request<Customer[]>('GET', `/api/operations/customers/search${qs ? '?' + qs : ''}`)
  },
  async listCustomers(params?: { page?: number; page_size?: number }): Promise<{ total: number; items: Customer[]; page: number; page_size: number }> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    const qs = q.toString()
    return request('GET', `/api/operations/customers${qs ? '?' + qs : ''}`)
  },
  async getCustomer(customerId: string): Promise<Customer> {
    return request<Customer>('GET', `/api/operations/customers/${customerId}`)
  },
  async createCustomer(data: Partial<Customer>): Promise<Customer> {
    return request<Customer>('POST', '/api/operations/customers', data)
  },

  async getMemberCard(customerId: string): Promise<MemberCard> {
    return request<MemberCard>('GET', `/api/operations/member-cards/by-customer/${customerId}`)
  },
  async createMemberCard(data: Partial<MemberCard>): Promise<MemberCard> {
    return request<MemberCard>('POST', '/api/operations/member-cards', data)
  },
  async rechargeMemberCard(cardId: string, data: Partial<RechargeRecord>): Promise<RechargeRecord> {
    return request<RechargeRecord>('POST', `/api/operations/member-cards/${cardId}/recharge`, data)
  },

  async getRoomStatus(roomId: string): Promise<RoomStatusEntry> {
    return request<RoomStatusEntry>('GET', `/api/operations/room-status/current/${roomId}`)
  },
  async updateRoomStatus(roomId: string, data: Partial<RoomStatusEntry>): Promise<RoomStatusEntry> {
    return request<RoomStatusEntry>('PUT', `/api/operations/room-status/${roomId}`, data)
  },

  async listCleaningTasks(params?: { storeId?: string; status?: string }): Promise<CleaningTask[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<CleaningTask[]>('GET', `/api/operations/cleaning-tasks${qs ? '?' + qs : ''}`)
  },
  async getTodayCleaningTasks(storeId: string): Promise<CleaningTask[]> {
    return request<CleaningTask[]>('GET', `/api/operations/cleaning-tasks/today?storeId=${storeId}`)
  },
  async updateCleaningTaskStatus(taskId: string, status: string): Promise<CleaningTask> {
    return request<CleaningTask>('PUT', `/api/operations/cleaning-tasks/${taskId}/status`, { status })
  },

  async listInspectionTemplates(storeId: string): Promise<InspectionTemplate[]> {
    return request<InspectionTemplate[]>('GET', `/api/operations/inspection-templates?storeId=${storeId}`)
  },
  async createInspectionTask(data: Partial<InspectionTask>): Promise<InspectionTask> {
    return request<InspectionTask>('POST', '/api/operations/inspection-tasks', data)
  },
  async listPendingInspections(storeId: string): Promise<InspectionTask[]> {
    return request<InspectionTask[]>('GET', `/api/operations/inspection-tasks/pending?storeId=${storeId}`)
  },
  async listRectificationTasks(inspectionId: string): Promise<RectificationTask[]> {
    return request<RectificationTask[]>('GET', `/api/operations/rectification-tasks?inspectionId=${inspectionId}`)
  },
}

// ═══════════════════════════════════════════
// D04 Marketing (市场营销)
// ═══════════════════════════════════════════
export const marketingApi = {
  async listCampaigns(params?: { storeId?: string; status?: string }): Promise<Campaign[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<Campaign[]>('GET', `/api/marketing/campaigns${qs ? '?' + qs : ''}`)
  },
  async createCampaign(data: Partial<Campaign>): Promise<Campaign> {
    return request<Campaign>('POST', '/api/marketing/campaigns', data)
  },
  async updateCampaign(campaignId: string, data: Partial<Campaign>): Promise<Campaign> {
    return request<Campaign>('PUT', `/api/marketing/campaigns/${campaignId}`, data)
  },

  async listCouponTemplates(): Promise<CouponTemplate[]> {
    return request<CouponTemplate[]>('GET', '/api/marketing/coupon-templates')
  },
  async createCouponTemplate(data: Partial<CouponTemplate>): Promise<CouponTemplate> {
    return request<CouponTemplate>('POST', '/api/marketing/coupon-templates', data)
  },

  async getCouponsByCustomer(customerId: string): Promise<CouponEntry[]> {
    return request<CouponEntry[]>('GET', `/api/marketing/coupons/by-customer/${customerId}`)
  },
  async verifyCoupon(code: string): Promise<CouponEntry> {
    return request<CouponEntry>('GET', `/api/marketing/coupons/verify?code=${code}`)
  },

  async listLeads(params?: { status?: string }): Promise<Lead[]> {
    const q = params?.status ? `?status=${params.status}` : ''
    return request<Lead[]>('GET', `/api/marketing/leads${q}`)
  },
  async createLead(data: Partial<Lead>): Promise<Lead> {
    return request<Lead>('POST', '/api/marketing/leads', data)
  },
  async updateLead(leadId: string, data: Partial<Lead>): Promise<Lead> {
    return request<Lead>('PUT', `/api/marketing/leads/${leadId}`, data)
  },

  async listOpportunities(params?: { storeId?: string; status?: string }): Promise<Opportunity[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<Opportunity[]>('GET', `/api/marketing/opportunities${qs ? '?' + qs : ''}`)
  },
  async createOpportunity(data: Partial<Opportunity>): Promise<Opportunity> {
    return request<Opportunity>('POST', '/api/marketing/opportunities', data)
  },

  async listThirdPartyActivities(params?: { storeId?: string; platform?: string }): Promise<ThirdPartyActivity[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.platform) q.set('platform', params.platform)
    const qs = q.toString()
    return request<ThirdPartyActivity[]>('GET', `/api/marketing/third-party-activities${qs ? '?' + qs : ''}`)
  },
  async createThirdPartyActivity(data: Partial<ThirdPartyActivity>): Promise<ThirdPartyActivity> {
    return request<ThirdPartyActivity>('POST', '/api/marketing/third-party-activities', data)
  },
}

// ═══════════════════════════════════════════
// D06 Finance Ext (财务管理扩展)
// ═══════════════════════════════════════════
export const financeExtApi = {
  async getAccountSubjectTree(): Promise<AccountSubject[]> {
    return request<AccountSubject[]>('GET', '/api/finance-ext/account-subjects/tree')
  },
  async createAccountSubject(data: Partial<AccountSubject>): Promise<AccountSubject> {
    return request<AccountSubject>('POST', '/api/finance-ext/account-subjects', data)
  },

  async listJournalEntries(params?: { status?: string; periodId?: string }): Promise<JournalEntry[]> {
    const q = new URLSearchParams()
    if (params?.status) q.set('status', params.status)
    if (params?.periodId) q.set('periodId', params.periodId)
    const qs = q.toString()
    return request<JournalEntry[]>('GET', `/api/finance-ext/journal-entries${qs ? '?' + qs : ''}`)
  },
  async createJournalEntry(data: Partial<JournalEntry>): Promise<JournalEntry> {
    return request<JournalEntry>('POST', '/api/finance-ext/journal-entries', data)
  },
  async postJournalEntry(entryId: string): Promise<JournalEntry> {
    return request<JournalEntry>('POST', `/api/finance-ext/journal-entries/${entryId}/post`)
  },

  async listBudgets(params?: { storeId?: string; year?: number }): Promise<BudgetEntry[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.year) q.set('year', String(params.year))
    const qs = q.toString()
    return request<BudgetEntry[]>('GET', `/api/finance-ext/budgets${qs ? '?' + qs : ''}`)
  },
  async createBudget(data: Partial<BudgetEntry>): Promise<BudgetEntry> {
    return request<BudgetEntry>('POST', '/api/finance-ext/budgets', data)
  },
  async getBudgetComparison(params: { storeId: string; year: number }): Promise<any> {
    return request<any>('GET', `/api/finance-ext/budgets/comparison?storeId=${params.storeId}&year=${params.year}`)
  },

  async listAdvanceRequests(params?: { storeId?: string; status?: string }): Promise<AdvanceRequest[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<AdvanceRequest[]>('GET', `/api/finance-ext/advance-requests${qs ? '?' + qs : ''}`)
  },
  async createAdvanceRequest(data: Partial<AdvanceRequest>): Promise<AdvanceRequest> {
    return request<AdvanceRequest>('POST', '/api/finance-ext/advance-requests', data)
  },

  async listReimbursements(params?: { storeId?: string; status?: string }): Promise<ReimbursementEntry[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<ReimbursementEntry[]>('GET', `/api/finance-ext/reimbursements${qs ? '?' + qs : ''}`)
  },
  async createReimbursement(data: Partial<ReimbursementEntry>): Promise<ReimbursementEntry> {
    return request<ReimbursementEntry>('POST', '/api/finance-ext/reimbursements', data)
  },

  async listAccountsPayable(params?: { storeId?: string; status?: string }): Promise<AccountsPayable[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<AccountsPayable[]>('GET', `/api/finance-ext/accounts-payable${qs ? '?' + qs : ''}`)
  },

  async listBankAccounts(legalEntityId: string): Promise<BankAccount[]> {
    return request<BankAccount[]>('GET', `/api/finance-ext/bank-accounts?legalEntityId=${legalEntityId}`)
  },

  async listInvoices(params?: { storeId?: string; direction?: string }): Promise<Invoice[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.direction) q.set('direction', params.direction)
    const qs = q.toString()
    return request<Invoice[]>('GET', `/api/finance-ext/invoices${qs ? '?' + qs : ''}`)
  },
  async createInvoice(data: Partial<Invoice>): Promise<Invoice> {
    return request<Invoice>('POST', '/api/finance-ext/invoices', data)
  },
}

// ═══════════════════════════════════════════
// D07 HR (人力资源)
// ═══════════════════════════════════════════
export const hrApi = {
  async getDepartmentTree(storeId: string): Promise<Department[]> {
    return request<Department[]>('GET', `/api/hr/departments/tree?storeId=${storeId}`)
  },
  async createDepartment(data: Partial<Department>): Promise<Department> {
    return request<Department>('POST', '/api/hr/departments', data)
  },
  async updateDepartment(deptId: string, data: Partial<Department>): Promise<Department> {
    return request<Department>('PUT', `/api/hr/departments/${deptId}`, data)
  },

  async listPositions(departmentId: string): Promise<Position[]> {
    return request<Position[]>('GET', `/api/hr/positions?departmentId=${departmentId}`)
  },
  async createPosition(data: Partial<Position>): Promise<Position> {
    return request<Position>('POST', '/api/hr/positions', data)
  },

  async searchEmployees(params?: { storeId?: string; name?: string; phone?: string }): Promise<Employee[]> {
    const q = new URLSearchParams()
    if (params?.storeId) q.set('storeId', params.storeId)
    if (params?.name) q.set('name', params.name)
    if (params?.phone) q.set('phone', params.phone)
    const qs = q.toString()
    return request<Employee[]>('GET', `/api/hr/employees/search${qs ? '?' + qs : ''}`)
  },
  async listEmployees(params?: { page?: number; page_size?: number; storeId?: string }): Promise<{ total: number; items: Employee[]; page: number; page_size: number }> {
    const q = new URLSearchParams()
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    if (params?.storeId) q.set('storeId', params.storeId)
    const qs = q.toString()
    return request('GET', `/api/hr/employees${qs ? '?' + qs : ''}`)
  },
  async getEmployee(employeeId: string): Promise<Employee> {
    return request<Employee>('GET', `/api/hr/employees/${employeeId}`)
  },
  async createEmployee(data: Partial<Employee>): Promise<Employee> {
    return request<Employee>('POST', '/api/hr/employees', data)
  },
  async updateEmployee(employeeId: string, data: Partial<Employee>): Promise<Employee> {
    return request<Employee>('PUT', `/api/hr/employees/${employeeId}`, data)
  },
  async deleteEmployee(employeeId: string): Promise<void> {
    return request('DELETE', `/api/hr/employees/${employeeId}`)
  },

  async listExternalStaff(storeId: string): Promise<ExternalStaff[]> {
    return request<ExternalStaff[]>('GET', `/api/hr/external-staff?storeId=${storeId}`)
  },
  async createExternalStaff(data: Partial<ExternalStaff>): Promise<ExternalStaff> {
    return request<ExternalStaff>('POST', '/api/hr/external-staff', data)
  },

  async getTodayAttendance(storeId: string): Promise<AttendanceEntry[]> {
    return request<AttendanceEntry[]>('GET', `/api/hr/attendances/today?storeId=${storeId}`)
  },
  async clockIn(storeId: string, employeeId: string): Promise<AttendanceEntry> {
    return request<AttendanceEntry>('POST', '/api/hr/attendances/clock-in', { storeId, employeeId })
  },
  async clockOut(attendanceId: string): Promise<AttendanceEntry> {
    return request<AttendanceEntry>('PUT', `/api/hr/attendances/${attendanceId}/clock-out`)
  },

  async getWeeklySchedule(params: { storeId: string; weekStart: string }): Promise<ScheduleEntry[]> {
    return request<ScheduleEntry[]>('GET', `/api/hr/schedules/weekly?storeId=${params.storeId}&weekStart=${params.weekStart}`)
  },
  async createSchedule(data: Partial<ScheduleEntry>): Promise<ScheduleEntry> {
    return request<ScheduleEntry>('POST', '/api/hr/schedules', data)
  },

  async listLeaveRequests(params?: { employeeId?: string; status?: string }): Promise<LeaveRequestEntry[]> {
    const q = new URLSearchParams()
    if (params?.employeeId) q.set('employeeId', params.employeeId)
    if (params?.status) q.set('status', params.status)
    const qs = q.toString()
    return request<LeaveRequestEntry[]>('GET', `/api/hr/leave-requests${qs ? '?' + qs : ''}`)
  },
  async createLeaveRequest(data: Partial<LeaveRequestEntry>): Promise<LeaveRequestEntry> {
    return request<LeaveRequestEntry>('POST', '/api/hr/leave-requests', data)
  },
  async approveLeaveRequest(leaveId: string, approvedBy: string): Promise<LeaveRequestEntry> {
    return request<LeaveRequestEntry>('PUT', `/api/hr/leave-requests/${leaveId}/approve`, { approvedBy })
  },

  async listPayrolls(params: { storeId: string; yearMonth: string }): Promise<PayrollEntry[]> {
    return request<PayrollEntry[]>('GET', `/api/hr/payrolls/by-month?storeId=${params.storeId}&yearMonth=${params.yearMonth}`)
  },
  async createPayroll(data: Partial<PayrollEntry>): Promise<PayrollEntry> {
    return request<PayrollEntry>('POST', '/api/hr/payrolls', data)
  },
  async confirmPayroll(payrollId: string): Promise<PayrollEntry> {
    return request<PayrollEntry>('PUT', `/api/hr/payrolls/${payrollId}/confirm`)
  },

  async createPerformanceReview(data: Partial<PerformanceReviewEntry>): Promise<PerformanceReviewEntry> {
    return request<PerformanceReviewEntry>('POST', '/api/hr/performance-reviews', data)
  },
  async listPerformanceReviews(params?: { employeeId?: string; storeId?: string }): Promise<PerformanceReviewEntry[]> {
    const q = new URLSearchParams()
    if (params?.employeeId) q.set('employeeId', params.employeeId)
    if (params?.storeId) q.set('storeId', params.storeId)
    const qs = q.toString()
    return request<PerformanceReviewEntry[]>('GET', `/api/hr/performance-reviews${qs ? '?' + qs : ''}`)
  },
}

// ═══════════════════════════════════════════
// D08 Tech (技术管理)
// ═══════════════════════════════════════════
export const techApi = {
  async searchAuditLogs(params?: {
    userId?: string; action?: string; resource?: string; startDate?: string; endDate?: string; page?: number; page_size?: number
  }): Promise<{ total: number; items: AuditLogEntry[]; page: number; page_size: number }> {
    const q = new URLSearchParams()
    if (params?.userId) q.set('userId', params.userId)
    if (params?.action) q.set('action', params.action)
    if (params?.resource) q.set('resource', params.resource)
    if (params?.startDate) q.set('startDate', params.startDate)
    if (params?.endDate) q.set('endDate', params.endDate)
    if (params?.page) q.set('page', String(params.page))
    if (params?.page_size) q.set('page_size', String(params.page_size))
    const qs = q.toString()
    return request('GET', `/api/tech/audit-logs${qs ? '?' + qs : ''}`)
  },

  async listAlertRules(): Promise<AlertRule[]> {
    return request<AlertRule[]>('GET', '/api/tech/alert-rules')
  },
  async createAlertRule(data: Partial<AlertRule>): Promise<AlertRule> {
    return request<AlertRule>('POST', '/api/tech/alert-rules', data)
  },

  async listSystemJobs(): Promise<SystemJob[]> {
    return request<SystemJob[]>('GET', '/api/tech/system-jobs')
  },
  async getActiveJobs(): Promise<SystemJob[]> {
    return request<SystemJob[]>('GET', '/api/tech/system-jobs/active')
  },

  async getLatestBackup(): Promise<BackupRecord> {
    return request<BackupRecord>('GET', '/api/tech/backup-records/latest')
  },
  async listBackupRecords(): Promise<BackupRecord[]> {
    return request<BackupRecord[]>('GET', '/api/tech/backup-records')
  },

  async getDeviceEventHistory(deviceId: string, limit?: number): Promise<DeviceEvent[]> {
    const q = limit ? `?limit=${limit}` : ''
    return request<DeviceEvent[]>('GET', `/api/tech/device-events/${deviceId}/history${q}`)
  },

  async getPendingCommands(): Promise<CommandQueueEntry[]> {
    return request<CommandQueueEntry[]>('GET', '/api/tech/command-queue/pending')
  },
}

// ═══════════════════════════════════════════
// Scan QR — 扫码消费
// ═══════════════════════════════════════════
export const scanApi = {
  /** 获取房间二维码（返回payload，不返回图片文件） */
  async getRoomQrCode(roomId: string, tableId?: string): Promise<QrCodeData> {
    const q = tableId ? `?tableId=${tableId}` : ''
    return request<QrCodeData>('GET', `/api/scan/qrcode/${roomId}${q}`)
  },

  /** 批量生成门店房间二维码 */
  async batchQrCodes(storeId: string, roomIds?: string[]): Promise<QrCodeBatchData> {
    const q = new URLSearchParams({ storeId })
    if (roomIds?.length) q.set('roomIds', roomIds.join(','))
    return request<QrCodeBatchData>('GET', `/api/scan/qrcode/batch?${q}`)
  },

  /** 更换房间二维码 */
  async renewQrCode(roomId: string): Promise<QrRenewData> {
    return request<QrRenewData>('POST', `/api/scan/qrcode/${roomId}/renew`)
  },

  /** 扫码验证房间状态（防误扫） */
  async getRoomScanStatus(roomId: string): Promise<RoomScanStatus> {
    return request<RoomScanStatus>('GET', `/api/scan/room/${roomId}`)
  },

  /** 扫码下单/加购 */
  async createScanOrder(data: ScanOrderCreateReq): Promise<ScanOrderResult> {
    return request<ScanOrderResult>('POST', '/api/scan/order', data)
  },

  /** 查询房间扫码账单 */
  async getRoomBill(roomId: string): Promise<ScanBillInfo> {
    return request<ScanBillInfo>('GET', `/api/scan/bill/${roomId}`)
  },

  /** 撤销扫码订单 */
  async cancelScanOrder(orderId: string): Promise<CancelScanResult> {
    return request<CancelScanResult>('PUT', `/api/scan/order/${orderId}/cancel`)
  },

  /** 结算房间挂账 */
  async settleRoomBill(roomId: string, data: SettleBillReq): Promise<SettleBillResult> {
    return request<SettleBillResult>('POST', `/api/scan/bill/${roomId}/settle`, data)
  },
}

// ── Type Definitions ──

export interface QrCodeData {
  roomId: string
  roomName: string
  storeId: string
  scanUrl: string
  qrPayload: string
}

export interface QrCodeBatchItem {
  roomId: string
  roomName: string
  qrPayload: string
  scanUrl: string
}

export interface QrCodeBatchData {
  storeId: string
  count: number
  items: QrCodeBatchItem[]
}

export interface QrRenewData {
  roomId: string
  oldRoomCode: string
  newRoomCode: string
  qrPayload: string
  scanUrl: string
}

export interface RoomScanStatus {
  roomId: string
  roomName: string
  storeId: string
  storeName?: string
  status: string
  hasActiveOrder: boolean
  activeOrderId?: string
  message: string
}

export interface ScanOrderItemReq {
  productId: string
  quantity?: number
  unitPrice?: number
  specId?: string
  remark?: string
}

export interface ScanOrderCreateReq {
  roomId: string
  storeId: string
  customerId?: string
  customerName?: string
  customerPhone?: string
  items: ScanOrderItemReq[]
  source?: string
}

export interface ScanOrderResult {
  orderId: string
  orderNumber: string
  roomId: string
  storeId: string
  totalAmount: number
  itemCount: number
  status: string
  tags?: string[]
  message: string
}

export interface ScanBillSummary {
  roomCharge: number
  scanTotal: number
  pendingPayment: number
  totalPaid: number
}

export interface ScanBillOrderItem {
  productName: string
  quantity: number
  subtotal: number
}

export interface ScanBillOrderInfo {
  orderId: string
  orderNumber: string
  createdAt: string
  items: ScanBillOrderItem[]
  totalAmount: number
  status: string
  canCancel: boolean
}

export interface ScanBillInfo {
  roomId: string
  roomName?: string
  activeOrderId?: string
  billId?: string
  billStatus?: string
  billSummary: ScanBillSummary
  scanOrders: ScanBillOrderInfo[]
}

export interface SettleBillReq {
  paymentMethod?: string
  settleItems?: string
  useMemberBalance?: boolean
  issueInvoice?: boolean
}

export interface SettleBillResult {
  success: boolean
  settleId?: string
  roomId: string
  totalAmount: number
  memberBalanceUsed: number
  paymentAmount: number
  paymentMethod: string
  ordersSettled: number
  invoiceNumber?: string
  message: string
}

export interface CancelScanResult {
  success: boolean
  orderId: string
  refundStatus: string
  stockRollback: boolean
  cancelledAt?: string
  message: string
}
