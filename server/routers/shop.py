from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.order import ShopOrder, ShopOrderItem
from models.product import Product
from models.user import User
from schemas.order import ShopOrderCreate, ShopOrderOut
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/shop", tags=["商城订单"])


@router.post("/orders", response_model=ShopOrderOut)
async def create_shop_order(
    data: ShopOrderCreate,
    db: AsyncSession = Depends(get_db),
):
    # Generate order_no
    result = await db.execute(select(func.count()).select_from(ShopOrder))
    count = result.scalar() or 0
    order_no = f"SHOP{count + 1:06d}"

    total = 0
    items = []
    for item_data in data.items:
        subtotal = item_data.quantity * item_data.unit_price
        total += subtotal
        item = ShopOrderItem(
            product_id=item_data.product_id,
            product_name=item_data.product_name,
            spec=item_data.spec,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=subtotal,
        )
        items.append(item)

    order = ShopOrder(
        order_no=order_no,
        customer_name=data.customer_name,
        customer_phone=data.customer_phone,
        room_id=data.room_id,
        table_id=data.table_id,
        total_amount=total,
        status="pending",
        payment_method=data.payment_method,
        note=data.note,
        items=items,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("/orders", response_model=list[ShopOrderOut])
async def list_shop_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = select(ShopOrder)
    if status:
        query = query.where(ShopOrder.status == status)
    query = query.order_by(ShopOrder.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/orders/{order_id}", response_model=ShopOrderOut)
async def get_shop_order(order_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShopOrder).where(ShopOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order
