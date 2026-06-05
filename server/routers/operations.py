"""门店运营管理 API — Customer / MemberCard / RoomAppointment / Cleaning / Inspection 等"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from datetime import datetime, date

from database import get_db
from models.operations import (
    Customer, CustomerTag, MemberCard, RechargeRecord,
    RoomAppointment, RoomStatus, CleaningTask,
    InspectionTemplate, InspectionTask, InspectionItemResult, RectificationTask,
)
from models.store_dev import Store, Room
from models.user import User
from schemas.operations import (
    CustomerCreate, CustomerUpdate, CustomerOut, CustomerListOut,
    CustomerTagCreate, CustomerTagOut, CustomerTagListOut,
    MemberCardCreate, MemberCardUpdate, MemberCardOut, MemberCardListOut,
    RechargeRecordCreate, RechargeRecordUpdate, RechargeRecordOut, RechargeRecordListOut,
    RoomAppointmentCreate, RoomAppointmentUpdate, RoomAppointmentOut, RoomAppointmentListOut,
    RoomStatusCreate, RoomStatusOut, RoomStatusListOut,
    CleaningTaskCreate, CleaningTaskUpdate, CleaningTaskOut, CleaningTaskListOut,
    InspectionTemplateCreate, InspectionTemplateUpdate, InspectionTemplateOut, InspectionTemplateListOut,
    InspectionTaskCreate, InspectionTaskUpdate, InspectionTaskOut, InspectionTaskListOut,
    InspectionItemResultCreate, InspectionItemResultUpdate, InspectionItemResultOut, InspectionItemResultListOut,
    RectificationTaskCreate, RectificationTaskUpdate, RectificationTaskOut, RectificationTaskListOut,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/operations", tags=["门店运营管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ═══════════════════════════════════════════════════════════════
# Customer 客户
# ═══════════════════════════════════════════════════════════════

@router.get("/customers/search", response_model=CustomerListOut)
async def search_customers(
    phone: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    wx_open_id: Optional[str] = Query(None, alias="wxOpenId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Search customers by phone, name, or wxOpenId."""
    q = select(Customer)
    if phone:
        q = q.where(Customer.phone.contains(phone))
    if name:
        q = q.where(Customer.name.contains(name))
    if wx_open_id:
        q = q.where(Customer.wxOpenId == wx_open_id)
    q = q.order_by(Customer.createdAt.desc())

    count_q = select(func.count(Customer.customerId)).select_from(Customer)
    if phone:
        count_q = count_q.where(Customer.phone.contains(phone))
    if name:
        count_q = count_q.where(Customer.name.contains(name))
    if wx_open_id:
        count_q = count_q.where(Customer.wxOpenId == wx_open_id)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CustomerListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/customers", response_model=CustomerListOut)
