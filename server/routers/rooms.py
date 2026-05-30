import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from database import get_db
from models.room import Store, Room, RoomOrder
from models.user import User
from schemas.order import StoreOut, RoomOut, RoomOrderOut, RoomOrderCreate
from services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["房间管理"])


@router.get("/stores", response_model=list[StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Store).where(Store.is_active == True))
    stores = result.scalars().all()
    out = []
    for s in stores:
        room_result = await db.execute(
            select(Room).where(Room.store_id == s.store_id, Room.is_active == True)
        )
        rooms_list = room_result.scalars().all()
        store_out = StoreOut(
            id=s.id, store_id=s.store_id, name=s.name,
            address=s.address, phone=s.phone, is_active=s.is_active,
            rooms=[RoomOut(
                id=r.id, room_id=r.room_id, store_id=r.store_id,
                name=r.name, type=r.type, capacity=r.capacity,
                floor=r.floor, price_per_hour=r.price_per_hour,
                price_per_half_hour=r.price_per_half_hour,
                facilities=json.loads(r.facilities) if isinstance(r.facilities, str) else (r.facilities or []),
                description=r.description, is_active=r.is_active,
            ) for r in rooms_list]
        )
        out.append(store_out)
    return out


@router.get("/rooms", response_model=list[RoomOut])
async def list_rooms(
    store_id: Optional[str] = None,
    room_type: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Room).where(Room.is_active == True)
    if store_id:
        query = query.where(Room.store_id == store_id)
    if room_type:
        query = query.where(Room.type == room_type)

    result = await db.execute(query.order_by(Room.name))
    rooms = result.scalars().all()
    return [RoomOut(
        id=r.id, room_id=r.room_id, store_id=r.store_id,
        name=r.name, type=r.type, capacity=r.capacity,
        floor=r.floor, price_per_hour=r.price_per_hour,
        price_per_half_hour=r.price_per_half_hour,
        facilities=json.loads(r.facilities) if isinstance(r.facilities, str) else (r.facilities or []),
        description=r.description, is_active=r.is_active,
    ) for r in rooms]


@router.get("/rooms/{room_id}", response_model=RoomOut)
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Room).where(Room.room_id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    return RoomOut(
        id=room.id, room_id=room.room_id, store_id=room.store_id,
        name=room.name, type=room.type, capacity=room.capacity,
        floor=room.floor, price_per_hour=room.price_per_hour,
        price_per_half_hour=room.price_per_half_hour,
        facilities=json.loads(room.facilities) if isinstance(room.facilities, str) else (room.facilities or []),
        description=room.description, is_active=room.is_active,
    )


# ── Room Orders ──

@router.get("/orders", response_model=list[RoomOrderOut])
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(RoomOrder)
    if status_filter:
        query = query.where(RoomOrder.status == status_filter)
    query = query.order_by(RoomOrder.created_at.desc())
    result = await db.execute(query)
    orders = result.scalars().all()

    out = []
    for o in orders:
        room = None
        if o.room_id:
            r_result = await db.execute(select(Room).where(Room.room_id == o.room_id))
            r = r_result.scalar_one_or_none()
            if r:
                room = RoomOut(
                    id=r.id, room_id=r.room_id, store_id=r.store_id,
                    name=r.name, type=r.type, capacity=r.capacity,
                    floor=r.floor, price_per_hour=r.price_per_hour,
                    price_per_half_hour=r.price_per_half_hour,
                    facilities=json.loads(r.facilities) if isinstance(r.facilities, str) else (r.facilities or []),
                    description=r.description, is_active=r.is_active,
                )

        out.append(RoomOrderOut(
            id=o.id, order_id=o.order_id, room_id=o.room_id,
            customer_name=o.customer_name, customer_phone=o.customer_phone,
            date=o.date, start_time=o.start_time, end_time=o.end_time,
            duration=o.duration, total_amount=o.total_amount,
            status=o.status, scene=o.scene, door_code=o.door_code,
            source=o.source, payment_status=o.payment_status,
            check_in_time=o.check_in_time, check_out_time=o.check_out_time,
            created_at=o.created_at, room=room,
        ))
    return out


@router.get("/orders/active", response_model=list[RoomOrderOut])
async def get_active_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RoomOrder).where(
            or_(RoomOrder.status == "InUse", RoomOrder.status == "Booked")
        ).order_by(RoomOrder.created_at.desc())
    )
    orders = result.scalars().all()

    out = []
    for o in orders:
        room = None
        if o.room_id:
            r_result = await db.execute(select(Room).where(Room.room_id == o.room_id))
            r = r_result.scalar_one_or_none()
            if r:
                room = RoomOut(
                    id=r.id, room_id=r.room_id, store_id=r.store_id,
                    name=r.name, type=r.type, capacity=r.capacity,
                    floor=r.floor, price_per_hour=r.price_per_hour,
                    price_per_half_hour=r.price_per_half_hour,
                    facilities=json.loads(r.facilities) if isinstance(r.facilities, str) else (r.facilities or []),
                    description=r.description, is_active=r.is_active,
                )
        out.append(RoomOrderOut(
            id=o.id, order_id=o.order_id, room_id=o.room_id,
            customer_name=o.customer_name, customer_phone=o.customer_phone,
            date=o.date, start_time=o.start_time, end_time=o.end_time,
            duration=o.duration, total_amount=o.total_amount,
            status=o.status, scene=o.scene, door_code=o.door_code,
            source=o.source, payment_status=o.payment_status,
            check_in_time=o.check_in_time, check_out_time=o.check_out_time,
            created_at=o.created_at, room=room,
        ))
    return out


@router.post("/orders", response_model=RoomOrderOut)
async def create_order(
    data: RoomOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    # Generate order_id
    result = await db.execute(select(func.count()).select_from(RoomOrder))
    count = result.scalar() or 0
    order_id = f"ORD{count + 1:06d}"

    order = RoomOrder(
        order_id=order_id,
        room_id=data.room_id,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
        duration=data.duration,
        total_amount=data.total_amount,
        scene=data.scene,
        source=data.source,
        status="Booked",
        payment_status="Unpaid",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return RoomOrderOut(
        id=order.id, order_id=order.order_id, room_id=order.room_id,
        customer_name=order.customer_name, customer_phone=order.customer_phone,
        date=order.date, start_time=order.start_time, end_time=order.end_time,
        duration=order.duration, total_amount=order.total_amount,
        status=order.status, scene=order.scene, door_code=order.door_code,
        source=order.source, payment_status=order.payment_status,
        created_at=order.created_at,
    )
