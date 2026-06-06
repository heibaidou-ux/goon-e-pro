"""D03 门店运营域 — Customer, Order, RoomAppointment, CleaningTask, Inspection 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customerId = Column(String(32), unique=True, nullable=False, index=True)
    wxOpenId = Column(String(100), unique=True, nullable=False)
    wxUnionId = Column(String(100))
    phone = Column(String(20))
    name = Column(String(50))
    nickname = Column(String(100))
    avatar = Column(String(500))
    gender = Column(String(10))
    birthday = Column(Date)
    memberLevel = Column(String(20), default="Normal")  # Normal/Silver/Gold/Platinum
    registerStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    registerTime = Column(DateTime, server_default=func.now())
    tags = Column(Text)
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class CustomerTag(Base):
    __tablename__ = "customer_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tagId = Column(String(32), unique=True, nullable=False, index=True)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    tagType = Column(String(50), nullable=False)
    tagValue = Column(String(100), nullable=False)
    source = Column(String(10), default="Auto")  # Auto / Manual
    createdAt = Column(DateTime, server_default=func.now())


class MemberCard(Base):
    __tablename__ = "member_cards"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cardId = Column(String(32), unique=True, nullable=False, index=True)
    cardNumber = Column(String(20), unique=True, nullable=False)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    balance = Column(Float, default=0, nullable=False)
    bonusBalance = Column(Float, default=0)
    totalRecharge = Column(Float, default=0, nullable=False)
    totalConsume = Column(Float, default=0, nullable=False)
    status = Column(String(20), default="Active")  # Active/Frozen/Closed
    createdAt = Column(DateTime, server_default=func.now())


class RechargeRecord(Base):
    __tablename__ = "recharge_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rechargeId = Column(String(32), unique=True, nullable=False, index=True)
    cardId = Column(String(32), ForeignKey("member_cards.cardId"), nullable=False)
    amount = Column(Float, nullable=False)
    bonusAmount = Column(Float, default=0)
    paymentMethod = Column(String(20), nullable=False)  # WxPay/AliPay/BankTransfer
    transactionId = Column(String(64))
    isRevenue = Column(Boolean, default=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(String(32), unique=True, nullable=False, index=True)
    orderNumber = Column(String(30), unique=True, nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=True)
    orderType = Column(String(20), nullable=False)  # Room / Retail / Mixed
    status = Column(String(20), default="PendingPay")  # PendingPay/PendingUse/InUse/Completed/Cancelled/Refunded
    totalAmount = Column(Float, nullable=False)
    discountAmount = Column(Float, default=0)
    paidAmount = Column(Float)
    paymentMethod = Column(String(30))
    paymentTime = Column(DateTime)
    platform = Column(String(20), nullable=False)  # MiniProgram/MT/DY/Offline/ScanQR
    platformOrderId = Column(String(64))
    bookingStartTime = Column(DateTime)
    bookingEndTime = Column(DateTime)
    actualStartTime = Column(DateTime)
    actualEndTime = Column(DateTime)
    doorPassword = Column(String(50))
    settleCycle = Column(String(10))
    cancellationTime = Column(DateTime)
    cancellationReason = Column(String(500))
    # V1.1 扫码消费扩展字段
    tags = Column(Text)  # JSON array: ["扫码加购","房间888"]
    tagMeta = Column(Text)  # JSON object: {"sourceRoom":"R888","billStatus":"挂账中"}
    parentRoomOrderId = Column(String(32), ForeignKey("orders.orderId"), nullable=True)  # 所属房间主订单ID
    billId = Column(String(32), nullable=True)  # FK→ScanBill（挂账结算关联）
    createdAt = Column(DateTime, server_default=func.now())
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class ScanBill(Base):
    """扫码挂账账单 — 记录一个房间在入住期间的扫码消费汇总"""
    __tablename__ = "scan_bills"
    id = Column(Integer, primary_key=True, autoincrement=True)
    billId = Column(String(32), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    roomOrderId = Column(String(32), ForeignKey("orders.orderId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    status = Column(String(20), default="Active")  # Active(挂账中)/Settled(已结算)/Cancelled(已撤销)
    totalAmount = Column(Float, nullable=False, default=0)
    settledAmount = Column(Float, nullable=False, default=0)
    orderCount = Column(Integer, nullable=False, default=0)
    settledOrderCount = Column(Integer, nullable=False, default=0)
    memberBalanceUsed = Column(Float, default=0)
    paymentAmount = Column(Float, default=0)
    paymentMethod = Column(String(30))
    settledAt = Column(DateTime)
    invoiceNumber = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    itemId = Column(String(32), unique=True, nullable=False, index=True)
    orderId = Column(String(32), ForeignKey("orders.orderId"), nullable=False)
    itemType = Column(String(20), nullable=False)  # Room / Product
    productId = Column(String(32), nullable=True)
    roomId = Column(String(32), nullable=True)
    quantity = Column(Integer, nullable=False)
    unitPrice = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    discountAmount = Column(Float, default=0)
    couponId = Column(String(32))
    order = relationship("Order", back_populates="items")


class RoomAppointment(Base):
    __tablename__ = "room_appointments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointmentId = Column(String(32), unique=True, nullable=False, index=True)
    orderId = Column(String(32), ForeignKey("orders.orderId"), nullable=False)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    customerId = Column(String(32), ForeignKey("customers.customerId"), nullable=False)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    status = Column(String(20), default="Confirmed")  # Confirmed/InUse/Completed/Cancelled/NoShow
    cancelTime = Column(DateTime)
    cancelReason = Column(String(500))
    doorPassword = Column(String(50))
    preOpenSent = Column(Boolean, default=False)


class RoomStatus(Base):
    __tablename__ = "room_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    statusId = Column(String(32), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    status = Column(String(20), nullable=False)  # Free/Booked/InUse/Cleaning/Maintenance
    currentOrderId = Column(String(32), ForeignKey("orders.orderId"), nullable=True)
    lastStatusChange = Column(DateTime, nullable=False)
    changedBy = Column(String(32))
    changeReason = Column(String(200))
    isManual = Column(Boolean, default=False)
    createdAt = Column(DateTime, server_default=func.now())


class CleaningTask(Base):
    __tablename__ = "cleaning_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    taskId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    orderId = Column(String(32), ForeignKey("orders.orderId"), nullable=True)
    assignedType = Column(String(20), nullable=False)  # Employee / ExternalStaff
    assignedId = Column(String(32), nullable=False)
    status = Column(String(20), default="Pending")  # Pending/Accepted/InProgress/Completed
    createTime = Column(DateTime, nullable=False)
    acceptTime = Column(DateTime)
    completeTime = Column(DateTime)
    deadline = Column(DateTime, nullable=False)
    deviceFaultReported = Column(Boolean, default=False)
    deviceFaultDescription = Column(String(500))


class InspectionTemplate(Base):
    __tablename__ = "inspection_templates"
    id = Column(Integer, primary_key=True, autoincrement=True)
    templateId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    items = Column(Text, nullable=False)
    isDefault = Column(Boolean, default=False)
    frequency = Column(String(20), default="Daily")  # Daily/Monthly/Custom
    status = Column(String(20), default="Active")


class InspectionTask(Base):
    __tablename__ = "inspection_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    inspectionId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    templateId = Column(String(32), ForeignKey("inspection_templates.templateId"), nullable=False)
    assigneeId = Column(String(32), nullable=False)
    status = Column(String(20), default="Pending")  # Pending/InProgress/Submitted/Reviewed
    deadline = Column(DateTime, nullable=False)
    submitTime = Column(DateTime)
    abnormalCount = Column(Integer)
    reviewerId = Column(String(32))
    reviewComment = Column(String(500))


class InspectionItemResult(Base):
    __tablename__ = "inspection_item_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resultId = Column(String(32), unique=True, nullable=False, index=True)
    inspectionId = Column(String(32), ForeignKey("inspection_tasks.inspectionId"), nullable=False)
    itemName = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)  # Operation/Quality/Fire/Hygiene/Equipment
    isNormal = Column(Boolean, nullable=False)
    photoUrls = Column(Text)
    remark = Column(String(500))
    rectificationStatus = Column(String(20), default="None")  # None/Pending/InProgress/Completed


class RectificationTask(Base):
    __tablename__ = "rectification_tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rectificationId = Column(String(32), unique=True, nullable=False, index=True)
    inspectionId = Column(String(32), ForeignKey("inspection_tasks.inspectionId"), nullable=False)
    itemResultId = Column(String(32), ForeignKey("inspection_item_results.resultId"), nullable=False)
    assigneeId = Column(String(32), nullable=False)
    description = Column(String(500), nullable=False)
    deadline = Column(Date, nullable=False)
    completeTime = Column(DateTime)
    completePhotoUrls = Column(Text)
    status = Column(String(20), default="Pending")  # Pending/InProgress/Completed/Verified
    verifiedBy = Column(String(32))
