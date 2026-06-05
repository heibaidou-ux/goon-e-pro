"""D02 门店拓展域 — Store, Room, RoomPricing, Pricing规则, 建设等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class LegalEntity(Base):
    __tablename__ = "legal_entities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    legalEntityId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # Limited / SoleProprietor
    creditCode = Column(String(18), unique=True)
    legalRep = Column(String(50), nullable=False)
    registeredCapital = Column(Float)
    registeredAddress = Column(String(200))
    businessScope = Column(String(500))
    establishedDate = Column(Date)
    status = Column(String(20), default="Active")


class Territory(Base):
    __tablename__ = "territories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    territoryId = Column(String(32), unique=True, nullable=False, index=True)
    parentId = Column(String(32), ForeignKey("territories.territoryId"), nullable=True)
    name = Column(String(100), nullable=False)
    level = Column(Integer, nullable=False)  # 1=省 / 2=市 / 3=区
    status = Column(String(20), default="Active")


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, autoincrement=True)
    storeId = Column(String(32), unique=True, nullable=False, index=True)
    storeCode = Column(String(20), unique=True, nullable=False)
    legalEntityId = Column(String(32), ForeignKey("legal_entities.legalEntityId"), nullable=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=False)
    territoryId = Column(String(32), ForeignKey("territories.territoryId"), nullable=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # Direct / Franchise
    address = Column(String(200), nullable=False)
    lat = Column(Float)
    lng = Column(Float)
    phone = Column(String(20))
    businessHours = Column(Text)
    area = Column(Float)
    wxMerchantId = Column(String(50))
    mtShopId = Column(String(50))
    dyShopId = Column(String(50))
    status = Column(String(20), default="Operating")  # Operating/Suspended/Renovating/Closed
    openDate = Column(Date)
    closeDate = Column(Date)
    cleaningTimeout = Column(Integer, default=30)
    createdAt = Column(DateTime, server_default=func.now())


class StoreSiteSelection(Base):
    __tablename__ = "store_site_selections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    selectionId = Column(String(32), unique=True, nullable=False, index=True)
    source = Column(String(20), nullable=False)  # Manager / Franchisee / HQ
    region = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    area = Column(Float)
    rent = Column(Float)
    environmentAssessment = Column(String(1000))
    recommendationReason = Column(String(500))
    investorFeedback = Column(String(1000))
    investorConfirmed = Column(Boolean, default=False)
    investorAmount = Column(Float)
    approvalStatus = Column(String(20), default="Pending")  # Pending/UnderReview/Approved/Rejected
    approvalFlowId = Column(String(32))
    resultStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    submittedBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class StoreConstruction(Base):
    __tablename__ = "store_constructions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    constructionId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    planStartDate = Column(Date, nullable=False)
    planEndDate = Column(Date, nullable=False)
    actualStartDate = Column(Date)
    actualEndDate = Column(Date)
    totalCost = Column(Float)
    status = Column(String(20), default="Planned")  # Planned/InProgress/Completed/Sealed
    sealedAt = Column(DateTime)
    sealedBy = Column(String(32))


class ConstructionCost(Base):
    __tablename__ = "construction_costs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    costId = Column(String(32), unique=True, nullable=False, index=True)
    constructionId = Column(String(32), ForeignKey("store_constructions.constructionId"), nullable=False)
    category = Column(String(20), nullable=False)  # Decoration/Equipment/Material/Labor/Other
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    supplierId = Column(String(32), nullable=True)
    voucherUrl = Column(String(500))
    incurredDate = Column(Date, nullable=False)


class DesignDrawing(Base):
    __tablename__ = "design_drawings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    drawingId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    constructionId = Column(String(32), ForeignKey("store_constructions.constructionId"), nullable=True)
    type = Column(String(20), nullable=False)  # Space/MEP/Fire/HVAC/Completion
    name = Column(String(200), nullable=False)
    fileName = Column(String(200), nullable=False)
    fileFormat = Column(String(10), nullable=False)  # DWG/PDF/PNG
    version = Column(String(20), nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Approved/Construction/Archived
    uploadedBy = Column(String(32), nullable=False)
    approvedBy = Column(String(32))


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roomId = Column(String(32), unique=True, nullable=False, index=True)
    roomCode = Column(String(20), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # TeaRoom/MeetingRoom/Entertainment/Exhibition/Workspace
    floor = Column(String(20))
    capacity = Column(Integer, nullable=False)
    area = Column(Float)
    facilities = Column(Text)
    photos = Column(Text)
    description = Column(String(500))
    sortOrder = Column(Integer)
    status = Column(String(20), default="Active")  # Active/Inactive/Maintenance
    createdAt = Column(DateTime, server_default=func.now())


class RoomPricing(Base):
    __tablename__ = "room_pricings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pricingId = Column(String(32), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    basePrice = Column(Float, nullable=False)
    unit = Column(String(20), default="PerHour")  # PerHour / PerSession
    effectiveDate = Column(Date, nullable=False)
    expiryDate = Column(Date)
    status = Column(String(20), default="Active")  # Active/Inactive


class RoomPersonPricing(Base):
    __tablename__ = "room_person_pricings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    personPricingId = Column(String(32), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    personCount = Column(Integer, nullable=False)
    pricePerHour = Column(Float, nullable=False)
    status = Column(String(20), default="Active")


class TimeSlotCoefficient(Base):
    __tablename__ = "time_slot_coefficients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    coeffId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    dayType = Column(String(20), nullable=False)  # Weekday/Weekend/Holiday
    timeRange = Column(Text, nullable=False)
    coefficient = Column(Float, nullable=False)
    description = Column(String(200))


class HolidayCalendar(Base):
    __tablename__ = "holiday_calendars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    holidayId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    coefficient = Column(Float, nullable=False)
    recurrence = Column(String(10))  # None / Yearly
    status = Column(String(20), default="Active")


class ActivityCalendar(Base):
    __tablename__ = "activity_calendars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    activityId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    coefficient = Column(Float, nullable=False)  # >1=溢价, <1=折扣
    status = Column(String(20), default="Draft")  # Draft/Active/Expired


class DurationDiscountRule(Base):
    __tablename__ = "duration_discount_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ruleId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    minDuration = Column(Integer, nullable=False)
    maxDuration = Column(Integer)
    discountRate = Column(Float, nullable=False)
    status = Column(String(20), default="Active")


class NightPackage(Base):
    __tablename__ = "night_packages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    packageId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    packageType = Column(String(20), nullable=False)  # Night / Overnight
    price = Column(Float, nullable=False)
    durationMinutes = Column(Integer, nullable=False)
    applicableTimeRange = Column(Text, nullable=False)
    status = Column(String(20), default="Active")
