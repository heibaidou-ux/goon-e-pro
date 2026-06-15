"""扫码消费 API — QR码生成/验证/点单挂账/结算全链路"""
import json
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from datetime import datetime

from database import get_db
from models.operations import Order, OrderItem, Customer, ScanBill
from models.store_dev import Room, Store, QrCodeAuditLog
from models.supply_chain import Product, InventoryOnHand
from models.user import User
from services.auth_service import get_current_user, get_optional_user
from schemas.scan import (
    QrCodeOut, QrCodeBatchOut, QrCodeBatchItem, QrRenewOut,
    RoomScanInfo,
    ScanOrderCreate, ScanOrderOut, ScanOrderItemOut,
    ScanBillOut, ScanBillSummary, ScanBillOrder, ScanBillOrderItem,
    SettleRequest, SettleOut,
    CancelOut,
)

router = APIRouter(prefix="/api/scan", tags=["扫码消费"], dependencies=[Depends(get_current_user)])


# ── Helpers ──

def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


def _gen_room_code(store_code: str, room_no: str) -> str:
    """Generate room code: GA-{storeCode}-{roomNo}"""
    return f"GA-{store_code}-{room_no}"


def _gen_order_number() -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"SCAN{today}{uuid.uuid4().hex[:6].upper()}"


def _build_qr_payload(room_id: str, store_id: str, table_id: Optional[str] = None) -> str:
    """Build mini-program deep-link payload."""
    params = f"room_id={room_id}&store_id={store_id}"
    if table_id:
        params += f"&table_id={table_id}"
    params += f"&t={int(datetime.utcnow().timestamp())}"
    return f"gaoan://scan?{params}"


def _build_scan_url(room_id: str, store_id: str, table_id: Optional[str] = None) -> str:
    params = f"room_id={room_id}&store_id={store_id}"
    if table_id:
        params += f"&table_id={table_id}"
    return f"/pages/scan/landing?{params}"


# ═══════════════════════════════════════════
# 1. QR Code Generation (单房间)
# ═══════════════════════════════════════════

