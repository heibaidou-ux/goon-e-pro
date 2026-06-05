"""房间管理 API — 基于 D02/D03 新模型（store_dev, operations）"""
import json, uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from database import get_db
from models.store_dev import Store, Room
from models.operations import Order, OrderItem, Customer
from models.user import User
from schemas.order import StoreOut, RoomOut, RoomOrderOut, RoomOrderCreate
from services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["房间管理"])


@router.get("/stores", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
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
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
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
async def get_active_orders(db: AsyncSession = Depends(get_db)):
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
):
    order_id = uuid.uuid4().hex[:12]
    order = Order(
        orderId=order_id,
        orderNumber=f"ROOM{order_id[:8].upper()}",
        storeId="",
        customerId="",
        roomId=data.room_id,
        orderType="Room",
        status="PendingUse",
        totalAmount=data.total_amount,
        paidAmount=data.total_amount,
        platform=data.source or "Offline",
        bookingStartTime=f"{data.date} {data.start_time}" if data.date else None,
        bookingEndTime=f"{data.date} {data.end_time}" if data.date else None,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return RoomOrderOut(
        id=order.id, order_id=order.orderId, room_id=order.roomId or "",
        customer_name=data.customer_name, customer_phone=data.customer_phone,
        date=data.date, start_time=data.start_time, end_time=data.end_time,
        duration=data.duration, total_amount=data.total_amount,
        status=order.status, scene=data.scene or "", door_code="",
        source=data.source, payment_status="Paid",
        created_at=order.createdAt,
    )
