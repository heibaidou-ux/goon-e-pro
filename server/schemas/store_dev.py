"""D02 门店拓展域 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── LegalEntity ──

class LegalEntityCreate(BaseModel):
    name: str
    type: str  # Limited / SoleProprietor
    creditCode: Optional[str] = None
    legalRep: str
    registeredCapital: Optional[float] = None
    registeredAddress: Optional[str] = None
    businessScope: Optional[str] = None
    establishedDate: Optional[date] = None


class LegalEntityUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    creditCode: Optional[str] = None
    legalRep: Optional[str] = None
    registeredCapital: Optional[float] = None
    registeredAddress: Optional[str] = None
    businessScope: Optional[str] = None
    establishedDate: Optional[date] = None
    status: Optional[str] = None


class LegalEntityOut(BaseModel):
    legalEntityId: str
    name: str
    type: str
    creditCode: Optional[str] = None
    legalRep: str
    registeredCapital: Optional[float] = None
    registeredAddress: Optional[str] = None
    businessScope: Optional[str] = None
    establishedDate: Optional[date] = None
    status: str = "Active"

    class Config:
        from_attributes = True


class LegalEntityListOut(BaseModel):
    total: int
    items: List[LegalEntityOut]
    page: int = 1
    page_size: int = 20


# ── Territory ──

class TerritoryCreate(BaseModel):
    name: str
    level: int  # 1=省 / 2=市 / 3=区
    parentId: Optional[str] = None


class TerritoryUpdate(BaseModel):
    name: Optional[str] = None
    level: Optional[int] = None
    parentId: Optional[str] = None
    status: Optional[str] = None


class TerritoryOut(BaseModel):
    territoryId: str
    parentId: Optional[str] = None
    name: str
    level: int
    status: str = "Active"

    class Config:
        from_attributes = True


class TerritoryListOut(BaseModel):
    total: int
    items: List[TerritoryOut]
    page: int = 1
    page_size: int = 20


# ── StoreSiteSelection ──

class StoreSiteSelectionCreate(BaseModel):
    source: str  # Manager / Franchisee / HQ
    region: str
    address: str
    area: Optional[float] = None
    rent: Optional[float] = None
    environmentAssessment: Optional[str] = None
    recommendationReason: Optional[str] = None
    investorFeedback: Optional[str] = None
    investorConfirmed: Optional[bool] = False
    investorAmount: Optional[float] = None
    approvalFlowId: Optional[str] = None
    resultStoreId: Optional[str] = None
    submittedBy: str


class StoreSiteSelectionUpdate(BaseModel):
    source: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    area: Optional[float] = None
    rent: Optional[float] = None
    environmentAssessment: Optional[str] = None
    recommendationReason: Optional[str] = None
    investorFeedback: Optional[str] = None
    investorConfirmed: Optional[bool] = None
    investorAmount: Optional[float] = None
    approvalStatus: Optional[str] = None
    approvalFlowId: Optional[str] = None
    resultStoreId: Optional[str] = None


class StoreSiteSelectionOut(BaseModel):
    selectionId: str
    source: str
    region: str
    address: str
    area: Optional[float] = None
    rent: Optional[float] = None
    environmentAssessment: Optional[str] = None
    recommendationReason: Optional[str] = None
    investorFeedback: Optional[str] = None
    investorConfirmed: bool = False
    investorAmount: Optional[float] = None
    approvalStatus: str = "Pending"
    approvalFlowId: Optional[str] = None
    resultStoreId: Optional[str] = None
    resultStoreName: Optional[str] = None
    submittedBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class StoreSiteSelectionListOut(BaseModel):
    total: int
    items: List[StoreSiteSelectionOut]
    page: int = 1
    page_size: int = 20


# ── StoreConstruction ──

class StoreConstructionCreate(BaseModel):
    storeId: str
    planStartDate: date
    planEndDate: date
    actualStartDate: Optional[date] = None
    actualEndDate: Optional[date] = None


class StoreConstructionUpdate(BaseModel):
    planStartDate: Optional[date] = None
    planEndDate: Optional[date] = None
    actualStartDate: Optional[date] = None
    actualEndDate: Optional[date] = None
    totalCost: Optional[float] = None
    status: Optional[str] = None
    sealedBy: Optional[str] = None


class StoreConstructionOut(BaseModel):
    constructionId: str
    storeId: str
    storeName: Optional[str] = None
    planStartDate: date
    planEndDate: date
    actualStartDate: Optional[date] = None
    actualEndDate: Optional[date] = None
    totalCost: Optional[float] = None
    status: str = "Planned"
    sealedAt: Optional[datetime] = None
    sealedBy: Optional[str] = None

    class Config:
        from_attributes = True


class StoreConstructionListOut(BaseModel):
    total: int
    items: List[StoreConstructionOut]
    page: int = 1
    page_size: int = 20


# ── ConstructionCost ──

class ConstructionCostCreate(BaseModel):
    constructionId: str
    category: str  # Decoration/Equipment/Material/Labor/Other
    description: str
    amount: float
    supplierId: Optional[str] = None
    voucherUrl: Optional[str] = None
    incurredDate: date


class ConstructionCostUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    supplierId: Optional[str] = None
    voucherUrl: Optional[str] = None
    incurredDate: Optional[date] = None


class ConstructionCostOut(BaseModel):
    costId: str
    constructionId: str
    category: str
    description: str
    amount: float
    supplierId: Optional[str] = None
    voucherUrl: Optional[str] = None
    incurredDate: date

    class Config:
        from_attributes = True


class ConstructionCostListOut(BaseModel):
    total: float
    items: List[ConstructionCostOut]
    page: int = 1
    page_size: int = 20


# ── DesignDrawing ──

class DesignDrawingCreate(BaseModel):
    storeId: str
    constructionId: Optional[str] = None
    type: str  # Space/MEP/Fire/HVAC/Completion
    name: str
    fileName: str
    fileFormat: str  # DWG/PDF/PNG
    version: str
    uploadedBy: str


class DesignDrawingUpdate(BaseModel):
    type: Optional[str] = None
    name: Optional[str] = None
    fileName: Optional[str] = None
    fileFormat: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class DesignDrawingOut(BaseModel):
    drawingId: str
    storeId: str
    storeName: Optional[str] = None
    constructionId: Optional[str] = None
    type: str
    name: str
    fileName: str
    fileFormat: str
    version: str
    status: str = "Draft"
    uploadedBy: str
    approvedBy: Optional[str] = None

    class Config:
        from_attributes = True


class DesignDrawingListOut(BaseModel):
    total: int
    items: List[DesignDrawingOut]
    page: int = 1
    page_size: int = 20


# ── RoomPricing ──

class RoomPricingCreate(BaseModel):
    roomId: str
    basePrice: float
    unit: str = "PerHour"  # PerHour / PerSession
    effectiveDate: date
    expiryDate: Optional[date] = None


class RoomPricingUpdate(BaseModel):
    basePrice: Optional[float] = None
    unit: Optional[str] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[str] = None


class RoomPricingOut(BaseModel):
    pricingId: str
    roomId: str
    basePrice: float
    unit: str = "PerHour"
    effectiveDate: date
    expiryDate: Optional[date] = None
    status: str = "Active"

    class Config:
        from_attributes = True


class RoomPricingListOut(BaseModel):
    total: int
    items: List[RoomPricingOut]
    page: int = 1
    page_size: int = 20


# ── RoomPersonPricing ──

class RoomPersonPricingCreate(BaseModel):
    roomId: str
    personCount: int
    pricePerHour: float


class RoomPersonPricingUpdate(BaseModel):
    personCount: Optional[int] = None
    pricePerHour: Optional[float] = None
    status: Optional[str] = None


class RoomPersonPricingOut(BaseModel):
    personPricingId: str
    roomId: str
    personCount: int
    pricePerHour: float
    status: str = "Active"

    class Config:
        from_attributes = True


class RoomPersonPricingListOut(BaseModel):
    total: int
    items: List[RoomPersonPricingOut]
    page: int = 1
    page_size: int = 20


# ── TimeSlotCoefficient ──

class TimeSlotCoefficientCreate(BaseModel):
    storeId: str
    dayType: str  # Weekday/Weekend/Holiday
    timeRange: str
    coefficient: float
    description: Optional[str] = None


class TimeSlotCoefficientUpdate(BaseModel):
    dayType: Optional[str] = None
    timeRange: Optional[str] = None
    coefficient: Optional[float] = None
    description: Optional[str] = None


class TimeSlotCoefficientOut(BaseModel):
    coeffId: str
    storeId: str
    storeName: Optional[str] = None
    dayType: str
    timeRange: str
    coefficient: float
    description: Optional[str] = None

    class Config:
        from_attributes = True


class TimeSlotCoefficientListOut(BaseModel):
    total: int
    items: List[TimeSlotCoefficientOut]
    page: int = 1
    page_size: int = 20


# ── HolidayCalendar ──

class HolidayCalendarCreate(BaseModel):
    name: str
    startDate: date
    endDate: date
    coefficient: float
    recurrence: Optional[str] = None  # None / Yearly


class HolidayCalendarUpdate(BaseModel):
    name: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    coefficient: Optional[float] = None
    recurrence: Optional[str] = None
    status: Optional[str] = None


class HolidayCalendarOut(BaseModel):
    holidayId: str
    name: str
    startDate: date
    endDate: date
    coefficient: float
    recurrence: Optional[str] = None
    status: str = "Active"

    class Config:
        from_attributes = True


class HolidayCalendarListOut(BaseModel):
    total: int
    items: List[HolidayCalendarOut]
    page: int = 1
    page_size: int = 20


# ── ActivityCalendar ──

class ActivityCalendarCreate(BaseModel):
    storeId: str
    name: str
    startDate: date
    endDate: date
    coefficient: float  # >1=溢价, <1=折扣


class ActivityCalendarUpdate(BaseModel):
    name: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    coefficient: Optional[float] = None
    status: Optional[str] = None


class ActivityCalendarOut(BaseModel):
    activityId: str
    storeId: str
    storeName: Optional[str] = None
    name: str
    startDate: date
    endDate: date
    coefficient: float
    status: str = "Draft"

    class Config:
        from_attributes = True


class ActivityCalendarListOut(BaseModel):
    total: int
    items: List[ActivityCalendarOut]
    page: int = 1
    page_size: int = 20


# ── DurationDiscountRule ──

class DurationDiscountRuleCreate(BaseModel):
    storeId: str
    minDuration: int
    maxDuration: Optional[int] = None
    discountRate: float


class DurationDiscountRuleUpdate(BaseModel):
    minDuration: Optional[int] = None
    maxDuration: Optional[int] = None
    discountRate: Optional[float] = None
    status: Optional[str] = None


class DurationDiscountRuleOut(BaseModel):
    ruleId: str
    storeId: str
    storeName: Optional[str] = None
    minDuration: int
    maxDuration: Optional[int] = None
    discountRate: float
    status: str = "Active"

    class Config:
        from_attributes = True


class DurationDiscountRuleListOut(BaseModel):
    total: int
    items: List[DurationDiscountRuleOut]
    page: int = 1
    page_size: int = 20


# ── NightPackage ──

class NightPackageCreate(BaseModel):
    storeId: str
    packageType: str  # Night / Overnight
    price: float
    durationMinutes: int
    applicableTimeRange: str


class NightPackageUpdate(BaseModel):
    packageType: Optional[str] = None
    price: Optional[float] = None
    durationMinutes: Optional[int] = None
    applicableTimeRange: Optional[str] = None
    status: Optional[str] = None


class NightPackageOut(BaseModel):
    packageId: str
    storeId: str
    storeName: Optional[str] = None
    packageType: str
    price: float
    durationMinutes: int
    applicableTimeRange: str
    status: str = "Active"

    class Config:
        from_attributes = True


class NightPackageListOut(BaseModel):
    total: int
    items: List[NightPackageOut]
    page: int = 1
    page_size: int = 20