@router.get("/qrcode/{room_id}", response_model=QrCodeOut)
async def get_room_qrcode(
    room_id: str,
    table_id: Optional[str] = Query(None, alias="tableId"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate QR code payload for a room.
    Returns the deep-link URL that the mini-program handles.
    The actual QR image should be generated client-side from `qrPayload`.
    """
    r = await db.execute(
        select(Room).where(Room.roomId == room_id)
    )
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    return QrCodeOut(
        roomId=room_id,
        roomName=room.name,
        storeId=room.storeId,
        scanUrl=_build_scan_url(room_id, room.storeId, table_id),
        qrPayload=_build_qr_payload(room_id, room.storeId, table_id),
    )


# ═══════════════════════════════════════════
# 2. Batch QR Code Generation (批量)
# ═══════════════════════════════════════════

@router.get("/qrcode/batch", response_model=QrCodeBatchOut)
async def batch_room_qrcodes(
    store_id: str = Query(..., alias="storeId"),
    room_ids: Optional[str] = Query(None, alias="roomIds"),  # comma-separated
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch generate QR codes for rooms in a store.
    If roomIds is omitted, generates for all active rooms in the store.
    Optional: creates/updates room records with QR metadata.
    """
    # Verify store
    store_r = await db.execute(select(Store).where(Store.storeId == store_id))
    store = store_r.scalar_one_or_none()
    if not store:
        raise HTTPException(404, "门店不存在")

    # Query rooms
    query = select(Room).where(Room.storeId == store_id, Room.status == "Active")
    if room_ids:
        ids_list = [r.strip() for r in room_ids.split(",") if r.strip()]
        query = query.where(Room.roomId.in_(ids_list))

    rooms_r = await db.execute(query)
    rooms = rooms_r.scalars().all()
    if not rooms:
        raise HTTPException(404, "未找到符合条件的房间")

    items = []
    for room in rooms:
        # Auto-generate roomCode if missing
        if not room.roomCode:
            room.roomCode = _gen_room_code(store.storeCode, room.roomId[-4:])
            room.qrUpdatedAt = datetime.utcnow()

        qr_payload = _build_qr_payload(room.roomId, store_id)
        scan_url = _build_scan_url(room.roomId, store_id)

        items.append(QrCodeBatchItem(
            roomId=room.roomId,
            roomName=room.name,
            qrPayload=qr_payload,
            scanUrl=scan_url,
        ))

        # Create audit log
        audit = QrCodeAuditLog(
            logId=_gen_id(),
            roomId=room.roomId,
            action="Generate",
            newRoomCode=room.roomCode,
            operatorId=current_user.userId,
        )
        db.add(audit)

    await db.commit()

    return QrCodeBatchOut(
        storeId=store_id,
        count=len(items),
        items=items,
    )


# ═══════════════════════════════════════════
# 3. QR Code Renew (更换码)
# ═══════════════════════════════════════════

@router.post("/qrcode/{room_id}/renew", response_model=QrRenewOut)
async def renew_room_qrcode(
    room_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Renew a room's QR code: generates a new roomCode and invalidates the old one.
    """
    r = await db.execute(select(Room).where(Room.roomId == room_id))
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    # Get store for code generation
    store_r = await db.execute(select(Store).where(Store.storeId == room.storeId))
    store = store_r.scalar_one_or_none()

    old_code = room.roomCode
    new_code = _gen_room_code(store.storeCode if store else "XX", uuid.uuid4().hex[:6].upper())
    room.roomCode = new_code
    room.qrUpdatedAt = datetime.utcnow()

    # Update QR history
    history = []
    if room.qrHistory:
        try:
            history = json.loads(room.qrHistory)
        except (json.JSONDecodeError, TypeError):
            history = []
    history.append({
        "oldCode": old_code,
        "newCode": new_code,
        "changedAt": datetime.utcnow().isoformat(),
        "changedBy": current_user.userId,
    })
    room.qrHistory = json.dumps(history, ensure_ascii=False)

    # Create audit log
    audit = QrCodeAuditLog(
        logId=_gen_id(),
        roomId=room_id,
        action="Renew",
        oldRoomCode=old_code,
        newRoomCode=new_code,
        operatorId=current_user.userId,
    )
    db.add(audit)
    await db.commit()

    return QrRenewOut(
        roomId=room_id,
        oldRoomCode=old_code or "",
        newRoomCode=new_code,
        qrPayload=_build_qr_payload(room_id, room.storeId),
        scanUrl=_build_scan_url(room_id, room.storeId),
    )


# ═══════════════════════════════════════════
# 4. Room Status (防误扫验证)
# ═══════════════════════════════════════════

@router.get("/room/{room_id}", response_model=RoomScanInfo)
async def get_room_scan_status(
    room_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Validate room status before allowing scan-to-order.
    Anti-mis-scan: only allow ordering if room has an active 'InUse' order.
    """
    r = await db.execute(select(Room).where(Room.roomId == room_id))
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    # Get store name
    store_r = await db.execute(
        select(Store.name).where(Store.storeId == room.storeId)
    )
    store_name = store_r.scalar_one_or_none()

    # Check for active order (InUse or PendingUse)
    order_r = await db.execute(
        select(Order).where(
            Order.roomId == room_id,
            Order.orderType == "Room",
            or_(Order.status == "InUse", Order.status == "PendingUse"),
        ).order_by(Order.createdAt.desc()).limit(1)
    )
    active_order = order_r.scalar_one_or_none()

    if room.status != "Active":
        return RoomScanInfo(
            roomId=room_id,
            roomName=room.name,
            storeId=room.storeId,
            storeName=store_name,
            status=room.status,
            hasActiveOrder=False,
            message="该房间当前不可使用，请联系店员",
        )

    if not active_order:
        return RoomScanInfo(
            roomId=room_id,
            roomName=room.name,
            storeId=room.storeId,
            storeName=store_name,
            status=room.status,
            hasActiveOrder=False,
            message="该房间暂无进行中的订单，请联系店员开房后再扫码点单",
        )

    return RoomScanInfo(
        roomId=room_id,
        roomName=room.name,
        storeId=room.storeId,
        storeName=store_name,
        status=room.status,
        hasActiveOrder=True,
        activeOrderId=active_order.orderId,
        message=f"欢迎使用 {room.name}，可扫码加购",
    )


# ═══════════════════════════════════════════
# 5. Scan-to-Order (扫码点单/加购)
# ═══════════════════════════════════════════

@router.post("/order", response_model=ScanOrderOut)
async def create_scan_order(
    data: ScanOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create an order from QR scan.
    Items are added to the room's active bill (挂账).
    """
    # 1. Validate room
    r = await db.execute(select(Room).where(Room.roomId == data.roomId))
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    if room.status != "Active":
        raise HTTPException(400, "该房间不可使用")

    # 2. Find active room order (or create one)
    order_r = await db.execute(
        select(Order).where(
            Order.roomId == data.roomId,
            Order.orderType == "Room",
            or_(Order.status == "InUse", Order.status == "PendingUse"),
        ).order_by(Order.createdAt.desc()).limit(1)
    )
    active_order = order_r.scalar_one_or_none()

    if not active_order:
        raise HTTPException(400, "该房间暂无进行中的订单，请联系店员开房后扫码")

    # 3. Lookup / create customer
    customer_id = data.customerId or ""
    if data.customerPhone and not customer_id:
        cust_r = await db.execute(
            select(Customer).where(Customer.phone == data.customerPhone)
        )
        customer = cust_r.scalar_one_or_none()
        if not customer:
            customer = Customer(
                customerId=_gen_id(),
                wxOpenId=f"scan_{_gen_id()}",
                phone=data.customerPhone,
                name=data.customerName or "扫码客人",
                registerStoreId=data.storeId,
            )
            db.add(customer)
            await db.flush()
        customer_id = customer.customerId

    # 4. Create scan order items (Retail-type, tied to room)
    order_id = _gen_id()
    total = 0
    items = []
    for item_data in data.items:
        # Verify product exists and is active
        prod_r = await db.execute(
            select(Product).where(
                Product.productId == item_data.productId,
                Product.isActive == True,
            )
        )
        product = prod_r.scalar_one_or_none()
        if not product:
            raise HTTPException(400, f"商品 {item_data.productId} 不存在或已下架")

        price = item_data.unitPrice or product.retailPrice
        subtotal = round(item_data.quantity * price, 2)
        total += subtotal

        item = OrderItem(
            itemId=_gen_id(),
            orderId=order_id,
            itemType="Product",
            productId=item_data.productId,
            quantity=item_data.quantity,
            unitPrice=price,
            subtotal=subtotal,
        )
        items.append(item)

    total = round(total, 2)

    # Build tags
    tags = json.dumps(["扫码加购", f"房间{room.name}"], ensure_ascii=False)
    tag_meta = json.dumps({
        "sourceRoom": data.roomId,
        "sourceOrder": active_order.orderId,
        "billStatus": "挂账中",
    }, ensure_ascii=False)

    # Find or create ScanBill
    bill_r = await db.execute(
        select(ScanBill).where(
            ScanBill.roomId == data.roomId,
            ScanBill.roomOrderId == active_order.orderId,
            ScanBill.status == "Active",
        )
    )
    bill = bill_r.scalar_one_or_none()
    if not bill:
        bill = ScanBill(
            billId=_gen_id(),
            roomId=data.roomId,
            roomOrderId=active_order.orderId,
            storeId=data.storeId,
            status="Active",
            totalAmount=0,
            settledAmount=0,
            orderCount=0,
            settledOrderCount=0,
        )
        db.add(bill)
        await db.flush()

    bill.totalAmount = round((bill.totalAmount or 0) + total, 2)
    bill.orderCount = (bill.orderCount or 0) + 1

    order = Order(
        orderId=order_id,
        orderNumber=_gen_order_number(),
        storeId=data.storeId,
        customerId=customer_id,
        roomId=data.roomId,
        orderType="Retail",
        status="Completed",  # Immediate completion in v1
        totalAmount=total,
        paidAmount=0,
        platform=data.source,
        tags=tags,
        tagMeta=tag_meta,
        parentRoomOrderId=active_order.orderId,
        billId=bill.billId,
        items=items,
    )
    db.add(order)
    await db.commit()

    return ScanOrderOut(
        orderId=order_id,
        orderNumber=order.orderNumber,
        roomId=data.roomId,
        storeId=data.storeId,
        totalAmount=total,
        itemCount=len(items),
        status=order.status,
        tags=["扫码加购", f"房间{room.name}"],
        message=f"扫码点单成功，共 {len(items)} 件商品，金额 ¥{total} 已挂入房间 {room.name}",
    )


# ═══════════════════════════════════════════
# 6. Cancel Scan Order (撤销扫码订单)
# ═══════════════════════════════════════════

@router.put("/order/{order_id}/cancel", response_model=CancelOut)
async def cancel_scan_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Cancel a scan-to-order order.
    Only cancellable if status is 'Completed' (挂账中, not yet settled).
    Rolls back inventory on cancellation.
    """
    # Find the order
    r = await db.execute(
        select(Order).options(selectinload(Order.items)).where(
            Order.orderId == order_id,
            Order.platform == "ScanQR",
        )
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "扫码订单不存在")

    if order.status != "Completed":
        raise HTTPException(400, f"当前订单状态为 {order.status}，不可撤销")

    if order.paidAmount and order.paidAmount > 0:
        raise HTTPException(400, "该订单已有支付记录，请走退款流程")

    # Update order status
    order.status = "Cancelled"
    order.cancellationTime = datetime.utcnow()
    order.cancellationReason = "扫码订单客人手动撤销"

    # Update tagMeta
    if order.tagMeta:
        try:
            meta = json.loads(order.tagMeta)
            meta["billStatus"] = "已撤销"
            order.tagMeta = json.dumps(meta, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            pass

    # Roll back inventory (increase stock)
    stock_rollback = False
    if order.items:
        for item in order.items:
            if item.productId:
                inv_r = await db.execute(
                    select(InventoryOnHand).where(
                        InventoryOnHand.productId == item.productId,
                    ).limit(1)
                )
                inv = inv_r.scalar_one_or_none()
                if inv:
                    inv.quantity = round((inv.quantity or 0) + item.quantity, 2)
                    stock_rollback = True

    # Update ScanBill totals
    if order.billId:
        bill_r = await db.execute(
            select(ScanBill).where(ScanBill.billId == order.billId)
        )
        bill = bill_r.scalar_one_or_none()
        if bill:
            bill.totalAmount = round(max(0, (bill.totalAmount or 0) - (order.totalAmount or 0)), 2)
            bill.orderCount = max(0, (bill.orderCount or 0) - 1)

    await db.commit()

    return CancelOut(
        success=True,
        orderId=order_id,
        refundStatus="无需退款（挂账未支付）",
        stockRollback=stock_rollback,
        cancelledAt=order.cancellationTime,
        message="扫码订单已成功撤销",
    )


# ═══════════════════════════════════════════
# 7. Query Bill (查询房间账单)
# ═══════════════════════════════════════════

@router.get("/bill/{room_id}", response_model=ScanBillOut)
async def get_room_bill(
    room_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Query the scan bill summary for a room.
    Returns all scan-to-order items and their totals.
    """
    # Get room info
    r = await db.execute(select(Room).where(Room.roomId == room_id))
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    # Find active room order
    order_r = await db.execute(
        select(Order).where(
            Order.roomId == room_id,
            Order.orderType == "Room",
            or_(Order.status == "InUse", Order.status == "PendingUse"),
        ).order_by(Order.createdAt.desc()).limit(1)
    )
    active_order = order_r.scalar_one_or_none()
    active_order_id = active_order.orderId if active_order else None

    # Get scan orders (Retail-type with ScanQR platform, linked to this room)
    scan_orders_r = await db.execute(
        select(Order).options(selectinload(Order.items)).where(
            Order.roomId == room_id,
            Order.platform == "ScanQR",
            Order.status != "Cancelled",
        ).order_by(Order.createdAt.asc())
    )
    scan_orders = scan_orders_r.scalars().all()

    # Get active bill
    bill_r = await db.execute(
        select(ScanBill).where(
            ScanBill.roomId == room_id,
            ScanBill.status == "Active",
        ).limit(1)
    )
    bill = bill_r.scalar_one_or_none()

    # Build scan order list
    scan_order_list = []
    for so in scan_orders:
        items_list = []
        for soi in so.items or []:
            items_list.append(ScanBillOrderItem(
                productName=soi.productId or "商品",
                quantity=soi.quantity,
                subtotal=soi.subtotal,
            ))
        scan_order_list.append(ScanBillOrder(
            orderId=so.orderId,
            orderNumber=so.orderNumber,
            createdAt=so.createdAt,
            items=items_list,
            totalAmount=so.totalAmount,
            status="挂账中" if so.status == "Completed" else so.status,
            canCancel=so.status == "Completed" and (so.paidAmount is None or so.paidAmount == 0),
        ))

    scan_total = sum(o.totalAmount for o in scan_orders)
    room_charge = active_order.totalAmount if active_order else 0

    return ScanBillOut(
        roomId=room_id,
        roomName=room.name,
        activeOrderId=active_order_id,
        billId=bill.billId if bill else None,
        billStatus=bill.status if bill else None,
        billSummary=ScanBillSummary(
            roomCharge=room_charge,
            scanTotal=scan_total,
            pendingPayment=scan_total,
            totalPaid=room_charge,
        ),
        scanOrders=scan_order_list,
    )


# ═══════════════════════════════════════════
# 8. Settle Bill (挂账结算)
# ═══════════════════════════════════════════

@router.post("/bill/{room_id}/settle", response_model=SettleOut)
async def settle_room_bill(
    room_id: str,
    data: SettleRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Settle a room's scan bill.
    Supports full settlement ("all") or partial (specific orderIds).
    """
    # Validate room
    r = await db.execute(select(Room).where(Room.roomId == room_id))
    room = r.scalar_one_or_none()
    if not room:
        raise HTTPException(404, "房间不存在")

    # Find active bill
    bill_r = await db.execute(
        select(ScanBill).where(
            ScanBill.roomId == room_id,
            ScanBill.status == "Active",
        ).limit(1)
    )
    bill = bill_r.scalar_one_or_none()
    if not bill:
        raise HTTPException(400, "该房间没有进行中的挂账单")

    # Determine which orders to settle
    query = select(Order).options(selectinload(Order.items)).where(
        Order.billId == bill.billId,
        Order.platform == "ScanQR",
        Order.status == "Completed",
    )
    orders_r = await db.execute(query)
    orders = orders_r.scalars().all()

    if not orders:
        raise HTTPException(400, "没有待结算的扫码订单")

    settle_total = round(sum(o.totalAmount for o in orders), 2)

    # Handle member balance usage
    member_used = 0.0
    if data.useMemberBalance and data.paymentMethod == "MemberBalance":
        # In a full implementation, deduct from member card here
        member_used = settle_total

    payment_amount = round(settle_total - member_used, 2)

    # Update orders
    for o in orders:
        o.status = "Completed"  # settled within room context
        o.paidAmount = round(o.totalAmount - (member_used / len(orders) if len(orders) > 0 else 0), 2)
        o.paymentMethod = data.paymentMethod
        o.paymentTime = datetime.utcnow()
        if o.tagMeta:
            try:
                meta = json.loads(o.tagMeta)
                meta["billStatus"] = "已结算"
                o.tagMeta = json.dumps(meta, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                pass

    # Update bill
    bill.status = "Settled"
    bill.settledAmount = settle_total
    bill.settledOrderCount = len(orders)
    bill.memberBalanceUsed = member_used
    bill.paymentAmount = payment_amount
    bill.paymentMethod = data.paymentMethod
    bill.settledAt = datetime.utcnow()

    # Generate invoice number if requested
    invoice_number = None
    if data.issueInvoice:
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        bill.invoiceNumber = invoice_number

    await db.commit()

    return SettleOut(
        success=True,
        settleId=bill.billId,
        roomId=room_id,
        totalAmount=settle_total,
        memberBalanceUsed=member_used,
        paymentAmount=payment_amount,
        paymentMethod=data.paymentMethod,
        ordersSettled=len(orders),
        invoiceNumber=invoice_number,
        message=f"结算成功，共 {len(orders)} 笔订单，金额 ¥{settle_total}",
    )
