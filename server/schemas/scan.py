"""扫码消费 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── QR Code ──

class QrCodeOut(BaseModel):
    roomId: str
    roomName: str
    storeId: str
    scanUrl: str
    qrPayload: str


class QrCodeBatchItem(BaseModel):
    roomId: str
    roomName: str
    qrPayload: str
    scanUrl: str


class QrCodeBatchOut(BaseModel):
    storeId: str
    count: int
    items: List[QrCodeBatchItem]


class QrRenewOut(BaseModel):
    roomId: str
    oldRoomCode: str
    newRoomCode: str
    qrPayload: str
    scanUrl: str


# ── Room Scan Status ──

class RoomScanInfo(BaseModel):
    roomId: str
    roomName: str
    storeId: str
    storeName: Optional[str] = None
    status: str  # Active / Inactive / Maintenance
    hasActiveOrder: bool
    activeOrderId: Optional[str] = None
    message: str


# ── Scan Order ──

class ScanOrderItemCreate(BaseModel):
    productId: str
    quantity: float = 1
    unitPrice: float = 0
    specId: Optional[str] = None
    remark: Optional[str] = None


class ScanOrderCreate(BaseModel):
    """Create an order via QR scan — items auto-attach to room."""
    roomId: str
    storeId: str
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    items: List[ScanOrderItemCreate]
    source: str = "ScanQR"


class ScanOrderItemOut(BaseModel):
    productId: str
    productName: Optional[str] = None
    spec: Optional[str] = None
    quantity: float
    unitPrice: float
    subtotal: float


class ScanOrderOut(BaseModel):
    orderId: str
    orderNumber: str
    roomId: str
    storeId: str
    totalAmount: float
    itemCount: int
    items: Optional[List[ScanOrderItemOut]] = None
    status: str
    tags: Optional[List[str]] = None
    message: str


# ── Scan Bill ──

class ScanBillSummary(BaseModel):
    roomCharge: float = 0
    scanTotal: float = 0
    pendingPayment: float = 0
    totalPaid: float = 0


class ScanBillOrderItem(BaseModel):
    productName: str
    quantity: float
    subtotal: float


class ScanBillOrder(BaseModel):
    orderId: str
    orderNumber: str
    createdAt: datetime
    items: List[ScanBillOrderItem]
    totalAmount: float
    status: str
    canCancel: bool = True


class ScanBillOut(BaseModel):
    roomId: str
    roomName: Optional[str] = None
    activeOrderId: Optional[str] = None
    billId: Optional[str] = None
    billStatus: Optional[str] = None
    billSummary: ScanBillSummary
    scanOrders: List[ScanBillOrder]

    class Config:
        from_attributes = True


# ── Settle ──

class SettleRequest(BaseModel):
    paymentMethod: str = "WxPay"  # WxPay/AliPay/MemberBalance/Cash/BankTransfer
    settleItems: str = "all"  # "all" or list of orderIds as JSON string
    useMemberBalance: bool = False
    issueInvoice: bool = False


class SettleOut(BaseModel):
    success: bool
    settleId: Optional[str] = None
    roomId: str
    totalAmount: float = 0
    memberBalanceUsed: float = 0
    paymentAmount: float = 0
    paymentMethod: str
    ordersSettled: int = 0
    invoiceNumber: Optional[str] = None
    message: str


# ── Cancel ──

class CancelOut(BaseModel):
    success: bool
    orderId: str
    refundStatus: str
    stockRollback: bool = False
    cancelledAt: Optional[datetime] = None
    message: str
