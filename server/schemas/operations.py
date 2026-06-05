"""D03 门店运营域 — Pydantic schemas（Customer, MemberCard, 预约, 保洁, 巡检等）"""
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date


# ── Customer ──

class CustomerCreate(BaseModel):
    wxOpenId: str
    wxUnionId: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    memberLevel: str = "Normal"
    registerStoreId: Optional[str] = None
    tags: Optional[str] = None


class CustomerUpdate(BaseModel):
    phone: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    memberLevel: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None


class CustomerOut(BaseModel):
    customerId: str
    wxOpenId: str
    wxUnionId: Optional[str] = None
    phone: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    memberLevel: str = "Normal"
    registerStoreId: Optional[str] = None
    registerTime: Optional[datetime] = None
    tags: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerListOut(BaseModel):
    total: int
    items: List[CustomerOut]
    page: int = 1
    page_size: int = 20


# ── CustomerTag ──

class CustomerTagCreate(BaseModel):
    customerId: str
    tagType: str
    tagValue: str
    source: str = "Auto"


class CustomerTagOut(BaseModel):
    tagId: str
    customerId: str
    tagType: str
    tagValue: str
    source: str = "Auto"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CustomerTagListOut(BaseModel):
    total: int
    items: List[CustomerTagOut]
    page: int = 1
    page_size: int = 20


# ── MemberCard ──

class MemberCardCreate(BaseModel):
    cardNumber: str
    customerId: str
    balance: float = 0
    bonusBalance: float = 0
    totalRecharge: float = 0
    totalConsume: float = 0


class MemberCardUpdate(BaseModel):
    balance: Optional[float] = None
    bonusBalance: Optional[float] = None
    totalRecharge: Optional[float] = None
    totalConsume: Optional[float] = None
    status: Optional[str] = None


class MemberCardOut(BaseModel):
    cardId: str
    cardNumber: str
    customerId: str
    balance: float = 0
    bonusBalance: float = 0
    totalRecharge: float = 0
    totalConsume: float = 0
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class MemberCardListOut(BaseModel):
    total: int
    items: List[MemberCardOut]
    page: int = 1
    page_size: int = 20


# ── RechargeRecord ──

class RechargeRecordCreate(BaseModel):
    cardId: str
    amount: float
    bonusAmount: float = 0
    paymentMethod: str  # WxPay/AliPay/BankTransfer
    transactionId: Optional[str] = None
    isRevenue: bool = False
    storeId: str


class RechargeRecordUpdate(BaseModel):
    transactionId: Optional[str] = None
    isRevenue: Optional[bool] = None


class RechargeRecordOut(BaseModel):
    rechargeId: str
    cardId: str
    amount: float
    bonusAmount: float = 0
    paymentMethod: str
    transactionId: Optional[str] = None
    isRevenue: bool = False
    storeId: str
    storeName: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class RechargeRecordListOut(BaseModel):
    total: int
    items: List[RechargeRecordOut]
    page: int = 1
    page_size: int = 20


# ── RoomAppointment ──

class RoomAppointmentCreate(BaseModel):
    orderId: str
    roomId: str
    customerId: str
    startTime: datetime
    endTime: datetime
    doorPassword: Optional[str] = None


class RoomAppointmentUpdate(BaseModel):
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    status: Optional[str] = None
    cancelTime: Optional[datetime] = None
    cancelReason: Optional[str] = None
    doorPassword: Optional[str] = None
    preOpenSent: Optional[bool] = None


class RoomAppointmentOut(BaseModel):
    appointmentId: str
    orderId: str
    roomId: str
    roomName: Optional[str] = None
    customerId: str
    customerName: Optional[str] = None
    startTime: datetime
    endTime: datetime
    status: str = "Confirmed"
    cancelTime: Optional[datetime] = None
    cancelReason: Optional[str] = None
    doorPassword: Optional[str] = None
    preOpenSent: bool = False

    class Config:
        from_attributes = True


class RoomAppointmentListOut(BaseModel):
    total: int
    items: List[RoomAppointmentOut]
    page: int = 1
    page_size: int = 20


# ── RoomStatus ──

class RoomStatusCreate(BaseModel):
    roomId: str
    status: str  # Free/Booked/InUse/Cleaning/Maintenance
    currentOrderId: Optional[str] = None
    lastStatusChange: datetime
    changedBy: Optional[str] = None
    changeReason: Optional[str] = None
    isManual: bool = False


class RoomStatusOut(BaseModel):
    statusId: str
    roomId: str
    roomName: Optional[str] = None
    status: str
    currentOrderId: Optional[str] = None
    lastStatusChange: datetime
    changedBy: Optional[str] = None
    changeReason: Optional[str] = None
    isManual: bool = False
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomStatusListOut(BaseModel):
    total: int
    items: List[RoomStatusOut]
    page: int = 1
    page_size: int = 20


# ── CleaningTask ──

