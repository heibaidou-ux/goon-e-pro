from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(300))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    rooms = relationship("Room", back_populates="store")


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(String(20), unique=True, nullable=False, index=True)
    store_id = Column(String(20), ForeignKey("stores.store_id"))
    name = Column(String(100), nullable=False)
    type = Column(String(30))  # MeetingRoom, TeaRoom, Exhibition, Workspace
    capacity = Column(Integer, default=4)
    floor = Column(String(20))
    price_per_hour = Column(Float, default=0)
    price_per_half_hour = Column(Float, default=0)
    facilities = Column(Text)  # JSON array
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="rooms")
    orders = relationship("RoomOrder", back_populates="room")


class RoomOrder(Base):
    __tablename__ = "room_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(20), unique=True, nullable=False, index=True)
    room_id = Column(String(20), ForeignKey("rooms.room_id"))
    customer_name = Column(String(100))
    customer_phone = Column(String(20))
    date = Column(String(20))
    start_time = Column(String(10))
    end_time = Column(String(10))
    duration = Column(Float)  # hours
    total_amount = Column(Float)
    status = Column(String(20), default="Booked")  # Booked, InUse, Completed, Cancelled
    scene = Column(String(50))  # 品茶, 会议, K歌
    door_code = Column(String(20))
    source = Column(String(30))  # 美团, 抖音, 到店, etc.
    payment_status = Column(String(20), default="Paid")
    check_in_time = Column(String(20))
    check_out_time = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    room = relationship("Room", back_populates="orders")
