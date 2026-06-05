"""扫码消费 API — QR码生成与扫码下单（Plan B）"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from pydantic import BaseModel

from database import get_db
from models.operations import Order, OrderItem, Customer
from models.store_dev import Room, Store
from models.supply_chain import Product
from models.user import User
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/scan", tags=["扫码消费"])


# ── Schemas ──

class ScanOrderItemCreate(BaseModel):
    productId: str
    quantity: float = 1
    unitPrice: float = 0
    remark: Optional[str] = None


class ScanOrderCreate(BaseModel):
    """Create an order via QR scan — items auto-attach to room."""
    roomId: str
    storeId: str
    customerId: Optional[str] = None
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    items: list[ScanOrderItemCreate]
    source: str = "ScanQR"


class RoomScanInfo(BaseModel):
    """Room info returned by QR scan validation."""
    roomId: str
    roomName: str
    storeId: str
    storeName: Optional[str] = None
    status: str  # Active / InUse / Inactive
    hasActiveOrder: bool
    activeOrderId: Optional[str] = None
    message: str


class QrCodeOut(BaseModel):
    """QR code data for a room."""
    roomId: str
    roomName: str
    storeId: str
    scanUrl: str
    qrPayload: str


class ScanOrderOut(BaseModel):
    orderId: str
    orderNumber: str
    roomId: str
    storeId: str
    totalAmount: float
    itemCount: int
    status: str
    message: str


# ── Helpers ──

def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


def _gen_order_number() -> str:
    today = datetime.utcnow().strftime("%Y%m%d")
    return f"SCAN{today}{uuid.uuid4().hex[:6].upper()}"


# ═══════════════════════════════════════════
# QR Code Generation
# ═══════════════════════════════════════════

@router.get("/qrcode/{room_id}", response_model=QrCodeOut)
async def get_room_qrcode(
    room_id: str,
    table_id: Optional[str] = Query(None, alias="tableId"),
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

    # Build mini-program deep link params
    params = f"room_id={room_id}&store_id={room.storeId}"
    if table_id:
        params += f"&table_id={table_id}"

    # Mini-program scheme URL (to be configured with actual appID)
    # Format: pages/scan/landing?room_id=XXX&store_id=YYY
    scan_url = f"/pages/scan/landing?{params}"
    qr_payload = f"gaoan://scan?{params}"

    return QrCodeOut(
        roomId=room_id,
        roomName=room.name,
        storeId=room.storeId,
        scanUrl=scan_url,
        qrPayload=qr_payload,
    )


# ═══════════════════════════════════════════
# Room Status (anti-mis-scan)
# ═══════════════════════════════════════════

@router.get("/room/{room_id}", response_model=RoomScanInfo)
async def get_room_scan_status(
    room_id: str,
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
# Scan-to-Order
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

    # 4. Create scan order items (type="Retail" sub-orders attached to room)
    #    Each scan creates a separate "ScanOrder" linked to the room
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

    order = Order(
        orderId=order_id,
        orderNumber=_gen_order_number(),
        storeId=data.storeId,
        customerId=customer_id,
        roomId=data.roomId,
        orderType="Retail",  # Scan orders are retail-type, tied to room
        status="Completed",  # Immediate completion in v1
        totalAmount=total,
        paidAmount=total,
        platform=data.source,
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
        message=f"扫码点单成功，共 {len(items)} 件商品，金额 ¥{total} 已挂入房间 {room.name}",
    )
