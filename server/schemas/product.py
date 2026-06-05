"""D05 供应链域 — Pydantic schemas for all supply chain entities."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


# ═══════════════════════════════════════════
# ProductCategory
# ═══════════════════════════════════════════

class ProductCategoryCreate(BaseModel):
    name: str
    storeId: str = ""
    parentId: Optional[str] = None
    sortOrder: int = 0


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    parentId: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[str] = None


class ProductCategoryOut(BaseModel):
    categoryId: str
    storeId: Optional[str] = ""
    name: str
    parentId: Optional[str] = None
    sortOrder: int = 0
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductCategoryTreeOut(ProductCategoryOut):
    """Category with children list for tree view."""
    children: List["ProductCategoryTreeOut"] = []


# ═══════════════════════════════════════════
# ProductImage
# ═══════════════════════════════════════════

class ProductImageOut(BaseModel):
    imageId: str
    productId: str
    urlOriginal: str
    urlThumbnail: Optional[str] = None
    urlMedium: Optional[str] = None
    urlLarge: Optional[str] = None
    isCover: bool = False
    sortOrder: int = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductImageUpdate(BaseModel):
    isCover: Optional[bool] = None
    sortOrder: Optional[int] = None


# ═══════════════════════════════════════════
# Product
# ═══════════════════════════════════════════

class ProductCreate(BaseModel):
    code: str
    name: str
    categoryId: Optional[str] = None
    storeId: str = ""
    brand: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    basePrice: float = 0
    retailPrice: float = 0
    marketPrice: float = 0
    isFood: bool = False
    shelfLife: Optional[int] = None
    description: Optional[str] = None
    story: Optional[str] = None
    origin: Optional[str] = None
    brewingTips: Optional[str] = None
    status: str = "上架"
    sortOrder: int = 0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    categoryId: Optional[str] = None
    brand: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    basePrice: Optional[float] = None
    retailPrice: Optional[float] = None
    marketPrice: Optional[float] = None
    isFood: Optional[bool] = None
    shelfLife: Optional[int] = None
    description: Optional[str] = None
    story: Optional[str] = None
    origin: Optional[str] = None
    brewingTips: Optional[str] = None
    status: Optional[str] = None
    sortOrder: Optional[int] = None
    isActive: Optional[bool] = None
    code: Optional[str] = None
    categoryId: Optional[str] = None


class ProductOut(BaseModel):
    productId: str
    code: str
    name: str
    categoryId: Optional[str] = None
    categoryName: Optional[str] = None
    storeId: Optional[str] = ""
    brand: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    basePrice: float = 0
    retailPrice: float = 0
    marketPrice: float = 0
    isFood: bool = False
    shelfLife: Optional[int] = None
    description: Optional[str] = None
    story: Optional[str] = None
    origin: Optional[str] = None
    brewingTips: Optional[str] = None
    isActive: bool = True
    status: str = "上架"
    sortOrder: int = 0
    images: List[ProductImageOut] = []
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductListOut(BaseModel):
    total: int
    items: List[ProductOut]
    page: int = 1
    page_size: int = 20


# ═══════════════════════════════════════════
# UnitOfMeasure
# ═══════════════════════════════════════════

class UnitOfMeasureCreate(BaseModel):
    name: str
    category: Optional[str] = None


class UnitOfMeasureUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None


class UnitOfMeasureOut(BaseModel):
    unitId: str
    name: str
    category: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# PriceList
# ═══════════════════════════════════════════

class PriceListCreate(BaseModel):
    name: str
    type: str  # Purchase / Retail / Member
    effectiveDate: date
    expiryDate: Optional[date] = None


class PriceListUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    effectiveDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: Optional[str] = None


class PriceListOut(BaseModel):
    priceListId: str
    name: str
    type: str
    effectiveDate: date
    expiryDate: Optional[date] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# Supplier
# ═══════════════════════════════════════════

class SupplierCreate(BaseModel):
    code: str
    name: str
    contactPerson: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bankInfo: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contactPerson: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bankInfo: Optional[str] = None
    status: Optional[str] = None


class SupplierOut(BaseModel):
    supplierId: str
    code: str
    name: str
    contactPerson: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bankInfo: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# SupplierPrice
# ═══════════════════════════════════════════

class SupplierPriceCreate(BaseModel):
    supplierId: str
    productId: str
    price: float
    effectiveDate: date


class SupplierPriceUpdate(BaseModel):
    price: Optional[float] = None
    effectiveDate: Optional[date] = None
    status: Optional[str] = None


class SupplierPriceOut(BaseModel):
    supplierPriceId: str
    supplierId: str
    productId: str
    price: float
    effectiveDate: date
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# PurchaseOrder / PurchaseOrderLine
# ═══════════════════════════════════════════

class PurchaseOrderLineCreate(BaseModel):
    productId: str
    quantity: float
    unitPrice: float
    remark: Optional[str] = None


class PurchaseOrderLineUpdate(BaseModel):
    quantity: Optional[float] = None
    unitPrice: Optional[float] = None
    receivedQuantity: Optional[float] = None
    remark: Optional[str] = None


class PurchaseOrderLineOut(BaseModel):
    lineId: str
    purchaseOrderId: str
    productId: str
    quantity: float
    unitPrice: float
    subtotal: float
    receivedQuantity: float = 0
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    storeId: str
    supplierId: str
    lines: List[PurchaseOrderLineCreate]


class PurchaseOrderUpdate(BaseModel):
    status: Optional[str] = None
    supplierId: Optional[str] = None


class PurchaseOrderOut(BaseModel):
    purchaseOrderId: str
    storeId: str
    supplierId: str
    orderNumber: str
    totalAmount: float
    status: str = "Draft"
    orderedAt: Optional[datetime] = None
    receivedAt: Optional[datetime] = None
    lines: List[PurchaseOrderLineOut] = []
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PurchaseOrderListOut(BaseModel):
    total: int
    items: List[PurchaseOrderOut]
    page: int = 1
    page_size: int = 20


# ═══════════════════════════════════════════
# Warehouse
# ═══════════════════════════════════════════

class WarehouseCreate(BaseModel):
    storeId: str
    name: str
    type: str = "Main"  # Main / Front
    address: Optional[str] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None


class WarehouseOut(BaseModel):
    warehouseId: str
    storeId: str
    name: str
    type: str = "Main"
    address: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# InventoryOnHand
# ═══════════════════════════════════════════

class InventoryAdjust(BaseModel):
    warehouseId: str
    productId: str
    quantity: float  # new quantity (absolute, not delta)
    reason: Optional[str] = None


class InventoryOnHandOut(BaseModel):
    inventoryId: str
    warehouseId: str
    productId: str
    quantity: float
    lastCountDate: Optional[date] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryOnHandListOut(BaseModel):
    total: int
    items: List[InventoryOnHandOut]
    page: int = 1
    page_size: int = 20


# ═══════════════════════════════════════════
# InventoryLot
# ═══════════════════════════════════════════

class InventoryLotCreate(BaseModel):
    warehouseId: str
    productId: str
    batchNo: str
    quantity: float
    unitPrice: float = 0
    productionDate: Optional[date] = None
    expiryDate: Optional[date] = None


class InventoryLotUpdate(BaseModel):
    quantity: Optional[float] = None
    unitPrice: Optional[float] = None
    expiryDate: Optional[date] = None
    status: Optional[str] = None


class InventoryLotOut(BaseModel):
    lotId: str
    warehouseId: str
    productId: str
    batchNo: str
    quantity: float
    unitPrice: float = 0
    productionDate: Optional[date] = None
    expiryDate: Optional[date] = None
    status: str = "Normal"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class InventoryLotListOut(BaseModel):
    total: int
    items: List[InventoryLotOut]
    page: int = 1
    page_size: int = 20


# ═══════════════════════════════════════════
# InventoryTransfer
# ═══════════════════════════════════════════

class InventoryTransferCreate(BaseModel):
    fromWarehouseId: str
    toWarehouseId: str
    productId: str
    quantity: float
    transferredBy: str
    remark: Optional[str] = None


class InventoryTransferOut(BaseModel):
    transferId: str
    fromWarehouseId: str
    toWarehouseId: str
    productId: str
    quantity: float
    transferredBy: str
    transferredAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# TransferRequest / InternalSettlement
# ═══════════════════════════════════════════

class TransferRequestCreate(BaseModel):
    fromStoreId: str
    toStoreId: str
    appliedBy: str


class TransferRequestUpdate(BaseModel):
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class TransferRequestOut(BaseModel):
    transferRequestId: str
    fromStoreId: str
    toStoreId: str
    status: str = "Draft"
    appliedBy: str
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class InternalSettlementOut(BaseModel):
    settlementId: str
    transferRequestId: str
    fromStoreId: str
    toStoreId: str
    totalAmount: float
    status: str = "Pending"
    settledAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════
# StockCount / StockCountLine
# ═══════════════════════════════════════════

class StockCountLineCreate(BaseModel):
    productId: str
    bookQuantity: float
    actualQuantity: float
    unitPrice: float = 0
    remark: Optional[str] = None


class StockCountLineOut(BaseModel):
    lineId: str
    countId: str
    productId: str
    bookQuantity: float
    actualQuantity: float
    differenceQuantity: float
    unitPrice: float = 0
    differenceAmount: float = 0
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class StockCountCreate(BaseModel):
    warehouseId: str
    storeId: str
    type: str = "Full"  # Full / Cycle
    countedBy: str
    countDate: Optional[date] = None
    lines: List[StockCountLineCreate]


class StockCountUpdate(BaseModel):
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class StockCountOut(BaseModel):
    countId: str
    warehouseId: str
    storeId: str
    countNumber: str
    type: str = "Full"
    status: str = "Draft"
    countedBy: str
    approvedBy: Optional[str] = None
    countDate: Optional[date] = None
    lines: List[StockCountLineOut] = []
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockCountListOut(BaseModel):
    total: int
    items: List[StockCountOut]
    page: int = 1
    page_size: int = 20