async def list_customers(
    member_level: Optional[str] = Query(None, alias="memberLevel"),
    register_store_id: Optional[str] = Query(None, alias="registerStoreId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Customer)
    if member_level:
        q = q.where(Customer.memberLevel == member_level)
    if register_store_id:
        q = q.where(Customer.registerStoreId == register_store_id)
    if status:
        q = q.where(Customer.status == status)
    q = q.order_by(Customer.createdAt.desc())

    count_q = select(func.count(Customer.customerId)).select_from(Customer)
    if member_level:
        count_q = count_q.where(Customer.memberLevel == member_level)
    if register_store_id:
        count_q = count_q.where(Customer.registerStoreId == register_store_id)
    if status:
        count_q = count_q.where(Customer.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CustomerListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/customers/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Customer).where(Customer.customerId == customer_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "客户不存在")
    return CustomerOut.model_validate(item)


@router.post("/customers", response_model=CustomerOut, status_code=201)
async def create_customer(
    data: CustomerCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check wxOpenId uniqueness
    r = await db.execute(select(Customer).where(Customer.wxOpenId == data.wxOpenId))
    if r.scalar_one_or_none():
        raise HTTPException(409, "该微信 OpenID 已注册")

    item = Customer(
        customerId=_gen_id(),
        wxOpenId=data.wxOpenId,
        wxUnionId=data.wxUnionId,
        phone=data.phone,
        name=data.name,
        nickname=data.nickname,
        avatar=data.avatar,
        gender=data.gender,
        birthday=data.birthday,
        memberLevel=data.memberLevel,
        registerStoreId=data.registerStoreId,
        tags=data.tags,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CustomerOut.model_validate(item)


@router.put("/customers/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: str,
    data: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Customer).where(Customer.customerId == customer_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "客户不存在")
    if data.phone is not None:
        item.phone = data.phone
    if data.name is not None:
        item.name = data.name
    if data.nickname is not None:
        item.nickname = data.nickname
    if data.avatar is not None:
        item.avatar = data.avatar
    if data.gender is not None:
        item.gender = data.gender
    if data.birthday is not None:
        item.birthday = data.birthday
    if data.memberLevel is not None:
        item.memberLevel = data.memberLevel
    if data.tags is not None:
        item.tags = data.tags
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return CustomerOut.model_validate(item)


# ═══════════════════════════════════════════════════════════════
# CustomerTag 客户标签
# ═══════════════════════════════════════════════════════════════

@router.get("/customer-tags", response_model=CustomerTagListOut)
async def list_customer_tags(
    customer_id: Optional[str] = Query(None, alias="customerId"),
    tag_type: Optional[str] = Query(None, alias="tagType"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CustomerTag)
    if customer_id:
        q = q.where(CustomerTag.customerId == customer_id)
    if tag_type:
        q = q.where(CustomerTag.tagType == tag_type)
    q = q.order_by(CustomerTag.createdAt.desc())

    count_q = select(func.count(CustomerTag.tagId)).select_from(CustomerTag)
    if customer_id:
        count_q = count_q.where(CustomerTag.customerId == customer_id)
    if tag_type:
        count_q = count_q.where(CustomerTag.tagType == tag_type)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CustomerTagListOut(total=total, items=items, page=page, page_size=page_size)


@router.post("/customer-tags", response_model=CustomerTagOut, status_code=201)
async def create_customer_tag(
    data: CustomerTagCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify customer exists
    r = await db.execute(select(Customer).where(Customer.customerId == data.customerId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "客户不存在")

    item = CustomerTag(
        tagId=_gen_id(),
        customerId=data.customerId,
        tagType=data.tagType,
        tagValue=data.tagValue,
        source=data.source,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CustomerTagOut.model_validate(item)


@router.delete("/customer-tags/{tag_id}", status_code=204)
async def delete_customer_tag(tag_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CustomerTag).where(CustomerTag.tagId == tag_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "标签不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════════════════════════
# MemberCard 会员卡
# ═══════════════════════════════════════════════════════════════

@router.get("/member-cards/by-customer/{customer_id}", response_model=list[MemberCardOut])
async def get_customer_member_cards(
    customer_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get all member cards for a customer."""
    r = await db.execute(
        select(MemberCard).where(MemberCard.customerId == customer_id)
        .order_by(MemberCard.createdAt.desc())
    )
    items = r.scalars().all()
    return [MemberCardOut.model_validate(item) for item in items]


@router.get("/member-cards", response_model=MemberCardListOut)
async def list_member_cards(
    customer_id: Optional[str] = Query(None, alias="customerId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(MemberCard)
    if customer_id:
        q = q.where(MemberCard.customerId == customer_id)
    if status:
        q = q.where(MemberCard.status == status)
    q = q.order_by(MemberCard.createdAt.desc())

    count_q = select(func.count(MemberCard.cardId)).select_from(MemberCard)
    if customer_id:
        count_q = count_q.where(MemberCard.customerId == customer_id)
    if status:
        count_q = count_q.where(MemberCard.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return MemberCardListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/member-cards/{card_id}", response_model=MemberCardOut)
async def get_member_card(card_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(MemberCard).where(MemberCard.cardId == card_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会员卡不存在")
    return MemberCardOut.model_validate(item)


@router.post("/member-cards", response_model=MemberCardOut, status_code=201)
async def create_member_card(
    data: MemberCardCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check cardNumber uniqueness
    r = await db.execute(select(MemberCard).where(MemberCard.cardNumber == data.cardNumber))
    if r.scalar_one_or_none():
        raise HTTPException(409, "卡号已存在")

    # Verify customer exists
    r = await db.execute(select(Customer).where(Customer.customerId == data.customerId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "客户不存在")

    item = MemberCard(
        cardId=_gen_id(),
        cardNumber=data.cardNumber,
        customerId=data.customerId,
        balance=data.balance,
        bonusBalance=data.bonusBalance,
        totalRecharge=data.totalRecharge,
        totalConsume=data.totalConsume,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return MemberCardOut.model_validate(item)


@router.put("/member-cards/{card_id}", response_model=MemberCardOut)
async def update_member_card(
    card_id: str,
    data: MemberCardUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(MemberCard).where(MemberCard.cardId == card_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会员卡不存在")
    if data.balance is not None:
        item.balance = data.balance
    if data.bonusBalance is not None:
        item.bonusBalance = data.bonusBalance
    if data.totalRecharge is not None:
        item.totalRecharge = data.totalRecharge
    if data.totalConsume is not None:
        item.totalConsume = data.totalConsume
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return MemberCardOut.model_validate(item)


# ═══════════════════════════════════════════════════════════════
# RechargeRecord 充值记录
# ═══════════════════════════════════════════════════════════════

@router.get("/recharge-records", response_model=RechargeRecordListOut)
async def list_recharge_records(
    card_id: Optional[str] = Query(None, alias="cardId"),
    store_id: Optional[str] = Query(None, alias="storeId"),
    payment_method: Optional[str] = Query(None, alias="paymentMethod"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RechargeRecord)
    if card_id:
        q = q.where(RechargeRecord.cardId == card_id)
    if store_id:
        q = q.where(RechargeRecord.storeId == store_id)
    if payment_method:
        q = q.where(RechargeRecord.paymentMethod == payment_method)
    q = q.order_by(RechargeRecord.createdAt.desc())

    count_q = select(func.count(RechargeRecord.rechargeId)).select_from(RechargeRecord)
    if card_id:
        count_q = count_q.where(RechargeRecord.cardId == card_id)
    if store_id:
        count_q = count_q.where(RechargeRecord.storeId == store_id)
    if payment_method:
        count_q = count_q.where(RechargeRecord.paymentMethod == payment_method)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(RechargeRecordOut(
            rechargeId=item.rechargeId,
            cardId=item.cardId,
            amount=item.amount,
            bonusAmount=item.bonusAmount,
            paymentMethod=item.paymentMethod,
            transactionId=item.transactionId,
            isRevenue=item.isRevenue,
            storeId=item.storeId,
            storeName=store_name,
            createdAt=item.createdAt,
        ))

    return RechargeRecordListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/recharge-records/{recharge_id}", response_model=RechargeRecordOut)
async def get_recharge_record(recharge_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RechargeRecord).where(RechargeRecord.rechargeId == recharge_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "充值记录不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return RechargeRecordOut(
        rechargeId=item.rechargeId,
        cardId=item.cardId,
        amount=item.amount,
        bonusAmount=item.bonusAmount,
        paymentMethod=item.paymentMethod,
        transactionId=item.transactionId,
        isRevenue=item.isRevenue,
        storeId=item.storeId,
        storeName=store_name,
        createdAt=item.createdAt,
    )


@router.post("/recharge-records", response_model=RechargeRecordOut, status_code=201)
async def create_recharge_record(
    data: RechargeRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify card exists
    r = await db.execute(select(MemberCard).where(MemberCard.cardId == data.cardId))
    card = r.scalar_one_or_none()
    if not card:
        raise HTTPException(404, "会员卡不存在")

    item = RechargeRecord(
        rechargeId=_gen_id(),
        cardId=data.cardId,
        amount=data.amount,
        bonusAmount=data.bonusAmount,
        paymentMethod=data.paymentMethod,
        transactionId=data.transactionId,
        isRevenue=data.isRevenue,
        storeId=data.storeId,
    )
    db.add(item)

    # Update card balance
    card.balance += data.amount
    card.totalRecharge += data.amount
    if data.bonusAmount > 0:
        card.bonusBalance += data.bonusAmount

    await db.commit()
    await db.refresh(item)

    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return RechargeRecordOut(
        rechargeId=item.rechargeId,
        cardId=item.cardId,
        amount=item.amount,
        bonusAmount=item.bonusAmount,
        paymentMethod=item.paymentMethod,
        transactionId=item.transactionId,
        isRevenue=item.isRevenue,
        storeId=item.storeId,
        storeName=store_name,
        createdAt=item.createdAt,
    )


@router.put("/recharge-records/{recharge_id}", response_model=RechargeRecordOut)
async def update_recharge_record(
    recharge_id: str,
    data: RechargeRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RechargeRecord).where(RechargeRecord.rechargeId == recharge_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "充值记录不存在")
    if data.transactionId is not None:
        item.transactionId = data.transactionId
    if data.isRevenue is not None:
        item.isRevenue = data.isRevenue
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return RechargeRecordOut(
        rechargeId=item.rechargeId,
        cardId=item.cardId,
        amount=item.amount,
        bonusAmount=item.bonusAmount,
        paymentMethod=item.paymentMethod,
        transactionId=item.transactionId,
        isRevenue=item.isRevenue,
        storeId=item.storeId,
        storeName=store_name,
        createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════════════
# RoomAppointment 房间预约
# ═══════════════════════════════════════════════════════════════

@router.get("/room-appointments", response_model=RoomAppointmentListOut)
async def list_room_appointments(
    room_id: Optional[str] = Query(None, alias="roomId"),
    customer_id: Optional[str] = Query(None, alias="customerId"),
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RoomAppointment)
    if room_id:
        q = q.where(RoomAppointment.roomId == room_id)
    if customer_id:
        q = q.where(RoomAppointment.customerId == customer_id)
    if status:
        q = q.where(RoomAppointment.status == status)
    if start_date:
        q = q.where(RoomAppointment.startTime >= start_date)
    if end_date:
        q = q.where(RoomAppointment.endTime <= end_date + " 23:59:59")
    q = q.order_by(RoomAppointment.startTime.desc())

    count_q = select(func.count(RoomAppointment.appointmentId)).select_from(RoomAppointment)
    if room_id:
        count_q = count_q.where(RoomAppointment.roomId == room_id)
    if customer_id:
        count_q = count_q.where(RoomAppointment.customerId == customer_id)
    if status:
        count_q = count_q.where(RoomAppointment.status == status)
    if start_date:
        count_q = count_q.where(RoomAppointment.startTime >= start_date)
    if end_date:
        count_q = count_q.where(RoomAppointment.endTime <= end_date + " 23:59:59")

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        room_name = None
        if item.roomId:
            sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
            room_name = sr.scalar_one_or_none()
        customer_name = None
        if item.customerId:
            sr = await db.execute(select(Customer.name).where(Customer.customerId == item.customerId))
            customer_name = sr.scalar_one_or_none()
        result.append(RoomAppointmentOut(
            appointmentId=item.appointmentId,
            orderId=item.orderId,
            roomId=item.roomId,
            roomName=room_name,
            customerId=item.customerId,
            customerName=customer_name,
            startTime=item.startTime,
            endTime=item.endTime,
            status=item.status,
            cancelTime=item.cancelTime,
            cancelReason=item.cancelReason,
            doorPassword=item.doorPassword,
            preOpenSent=item.preOpenSent,
        ))

    return RoomAppointmentListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/room-appointments/{appointment_id}", response_model=RoomAppointmentOut)
async def get_room_appointment(appointment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomAppointment).where(RoomAppointment.appointmentId == appointment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预约记录不存在")
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    customer_name = None
    if item.customerId:
        sr = await db.execute(select(Customer.name).where(Customer.customerId == item.customerId))
        customer_name = sr.scalar_one_or_none()
    return RoomAppointmentOut(
        appointmentId=item.appointmentId,
        orderId=item.orderId,
        roomId=item.roomId,
        roomName=room_name,
        customerId=item.customerId,
        customerName=customer_name,
        startTime=item.startTime,
        endTime=item.endTime,
        status=item.status,
        cancelTime=item.cancelTime,
        cancelReason=item.cancelReason,
        doorPassword=item.doorPassword,
        preOpenSent=item.preOpenSent,
    )


@router.post("/room-appointments", response_model=RoomAppointmentOut, status_code=201)
async def create_room_appointment(
    data: RoomAppointmentCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify room exists
    r = await db.execute(select(Room).where(Room.roomId == data.roomId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "房间不存在")

    item = RoomAppointment(
        appointmentId=_gen_id(),
        orderId=data.orderId,
        roomId=data.roomId,
        customerId=data.customerId,
        startTime=data.startTime,
        endTime=data.endTime,
        doorPassword=data.doorPassword,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    customer_name = None
    if item.customerId:
        sr = await db.execute(select(Customer.name).where(Customer.customerId == item.customerId))
        customer_name = sr.scalar_one_or_none()
    return RoomAppointmentOut(
        appointmentId=item.appointmentId,
        orderId=item.orderId,
        roomId=item.roomId,
        roomName=room_name,
        customerId=item.customerId,
        customerName=customer_name,
        startTime=item.startTime,
        endTime=item.endTime,
        status=item.status,
        cancelTime=item.cancelTime,
        cancelReason=item.cancelReason,
        doorPassword=item.doorPassword,
        preOpenSent=item.preOpenSent,
    )


@router.put("/room-appointments/{appointment_id}", response_model=RoomAppointmentOut)
async def update_room_appointment(
    appointment_id: str,
    data: RoomAppointmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RoomAppointment).where(RoomAppointment.appointmentId == appointment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预约记录不存在")
    if data.startTime is not None:
        item.startTime = data.startTime
    if data.endTime is not None:
        item.endTime = data.endTime
    if data.status is not None:
        item.status = data.status
    if data.cancelTime is not None:
        item.cancelTime = data.cancelTime
    if data.cancelReason is not None:
        item.cancelReason = data.cancelReason
    if data.doorPassword is not None:
        item.doorPassword = data.doorPassword
    if data.preOpenSent is not None:
        item.preOpenSent = data.preOpenSent
    await db.commit()
    await db.refresh(item)

    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    customer_name = None
    if item.customerId:
        sr = await db.execute(select(Customer.name).where(Customer.customerId == item.customerId))
        customer_name = sr.scalar_one_or_none()
    return RoomAppointmentOut(
        appointmentId=item.appointmentId,
        orderId=item.orderId,
        roomId=item.roomId,
        roomName=room_name,
        customerId=item.customerId,
        customerName=customer_name,
        startTime=item.startTime,
        endTime=item.endTime,
        status=item.status,
        cancelTime=item.cancelTime,
        cancelReason=item.cancelReason,
        doorPassword=item.doorPassword,
        preOpenSent=item.preOpenSent,
    )


# ═══════════════════════════════════════════════════════════════
# RoomStatus 房间状态
# ═══════════════════════════════════════════════════════════════

@router.get("/room-status/current/{room_id}", response_model=RoomStatusOut)
async def get_current_room_status(room_id: str, db: AsyncSession = Depends(get_db)):
    """Get the current (latest) status for a room."""
    r = await db.execute(
        select(RoomStatus)
        .where(RoomStatus.roomId == room_id)
        .order_by(RoomStatus.lastStatusChange.desc())
        .limit(1)
    )
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "该房间无状态记录")
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    return RoomStatusOut(
        statusId=item.statusId,
        roomId=item.roomId,
        roomName=room_name,
        status=item.status,
        currentOrderId=item.currentOrderId,
        lastStatusChange=item.lastStatusChange,
        changedBy=item.changedBy,
        changeReason=item.changeReason,
        isManual=item.isManual,
        createdAt=item.createdAt,
    )


@router.get("/room-status", response_model=RoomStatusListOut)
async def list_room_statuses(
    room_id: Optional[str] = Query(None, alias="roomId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RoomStatus)
    if room_id:
        q = q.where(RoomStatus.roomId == room_id)
    if status:
        q = q.where(RoomStatus.status == status)
    q = q.order_by(RoomStatus.lastStatusChange.desc())

    count_q = select(func.count(RoomStatus.statusId)).select_from(RoomStatus)
    if room_id:
        count_q = count_q.where(RoomStatus.roomId == room_id)
    if status:
        count_q = count_q.where(RoomStatus.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        room_name = None
        if item.roomId:
            sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
            room_name = sr.scalar_one_or_none()
        result.append(RoomStatusOut(
            statusId=item.statusId,
            roomId=item.roomId,
            roomName=room_name,
            status=item.status,
            currentOrderId=item.currentOrderId,
            lastStatusChange=item.lastStatusChange,
            changedBy=item.changedBy,
            changeReason=item.changeReason,
            isManual=item.isManual,
            createdAt=item.createdAt,
        ))

    return RoomStatusListOut(total=total, items=result, page=page, page_size=page_size)


@router.post("/room-status", response_model=RoomStatusOut, status_code=201)
async def create_room_status(
    data: RoomStatusCreate,
    db: AsyncSession = Depends(get_db),
):
    item = RoomStatus(
        statusId=_gen_id(),
        roomId=data.roomId,
        status=data.status,
        currentOrderId=data.currentOrderId,
        lastStatusChange=data.lastStatusChange,
        changedBy=data.changedBy,
        changeReason=data.changeReason,
        isManual=data.isManual,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    return RoomStatusOut(
        statusId=item.statusId,
        roomId=item.roomId,
        roomName=room_name,
        status=item.status,
        currentOrderId=item.currentOrderId,
        lastStatusChange=item.lastStatusChange,
        changedBy=item.changedBy,
        changeReason=item.changeReason,
        isManual=item.isManual,
        createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════════════
# CleaningTask 保洁任务
# ═══════════════════════════════════════════════════════════════

@router.get("/cleaning-tasks/today", response_model=CleaningTaskListOut)
async def get_today_cleaning_tasks(
    store_id: str = Query(..., alias="storeId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get today's cleaning tasks for a store."""
    today_start = datetime.utcnow().strftime("%Y-%m-%d") + " 00:00:00"
    today_end = datetime.utcnow().strftime("%Y-%m-%d") + " 23:59:59"

    q = select(CleaningTask).where(
        CleaningTask.storeId == store_id,
        CleaningTask.createTime >= today_start,
        CleaningTask.createTime <= today_end,
    ).order_by(CleaningTask.createTime.desc())

    count_q = select(func.count(CleaningTask.taskId)).select_from(CleaningTask).where(
        CleaningTask.storeId == store_id,
        CleaningTask.createTime >= today_start,
        CleaningTask.createTime <= today_end,
    )

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        room_name = None
        if item.roomId:
            sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
            room_name = sr.scalar_one_or_none()
        result.append(CleaningTaskOut(
            taskId=item.taskId,
            storeId=item.storeId,
            storeName=store_name,
            roomId=item.roomId,
            roomName=room_name,
            orderId=item.orderId,
            assignedType=item.assignedType,
            assignedId=item.assignedId,
            status=item.status,
            createTime=item.createTime,
            acceptTime=item.acceptTime,
            completeTime=item.completeTime,
            deadline=item.deadline,
            deviceFaultReported=item.deviceFaultReported,
            deviceFaultDescription=item.deviceFaultDescription,
        ))

    return CleaningTaskListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/cleaning-tasks", response_model=CleaningTaskListOut)
async def list_cleaning_tasks(
    store_id: Optional[str] = Query(None, alias="storeId"),
    room_id: Optional[str] = Query(None, alias="roomId"),
    status: Optional[str] = None,
    assigned_id: Optional[str] = Query(None, alias="assignedId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CleaningTask)
    if store_id:
        q = q.where(CleaningTask.storeId == store_id)
    if room_id:
        q = q.where(CleaningTask.roomId == room_id)
    if status:
        q = q.where(CleaningTask.status == status)
    if assigned_id:
        q = q.where(CleaningTask.assignedId == assigned_id)
    q = q.order_by(CleaningTask.createTime.desc())

    count_q = select(func.count(CleaningTask.taskId)).select_from(CleaningTask)
    if store_id:
        count_q = count_q.where(CleaningTask.storeId == store_id)
    if room_id:
        count_q = count_q.where(CleaningTask.roomId == room_id)
    if status:
        count_q = count_q.where(CleaningTask.status == status)
    if assigned_id:
        count_q = count_q.where(CleaningTask.assignedId == assigned_id)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        room_name = None
        if item.roomId:
            sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
            room_name = sr.scalar_one_or_none()
        result.append(CleaningTaskOut(
            taskId=item.taskId,
            storeId=item.storeId,
            storeName=store_name,
            roomId=item.roomId,
            roomName=room_name,
            orderId=item.orderId,
            assignedType=item.assignedType,
            assignedId=item.assignedId,
            status=item.status,
            createTime=item.createTime,
            acceptTime=item.acceptTime,
            completeTime=item.completeTime,
            deadline=item.deadline,
            deviceFaultReported=item.deviceFaultReported,
            deviceFaultDescription=item.deviceFaultDescription,
        ))

    return CleaningTaskListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/cleaning-tasks/{task_id}", response_model=CleaningTaskOut)
async def get_cleaning_task(task_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CleaningTask).where(CleaningTask.taskId == task_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "保洁任务不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    return CleaningTaskOut(
        taskId=item.taskId,
        storeId=item.storeId,
        storeName=store_name,
        roomId=item.roomId,
        roomName=room_name,
        orderId=item.orderId,
        assignedType=item.assignedType,
        assignedId=item.assignedId,
        status=item.status,
        createTime=item.createTime,
        acceptTime=item.acceptTime,
        completeTime=item.completeTime,
        deadline=item.deadline,
        deviceFaultReported=item.deviceFaultReported,
        deviceFaultDescription=item.deviceFaultDescription,
    )


@router.post("/cleaning-tasks", response_model=CleaningTaskOut, status_code=201)
async def create_cleaning_task(
    data: CleaningTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CleaningTask(
        taskId=_gen_id(),
        storeId=data.storeId,
        roomId=data.roomId,
        orderId=data.orderId,
        assignedType=data.assignedType,
        assignedId=data.assignedId,
        status="Pending",
        createTime=datetime.utcnow(),
        deadline=data.deadline,
        deviceFaultReported=data.deviceFaultReported,
        deviceFaultDescription=data.deviceFaultDescription,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    return CleaningTaskOut(
        taskId=item.taskId,
        storeId=item.storeId,
        storeName=store_name,
        roomId=item.roomId,
        roomName=room_name,
        orderId=item.orderId,
        assignedType=item.assignedType,
        assignedId=item.assignedId,
        status=item.status,
        createTime=item.createTime,
        acceptTime=item.acceptTime,
        completeTime=item.completeTime,
        deadline=item.deadline,
        deviceFaultReported=item.deviceFaultReported,
        deviceFaultDescription=item.deviceFaultDescription,
    )


@router.put("/cleaning-tasks/{task_id}", response_model=CleaningTaskOut)
async def update_cleaning_task(
    task_id: str,
    data: CleaningTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CleaningTask).where(CleaningTask.taskId == task_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "保洁任务不存在")
    if data.status is not None:
        item.status = data.status
    if data.acceptTime is not None:
        item.acceptTime = data.acceptTime
    if data.completeTime is not None:
        item.completeTime = data.completeTime
    if data.deviceFaultReported is not None:
        item.deviceFaultReported = data.deviceFaultReported
    if data.deviceFaultDescription is not None:
        item.deviceFaultDescription = data.deviceFaultDescription
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    room_name = None
    if item.roomId:
        sr = await db.execute(select(Room.name).where(Room.roomId == item.roomId))
        room_name = sr.scalar_one_or_none()
    return CleaningTaskOut(
        taskId=item.taskId,
        storeId=item.storeId,
        storeName=store_name,
        roomId=item.roomId,
        roomName=room_name,
        orderId=item.orderId,
        assignedType=item.assignedType,
        assignedId=item.assignedId,
        status=item.status,
        createTime=item.createTime,
        acceptTime=item.acceptTime,
        completeTime=item.completeTime,
        deadline=item.deadline,
        deviceFaultReported=item.deviceFaultReported,
        deviceFaultDescription=item.deviceFaultDescription,
    )


# ═══════════════════════════════════════════════════════════════
# InspectionTemplate 巡检模板
# ═══════════════════════════════════════════════════════════════

@router.get("/inspection-templates", response_model=InspectionTemplateListOut)
async def list_inspection_templates(
    store_id: Optional[str] = Query(None, alias="storeId"),
    frequency: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(InspectionTemplate)
    if store_id:
        q = q.where(InspectionTemplate.storeId == store_id)
    if frequency:
        q = q.where(InspectionTemplate.frequency == frequency)
    if status:
        q = q.where(InspectionTemplate.status == status)
    q = q.order_by(InspectionTemplate.name.asc())

    count_q = select(func.count(InspectionTemplate.templateId)).select_from(InspectionTemplate)
    if store_id:
        count_q = count_q.where(InspectionTemplate.storeId == store_id)
    if frequency:
        count_q = count_q.where(InspectionTemplate.frequency == frequency)
    if status:
        count_q = count_q.where(InspectionTemplate.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(InspectionTemplateOut(
            templateId=item.templateId,
            storeId=item.storeId,
            storeName=store_name,
            name=item.name,
            items=item.items,
            isDefault=item.isDefault,
            frequency=item.frequency,
            status=item.status,
        ))

    return InspectionTemplateListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/inspection-templates/{template_id}", response_model=InspectionTemplateOut)
async def get_inspection_template(template_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(InspectionTemplate).where(InspectionTemplate.templateId == template_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检模板不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InspectionTemplateOut(
        templateId=item.templateId,
        storeId=item.storeId,
        storeName=store_name,
        name=item.name,
        items=item.items,
        isDefault=item.isDefault,
        frequency=item.frequency,
        status=item.status,
    )


@router.post("/inspection-templates", response_model=InspectionTemplateOut, status_code=201)
async def create_inspection_template(
    data: InspectionTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    item = InspectionTemplate(
        templateId=_gen_id(),
        storeId=data.storeId,
        name=data.name,
        items=data.items,
        isDefault=data.isDefault,
        frequency=data.frequency,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InspectionTemplateOut(
        templateId=item.templateId,
        storeId=item.storeId,
        storeName=store_name,
        name=item.name,
        items=item.items,
        isDefault=item.isDefault,
        frequency=item.frequency,
        status=item.status,
    )


@router.put("/inspection-templates/{template_id}", response_model=InspectionTemplateOut)
async def update_inspection_template(
    template_id: str,
    data: InspectionTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(InspectionTemplate).where(InspectionTemplate.templateId == template_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检模板不存在")
    if data.name is not None:
        item.name = data.name
    if data.items is not None:
        item.items = data.items
    if data.isDefault is not None:
        item.isDefault = data.isDefault
    if data.frequency is not None:
        item.frequency = data.frequency
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InspectionTemplateOut(
        templateId=item.templateId,
        storeId=item.storeId,
        storeName=store_name,
        name=item.name,
        items=item.items,
        isDefault=item.isDefault,
        frequency=item.frequency,
        status=item.status,
    )


# ═══════════════════════════════════════════════════════════════
# InspectionTask 巡检任务
# ═══════════════════════════════════════════════════════════════

@router.get("/inspection-tasks/pending", response_model=InspectionTaskListOut)
async def get_pending_inspection_tasks(
    store_id: str = Query(..., alias="storeId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Get pending/submitted inspection tasks for a store."""
    q = select(InspectionTask).where(
        InspectionTask.storeId == store_id,
        InspectionTask.status.in_(["Pending", "InProgress", "Submitted"]),
    ).order_by(InspectionTask.deadline.asc())

    count_q = select(func.count(InspectionTask.inspectionId)).select_from(InspectionTask).where(
        InspectionTask.storeId == store_id,
        InspectionTask.status.in_(["Pending", "InProgress", "Submitted"]),
    )

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        template_name = None
        if item.templateId:
            sr = await db.execute(select(InspectionTemplate.name).where(InspectionTemplate.templateId == item.templateId))
            template_name = sr.scalar_one_or_none()
        result.append(InspectionTaskOut(
            inspectionId=item.inspectionId,
            storeId=item.storeId,
            storeName=store_name,
            templateId=item.templateId,
            templateName=template_name,
            assigneeId=item.assigneeId,
            status=item.status,
            deadline=item.deadline,
            submitTime=item.submitTime,
            abnormalCount=item.abnormalCount,
            reviewerId=item.reviewerId,
            reviewComment=item.reviewComment,
        ))

    return InspectionTaskListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/inspection-tasks", response_model=InspectionTaskListOut)
async def list_inspection_tasks(
    store_id: Optional[str] = Query(None, alias="storeId"),
    template_id: Optional[str] = Query(None, alias="templateId"),
    assignee_id: Optional[str] = Query(None, alias="assigneeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(InspectionTask)
    if store_id:
        q = q.where(InspectionTask.storeId == store_id)
    if template_id:
        q = q.where(InspectionTask.templateId == template_id)
    if assignee_id:
        q = q.where(InspectionTask.assigneeId == assignee_id)
    if status:
        q = q.where(InspectionTask.status == status)
    q = q.order_by(InspectionTask.deadline.asc())

    count_q = select(func.count(InspectionTask.inspectionId)).select_from(InspectionTask)
    if store_id:
        count_q = count_q.where(InspectionTask.storeId == store_id)
    if template_id:
        count_q = count_q.where(InspectionTask.templateId == template_id)
    if assignee_id:
        count_q = count_q.where(InspectionTask.assigneeId == assignee_id)
    if status:
        count_q = count_q.where(InspectionTask.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        template_name = None
        if item.templateId:
            sr = await db.execute(select(InspectionTemplate.name).where(InspectionTemplate.templateId == item.templateId))
            template_name = sr.scalar_one_or_none()
        result.append(InspectionTaskOut(
            inspectionId=item.inspectionId,
            storeId=item.storeId,
            storeName=store_name,
            templateId=item.templateId,
            templateName=template_name,
            assigneeId=item.assigneeId,
            status=item.status,
            deadline=item.deadline,
            submitTime=item.submitTime,
            abnormalCount=item.abnormalCount,
            reviewerId=item.reviewerId,
            reviewComment=item.reviewComment,
        ))

    return InspectionTaskListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/inspection-tasks/{inspection_id}", response_model=InspectionTaskOut)
async def get_inspection_task(inspection_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(InspectionTask).where(InspectionTask.inspectionId == inspection_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检任务不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    template_name = None
    if item.templateId:
        sr = await db.execute(select(InspectionTemplate.name).where(InspectionTemplate.templateId == item.templateId))
        template_name = sr.scalar_one_or_none()
    return InspectionTaskOut(
        inspectionId=item.inspectionId,
        storeId=item.storeId,
        storeName=store_name,
        templateId=item.templateId,
        templateName=template_name,
        assigneeId=item.assigneeId,
        status=item.status,
        deadline=item.deadline,
        submitTime=item.submitTime,
        abnormalCount=item.abnormalCount,
        reviewerId=item.reviewerId,
        reviewComment=item.reviewComment,
    )


@router.post("/inspection-tasks", response_model=InspectionTaskOut, status_code=201)
async def create_inspection_task(
    data: InspectionTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify template exists
    r = await db.execute(select(InspectionTemplate).where(InspectionTemplate.templateId == data.templateId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "巡检模板不存在")

    item = InspectionTask(
        inspectionId=_gen_id(),
        storeId=data.storeId,
        templateId=data.templateId,
        assigneeId=data.assigneeId,
        deadline=data.deadline,
        reviewerId=data.reviewerId,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    template_name = None
    if item.templateId:
        sr = await db.execute(select(InspectionTemplate.name).where(InspectionTemplate.templateId == item.templateId))
        template_name = sr.scalar_one_or_none()
    return InspectionTaskOut(
        inspectionId=item.inspectionId,
        storeId=item.storeId,
        storeName=store_name,
        templateId=item.templateId,
        templateName=template_name,
        assigneeId=item.assigneeId,
        status=item.status,
        deadline=item.deadline,
        submitTime=item.submitTime,
        abnormalCount=item.abnormalCount,
        reviewerId=item.reviewerId,
        reviewComment=item.reviewComment,
    )


@router.put("/inspection-tasks/{inspection_id}", response_model=InspectionTaskOut)
async def update_inspection_task(
    inspection_id: str,
    data: InspectionTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(InspectionTask).where(InspectionTask.inspectionId == inspection_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检任务不存在")
    if data.status is not None:
        item.status = data.status
    if data.submitTime is not None:
        item.submitTime = data.submitTime
    if data.abnormalCount is not None:
        item.abnormalCount = data.abnormalCount
    if data.reviewerId is not None:
        item.reviewerId = data.reviewerId
    if data.reviewComment is not None:
        item.reviewComment = data.reviewComment
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    template_name = None
    if item.templateId:
        sr = await db.execute(select(InspectionTemplate.name).where(InspectionTemplate.templateId == item.templateId))
        template_name = sr.scalar_one_or_none()
    return InspectionTaskOut(
        inspectionId=item.inspectionId,
        storeId=item.storeId,
        storeName=store_name,
        templateId=item.templateId,
        templateName=template_name,
        assigneeId=item.assigneeId,
        status=item.status,
        deadline=item.deadline,
        submitTime=item.submitTime,
        abnormalCount=item.abnormalCount,
        reviewerId=item.reviewerId,
        reviewComment=item.reviewComment,
    )


# ═══════════════════════════════════════════════════════════════
# InspectionItemResult 巡检项目结果
# ═══════════════════════════════════════════════════════════════

@router.get("/inspection-item-results", response_model=InspectionItemResultListOut)
async def list_inspection_item_results(
    inspection_id: Optional[str] = Query(None, alias="inspectionId"),
    category: Optional[str] = None,
    is_normal: Optional[bool] = Query(None, alias="isNormal"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(InspectionItemResult)
    if inspection_id:
        q = q.where(InspectionItemResult.inspectionId == inspection_id)
    if category:
        q = q.where(InspectionItemResult.category == category)
    if is_normal is not None:
        q = q.where(InspectionItemResult.isNormal == is_normal)
    q = q.order_by(InspectionItemResult.itemName.asc())

    count_q = select(func.count(InspectionItemResult.resultId)).select_from(InspectionItemResult)
    if inspection_id:
        count_q = count_q.where(InspectionItemResult.inspectionId == inspection_id)
    if category:
        count_q = count_q.where(InspectionItemResult.category == category)
    if is_normal is not None:
        count_q = count_q.where(InspectionItemResult.isNormal == is_normal)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return InspectionItemResultListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/inspection-item-results/{result_id}", response_model=InspectionItemResultOut)
async def get_inspection_item_result(result_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(InspectionItemResult).where(InspectionItemResult.resultId == result_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检项目结果不存在")
    return InspectionItemResultOut.model_validate(item)


@router.post("/inspection-item-results", response_model=InspectionItemResultOut, status_code=201)
async def create_inspection_item_result(
    data: InspectionItemResultCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify inspection task exists
    r = await db.execute(select(InspectionTask).where(InspectionTask.inspectionId == data.inspectionId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "巡检任务不存在")

    item = InspectionItemResult(
        resultId=_gen_id(),
        inspectionId=data.inspectionId,
        itemName=data.itemName,
        category=data.category,
        isNormal=data.isNormal,
        photoUrls=data.photoUrls,
        remark=data.remark,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return InspectionItemResultOut.model_validate(item)


@router.put("/inspection-item-results/{result_id}", response_model=InspectionItemResultOut)
async def update_inspection_item_result(
    result_id: str,
    data: InspectionItemResultUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(InspectionItemResult).where(InspectionItemResult.resultId == result_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "巡检项目结果不存在")
    if data.isNormal is not None:
        item.isNormal = data.isNormal
    if data.photoUrls is not None:
        item.photoUrls = data.photoUrls
    if data.remark is not None:
        item.remark = data.remark
    if data.rectificationStatus is not None:
        item.rectificationStatus = data.rectificationStatus
    await db.commit()
    await db.refresh(item)
    return InspectionItemResultOut.model_validate(item)


# ═══════════════════════════════════════════════════════════════
# RectificationTask 整改任务
# ═══════════════════════════════════════════════════════════════

@router.get("/rectification-tasks", response_model=RectificationTaskListOut)
async def list_rectification_tasks(
    inspection_id: Optional[str] = Query(None, alias="inspectionId"),
    assignee_id: Optional[str] = Query(None, alias="assigneeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RectificationTask)
    if inspection_id:
        q = q.where(RectificationTask.inspectionId == inspection_id)
    if assignee_id:
        q = q.where(RectificationTask.assigneeId == assignee_id)
    if status:
        q = q.where(RectificationTask.status == status)
    q = q.order_by(RectificationTask.deadline.asc())

    count_q = select(func.count(RectificationTask.rectificationId)).select_from(RectificationTask)
    if inspection_id:
        count_q = count_q.where(RectificationTask.inspectionId == inspection_id)
    if assignee_id:
        count_q = count_q.where(RectificationTask.assigneeId == assignee_id)
    if status:
        count_q = count_q.where(RectificationTask.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return RectificationTaskListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/rectification-tasks/{rectification_id}", response_model=RectificationTaskOut)
async def get_rectification_task(rectification_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RectificationTask).where(RectificationTask.rectificationId == rectification_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "整改任务不存在")
    return RectificationTaskOut.model_validate(item)


@router.post("/rectification-tasks", response_model=RectificationTaskOut, status_code=201)
async def create_rectification_task(
    data: RectificationTaskCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify item result exists
    r = await db.execute(select(InspectionItemResult).where(InspectionItemResult.resultId == data.itemResultId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "巡检项目结果不存在")

    item = RectificationTask(
        rectificationId=_gen_id(),
        inspectionId=data.inspectionId,
        itemResultId=data.itemResultId,
        assigneeId=data.assigneeId,
        description=data.description,
        deadline=data.deadline,
        completePhotoUrls=data.completePhotoUrls,
    )
    db.add(item)

    # Update item result rectification status
    r = await db.execute(select(InspectionItemResult).where(InspectionItemResult.resultId == data.itemResultId))
    result_item = r.scalar_one_or_none()
    if result_item and result_item.rectificationStatus == "None":
        result_item.rectificationStatus = "Pending"

    await db.commit()
    await db.refresh(item)
    return RectificationTaskOut.model_validate(item)


@router.put("/rectification-tasks/{rectification_id}", response_model=RectificationTaskOut)
async def update_rectification_task(
    rectification_id: str,
    data: RectificationTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RectificationTask).where(RectificationTask.rectificationId == rectification_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "整改任务不存在")
    if data.description is not None:
        item.description = data.description
    if data.deadline is not None:
        item.deadline = data.deadline
    if data.completeTime is not None:
        item.completeTime = data.completeTime
    if data.completePhotoUrls is not None:
        item.completePhotoUrls = data.completePhotoUrls
    if data.status is not None:
        item.status = data.status
    if data.verifiedBy is not None:
        item.verifiedBy = data.verifiedBy

    # Sync rectification status on item result when completed
    if data.status == "Completed" or data.status == "Verified":
        r = await db.execute(select(InspectionItemResult).where(InspectionItemResult.resultId == item.itemResultId))
        result_item = r.scalar_one_or_none()
        if result_item:
            result_item.rectificationStatus = "Completed" if data.status == "Completed" else "Completed"

    await db.commit()
    await db.refresh(item)
    return RectificationTaskOut.model_validate(item)


# ═══════════════════════════════════════════════════════════════
# Dashboard 运营总览
# ═══════════════════════════════════════════════════════════════

@router.get("/dashboard")
async def operations_dashboard(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated operations stats for dashboard."""
    now = datetime.utcnow()
    today_start = now.strftime("%Y-%m-%d") + " 00:00:00"
    today_end = now.strftime("%Y-%m-%d") + " 23:59:59"

    # Customer counts
    customer_q = select(func.count(Customer.customerId))
    if store_id:
        customer_q = customer_q.where(Customer.registerStoreId == store_id)
    total_customers = (await db.execute(customer_q)).scalar() or 0

    # Active appointments today
    appt_q = select(func.count(RoomAppointment.appointmentId)).where(
        RoomAppointment.status.in_(["Confirmed", "InUse"]),
        RoomAppointment.startTime >= today_start,
        RoomAppointment.startTime <= today_end,
    )
    if store_id:
        # Filter by room's store
        appt_q = appt_q.join(Room, RoomAppointment.roomId == Room.roomId).where(Room.storeId == store_id)
    active_appointments = (await db.execute(appt_q)).scalar() or 0

    # Cleaning tasks today
    clean_q = select(func.count(CleaningTask.taskId)).where(
        CleaningTask.createTime >= today_start,
        CleaningTask.createTime <= today_end,
    )
    if store_id:
        clean_q = clean_q.where(CleaningTask.storeId == store_id)
    today_cleaning = (await db.execute(clean_q)).scalar() or 0

    # Pending cleaning tasks
    pending_clean_q = select(func.count(CleaningTask.taskId)).where(
        CleaningTask.status.in_(["Pending", "Accepted"]),
    )
    if store_id:
        pending_clean_q = pending_clean_q.where(CleaningTask.storeId == store_id)
    pending_cleaning = (await db.execute(pending_clean_q)).scalar() or 0

    # Pending inspection tasks
    pending_insp_q = select(func.count(InspectionTask.inspectionId)).where(
        InspectionTask.status.in_(["Pending", "InProgress", "Submitted"]),
    )
    if store_id:
        pending_insp_q = pending_insp_q.where(InspectionTask.storeId == store_id)
    pending_inspections = (await db.execute(pending_insp_q)).scalar() or 0

    # Pending rectification tasks
    pending_rec_q = select(func.count(RectificationTask.rectificationId)).where(
        RectificationTask.status.in_(["Pending", "InProgress"]),
    )
    if store_id:
        # Join through inspection task to filter by store
        pending_rec_q = pending_rec_q.join(InspectionTask, RectificationTask.inspectionId == InspectionTask.inspectionId)
        pending_rec_q = pending_rec_q.where(InspectionTask.storeId == store_id)
    pending_rectifications = (await db.execute(pending_rec_q)).scalar() or 0

    return {
        "totalCustomers": total_customers,
        "activeAppointmentsToday": active_appointments,
        "todayCleaningTasks": today_cleaning,
        "pendingCleaningTasks": pending_cleaning,
        "pendingInspections": pending_inspections,
        "pendingRectifications": pending_rectifications,
        "reportTime": now.isoformat(),
    }
