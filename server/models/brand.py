"""D01 品牌运营域 — Organization, Shareholder, Contract, BusinessGoal 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    orgId = Column(String(32), unique=True, nullable=False, index=True)
    parentOrgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=True)
    name = Column(String(100), nullable=False)
    shortName = Column(String(50))
    type = Column(String(20), nullable=False)  # HQ / Franchisee
    creditCode = Column(String(18), unique=True)
    legalRep = Column(String(50))
    registeredAddress = Column(String(200))
    contactPhone = Column(String(20))
    logo = Column(String(500))
    status = Column(String(20), default="Active")
    establishedDate = Column(Date)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())
    children = relationship("Organization", backref="parent", remote_side=[orgId])


class BusinessGoal(Base):
    __tablename__ = "business_goals"
    id = Column(Integer, primary_key=True, autoincrement=True)
    goalId = Column(String(32), unique=True, nullable=False, index=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)
    revenueTarget = Column(Float)
    profitTarget = Column(Float)
    storeCountTarget = Column(Integer)
    memberGrowthTarget = Column(Integer)
    status = Column(String(20), default="Draft")  # Draft / Active / Closed
    createdAt = Column(DateTime, server_default=func.now())


class GoalMetric(Base):
    __tablename__ = "goal_metrics"
    id = Column(Integer, primary_key=True, autoincrement=True)
    metricId = Column(String(32), unique=True, nullable=False, index=True)
    goalId = Column(String(32), ForeignKey("business_goals.goalId"), nullable=False)
    metricName = Column(String(50), nullable=False)
    targetValue = Column(Float, nullable=False)
    actualValue = Column(Float)
    unit = Column(String(20), nullable=False)
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BrandAsset(Base):
    __tablename__ = "brand_assets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assetId = Column(String(32), unique=True, nullable=False, index=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=False)
    assetType = Column(String(30), nullable=False)  # Logo/VI/Manual/Template/PromotionMaterial
    name = Column(String(100), nullable=False)
    fileName = Column(String(200), nullable=False)
    fileSize = Column(Integer)
    version = Column(String(20), nullable=False)
    tags = Column(Text)
    status = Column(String(20), default="Active")
    uploadedBy = Column(String(32), nullable=False)
    uploadedAt = Column(DateTime, server_default=func.now())


class Contract(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    contractId = Column(String(32), unique=True, nullable=False, index=True)
    contractNumber = Column(String(50), unique=True, nullable=False)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=False)
    counterpartyId = Column(String(32), ForeignKey("organizations.orgId"), nullable=False)
    storeId = Column(String(32), nullable=True)
    contractType = Column(String(20), nullable=False)  # Franchise/Design/Management
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    paymentTerms = Column(String(500))
    attachmentUrls = Column(Text)
    status = Column(String(20), default="Draft")  # Draft/Active/Expired/Terminated
    signedAt = Column(Date)


class Shareholder(Base):
    __tablename__ = "shareholders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    shareholderId = Column(String(32), unique=True, nullable=False, index=True)
    shareholderNumber = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # Brand / Store
    idType = Column(String(20), nullable=False)  # IDCard / CreditCode
    idNumber = Column(String(50), nullable=False)
    phone = Column(String(20))
    address = Column(String(200))
    bankName = Column(String(100))
    bankAccountName = Column(String(100))
    bankAccountNumber = Column(String(50))
    totalDividend = Column(Float, default=0)
    status = Column(String(20), default="Active")  # Active/Frozen/Exited
    exitDate = Column(Date)
    exitReason = Column(String(500))
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Investment(Base):
    __tablename__ = "investments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investmentId = Column(String(32), unique=True, nullable=False, index=True)
    shareholderId = Column(String(32), ForeignKey("shareholders.shareholderId"), nullable=False)
    targetType = Column(String(20), nullable=False)  # Brand / Store
    targetId = Column(String(32), nullable=False)
    shareRatio = Column(Float, nullable=False)
    investmentAmount = Column(Float, nullable=False)
    investmentDate = Column(Date, nullable=False)
    exitDate = Column(Date)
    status = Column(String(20), default="Active")  # Active/Exited
    changeLogs = Column(Text)


class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True, autoincrement=True)
    milestoneId = Column(String(32), unique=True, nullable=False, index=True)
    goalId = Column(String(32), ForeignKey("business_goals.goalId"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    plannedDate = Column(Date, nullable=False)
    actualDate = Column(Date)
    status = Column(String(20), default="Planned")  # Planned/InProgress/Completed/Delayed
    sortOrder = Column(Integer)
