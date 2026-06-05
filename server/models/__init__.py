"""Register all 111+ models (D01-D08) for auto-import by database.py init_db()."""
# D01 品牌运营域
from models.brand import Organization, BusinessGoal, GoalMetric, BrandAsset, Contract, Shareholder, Investment, Milestone

# D02 门店拓展域
from models.store_dev import (LegalEntity, Territory, Store, StoreSiteSelection, StoreConstruction,
                              ConstructionCost, DesignDrawing, Room, RoomPricing, RoomPersonPricing,
                              TimeSlotCoefficient, HolidayCalendar, ActivityCalendar,
                              DurationDiscountRule, NightPackage)

# D03 门店运营域
from models.operations import (Customer, CustomerTag, MemberCard, RechargeRecord, Order, OrderItem,
                               RoomAppointment, RoomStatus, CleaningTask, InspectionTemplate,
                               InspectionTask, InspectionItemResult, RectificationTask)

# D04 市场营销域
from models.marketing import (Campaign, CouponTemplate, Coupon, Lead, Opportunity, MarketingList,
                              CustomerSegment, ThirdPartyActivity, CampaignEffect, Channel)

# D05 供应链域
from models.supply_chain import (ProductCategory, Product, ProductImage, UnitOfMeasure, PriceList,
                                 Supplier, SupplierPrice, PurchaseOrder, PurchaseOrderLine,
                                 TransferRequest, InternalSettlement, Warehouse, InventoryLot,
                                 InventoryOnHand, InventoryTransfer, StockCount, StockCountLine)

# D06 财务域
from models.finance import (AccountSubject, FiscalCalendar, JournalEntry, JournalEntryLine, Ledger,
                            Budget, RevenueFlow, ExpenseRecord, AdvanceRequest, Reimbursement,
                            Payment, AccountsPayable, ReconciliationTicket, DailySettlement,
                            MonthlySettlement, DividendRecord, FixedAsset, DepreciationRecord,
                            BankAccount, Invoice)

# D07 人力资源域
from models.hr import (Department, Position, Job, SalaryGrade, PromotionRecord, Employee,
                       ExternalStaff, Schedule, ScheduleSwap, Attendance, LeaveRequest, Payroll,
                       PayrollItem, PerformanceReview, CleanerAssessment)

# D08 技术域
from models.tech import (IoTDevice, DeviceEvent, SmartScene, SceneRule, RoomSceneBinding,
                         UserAccount, Role, Permission, AuditLog, AlertRule, AlertRecord,
                         SystemJob, BackupRecord, CommandQueue, HeartbeatRecord)

# Legacy auth model (keep until migration to UserAccount complete)
from models.user import User

all_models = [
    # D01
    Organization, BusinessGoal, GoalMetric, BrandAsset, Contract, Shareholder, Investment, Milestone,
    # D02
    LegalEntity, Territory, Store, StoreSiteSelection, StoreConstruction, ConstructionCost,
    DesignDrawing, Room, RoomPricing, RoomPersonPricing, TimeSlotCoefficient, HolidayCalendar,
    ActivityCalendar, DurationDiscountRule, NightPackage,
    # D03
    Customer, CustomerTag, MemberCard, RechargeRecord, Order, OrderItem, RoomAppointment, RoomStatus,
    CleaningTask, InspectionTemplate, InspectionTask, InspectionItemResult, RectificationTask,
    # D04
    Campaign, CouponTemplate, Coupon, Lead, Opportunity, MarketingList, CustomerSegment,
    ThirdPartyActivity, CampaignEffect, Channel,
    # D05
    ProductCategory, Product, ProductImage, UnitOfMeasure, PriceList, Supplier, SupplierPrice,
    PurchaseOrder, PurchaseOrderLine, TransferRequest, InternalSettlement, Warehouse, InventoryLot,
    InventoryOnHand, InventoryTransfer, StockCount, StockCountLine,
    # D06
    AccountSubject, FiscalCalendar, JournalEntry, JournalEntryLine, Ledger, Budget, RevenueFlow,
    ExpenseRecord, AdvanceRequest, Reimbursement, Payment, AccountsPayable, ReconciliationTicket,
    DailySettlement, MonthlySettlement, DividendRecord, FixedAsset, DepreciationRecord,
    BankAccount, Invoice,
    # D07
    Department, Position, Job, SalaryGrade, PromotionRecord, Employee, ExternalStaff, Schedule,
    ScheduleSwap, Attendance, LeaveRequest, Payroll, PayrollItem, PerformanceReview, CleanerAssessment,
    # D08
    IoTDevice, DeviceEvent, SmartScene, SceneRule, RoomSceneBinding, UserAccount, Role, Permission,
    AuditLog, AlertRule, AlertRecord, SystemJob, BackupRecord, CommandQueue, HeartbeatRecord,
    # Legacy
    User,
]
