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
  is_active: boolean
}

export interface ProductCategory {
  categoryId: string
  name: string
  parentId?: string
  sortOrder: number
  status?: string
  children?: ProductCategory[]
}

export interface ProductImage {
  imageId: string
  productId: string
  urlOriginal: string
  urlThumbnail?: string
  urlMedium?: string
  urlLarge?: string
  isCover: booleanean
  sortOrder: number
}

export interface Product {
  productId: string
  code: string
  name: string
  brand?: string
  categoryId?: string
  categoryName?: string
  spec?: string
  unit?: string
  basePrice: number
  retailPrice: number
  marketPrice: number
  isFood: booleanean
  shelfLife?: number
  isActive: booleanean
  status: string
  story?: string
  origin?: string
  brewingTips?: string
  description?: string
  images: ProductImage[]
  sortOrder: number
  createdAt?: string
  updatedAt?: string
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
  is_active: boolean
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
  is_active: boolean
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
  success: booleanean
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

// ── Finance (记账管理) ──

export interface RevenueFlow {
  revenueId: string
  storeId: string
  storeName?: string
  orderId?: string
  amount: number
  paymentMethod: string
  type: string
  channel?: string
  receivedAt: string
  createdAt?: string
}

export interface RevenueFlowListResult {
  total: number
  items: RevenueFlow[]
  page: number
  page_size: number
}

export interface ExpenseRecord {
  expenseId: string
  storeId: string
  storeName?: string
  category: string
  amount: number
  description?: string
  incurredDate: string
  status: string
  applicantId: string
  approvedBy?: string
  createdAt?: string
}

export interface ExpenseRecordListResult {
  total: number
  items: ExpenseRecord[]
  page: number
  page_size: number
}

export interface FixedAsset {
  assetId: string
  storeId: string
  storeName?: string
  name: string
  category: string
  originalValue: number
  currentValue: number
  purchaseDate: string
  depreciationMethod: string
  status: string
  createdAt?: string
}

export interface FixedAssetListResult {
  total: number
  items: FixedAsset[]
  page: number
  page_size: number
}

export interface DailySettlementOut {
  settlementId: string
  storeId: string
  storeName?: string
  settlementDate: string
  totalRevenue: number
  totalExpense: number
  cashAmount: number
  cardAmount: number
  transferAmount: number
  onlineAmount: number
  netAmount: number
  status: string
  closedBy?: string
  createdAt?: string
}

export interface MonthlySettlementOut {
  settlementId: string
  storeId: string
  storeName?: string
  yearMonth: string
  totalRevenue: number
  totalExpense: number
  netAmount: number
  dividendAmount: number
  status: string
  closedBy?: string
  createdAt?: string
}

export interface ReconciliationTicketOut {
  ticketId: string
  storeId: string
  storeName?: string
  period: string
  totalRevenue: number
  totalExpense: number
  netAmount: number
  status: string
  createdBy: string
  confirmedBy?: string
  createdAt?: string
}

export interface DividendRecordOut {
  dividendId: string
  monthlySettlementId: string
  shareholderId: string
  storeId: string
  storeName?: string
  amount: number
  ratio: number
  paidAt?: string
  status: string
  createdAt?: string
}

// ── Inventory (库存管理) ──

export interface Warehouse {
  warehouseId: string
  storeId: string
  name: string
  type: string
  address?: string
  status: string
}

export interface InventoryItem {
  inventoryId: string
  warehouseId: string
  productId: string
  quantity: number
  lastCountDate?: string
}

export interface InventoryListResult {
  total: number
  items: InventoryItem[]
  page: number
  page_size: number
}

export interface InventoryLot {
  lotId: string
  warehouseId: string
  productId: string
  batchNo: string
  quantity: number
  unitPrice: number
  productionDate?: string
  expiryDate?: string
  status: string
}

export interface StockCount {
  countId: string
  warehouseId: string
  storeId: string
  countNumber: string
  type: string
  status: string
  countedBy: string
  countDate: string
  lines: StockCountLine[]
}

export interface StockCountLine {
  lineId: string
  countId: string
  productId: string
  bookQuantity: number
  actualQuantity: number
  differenceQuantity: number
  unitPrice: number
  differenceAmount: number
  remark?: string
}

export interface FinanceDashboard {
  monthRevenue: number
  monthExpense: number
  monthNet: number
  pendingExpenses: number
  reportPeriod: string
}

// ═══════════════════════════════════════════
// D01 Brand Operations (品牌运营)
// ═══════════════════════════════════════════

export interface Organization {
  orgId: string
  parentOrgId?: string
  name: string
  shortName?: string
  type: string
  creditCode?: string
  legalRep?: string
  registeredAddress?: string
  contactPhone?: string
  logo?: string
  status: string
  establishedDate?: string
  createdAt?: string
  children?: Organization[]
}

export interface BusinessGoal {
  goalId: string
  orgId: string
  year: number
  quarter?: number
  revenueTarget?: number
  profitTarget?: number
  storeCountTarget?: number
  memberGrowthTarget?: number
  status: string
  createdAt?: string
}

export interface GoalMetric {
  metricId: string
  goalId: string
  metricName: string
  targetValue: number
  actualValue?: number
  unit: string
  updatedAt?: string
}

export interface BrandAsset {
  assetId: string
  orgId: string
  assetType: string
  name: string
  fileName: string
  fileSize?: number
  version: string
  tags?: string
  status: string
  uploadedBy: string
  uploadedAt?: string
}

export interface Contract {
  contractId: string
  contractNumber: string
  orgId: string
  counterpartyId: string
  storeId?: string
  contractType: string
  startDate: string
  endDate: string
  amount: number
  paymentTerms?: string
  attachmentUrls?: string
  status: string
  signedAt?: string
}

export interface Shareholder {
  shareholderId: string
  shareholderNumber: string
  name: string
  type: string
  idType: string
  idNumber: string
  phone?: string
  address?: string
  bankName?: string
  bankAccountName?: string
  bankAccountNumber?: string
  totalDividend: number
  status: string
  exitDate?: string
  exitReason?: string
  createdAt?: string
}

export interface Investment {
  investmentId: string
  shareholderId: string
  targetType: string
  targetId: string
  shareRatio: number
  investmentAmount: number
  investmentDate: string
  exitDate?: string
  status: string
  changeLogs?: string
}

export interface Milestone {
  milestoneId: string
  goalId: string
  name: string
  description?: string
  plannedDate: string
  actualDate?: string
  status: string
  sortOrder?: number
}

// ═══════════════════════════════════════════
// D02 Store Development (门店拓展)
// ═══════════════════════════════════════════

export interface LegalEntity {
  legalEntityId: string
  name: string
  type: string
  creditCode?: string
  legalRep: string
  registeredCapital?: number
  registeredAddress?: string
  businessScope?: string
  establishedDate?: string
  status: string
}

export interface StoreSiteSelection {
  selectionId: string
  source: string
  region: string
  address: string
  area?: number
  rent?: number
  environmentAssessment?: string
  recommendationReason?: string
  investorFeedback?: string
  investorConfirmed: boolean
  investorAmount?: number
  approvalStatus: string
  approvalFlowId?: string
  resultStoreId?: string
  submittedBy: string
  createdAt?: string
}

export interface StoreConstruction {
  constructionId: string
  storeId: string
  planStartDate: string
  planEndDate: string
  actualStartDate?: string
  actualEndDate?: string
  totalCost?: number
  status: string
  sealedAt?: string
  sealedBy?: string
}

export interface ConstructionCost {
  costId: string
  constructionId: string
  category: string
  description: string
  amount: number
  supplierId?: string
  voucherUrl?: string
  incurredDate: string
}

export interface DesignDrawing {
  drawingId: string
  storeId: string
  constructionId?: string
  type: string
  name: string
  fileName: string
  fileFormat: string
  version: string
  status: string
  uploadedBy: string
  approvedBy?: string
}

export interface RoomPricing {
  pricingId: string
  roomId: string
  basePrice: number
  unit: string
  effectiveDate: string
  expiryDate?: string
  status: string
}

export interface RoomPersonPricing {
  personPricingId: string
  roomId: string
  personCount: number
  pricePerHour: number
  status: string
}

export interface TimeSlotCoefficient {
  coeffId: string
  storeId: string
  dayType: string
  timeRange: string
  coefficient: number
  description?: string
}

export interface HolidayCalendar {
  holidayId: string
  name: string
  startDate: string
  endDate: string
  coefficient: number
  recurrence?: string
  status: string
}

export interface ActivityCalendar {
  activityId: string
  storeId: string
  name: string
  startDate: string
  endDate: string
  coefficient: number
  status: string
}

export interface DurationDiscountRule {
  ruleId: string
  storeId: string
  minDuration: number
  maxDuration?: number
  discountRate: number
  status: string
}

export interface NightPackage {
  packageId: string
  storeId: string
  packageType: string
  price: number
  durationMinutes: number
  applicableTimeRange: string
  status: string
}

// ═══════════════════════════════════════════
// D03 Operations (门店运营)
// ═══════════════════════════════════════════

export interface Customer {
  customerId: string
  wxOpenId: string
  wxUnionId?: string
  phone?: string
  name?: string
  nickname?: string
  avatar?: string
  gender?: string
  birthday?: string
  memberLevel: string
  registerStoreId?: string
  registerTime?: string
  tags?: string
  status: string
  createdAt?: string
}

export interface MemberCard {
  cardId: string
  cardNumber: string
  customerId: string
  customerName?: string
  balance: number
  bonusBalance: number
  totalRecharge: number
  totalConsume: number
  status: string
  createdAt?: string
}

export interface RechargeRecord {
  rechargeId: string
  cardId: string
  amount: number
  bonusAmount: number
  paymentMethod: string
  transactionId?: string
  isRevenue: boolean
  storeId: string
  createdAt?: string
}

export interface RoomAppointment {
  appointmentId: string
  orderId: string
  roomId: string
  customerId: string
  startTime: string
  endTime: string
  status: string
  cancelTime?: string
  cancelReason?: string
  doorPassword?: string
  preOpenSent: boolean
}

export interface RoomStatusEntry {
  statusId: string
  roomId: string
  status: string
  currentOrderId?: string
  lastStatusChange: string
  changedBy?: string
  changeReason?: string
  isManual: boolean
  createdAt?: string
}

export interface CleaningTask {
  taskId: string
  storeId: string
  roomId: string
  roomName?: string
  orderId?: string
  assignedType: string
  assignedId: string
  assignedName?: string
  status: string
  createTime: string
  acceptTime?: string
  completeTime?: string
  deadline: string
  deviceFaultReported: boolean
  deviceFaultDescription?: string
}

export interface InspectionTemplate {
  templateId: string
  storeId: string
  name: string
  items: string
  isDefault: boolean
  frequency: string
  status: string
}

export interface InspectionTask {
  inspectionId: string
  storeId: string
  templateId: string
  assigneeId: string
  status: string
  deadline: string
  submitTime?: string
  abnormalCount?: number
  reviewerId?: string
  reviewComment?: string
}

export interface RectificationTask {
  rectificationId: string
  inspectionId: string
  itemResultId: string
  assigneeId: string
  description: string
  deadline: string
  completeTime?: string
  completePhotoUrls?: string
  status: string
  verifiedBy?: string
}

// ═══════════════════════════════════════════
// D04 Marketing (市场营销)
// ═══════════════════════════════════════════

export interface Campaign {
  campaignId: string
  name: string
  type: string
  storeId: string
  storeName?: string
  startDate: string
  endDate: string
  budget: number
  usedAmount: number
  status: string
  description?: string
  createdBy: string
  createdAt?: string
}

export interface CouponTemplate {
  templateId: string
  name: string
  type: string
  value: number
  condition?: string
  totalCount: number
  perLimit: number
  startTime: string
  endTime: string
  applicableStoreIds?: string
  status: string
  createdBy: string
  createdAt?: string
}

export interface CouponEntry {
  couponId: string
  templateId: string
  customerId: string
  orderId?: string
  code: string
  status: string
  usedAt?: string
  expiredAt: string
  createdAt?: string
}

export interface Lead {
  leadId: string
  customerId?: string
  source: string
  storeId?: string
  intention?: string
  status: string
  assigneeId?: string
  description?: string
  createdAt?: string
}

export interface Opportunity {
  opportunityId: string
  leadId?: string
  customerId: string
  storeId: string
  expectedAmount: number
  probability: number
  expectedCloseDate?: string
  status: string
  remark?: string
  createdAt?: string
}

export interface ThirdPartyActivity {
  activityId: string
  storeId: string
  platform: string
  activityName: string
  activityBudget: number
  actualCost: number
  salesAmount: number
  startDate: string
  endDate: string
  status: string
  remark?: string
  createdAt?: string
}

// ═══════════════════════════════════════════
// D06 Finance Ext (财务管理扩展)
// ═══════════════════════════════════════════

export interface AccountSubject {
  subjectId: string
  code: string
  name: string
  parentId?: string
  level: number
  type: string
  direction: string
  isLeaf: boolean
  status: string
  children?: AccountSubject[]
}

export interface JournalEntry {
  entryId: string
  periodId: string
  entryNumber: string
  entryDate: string
  summary?: string
  attachmentCount: number
  status: string
  createdBy: string
  approvedBy?: string
  createdAt?: string
  lines?: JournalEntryLine[]
}

export interface JournalEntryLine {
  lineId: string
  entryId: string
  subjectId: string
  direction: string
  amount: number
  summary?: string
}

export interface BudgetEntry {
  budgetId: string
  orgId?: string
  storeId?: string
  year: number
  month?: number
  category: string
  budgetAmount: number
  actualAmount: number
  createdAt?: string
}

export interface AdvanceRequest {
  advanceId: string
  storeId: string
  employeeId: string
  employeeName?: string
  amount: number
  purpose?: string
  expectedRepayDate?: string
  status: string
  approvedBy?: string
  createdAt?: string
}

export interface ReimbursementEntry {
  reimbursementId: string
  storeId: string
  employeeId: string
  employeeName?: string
  amount: number
  expenseType: string
  description?: string
  receiptUrls?: string
  status: string
  approvedBy?: string
  paidAt?: string
  createdAt?: string
}

export interface PaymentEntry {
  paymentId: string
  storeId: string
  payeeType: string
  payeeId: string
  amount: number
  paymentMethod: string
  bankAccountId?: string
  transactionId?: string
  status: string
  paidAt?: string
  createdAt?: string
}

export interface AccountsPayable {
  payableId: string
  supplierId: string
  storeId: string
  purchaseOrderId?: string
  amount: number
  paidAmount: number
  dueDate: string
  status: string
  createdAt?: string
}

export interface BankAccount {
  accountId: string
  legalEntityId: string
  bankName: string
  branchName?: string
  accountName: string
  accountNumber: string
  type: string
  status: string
  createdAt?: string
}

export interface Invoice {
  invoiceId: string
  storeId: string
  invoiceNumber: string
  invoiceCode?: string
  amount: number
  type: string
  direction: string
  customerTaxId?: string
  issueDate: string
  status: string
  createdAt?: string
}

// ═══════════════════════════════════════════
// D07 HR (人力资源)
// ═══════════════════════════════════════════

export interface Department {
  departmentId: string
  storeId: string
  name: string
  parentId?: string
  sortOrder: number
  status: string
  children?: Department[]
}

export interface Position {
  positionId: string
  departmentId: string
  name: string
  jobLevel?: string
  description?: string
  status: string
}

export interface Employee {
  employeeId: string
  storeId: string
  storeName?: string
  departmentId?: string
  departmentName?: string
  positionId?: string
  positionName?: string
  employeeNumber: string
  name: string
  phone?: string
  idCard?: string
  gender?: string
  birthday?: string
  hireDate: string
  type: string
  education?: string
  bankName?: string
  bankAccount?: string
  status: string
  resignedDate?: string
  createdAt?: string
}

export interface ExternalStaff {
  staffId: string
  storeId: string
  company?: string
  name: string
  phone?: string
  idCard?: string
  serviceType: string
  contractStartDate?: string
  contractEndDate?: string
  status: string
  createdAt?: string
}

export interface ScheduleEntry {
  scheduleId: string
  storeId: string
  employeeId: string
  employeeName?: string
  workDate: string
  startTime: string
  endTime: string
  scheduleType: string
  isHoliday: boolean
  createdBy: string
  createdAt?: string
}

export interface AttendanceEntry {
  attendanceId: string
  storeId: string
  employeeId: string
  employeeName?: string
  date: string
  clockIn?: string
  clockOut?: string
  status: string
  remark?: string
  createdAt?: string
}

export interface LeaveRequestEntry {
  leaveId: string
  employeeId: string
  employeeName?: string
  leaveType: string
  startDate: string
  endDate: string
  duration: number
  reason?: string
  status: string
  approvedBy?: string
  createdAt?: string
}

export interface PayrollEntry {
  payrollId: string
  storeId: string
  employeeId: string
  employeeName?: string
  yearMonth: string
  totalAmount: number
  status: string
  paidAt?: string
  createdAt?: string
  items?: PayrollItemEntry[]
}

export interface PayrollItemEntry {
  itemId: string
  payrollId: string
  category: string
  amount: number
  remark?: string
}

export interface PerformanceReviewEntry {
  reviewId: string
  employeeId: string
  employeeName?: string
  storeId: string
  reviewDate: string
  score?: number
  rating?: string
  reviewContent?: string
  reviewerId: string
  status: string
  createdAt?: string
}

// ═══════════════════════════════════════════
// D08 Tech (技术管理)
// ═══════════════════════════════════════════

export interface AuditLogEntry {
  logId: string
  userId: string
  userName?: string
  action: string
  resource: string
  resourceId?: string
  detail?: string
  ipAddress?: string
  userAgent?: string
  createdAt?: string
}

export interface AlertRule {
  ruleId: string
  name: string
  deviceType?: string
  condition: string
  severity: string
  enabled: boolean
  createdAt?: string
}

export interface SystemJob {
  jobId: string
  name: string
  type: string
  schedule?: string
  lastRunAt?: string
  nextRunAt?: string
  status: string
  createdAt?: string
}

export interface BackupRecord {
  recordId: string
  fileName: string
  fileSize?: number
  type: string
  status: string
  startedAt?: string
  completedAt?: string
  createdAt?: string
}

export interface DeviceEvent {
  eventId: string
  deviceId: string
  roomId: string
  eventType: string
  eventData?: string
  occurredAt: string
  createdAt?: string
}

export interface CommandQueueEntry {
  commandId: string
  deviceId: string
  command: string
  params?: string
  status: string
  sentAt?: string
  responseAt?: string
  responseData?: string
  createdAt?: string
}

export interface HeartbeatEntry {
  heartbeatId: string
  deviceId: string
  status: string
  cpuUsage?: number
  memoryUsage?: number
  signalStrength?: number
  reportedAt: string
}
