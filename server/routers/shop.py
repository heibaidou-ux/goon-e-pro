"""商城订单 API — 基于 D03/D05 新模型（operations, supply_chain）"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.operations import Order, OrderItem
from models.supply_chain import Product
from models.user import User
from schemas.order import ShopOrderCreate, ShopOrderOut
from services.auth_service import get_current_user, get_optional_user

router = APIRouter(prefix="/api/shop", tags=["商城订单"], dependencies=[Depends(get_current_user)])


@router.post("/orders", response_model=ShopOrderOut)
async def create_shop_order(
    data: ShopOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    order_id = uuid.uuid4().hex[:12]
    total = 0
    items = []
    for item_data in data.items:
        subtotal = item_data.quantity * item_data.unit_price
        total += subtotal
        item = OrderItem(
            itemId=uuid.uuid4().hex[:12],
            orderId=order_id,
            itemType="Product",
            productId=str(item_data.product_id),
            quantity=item_data.quantity,
            unitPrice=item_data.unit_price,
            subtotal=subtotal,
        )
        items.append(item)

    order = Order(
        orderId=order_id,
        orderNumber=f"SHOP{order_id[:8].upper()}",
        storeId="",
        customerId="",
        orderType="Retail",
        totalAmount=total,
        paidAmount=total,
        platform="Offline",
        status="Completed",
        items=items,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return ShopOrderOut(
        id=order.id, order_no=order.orderNumber, customer_name=data.customer_name,
        customer_phone=data.customer_phone, room_id=data.room_id,
        table_id=data.table_id, total_amount=total,
        status="completed", payment_method=data.payment_method,
        note=data.note, created_at=order.createdAt,
        items=[{"id": i.id, "product_id": i.productId, "product_name": "",
                "quantity": i.quantity, "unit_price": i.unitPrice, "subtotal": i.subtotal}
               for i in items],
    )


@router.get("/orders", response_model=list[ShopOrderOut])
async def list_shop_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(Order).where(Order.orderType == "Retail")
    if status:
        query = query.where(Order.status == status)
    query = query.order_by(Order.createdAt.desc())
    result = await db.execute(query)
    orders = result.scalars().all()

    out = []
    for o in orders:
        out.append(ShopOrderOut(
            id=o.id, order_no=o.orderNumber, customer_name="",
            customer_phone="", room_id=o.roomId or "",
            table_id="", total_amount=o.totalAmount,
            status=o.status, payment_method=o.paymentMethod or "",
            note="", created_at=o.createdAt,
            items=[],
        ))
    return out


@router.get("/orders/{order_id}", response_model=ShopOrderOut)
async def get_shop_order(order_id: str, db: AsyncSession = Depends(get_db), user: Optional[User] = Depends(get_optional_user)):
    result = await db.execute(
        select(Order).where(Order.orderType == "Retail", Order.orderId == order_id)
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return ShopOrderOut(
        id=order.id, order_no=order.orderNumber, customer_name="",
        customer_phone="", room_id=order.roomId or "",
        table_id="", total_amount=order.totalAmount,
        status=order.status, payment_method=order.paymentMethod or "",
        note="", created_at=order.createdAt, items=[],
    )
