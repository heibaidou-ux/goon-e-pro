from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoomOut(BaseModel):
    id: int
    room_id: str
    store_id: Optional[str] = None
    name: str
    type: Optional[str] = None
    capacity: int
    floor: Optional[str] = None
    price_per_hour: float
    price_per_half_hour: float
    facilities: List[str] = []
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class StoreOut(BaseModel):
    id: int
    store_id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    rooms: List[RoomOut] = []

    class Config:
        from_attributes = True


class RoomOrderCreate(BaseModel):
    room_id: str
    customer_name: str = "客人"
    customer_phone: Optional[str] = None
    date: str
    start_time: str
    end_time: str
    duration: float
    total_amount: float
    scene: Optional[str] = None
    source: str = "到店"


class RoomOrderOut(BaseModel):
    id: int
    order_id: str
    room_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    total_amount: Optional[float] = None
    status: str
    scene: Optional[str] = None
    door_code: Optional[str] = None
    source: Optional[str] = None
    payment_status: Optional[str] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    created_at: Optional[datetime] = None
    room: Optional[RoomOut] = None

    class Config:
        from_attributes = True


class ShopOrderItemCreate(BaseModel):
    product_id: int
    product_name: str
    spec: Optional[str] = None
    quantity: float = 1
    unit_price: float = 0


class ShopOrderCreate(BaseModel):
    customer_name: str = "客人"
    customer_phone: Optional[str] = None
    room_id: Optional[str] = None
    table_id: Optional[str] = None
    payment_method: str = "wechat"
    note: Optional[str] = None
    items: List[ShopOrderItemCreate]


class ShopOrderOut(BaseModel):
    id: int
    order_no: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    room_id: Optional[str] = None
    table_id: Optional[str] = None
    total_amount: float
    status: str
    payment_method: Optional[str] = None
    note: Optional[str] = None
    items: List = []
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
