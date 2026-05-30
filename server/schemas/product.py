from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ProductCategoryCreate(BaseModel):
    name: str
    subcategories: List[str] = []
    sort_order: int = 0


class ProductCategoryOut(BaseModel):
    id: int
    name: str
    subcategories: List[str] = []
    sort_order: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductImageOut(BaseModel):
    id: int
    product_id: int
    url_original: str
    url_thumbnail: Optional[str] = None
    url_medium: Optional[str] = None
    url_large: Optional[str] = None
    is_cover: bool
    sort_order: int

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    code: str
    name: str
    brand: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    internal_price: float = 0
    retail_price: float = 0
    market_price: float = 0
    is_food: bool = False
    shelf_life: Optional[int] = None
    status: str = "上架"
    story: Optional[str] = None
    origin: Optional[str] = None
    brewing_tips: Optional[str] = None
    description: Optional[str] = None
    default_supplier: Optional[str] = None
    lead_time: int = 7
    safe_stock: float = 0
    max_stock: float = 0
    current_stock: float = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    internal_price: Optional[float] = None
    retail_price: Optional[float] = None
    market_price: Optional[float] = None
    is_food: Optional[bool] = None
    shelf_life: Optional[int] = None
    status: Optional[str] = None
    story: Optional[str] = None
    origin: Optional[str] = None
    brewing_tips: Optional[str] = None
    description: Optional[str] = None
    default_supplier: Optional[str] = None
    lead_time: Optional[int] = None
    safe_stock: Optional[float] = None
    max_stock: Optional[float] = None
    current_stock: Optional[float] = None


class ProductOut(BaseModel):
    id: int
    code: str
    name: str
    brand: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    internal_price: float
    retail_price: float
    market_price: float
    is_food: bool
    shelf_life: Optional[int] = None
    is_active: bool
    status: str
    story: Optional[str] = None
    origin: Optional[str] = None
    brewing_tips: Optional[str] = None
    description: Optional[str] = None
    default_supplier: Optional[str] = None
    lead_time: int
    safe_stock: float
    max_stock: float
    current_stock: float
    images: List[ProductImageOut] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListOut(BaseModel):
    total: int
    items: List[ProductOut]
    page: int = 1
    page_size: int = 20
