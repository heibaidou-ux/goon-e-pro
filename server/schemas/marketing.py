"""D04 市场营销域 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── Campaign ──

class CampaignCreate(BaseModel):
    name: str
    type: str  # Coupon/Points/Discount
    storeId: str
    startDate: date
    endDate: date
    budget: float = 0
    description: Optional[str] = None
    createdBy: str


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    storeId: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    budget: Optional[float] = None
    usedAmount: Optional[float] = None
    status: Optional[str] = None  # Draft/Active/Expired/Terminated
    description: Optional[str] = None


class CampaignOut(BaseModel):
    campaignId: str
    name: str
    type: str
    storeId: str
    storeName: Optional[str] = None
    startDate: date
    endDate: date
    budget: float = 0
    usedAmount: float = 0
    status: str = "Draft"
    description: Optional[str] = None
    createdBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignListOut(BaseModel):
    total: int
    items: List[CampaignOut]
    page: int = 1
    page_size: int = 20


# ── CouponTemplate ──

class CouponTemplateCreate(BaseModel):
    name: str
    type: str  # Discount/Flat/Product
    value: float
    condition: Optional[str] = None
    totalCount: int = 0
    perLimit: int = 1
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    applicableStoreIds: Optional[str] = None  # JSON text
    createdBy: str


class CouponTemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    value: Optional[float] = None
    condition: Optional[str] = None
    totalCount: Optional[int] = None
    perLimit: Optional[int] = None
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    applicableStoreIds: Optional[str] = None
    status: Optional[str] = None  # Active/Inactive


class CouponTemplateOut(BaseModel):
    templateId: str
    name: str
    type: str
    value: float
    condition: Optional[str] = None
    totalCount: int = 0
    perLimit: int = 1
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    applicableStoreIds: Optional[str] = None
    status: str = "Active"
    createdBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponTemplateListOut(BaseModel):
    total: int
    items: List[CouponTemplateOut]
    page: int = 1
    page_size: int = 20


# ── Coupon ──

class CouponCreate(BaseModel):
    templateId: str
    customerId: str
    orderId: Optional[str] = None
    code: str
    expiredAt: Optional[datetime] = None


class CouponUpdate(BaseModel):
    status: Optional[str] = None  # Unused/Used/Expired/Frozen
    orderId: Optional[str] = None
    usedAt: Optional[datetime] = None
    expiredAt: Optional[datetime] = None


class CouponOut(BaseModel):
    couponId: str
    templateId: str
    templateName: Optional[str] = None
    customerId: str
    orderId: Optional[str] = None
    code: str
    status: str = "Unused"
    usedAt: Optional[datetime] = None
    expiredAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CouponListOut(BaseModel):
    total: int
    items: List[CouponOut]
    page: int = 1
    page_size: int = 20


# ── Lead ──

class LeadCreate(BaseModel):
    customerId: str
    source: str  # MT/DY/Referral/WalkIn/Online
    storeId: str
    intention: str  # RoomRent/TeaPurchase/MemberCard/Cooperation
    assigneeId: Optional[str] = None
    description: Optional[str] = None


class LeadUpdate(BaseModel):
    source: Optional[str] = None
    storeId: Optional[str] = None
    intention: Optional[str] = None
    status: Optional[str] = None  # New/Contacted/Converted/Abandoned
    assigneeId: Optional[str] = None
    description: Optional[str] = None


class LeadOut(BaseModel):
    leadId: str
    customerId: str
    source: str
    storeId: str
    storeName: Optional[str] = None
    intention: str
    status: str = "New"
    assigneeId: Optional[str] = None
    description: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeadListOut(BaseModel):
    total: int
    items: List[LeadOut]
    page: int = 1
    page_size: int = 20


# ── Opportunity ──

class OpportunityCreate(BaseModel):
    leadId: str
    customerId: str
    storeId: str
    expectedAmount: float = 0
    probability: int = 0  # 0-100
    expectedCloseDate: Optional[date] = None
    remark: Optional[str] = None


class OpportunityUpdate(BaseModel):
    expectedAmount: Optional[float] = None
    probability: Optional[int] = None  # 0-100
    expectedCloseDate: Optional[date] = None
    status: Optional[str] = None  # Open/Won/Lost/Abandoned
    remark: Optional[str] = None


class OpportunityOut(BaseModel):
    opportunityId: str
    leadId: str
    customerId: str
    storeId: str
    storeName: Optional[str] = None
    expectedAmount: float = 0
    probability: int = 0
    expectedCloseDate: Optional[date] = None
    status: str = "Open"
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class OpportunityListOut(BaseModel):
    total: int
    items: List[OpportunityOut]
    page: int = 1
    page_size: int = 20


# ── MarketingList ──

class MarketingListCreate(BaseModel):
    storeId: str
    name: str
    description: Optional[str] = None
    generatedBy: str


class MarketingListUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    customerCount: Optional[int] = None


class MarketingListOut(BaseModel):
    listId: str
    storeId: str
    storeName: Optional[str] = None
    name: str
    description: Optional[str] = None
    customerCount: int = 0
    generatedBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class MarketingListListOut(BaseModel):
    total: int
    items: List[MarketingListOut]
    page: int = 1
    page_size: int = 20


# ── CustomerSegment ──

class CustomerSegmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: Optional[str] = None  # JSON text


class CustomerSegmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[str] = None
    customerCount: Optional[int] = None


class CustomerSegmentOut(BaseModel):
    segmentId: str
    name: str
    description: Optional[str] = None
    conditions: Optional[str] = None
    customerCount: int = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerSegmentListOut(BaseModel):
    total: int
    items: List[CustomerSegmentOut]
    page: int = 1
    page_size: int = 20


# ── ThirdPartyActivity ──

class ThirdPartyActivityCreate(BaseModel):
    storeId: str
    platform: str  # MT/DY/Other
    activityName: str
    activityBudget: float = 0
    startDate: date
    endDate: date
    remark: Optional[str] = None


class ThirdPartyActivityUpdate(BaseModel):
    storeId: Optional[str] = None
    platform: Optional[str] = None
    activityName: Optional[str] = None
    activityBudget: Optional[float] = None
    actualCost: Optional[float] = None
    salesAmount: Optional[float] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    status: Optional[str] = None  # Draft/Active/Ended/Settled
    remark: Optional[str] = None


class ThirdPartyActivityOut(BaseModel):
    activityId: str
    storeId: str
    storeName: Optional[str] = None
    platform: str
    activityName: str
    activityBudget: float = 0
    actualCost: float = 0
    salesAmount: float = 0
    startDate: date
    endDate: date
    status: str = "Draft"
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ThirdPartyActivityListOut(BaseModel):
    total: int
    items: List[ThirdPartyActivityOut]
    page: int = 1
    page_size: int = 20


# ── CampaignEffect ──

class CampaignEffectCreate(BaseModel):
    campaignId: str
    metricName: str  # Views/Clicks/Redemption/Sales/Revenue
    metricValue: float = 0
    date: date


class CampaignEffectUpdate(BaseModel):
    metricName: Optional[str] = None
    metricValue: Optional[float] = None
    date: Optional[date] = None


class CampaignEffectOut(BaseModel):
    effectId: str
    campaignId: str
    metricName: str
    metricValue: float = 0
    date: date
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignEffectListOut(BaseModel):
    total: int
    items: List[CampaignEffectOut]
    page: int = 1
    page_size: int = 20


# ── Channel ──

class ChannelCreate(BaseModel):
    name: str
    type: str  # Online/Offline
    platform: Optional[str] = None  # MiniProgram/MT/DY/Offline
    commissionRate: float = 0


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    platform: Optional[str] = None
    commissionRate: Optional[float] = None
    status: Optional[str] = None  # Active/Inactive


class ChannelOut(BaseModel):
    channelId: str
    name: str
    type: str
    platform: Optional[str] = None
    commissionRate: float = 0
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChannelListOut(BaseModel):
    total: int
    items: List[ChannelOut]
    page: int = 1
    page_size: int = 20
