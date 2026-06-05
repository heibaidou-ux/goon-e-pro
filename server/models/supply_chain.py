"""D05 供应链域 — Product, Supplier, Warehouse, Inventory, PurchaseOrder, StockCount 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    categoryId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    name = Column(String(50), nullable=False)
    parentId = Column(String(32), ForeignKey("product_categories.categoryId"), nullable=True)
    sortOrder = Column(Integer, default=0)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    productId = Column(String(32), unique=True, nullable=False, index=True)
    categoryId = Column(String(32), ForeignKey("product_categories.categoryId"), nullable=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    brand = Column(String(100))
    spec = Column(String(100))
    unit = Column(String(20))
    basePrice = Column(Float, default=0)
    retailPrice = Column(Float, default=0)
    marketPrice = Column(Float, default=0)
    isFood = Column(Boolean, default=False)
    shelfLife = Column(Integer)
    description = Column(Text)
    story = Column(Text)
    origin = Column(String(200))
    brewingTips = Column(Text)
    isActive = Column(Boolean, default=True)
    status = Column(String(10), default="上架")  # 上架/下架
    sortOrder = Column(Integer, default=0)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())

    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan",
                          order_by="ProductImage.sortOrder")


class ProductImage(Base):
    __tablename__ = "product_images"
    id = Column(Integer, primary_key=True, autoincrement=True)
    imageId = Column(String(32), unique=True, nullable=False, index=True)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    urlOriginal = Column(String(500), nullable=False)
    urlThumbnail = Column(String(500))
    urlMedium = Column(String(500))
    urlLarge = Column(String(500))
    isCover = Column(Boolean, default=False)
    sortOrder = Column(Integer, default=0)
    createdAt = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="images")


class UnitOfMeasure(Base):
    __tablename__ = "units_of_measure"
    id = Column(Integer, primary_key=True, autoincrement=True)
    unitId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(20), nullable=False)  # 个/斤/克/包/盒
    category = Column(String(20))
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class PriceList(Base):
    __tablename__ = "price_lists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    priceListId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # Purchase/Retail/Member
    effectiveDate = Column(Date, nullable=False)
    expiryDate = Column(Date)
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplierId = Column(String(32), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    contactPerson = Column(String(50))
    phone = Column(String(20))
    address = Column(String(200))
    bankInfo = Column(Text)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class SupplierPrice(Base):
    __tablename__ = "supplier_prices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplierPriceId = Column(String(32), unique=True, nullable=False, index=True)
    supplierId = Column(String(32), ForeignKey("suppliers.supplierId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    price = Column(Float, nullable=False)
    effectiveDate = Column(Date, nullable=False)
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchaseOrderId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    supplierId = Column(String(32), ForeignKey("suppliers.supplierId"), nullable=False)
    orderNumber = Column(String(30), unique=True, nullable=False)
    totalAmount = Column(Float, nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Submitted/Approved/Shipped/Received/Completed/Cancelled
    orderedAt = Column(DateTime)
    receivedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())

    lines = relationship("PurchaseOrderLine", back_populates="purchaseOrder", cascade="all, delete-orphan")


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lineId = Column(String(32), unique=True, nullable=False, index=True)
    purchaseOrderId = Column(String(32), ForeignKey("purchase_orders.purchaseOrderId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    quantity = Column(Float, nullable=False)
    unitPrice = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    receivedQuantity = Column(Float, default=0)
    remark = Column(String(200))

    purchaseOrder = relationship("PurchaseOrder", back_populates="lines")


class TransferRequest(Base):
    __tablename__ = "transfer_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transferRequestId = Column(String(32), unique=True, nullable=False, index=True)
    fromStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    toStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Approved/InTransit/Completed/Rejected
    appliedBy = Column(String(32), nullable=False)
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class InternalSettlement(Base):
    __tablename__ = "internal_settlements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    settlementId = Column(String(32), unique=True, nullable=False, index=True)
    transferRequestId = Column(String(32), ForeignKey("transfer_requests.transferRequestId"), nullable=False)
    fromStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    toStoreId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    totalAmount = Column(Float, nullable=False)
    status = Column(String(20), default="Pending")  # Pending/Settled
    settledAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    warehouseId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="Main")  # Main/Front
    address = Column(String(200))
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class InventoryLot(Base):
    __tablename__ = "inventory_lots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lotId = Column(String(32), unique=True, nullable=False, index=True)
    warehouseId = Column(String(32), ForeignKey("warehouses.warehouseId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    batchNo = Column(String(50), nullable=False)
    quantity = Column(Float, nullable=False)
    unitPrice = Column(Float, default=0)
    productionDate = Column(Date)
    expiryDate = Column(Date)
    status = Column(String(20), default="Normal")  # Normal/Expired/Frozen
    createdAt = Column(DateTime, server_default=func.now())


class InventoryOnHand(Base):
    __tablename__ = "inventory_on_hand"
    id = Column(Integer, primary_key=True, autoincrement=True)
    inventoryId = Column(String(32), unique=True, nullable=False, index=True)
    warehouseId = Column(String(32), ForeignKey("warehouses.warehouseId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    quantity = Column(Float, nullable=False)
    lastCountDate = Column(Date)
    createdAt = Column(DateTime, server_default=func.now())


class InventoryTransfer(Base):
    __tablename__ = "inventory_transfers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transferId = Column(String(32), unique=True, nullable=False, index=True)
    fromWarehouseId = Column(String(32), ForeignKey("warehouses.warehouseId"), nullable=False)
    toWarehouseId = Column(String(32), ForeignKey("warehouses.warehouseId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    quantity = Column(Float, nullable=False)
    transferredBy = Column(String(32), nullable=False)
    transferredAt = Column(DateTime)
    remark = Column(String(200))
    createdAt = Column(DateTime, server_default=func.now())


class StockCount(Base):
    __tablename__ = "stock_counts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    countId = Column(String(32), unique=True, nullable=False, index=True)
    warehouseId = Column(String(32), ForeignKey("warehouses.warehouseId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    countNumber = Column(String(30), unique=True, nullable=False)
    type = Column(String(10), default="Full")  # Full/Cycle
    status = Column(String(20), default="Draft")  # Draft/InProgress/Completed/Approved
    countedBy = Column(String(32), nullable=False)
    approvedBy = Column(String(32))
    countDate = Column(Date)
    createdAt = Column(DateTime, server_default=func.now())

    lines = relationship("StockCountLine", back_populates="stockCount", cascade="all, delete-orphan")


class StockCountLine(Base):
    __tablename__ = "stock_count_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lineId = Column(String(32), unique=True, nullable=False, index=True)
    countId = Column(String(32), ForeignKey("stock_counts.countId"), nullable=False)
    productId = Column(String(32), ForeignKey("products.productId"), nullable=False)
    bookQuantity = Column(Float, nullable=False)
    actualQuantity = Column(Float, nullable=False)
    differenceQuantity = Column(Float, nullable=False)
    unitPrice = Column(Float, default=0)
    differenceAmount = Column(Float, default=0)
    remark = Column(String(200))

    stockCount = relationship("StockCount", back_populates="lines")
