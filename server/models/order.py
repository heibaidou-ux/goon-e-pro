from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from database import Base


class ShopOrder(Base):
    __tablename__ = "shop_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(30), unique=True, nullable=False, index=True)
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    room_id = Column(String(20))
    table_id = Column(String(10))
    total_amount = Column(Float, default=0)
    status = Column(String(20), default="pending")  # pending, paid, completed, cancelled
    payment_method = Column(String(30))
    note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    items = relationship("ShopOrderItem", back_populates="order", cascade="all, delete-orphan")


class ShopOrderItem(Base):
    __tablename__ = "shop_order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("shop_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    product_name = Column(String(200))
    spec = Column(String(100))
    quantity = Column(Float, default=1)
    unit_price = Column(Float, default=0)
    subtotal = Column(Float, default=0)

    order = relationship("ShopOrder", back_populates="items")
