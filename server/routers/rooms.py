"""房间管理 API — 基于 D02/D03 新模型（store_dev, operations），含IoT场景联动"""
import json, uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from database import get_db
from models.store_dev import Store, Room
from models.operations import Order, OrderItem, Customer
from models.user import User
from schemas.order import StoreOut, RoomOut, RoomOrderOut, RoomOrderCreate
from services.auth_service import get_current_user, get_optional_user
from services.order_iot import on_order_paid, on_order_checkin, on_order_checkout

router = APIRouter(prefix="/api", tags=["房间管理"])


@router.get("/stores", response_model=list[StoreOut])
async def list_stores(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    result = await db.execute(select(Store).where(Store.status != "Closed"))
    stores = result.scalars().all()
    out = []
    for s in stores:
        room_result = await db.execute(
            select(Room).where(Room.storeId == s.storeId, Room.status == "Active")
        )
        rooms_list = room_result.scalars().all()
        out.append(StoreOut(
            id=s.id, store_id=s.storeId, name=s.name,
            address=s.address, phone=s.phone, is_active=(s.status == "Operating"),
            rooms=[RoomOut(
                id=r.id, room_id=r.roomId, store_id=r.storeId,
                name=r.name, type=r.type, capacity=r.capacity,
                floor=r.floor or "", price_per_hour=0,
                price_per_half_hour=0,
                facilities=json.loads(r.facilities) if isinstance(r.facilities, str) and r.facilities else [],
                description=r.description or "", is_active=(r.status == "Active"),
            ) for r in rooms_list]
        ))
    return out


@router.get("/rooms", response_model=list[RoomOut])
async def list_rooms(
    store_id: Optional[str] = None,
    room_type: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(Room).where(Room.status == "Active")
    if store_id:
        query = query.where(Room.storeId == store_id)
    if room_type:
        query = query.where(Room.type == room_type)

    result = await db.execute(query.order_by(Room.name))
    rooms = result.scalars().all()
    return [RoomOut(
        id=r.id, room_id=r.roomId, store_id=r.storeId,
        name=r.name, type=r.type, capacity=r.capacity,
        floor=r.floor or "", price_per_hour=0, price_per_half_hour=0,
        facilities=json.loads(r.facilities) if isinstance(r.facilities, str) and r.facilities else [],
        description=r.description or "", is_active=(r.status == "Active"),
    ) for r in rooms]


@router.get("/rooms/{room_id}", response_model=RoomOut)
async def get_room(
    room_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    result = await db.execute(select(Room).where(Room.roomId == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    return RoomOut(
        id=room.id, room_id=room.roomId, store_id=room.storeId,
        name=room.name, type=room.type, capacity=room.capacity,
        floor=room.floor or "", price_per_hour=0, price_per_half_hour=0,
        facilities=json.loads(room.facilities) if isinstance(room.facilities, str) and room.facilities else [],
        description=room.description or "", is_active=(room.status == "Active"),
    )


# ── Room Orders (from new Order model, orderType='Room') ──

@router.get("/orders", response_model=list[RoomOrderOut])
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(Order).where(Order.orderType == "Room")
    if status_filter:
        query = query.where(Order.status == status_filter)
    query = query.order_by(Order.createdAt.desc())
    result = await db.execute(query)
    orders = result.scalars().all()

    out = []
    for o in orders:
        room = None
        if o.roomId:
            r_result = await db.execute(select(Room).where(Room.roomId == o.roomId))
            r = r_result.scalar_one_or_none()
            if r:
                room = RoomOut(
                    id=r.id, room_id=r.roomId, store_id=r.storeId,
                    name=r.name, type=r.type, capacity=r.capacity,
                    floor=r.floor or "", price_per_hour=0, price_per_half_hour=0,
                    facilities=json.loads(r.facilities) if isinstance(r.facilities, str) and r.facilities else [],
                    description=r.description or "", is_active=(r.status == "Active"),
                )

        out.append(RoomOrderOut(
            id=o.id, order_id=o.orderId, room_id=o.roomId or "",
            customer_name="", customer_phone="",
            date=o.bookingStartTime.strftime("%Y-%m-%d") if o.bookingStartTime else "",
            start_time=o.bookingStartTime.strftime("%H:%M") if o.bookingStartTime else "",
            end_time=o.bookingEndTime.strftime("%H:%M") if o.bookingEndTime else "",
            duration=0,
            total_amount=o.totalAmount,
            status=o.status, scene="", door_code=o.doorPassword or "",
            source=o.platform, payment_status="Paid" if o.paidAmount else "Unpaid",
            check_in_time=o.actualStartTime.strftime("%H:%M") if o.actualStartTime else None,
            check_out_time=o.actualEndTime.strftime("%H:%M") if o.actualEndTime else None,
            created_at=o.createdAt, room=room,
        ))
    return out


@router.get("/orders/active", response_model=list[RoomOrderOut])
async def get_active_orders(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    result = await db.execute(
        select(Order).where(
            Order.orderType == "Room",
            or_(Order.status == "InUse", Order.status == "PendingUse")
        ).order_by(Order.createdAt.desc())
    )
    orders = result.scalars().all()

    out = []
    for o in orders:
        room = None
        if o.roomId:
            r_result = await db.execute(select(Room).where(Room.roomId == o.roomId))
            r = r_result.scalar_one_or_none()
            if r:
                room = RoomOut(
                    id=r.id, room_id=r.roomId, store_id=r.storeId,
                    name=r.name, type=r.type, capacity=r.capacity,
                    floor=r.floor or "", price_per_hour=0, price_per_half_hour=0,
                    facilities=json.loads(r.facilities) if isinstance(r.facilities, str) and r.facilities else [],
                    description=r.description or "", is_active=(r.status == "Active"),
                )
        out.append(RoomOrderOut(
            id=o.id, order_id=o.orderId, room_id=o.roomId or "",
            customer_name="", customer_phone="",
            date=o.bookingStartTime.strftime("%Y-%m-%d") if o.bookingStartTime else "",
            start_time=o.bookingStartTime.strftime("%H:%M") if o.bookingStartTime else "",
            end_time=o.bookingEndTime.strftime("%H:%M") if o.bookingEndTime else "",
            duration=0, total_amount=o.totalAmount,
            status=o.status, scene="", door_code=o.doorPassword or "",
            source=o.platform, payment_status="Paid" if o.paidAmount else "Unpaid",
            check_in_time=o.actualStartTime.strftime("%H:%M") if o.actualStartTime else None,
            check_out_time=o.actualEndTime.strftime("%H:%M") if o.actualEndTime else None,
            created_at=o.createdAt, room=room,
        ))
    return out


@router.post("/orders", response_model=RoomOrderOut)
async def create_order(
    data: RoomOrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # ── 时段冲突检测 ──
    if not data.date or not data.start_time or not data.end_time:
        raise HTTPException(status_code=400, detail="请提供完整的预订日期和时段")

    # 使用 select_for_update 加行锁，防并发双卖
    async with db.begin():
        # 查该房间该日期所有未取消的订单
        result = await db.execute(
            select(Order).where(
                Order.roomId == data.room_id,
                Order.orderType == "Room",
                Order.status.in_(["PendingPay", "PendingUse", "InUse"]),
                Order.bookingStartTime >= f"{data.date} 00:00:00",
                Order.bookingStartTime <= f"{data.date} 23:59:59",
            ).with_for_update()
        )
        existing = result.scalars().all()

        # 检测时间重叠
        new_start = data.start_time
        new_end = data.end_time
        for ex in existing:
            if not ex.bookingStartTime or not ex.bookingEndTime:
                continue
            ex_start = ex.bookingStartTime.strftime("%H:%M")
            ex_end = ex.bookingEndTime.strftime("%H:%M")
            # 重叠条件：新开始 < 旧结束 AND 新结束 > 旧开始
            if new_start < ex_end and new_end > ex_start:
                raise HTTPException(
                    status_code=409,
                    detail=f"该时段已被占用 ({ex_start}-{ex_end})，请选择其他时段"
                )

        order_id = uuid.uuid4().hex[:12]
        order = Order(
            orderId=order_id,
            orderNumber=f"ROOM{order_id[:8].upper()}",
            storeId="",
            customerId="",
            roomId=data.room_id,
            orderType="Room",
            status="PendingPay",  # 先待支付，支付成功后才变为 PendingUse
            totalAmount=data.total_amount,
            paidAmount=0,
            platform=data.source or "Offline",
            bookingStartTime=f"{data.date} {data.start_time}",
            bookingEndTime=f"{data.date} {data.end_time}",
        )
        db.add(order)

    await db.refresh(order)
    return RoomOrderOut(
        id=order.id, order_id=order.orderId, room_id=order.roomId or "",
        customer_name=data.customer_name, customer_phone=data.customer_phone,
        date=data.date, start_time=data.start_time, end_time=data.end_time,
        duration=data.duration, total_amount=data.total_amount,
        status=order.status, scene=data.scene or "", door_code="",
        source=data.source, payment_status="Unpaid",
        created_at=order.createdAt,
    )


# ═══════════════════════════════════════════════════════════
# IoT场景联动 — 支付/签入/签出
# ═══════════════════════════════════════════════════════════

@router.post("/orders/{order_id}/pay", response_model=dict)
async def confirm_payment(
    order_id: str,
    payment_method: str = Query("WxPay"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """确认订单支付 → 状态变更为 PendingUse + 触发IoT预开模式"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "订单不存在")
    if order.status != "PendingPay":
        raise HTTPException(400, f"当前状态 {order.status}，不可确认支付")

    order.status = "PendingUse"
    order.paidAmount = order.totalAmount
    order.paymentMethod = payment_method
    order.paymentTime = datetime.utcnow()

    # 生成门锁密码（4位随机码）
    import random
    order.doorPassword = str(random.randint(1000, 9999))

    await db.commit()

    # ── IoT联动：支付成功 → 预开模式（空调提前开）──
    iot_result = await on_order_paid(order_id, db)

    return {
        "success": True,
        "order_id": order_id,
        "status": "PendingUse",
        "door_password": order.doorPassword,
        "iot_scene": iot_result,
        "message": "支付成功，房间已预开空调",
    }


@router.post("/orders/{order_id}/checkin", response_model=dict)
async def checkin_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """签到入住 → 状态变更为 InUse + 触发IoT迎宾模式"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "订单不存在")
    if order.status not in ("PendingUse", "PendingPay"):
        raise HTTPException(400, f"当前状态 {order.status}，不可签到")

    order.status = "InUse"
    order.actualStartTime = datetime.utcnow()
    await db.commit()

    # ── IoT联动：签到 → 迎宾模式（全开灯/窗帘/音乐）──
    iot_result = await on_order_checkin(order_id, db)

    return {
        "success": True,
        "order_id": order_id,
        "status": "InUse",
        "iot_scene": iot_result,
        "message": "签到成功，欢迎使用！",
    }


@router.post("/orders/{order_id}/checkout", response_model=dict)
async def checkout_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """退房 → 状态变更为 Completed + 触发IoT退房模式"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "订单不存在")
    if order.status != "InUse":
        raise HTTPException(400, f"当前状态 {order.status}，不可退房")

    order.status = "Completed"
    order.actualEndTime = datetime.utcnow()
    await db.commit()

    # ── IoT联动：退房 → 退房模式（关所有设备+锁门）──
    iot_result = await on_order_checkout(order_id, db)

    return {
        "success": True,
        "order_id": order_id,
        "status": "Completed",
        "iot_scene": iot_result,
        "message": "退房成功，欢迎再次光临！",
    }