class CleaningTaskCreate(BaseModel):
    storeId: str
    roomId: str
    orderId: Optional[str] = None
    assignedType: str  # Employee / ExternalStaff
    assignedId: str
    deadline: datetime
    deviceFaultReported: bool = False
    deviceFaultDescription: Optional[str] = None


class CleaningTaskUpdate(BaseModel):
    status: Optional[str] = None
    acceptTime: Optional[datetime] = None
    completeTime: Optional[datetime] = None
    deviceFaultReported: Optional[bool] = None
    deviceFaultDescription: Optional[str] = None


class CleaningTaskOut(BaseModel):
    taskId: str
    storeId: str
    storeName: Optional[str] = None
    roomId: str
    roomName: Optional[str] = None
    orderId: Optional[str] = None
    assignedType: str
    assignedId: str
    status: str = "Pending"
    createTime: datetime
    acceptTime: Optional[datetime] = None
    completeTime: Optional[datetime] = None
    deadline: datetime
    deviceFaultReported: bool = False
    deviceFaultDescription: Optional[str] = None

    class Config:
        from_attributes = True


class CleaningTaskListOut(BaseModel):
    total: int
    items: List[CleaningTaskOut]
    page: int = 1
    page_size: int = 20


# ── InspectionTemplate ──

class InspectionTemplateCreate(BaseModel):
    storeId: str
    name: str
    items: str  # JSON string
    isDefault: bool = False
    frequency: str = "Daily"  # Daily/Monthly/Custom


class InspectionTemplateUpdate(BaseModel):
    name: Optional[str] = None
    items: Optional[str] = None
    isDefault: Optional[bool] = None
    frequency: Optional[str] = None
    status: Optional[str] = None


class InspectionTemplateOut(BaseModel):
    templateId: str
    storeId: str
    storeName: Optional[str] = None
    name: str
    items: str
    isDefault: bool = False
    frequency: str = "Daily"
    status: str = "Active"

    class Config:
        from_attributes = True


class InspectionTemplateListOut(BaseModel):
    total: int
    items: List[InspectionTemplateOut]
    page: int = 1
    page_size: int = 20


# ── InspectionTask ──

class InspectionTaskCreate(BaseModel):
    storeId: str
    templateId: str
    assigneeId: str
    deadline: datetime
    reviewerId: Optional[str] = None


class InspectionTaskUpdate(BaseModel):
    status: Optional[str] = None
    submitTime: Optional[datetime] = None
    abnormalCount: Optional[int] = None
    reviewerId: Optional[str] = None
    reviewComment: Optional[str] = None


class InspectionTaskOut(BaseModel):
    inspectionId: str
    storeId: str
    storeName: Optional[str] = None
    templateId: str
    templateName: Optional[str] = None
    assigneeId: str
    status: str = "Pending"
    deadline: datetime
    submitTime: Optional[datetime] = None
    abnormalCount: Optional[int] = None
    reviewerId: Optional[str] = None
    reviewComment: Optional[str] = None

    class Config:
        from_attributes = True


class InspectionTaskListOut(BaseModel):
    total: int
    items: List[InspectionTaskOut]
    page: int = 1
    page_size: int = 20


# ── InspectionItemResult ──

class InspectionItemResultCreate(BaseModel):
    inspectionId: str
    itemName: str
    category: str  # Operation/Quality/Fire/Hygiene/Equipment
    isNormal: bool
    photoUrls: Optional[str] = None
    remark: Optional[str] = None


class InspectionItemResultUpdate(BaseModel):
    isNormal: Optional[bool] = None
    photoUrls: Optional[str] = None
    remark: Optional[str] = None
    rectificationStatus: Optional[str] = None


class InspectionItemResultOut(BaseModel):
    resultId: str
    inspectionId: str
    itemName: str
    category: str
    isNormal: bool
    photoUrls: Optional[str] = None
    remark: Optional[str] = None
    rectificationStatus: str = "None"

    class Config:
        from_attributes = True


class InspectionItemResultListOut(BaseModel):
    total: int
    items: List[InspectionItemResultOut]
    page: int = 1
    page_size: int = 20


# ── RectificationTask ──

class RectificationTaskCreate(BaseModel):
    inspectionId: str
    itemResultId: str
    assigneeId: str
    description: str
    deadline: date
    completePhotoUrls: Optional[str] = None


class RectificationTaskUpdate(BaseModel):
    description: Optional[str] = None
    deadline: Optional[date] = None
    completeTime: Optional[datetime] = None
    completePhotoUrls: Optional[str] = None
    status: Optional[str] = None
    verifiedBy: Optional[str] = None


class RectificationTaskOut(BaseModel):
    rectificationId: str
    inspectionId: str
    itemResultId: str
    assigneeId: str
    description: str
    deadline: date
    completeTime: Optional[datetime] = None
    completePhotoUrls: Optional[str] = None
    status: str = "Pending"
    verifiedBy: Optional[str] = None

    class Config:
        from_attributes = True


class RectificationTaskListOut(BaseModel):
    total: int
    items: List[RectificationTaskOut]
    page: int = 1
    page_size: int = 20
