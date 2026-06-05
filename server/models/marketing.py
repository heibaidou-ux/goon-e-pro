"""D04 市场营销域 — Campaign, CouponTemplate, Coupon, Lead, Opportunity, Channel 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaignId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # Coupon/Points/Discount
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    budget = Column(Float, default=0)
    usedAmount = Column(Float, default=0)
    status = Column(String(20), default="Draft")  # Draft/Active/Expired/Terminated
    description = Column(String(500))
    createdBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class CouponTemplate(Base):
    __tablename__ = "coupon_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    templateId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # Discount/Flat/Product
    value = Column(Float, nullable=False)
    condition = Column(String(200))
    totalCount = Column(Integer, default=0)
    perLimit = Column(Integer, default=1)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    applicableStoreIds = Column(Text)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class Coupon(Base):
    __tablename__ = "coupons"
    id = Column(Integer, primary_key=True, autoincrement=True)
    couponId = Column(String(32), unique=True, nullable=False, index=True)
    templateId = Column(String(32), ForeignKey("coupon_templates.templateId"), nullable=False)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    orderId = Column(String(32), ForeignKey("orders.orderId"), nullable=True)
    code = Column(String(32), unique=True, nullable=False)
    status = Column(String(20), default="Unused")  # Unused/Used/Expired/Frozen
    usedAt = Column(DateTime)
    expiredAt = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, autoincrement=True)
    leadId = Column(String(32), unique=True, nullable=False, index=True)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=True)
    source = Column(String(20), nullable=False)  ###### MT/DY/Referral/WalkIn/Online
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    intention = Column(String(30))  # RoomRent/TeaPurchase/MemberCard/Cooperation
    status = Column(String(20), default="New")  # New/Contacted/Converted/Abandoned
    assigneeId = Column(String(32))
    description = Column(String(500))
    createdAt = Column(DateTime, server_default=func.now())


class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunityId = Column(String(32), unique=True, nullable=False, index=True)
    leadId = Column(String(32), ForeignKey("leads.leadId"), nullable=True)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    expectedAmount = Column(Float, default=0)
    probability = Column(Integer, default=0)  # 0-100
    expectedCloseDate = Column(Date)
    status = Column(String(20), default="Open")  # Open/Won/Lost/Abandoned
    remark = Column(String(500))
    createdAt = Column(DateTime, server_default=func.now())


class MarketingList(Base):
    __tablename__ = "marketing_lists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    listId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    customerCount = Column(Integer, default=0)
    generatedBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class CustomerSegment(Base):
    __tablename__ = "customer_segments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    segmentId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    conditions = Column(Text)  # JSON
    customerCount = Column(Integer, default=0)
    createdAt = Column(DateTime, server_default=func.now())


class ThirdPartyActivity(Base):
    __tablename__ = "third_party_activities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    activityId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    platform = Column(String(10), nullable=False)  # MT/DY/Other
    activityName = Column(String(100), nullable=False)
    activityBudget = Column(Float, default=0)
    actualCost = Column(Float, default=0)
    salesAmount = Column(Float, default=0)
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Active/Ended/Settled
    remark = Column(String(500))
    createdAt = Column(DateTime, server_default=func.now())


class CampaignEffect(Base):
    __tablename__ = "campaign_effects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    effectId = Column(String(32), unique=True, nullable=False, index=True)
    campaignId = Column(String(32), ForeignKey("campaigns.campaignId"), nullable=False)
    metricName = Column(String(30), nullable=False)  # Views/Clicks/Redemption/Sales/Revenue
    metricValue = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    channelId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # Online/Offline
    platform = Column(String(30))  # MiniProgram/MT/DY/Offline
    commissionRate = Column(Float, default=0)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())
