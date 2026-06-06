"""D06 财务域 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── RevenueFlow ──

class RevenueFlowCreate(BaseModel):
    storeId: str
    orderId: Optional[str] = None
    amount: float
    paymentMethod: str
    type: str  # RoomRental/ProductSales/Recharge/Deposit
    channel: Optional[str] = None
    receivedAt: Optional[datetime] = None


class RevenueFlowUpdate(BaseModel):
    amount: Optional[float] = None
    paymentMethod: Optional[str] = None
    type: Optional[str] = None
    channel: Optional[str] = None


class RevenueFlowOut(BaseModel):
    revenueId: str
    storeId: str
    storeName: Optional[str] = None
    orderId: Optional[str] = None
    amount: float
    paymentMethod: str
    type: str
    channel: Optional[str] = None
    receivedAt: datetime
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class RevenueFlowListOut(BaseModel):
    total: int  # item count for pagination
    totalSum: float = 0  # sum of amounts
    items: List[RevenueFlowOut]
    page: int = 1
    page_size: int = 20


# ── ExpenseRecord ──

class ExpenseRecordCreate(BaseModel):
    storeId: str
    category: str
    amount: float
    description: str = ""
    incurredDate: date
    applicantId: str


class ExpenseRecordUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class ExpenseRecordOut(BaseModel):
    expenseId: str
    storeId: str
    storeName: Optional[str] = None
    category: str
    amount: float
    description: Optional[str] = None
    incurredDate: date
    status: str = "Draft"
    applicantId: str
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExpenseRecordListOut(BaseModel):
    total: float
    items: List[ExpenseRecordOut]
    page: int = 1
    page_size: int = 20


# ── DailySettlement ──

class DailySettlementCreate(BaseModel):
    storeId: str
    settlementDate: date


class DailySettlementOut(BaseModel):
    settlementId: str
    storeId: str
    storeName: Optional[str] = None
    settlementDate: date
    totalRevenue: float = 0
    totalExpense: float = 0
    cashAmount: float = 0
    cardAmount: float = 0
    transferAmount: float = 0
    onlineAmount: float = 0
    netAmount: float = 0
    status: str = "Open"
    closedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── MonthlySettlement ──

class MonthlySettlementOut(BaseModel):
    settlementId: str
    storeId: str
    storeName: Optional[str] = None
    yearMonth: str
    totalRevenue: float = 0
    totalExpense: float = 0
    netAmount: float = 0
    dividendAmount: float = 0
    status: str = "Open"
    closedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── ReconciliationTicket ──

class ReconciliationTicketCreate(BaseModel):
    storeId: str
    period: str
    createdBy: str


class ReconciliationTicketOut(BaseModel):
    ticketId: str
    storeId: str
    storeName: Optional[str] = None
    period: str
    totalRevenue: float = 0
    totalExpense: float = 0
    netAmount: float = 0
    status: str = "Draft"
    createdBy: str
    confirmedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── DividendRecord ──

class DividendRecordOut(BaseModel):
    dividendId: str
    monthlySettlementId: str
    shareholderId: str
    storeId: str
    storeName: Optional[str] = None
    amount: float
    ratio: float
    paidAt: Optional[datetime] = None
    status: str = "Pending"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── FixedAsset ──

class FixedAssetCreate(BaseModel):
    storeId: str
    name: str
    category: str
    originalValue: float
    purchaseDate: date
    depreciationMethod: str = "StraightLine"


class FixedAssetUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    originalValue: Optional[float] = None
    currentValue: Optional[float] = None
    purchaseDate: Optional[date] = None
    depreciationMethod: Optional[str] = None
    status: Optional[str] = None


class FixedAssetOut(BaseModel):
    assetId: str
    storeId: str
    storeName: Optional[str] = None
    name: str
    category: str
    originalValue: float
    currentValue: float
    purchaseDate: date
    depreciationMethod: str = "StraightLine"
    status: str = "InUse"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class FixedAssetListOut(BaseModel):
    total: int
    items: List[FixedAssetOut]
    page: int = 1
    page_size: int = 20
