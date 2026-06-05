"""D01 品牌运营域 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── Organization ──

class OrganizationCreate(BaseModel):
    parentOrgId: Optional[str] = None
    name: str
    shortName: Optional[str] = None
    type: str  # HQ / Franchisee
    creditCode: Optional[str] = None
    legalRep: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPhone: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[str] = "Active"
    establishedDate: Optional[date] = None


class OrganizationUpdate(BaseModel):
    parentOrgId: Optional[str] = None
    name: Optional[str] = None
    shortName: Optional[str] = None
    type: Optional[str] = None
    creditCode: Optional[str] = None
    legalRep: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPhone: Optional[str] = None
    logo: Optional[str] = None
    status: Optional[str] = None
    establishedDate: Optional[date] = None


class OrganizationOut(BaseModel):
    orgId: str
    parentOrgId: Optional[str] = None
    name: str
    shortName: Optional[str] = None
    type: str
    creditCode: Optional[str] = None
    legalRep: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPhone: Optional[str] = None
    logo: Optional[str] = None
    status: str
    establishedDate: Optional[date] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrganizationListOut(BaseModel):
    total: int
    items: List[OrganizationOut]
    page: int = 1
    page_size: int = 20


# ── BusinessGoal ──

class BusinessGoalCreate(BaseModel):
    orgId: str
    year: int
    quarter: Optional[int] = None
    revenueTarget: Optional[float] = None
    profitTarget: Optional[float] = None
    storeCountTarget: Optional[int] = None
    memberGrowthTarget: Optional[int] = None
    status: Optional[str] = "Draft"


class BusinessGoalUpdate(BaseModel):
    year: Optional[int] = None
    quarter: Optional[int] = None
    revenueTarget: Optional[float] = None
    profitTarget: Optional[float] = None
    storeCountTarget: Optional[int] = None
    memberGrowthTarget: Optional[int] = None
    status: Optional[str] = None


class BusinessGoalOut(BaseModel):
    goalId: str
    orgId: str
    orgName: Optional[str] = None
    year: int
    quarter: Optional[int] = None
    revenueTarget: Optional[float] = None
    profitTarget: Optional[float] = None
    storeCountTarget: Optional[int] = None
    memberGrowthTarget: Optional[int] = None
    status: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class BusinessGoalListOut(BaseModel):
    total: int
    items: List[BusinessGoalOut]
    page: int = 1
    page_size: int = 20


# ── GoalMetric ──

class GoalMetricCreate(BaseModel):
    goalId: str
    metricName: str
    targetValue: float
    actualValue: Optional[float] = None
    unit: str


class GoalMetricUpdate(BaseModel):
    metricName: Optional[str] = None
    targetValue: Optional[float] = None
    actualValue: Optional[float] = None
    unit: Optional[str] = None


class GoalMetricOut(BaseModel):
    metricId: str
    goalId: str
    metricName: str
    targetValue: float
    actualValue: Optional[float] = None
    unit: str
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class GoalMetricListOut(BaseModel):
    total: int
    items: List[GoalMetricOut]
    page: int = 1
    page_size: int = 20


# ── BrandAsset ──

class BrandAssetCreate(BaseModel):
    orgId: str
    assetType: str  # Logo/VI/Manual/Template/PromotionMaterial
    name: str
    fileName: str
    fileSize: Optional[int] = None
    version: str
    tags: Optional[str] = None
    status: Optional[str] = "Active"
    uploadedBy: str


class BrandAssetUpdate(BaseModel):
    name: Optional[str] = None
    fileName: Optional[str] = None
    fileSize: Optional[int] = None
    version: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class BrandAssetOut(BaseModel):
    assetId: str
    orgId: str
    orgName: Optional[str] = None
    assetType: str
    name: str
    fileName: str
    fileSize: Optional[int] = None
    version: str
    tags: Optional[str] = None
    status: str
    uploadedBy: str
    uploadedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class BrandAssetListOut(BaseModel):
    total: int
    items: List[BrandAssetOut]
    page: int = 1
    page_size: int = 20


# ── Contract ──

class ContractCreate(BaseModel):
    contractNumber: str
    orgId: str
    counterpartyId: str
    storeId: Optional[str] = None
    contractType: str  # Franchise/Design/Management
    startDate: date
    endDate: date
    amount: float
    paymentTerms: Optional[str] = None
    attachmentUrls: Optional[str] = None
    status: Optional[str] = "Draft"
    signedAt: Optional[date] = None


class ContractUpdate(BaseModel):
    contractNumber: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None
    amount: Optional[float] = None
    paymentTerms: Optional[str] = None
    attachmentUrls: Optional[str] = None
    status: Optional[str] = None
    signedAt: Optional[date] = None


class ContractOut(BaseModel):
    contractId: str
    contractNumber: str
    orgId: str
    orgName: Optional[str] = None
    counterpartyId: str
    counterpartyName: Optional[str] = None
    storeId: Optional[str] = None
    storeName: Optional[str] = None
    contractType: str
    startDate: date
    endDate: date
    amount: float
    paymentTerms: Optional[str] = None
    attachmentUrls: Optional[str] = None
    status: str
    signedAt: Optional[date] = None

    class Config:
        from_attributes = True


class ContractListOut(BaseModel):
    total: int
    items: List[ContractOut]
    page: int = 1
    page_size: int = 20


# ── Shareholder ──

class ShareholderCreate(BaseModel):
    shareholderNumber: str
    name: str
    type: str  # Brand / Store
    idType: str  # IDCard / CreditCode
    idNumber: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bankName: Optional[str] = None
    bankAccountName: Optional[str] = None
    bankAccountNumber: Optional[str] = None
    totalDividend: Optional[float] = 0
    status: Optional[str] = "Active"
    exitDate: Optional[date] = None
    exitReason: Optional[str] = None


class ShareholderUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    idType: Optional[str] = None
    idNumber: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bankName: Optional[str] = None
    bankAccountName: Optional[str] = None
    bankAccountNumber: Optional[str] = None
    totalDividend: Optional[float] = None
    status: Optional[str] = None
    exitDate: Optional[date] = None
    exitReason: Optional[str] = None


class ShareholderOut(BaseModel):
    shareholderId: str
    shareholderNumber: str
    name: str
    type: str
    idType: str
    idNumber: str
    phone: Optional[str] = None
    address: Optional[str] = None
    bankName: Optional[str] = None
    bankAccountName: Optional[str] = None
    bankAccountNumber: Optional[str] = None
    totalDividend: float = 0
    status: str
    exitDate: Optional[date] = None
    exitReason: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ShareholderListOut(BaseModel):
    total: int
    totalDividend: float = 0
    items: List[ShareholderOut]
    page: int = 1
    page_size: int = 20


# ── Investment ──

class InvestmentCreate(BaseModel):
    shareholderId: str
    targetType: str  # Brand / Store
    targetId: str
    shareRatio: float
    investmentAmount: float
    investmentDate: date
    exitDate: Optional[date] = None
    status: Optional[str] = "Active"
    changeLogs: Optional[str] = None


class InvestmentUpdate(BaseModel):
    shareRatio: Optional[float] = None
    investmentAmount: Optional[float] = None
    investmentDate: Optional[date] = None
    exitDate: Optional[date] = None
    status: Optional[str] = None
    changeLogs: Optional[str] = None


class InvestmentOut(BaseModel):
    investmentId: str
    shareholderId: str
    shareholderName: Optional[str] = None
    targetType: str
    targetId: str
    shareRatio: float
    investmentAmount: float
    investmentDate: date
    exitDate: Optional[date] = None
    status: str
    changeLogs: Optional[str] = None

    class Config:
        from_attributes = True


class InvestmentListOut(BaseModel):
    total: int
    items: List[InvestmentOut]
    page: int = 1
    page_size: int = 20


# ── Milestone ──

class MilestoneCreate(BaseModel):
    goalId: str
    name: str
    description: Optional[str] = None
    plannedDate: date
    actualDate: Optional[date] = None
    status: Optional[str] = "Planned"
    sortOrder: Optional[int] = None


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    plannedDate: Optional[date] = None
    actualDate: Optional[date] = None
    status: Optional[str] = None
    sortOrder: Optional[int] = None


class MilestoneOut(BaseModel):
    milestoneId: str
    goalId: str
    name: str
    description: Optional[str] = None
    plannedDate: date
    actualDate: Optional[date] = None
    status: str
    sortOrder: Optional[int] = None

    class Config:
        from_attributes = True


class MilestoneListOut(BaseModel):
    total: int
    items: List[MilestoneOut]
    page: int = 1
    page_size: int = 20
