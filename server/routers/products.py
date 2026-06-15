"""商品管理 API — 基于 D05 供应链域新模型（supply_chain.py）"""
import json, uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from database import get_db
from models.supply_chain import (
    Product, ProductCategory, ProductImage,
    UnitOfMeasure, PriceList,
    Supplier, SupplierPrice,
    PurchaseOrder, PurchaseOrderLine,
    Warehouse, InventoryLot, InventoryOnHand, InventoryTransfer,
    TransferRequest, InternalSettlement,
    StockCount, StockCountLine,
)
from models.user import User
from schemas.product import (
    # Product / Category / Image
    ProductCreate, ProductUpdate, ProductOut, ProductListOut,
    ProductCategoryCreate, ProductCategoryUpdate, ProductCategoryOut, ProductCategoryTreeOut,
    ProductImageOut, ProductImageUpdate,
    # UnitOfMeasure
    UnitOfMeasureCreate, UnitOfMeasureUpdate, UnitOfMeasureOut,
    # PriceList
    PriceListCreate, PriceListUpdate, PriceListOut,
    # Supplier
    SupplierCreate, SupplierUpdate, SupplierOut,
    SupplierPriceCreate, SupplierPriceUpdate, SupplierPriceOut,
    # PurchaseOrder
    PurchaseOrderCreate, PurchaseOrderUpdate, PurchaseOrderOut, PurchaseOrderListOut,
    PurchaseOrderLineOut,
    # Warehouse
    WarehouseCreate, WarehouseUpdate, WarehouseOut,
    # Inventory
    InventoryAdjust, InventoryOnHandOut, InventoryOnHandListOut,
    InventoryLotCreate, InventoryLotUpdate, InventoryLotOut, InventoryLotListOut,
    InventoryTransferCreate, InventoryTransferOut,
    # Transfer / Settlement
    TransferRequestCreate, TransferRequestUpdate, TransferRequestOut,
    InternalSettlementOut,
    # StockCount
    StockCountCreate, StockCountUpdate, StockCountOut, StockCountListOut,
    StockCountLineOut,
)
from services.auth_service import get_current_user, get_optional_user
from services.image_service import image_service

router = APIRouter(prefix="/api/products", tags=["商品管理"])


# ── Helpers ──

def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


def _gen_order_number(prefix: str = "PO") -> str:
    """Generate a unique order number like PO20260602XXXX."""
    today = date.today().strftime("%Y%m%d")
    return f"{prefix}{today}{uuid.uuid4().hex[:6].upper()}"


async def _get_category_name(db: AsyncSession, categoryId: Optional[str]) -> Optional[str]:
    if not categoryId:
        return None
    r = await db.execute(select(ProductCategory.name).where(ProductCategory.categoryId == categoryId))
    return r.scalar_one_or_none()


async def _product_to_out(db: AsyncSession, product: Product) -> ProductOut:
    """Convert Product model to ProductOut with joined category name."""
    cat_name = await _get_category_name(db, product.categoryId)
    exclude_fields = {"categoryName", "images"}
    data = {
        k: getattr(product, k)
        for k in ProductOut.model_fields
        if hasattr(product, k) and k not in exclude_fields
    }
    return ProductOut(
        **data,
        categoryName=cat_name,
        images=[ProductImageOut.model_validate(img) for img in (product.images or [])],
    )


# ═══════════════════════════════════════════════════════
# ProductCategory 商品分类
# ═══════════════════════════════════════════════════════

@router.get("/categories", response_model=list[ProductCategoryTreeOut])
async def list_categories(
    storeId: str = "",
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Get all categories as a tree."""
    query = select(ProductCategory).where(ProductCategory.status == "Active")
    if storeId:
        query = query.where(
            or_(ProductCategory.storeId == storeId, ProductCategory.storeId == "")
        )
    query = query.order_by(ProductCategory.sortOrder)
    result = await db.execute(query)
    cats = result.scalars().all()

    # Build tree
    cat_map = {c.categoryId: ProductCategoryTreeOut.model_validate(c) for c in cats}
    roots: list[ProductCategoryTreeOut] = []
    for c in cats:
        node = cat_map[c.categoryId]
        if c.parentId and c.parentId in cat_map:
            cat_map[c.parentId].children.append(node)
        else:
            roots.append(node)
    return roots


@router.post("/categories", response_model=ProductCategoryOut)
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    cat = ProductCategory(
        categoryId=_gen_id(),
        storeId=data.storeId,
        name=data.name,
        parentId=data.parentId,
        sortOrder=data.sortOrder,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.put("/categories/{category_id}", response_model=ProductCategoryOut)
async def update_category(
    category_id: str,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(ProductCategory).where(ProductCategory.categoryId == category_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "分类不存在")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(cat, k, v)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(ProductCategory).where(ProductCategory.categoryId == category_id))
    cat = r.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, "分类不存在")

    # Check if any active products reference this category
    prod_r = await db.execute(
        select(func.count(Product.id)).where(
            Product.categoryId == category_id, Product.isActive == True
        )
    )
    prod_count = prod_r.scalar() or 0
    if prod_count > 0:
        raise HTTPException(400, f"该分类下还有 {prod_count} 个商品，请先移除或更改商品分类后再禁用")

    # Also check sub-categories
    child_r = await db.execute(
        select(func.count(ProductCategory.id)).where(
            ProductCategory.parentId == category_id, ProductCategory.status == "Active"
        )
    )
    child_count = child_r.scalar() or 0
    if child_count > 0:
        raise HTTPException(400, f"该分类下还有 {child_count} 个子分类，请先处理后再禁用")

    cat.status = "Inactive"
    await db.commit()
    return {"message": "分类已禁用"}


# ═══════════════════════════════════════════════════════
# Product 商品
# ═══════════════════════════════════════════════════════

@router.get("", response_model=ProductListOut)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    categoryId: Optional[str] = None,
    status: Optional[str] = None,
    storeId: str = "",
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    # Build base filters (shared between count and data queries)
    base_filters = [Product.isActive == True]
    if search:
        base_filters.append(
            or_(Product.name.ilike(f"%{search}%"), Product.code.ilike(f"%{search}%"))
        )
    if categoryId:
        base_filters.append(Product.categoryId == categoryId)
    if status:
        base_filters.append(Product.status == status)
    if storeId:
        base_filters.append(Product.storeId == storeId)

    # Count query (no loader options)
    count_stmt = select(func.count(Product.id)).where(*base_filters)
    total = (await db.execute(count_stmt)).scalar() or 0

    # Data query (with selectinload for images)
    offset = (page - 1) * page_size
    data_stmt = (
        select(Product)
        .options(selectinload(Product.images))
        .where(*base_filters)
        .order_by(Product.updatedAt.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(data_stmt)
    products = result.scalars().all()

    items = [await _product_to_out(db, p) for p in products]
    return ProductListOut(total=total, items=items, page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(Product).where(Product.productId == product_id).options(selectinload(Product.images))
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")
    return await _product_to_out(db, product)


@router.post("", response_model=ProductOut)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check code uniqueness
    r = await db.execute(select(Product).where(Product.code == data.code))
    if r.scalar_one_or_none():
        raise HTTPException(400, "商品编码已存在")

    product = Product(
        productId=_gen_id(),
        **data.model_dump(),
    )
    product.storeId = data.storeId or "default"
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return await _product_to_out(db, product)


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: str,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(Product).where(Product.productId == product_id).options(selectinload(Product.images))
    )
    product = r.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")

    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    return await _product_to_out(db, product)


@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Product).where(Product.productId == product_id))
    product = r.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")
    product.isActive = False
    await db.commit()
    return {"message": "已删除"}


# ═══════════════════════════════════════════════════════
# ProductImage 商品图片
# ═══════════════════════════════════════════════════════

@router.post("/{product_id}/images", response_model=list[ProductImageOut])
async def upload_product_images(
    product_id: str,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Product).where(Product.productId == product_id))
    product = r.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "商品不存在")

    # Get current max sort_order
    img_r = await db.execute(
        select(func.max(ProductImage.sortOrder))
        .where(ProductImage.productId == product_id)
    )
    max_order = img_r.scalar() or -1

    created_images = []
    for i, file in enumerate(files):
        content = await file.read()
        ext = f".{file.filename.split('.')[-1]}" if file.filename else ".jpg"

        try:
            urls = image_service.process_product_image(content, product_id, ext)
        except ValueError as e:
            raise HTTPException(400, str(e))

        is_cover = (max_order + i) == 0

        img = ProductImage(
            imageId=_gen_id(),
            productId=product_id,
            urlOriginal=urls["original"],
            urlThumbnail=urls.get(240),
            urlMedium=urls.get(480),
            urlLarge=urls.get(800),
            isCover=is_cover,
            sortOrder=max_order + 1 + i,
        )
        db.add(img)
        created_images.append(img)

    await db.commit()
    for img in created_images:
        await db.refresh(img)
    return [ProductImageOut.model_validate(img) for img in created_images]


@router.put("/{product_id}/images/{image_id}", response_model=ProductImageOut)
async def update_product_image(
    product_id: str,
    image_id: str,
    data: ProductImageUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(ProductImage).where(
            ProductImage.imageId == image_id,
            ProductImage.productId == product_id,
        )
    )
    img = r.scalar_one_or_none()
    if not img:
        raise HTTPException(404, "图片不存在")
    update_data = data.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(img, k, v)
    # If setting this as cover, unset others
    if data.isCover:
        others = (await db.execute(
            select(ProductImage).where(
                ProductImage.productId == product_id,
                ProductImage.imageId != image_id,
            )
        )).scalars().all()
        for o in others:
            o.isCover = False
    await db.commit()
    await db.refresh(img)
    return ProductImageOut.model_validate(img)


@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: str,
    image_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(ProductImage).where(
            ProductImage.imageId == image_id,
            ProductImage.productId == product_id,
        )
    )
    img = r.scalar_one_or_none()
    if not img:
        raise HTTPException(404, "图片不存在")
    await db.delete(img)
    await db.commit()
    return {"message": "图片已删除"}


# ═══════════════════════════════════════════════════════
# UnitOfMeasure 计量单位
# ═══════════════════════════════════════════════════════

@router.get("/units", response_model=list[UnitOfMeasureOut])
async def list_units(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """List all active units of measure."""
    result = await db.execute(
        select(UnitOfMeasure).where(UnitOfMeasure.status == "Active")
        .order_by(UnitOfMeasure.name)
    )
    return result.scalars().all()


@router.post("/units", response_model=UnitOfMeasureOut)
async def create_unit(
    data: UnitOfMeasureCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    unit = UnitOfMeasure(unitId=_gen_id(), **data.model_dump())
    db.add(unit)
    await db.commit()
    await db.refresh(unit)
    return unit


@router.put("/units/{unit_id}", response_model=UnitOfMeasureOut)
async def update_unit(
    unit_id: str,
    data: UnitOfMeasureUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(UnitOfMeasure).where(UnitOfMeasure.unitId == unit_id))
    unit = r.scalar_one_or_none()
    if not unit:
        raise HTTPException(404, "计量单位不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(unit, k, v)
    await db.commit()
    await db.refresh(unit)
    return unit


@router.delete("/units/{unit_id}")
async def delete_unit(
    unit_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(UnitOfMeasure).where(UnitOfMeasure.unitId == unit_id))
    unit = r.scalar_one_or_none()
    if not unit:
        raise HTTPException(404, "计量单位不存在")
    unit.status = "Inactive"
    await db.commit()
    return {"message": "计量单位已禁用"}


# ═══════════════════════════════════════════════════════
# PriceList 价格表
# ═══════════════════════════════════════════════════════

@router.get("/price-lists", response_model=list[PriceListOut])
async def list_price_lists(
    type_filter: Optional[str] = Query(None, alias="type"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(PriceList).where(PriceList.status == "Active")
    if type_filter:
        query = query.where(PriceList.type == type_filter)
    query = query.order_by(PriceList.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/price-lists", response_model=PriceListOut)
async def create_price_list(
    data: PriceListCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pl = PriceList(priceListId=_gen_id(), **data.model_dump())
    db.add(pl)
    await db.commit()
    await db.refresh(pl)
    return pl


@router.put("/price-lists/{price_list_id}", response_model=PriceListOut)
async def update_price_list(
    price_list_id: str,
    data: PriceListUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(PriceList).where(PriceList.priceListId == price_list_id))
    pl = r.scalar_one_or_none()
    if not pl:
        raise HTTPException(404, "价格表不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(pl, k, v)
    await db.commit()
    await db.refresh(pl)
    return pl


@router.delete("/price-lists/{price_list_id}")
async def delete_price_list(
    price_list_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(PriceList).where(PriceList.priceListId == price_list_id))
    pl = r.scalar_one_or_none()
    if not pl:
        raise HTTPException(404, "价格表不存在")
    pl.status = "Inactive"
    await db.commit()
    return {"message": "价格表已禁用"}


# ═══════════════════════════════════════════════════════
# Supplier 供应商
# ═══════════════════════════════════════════════════════

@router.get("/suppliers", response_model=list[SupplierOut])
async def list_suppliers(
    search: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(Supplier)
    if status_filter:
        query = query.where(Supplier.status == status_filter)
    if search:
        query = query.where(
            or_(
                Supplier.name.ilike(f"%{search}%"),
                Supplier.code.ilike(f"%{search}%"),
                Supplier.contactPerson.ilike(f"%{search}%"),
            )
        )
    query = query.order_by(Supplier.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/suppliers", response_model=SupplierOut)
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check code uniqueness
    r = await db.execute(select(Supplier).where(Supplier.code == data.code))
    if r.scalar_one_or_none():
        raise HTTPException(400, "供应商编码已存在")
    supplier = Supplier(supplierId=_gen_id(), **data.model_dump())
    db.add(supplier)
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.get("/suppliers/{supplier_id}", response_model=SupplierOut)
async def get_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    r = await db.execute(select(Supplier).where(Supplier.supplierId == supplier_id))
    supplier = r.scalar_one_or_none()
    if not supplier:
        raise HTTPException(404, "供应商不存在")
    return supplier


@router.put("/suppliers/{supplier_id}", response_model=SupplierOut)
async def update_supplier(
    supplier_id: str,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Supplier).where(Supplier.supplierId == supplier_id))
    supplier = r.scalar_one_or_none()
    if not supplier:
        raise HTTPException(404, "供应商不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(supplier, k, v)
    await db.commit()
    await db.refresh(supplier)
    return supplier


@router.delete("/suppliers/{supplier_id}")
async def delete_supplier(
    supplier_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Supplier).where(Supplier.supplierId == supplier_id))
    supplier = r.scalar_one_or_none()
    if not supplier:
        raise HTTPException(404, "供应商不存在")
    supplier.status = "Inactive"
    await db.commit()
    return {"message": "供应商已禁用"}


# ═══════════════════════════════════════════════════════
# SupplierPrice 供应商报价
# ═══════════════════════════════════════════════════════

@router.get("/suppliers/{supplier_id}/prices", response_model=list[SupplierPriceOut])
async def list_supplier_prices(
    supplier_id: str,
    product_id: Optional[str] = Query(None, alias="productId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(SupplierPrice).where(
        SupplierPrice.supplierId == supplier_id,
        SupplierPrice.status == "Active",
    )
    if product_id:
        query = query.where(SupplierPrice.productId == product_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/suppliers/{supplier_id}/prices", response_model=SupplierPriceOut)
async def create_supplier_price(
    supplier_id: str,
    data: SupplierPriceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Verify product exists
    r = await db.execute(select(Product).where(Product.productId == data.productId))
    if not r.scalar_one_or_none():
        raise HTTPException(404, "商品不存在")
    sp = SupplierPrice(
        supplierPriceId=_gen_id(),
        supplierId=supplier_id,
        **data.model_dump(exclude={"supplierId"}),
    )
    db.add(sp)
    await db.commit()
    await db.refresh(sp)
    return sp


@router.put("/supplier-prices/{price_id}", response_model=SupplierPriceOut)
async def update_supplier_price(
    price_id: str,
    data: SupplierPriceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(SupplierPrice).where(SupplierPrice.supplierPriceId == price_id))
    sp = r.scalar_one_or_none()
    if not sp:
        raise HTTPException(404, "报价不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(sp, k, v)
    await db.commit()
    await db.refresh(sp)
    return sp


@router.delete("/supplier-prices/{price_id}")
async def delete_supplier_price(
    price_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(SupplierPrice).where(SupplierPrice.supplierPriceId == price_id))
    sp = r.scalar_one_or_none()
    if not sp:
        raise HTTPException(404, "报价不存在")
    sp.status = "Inactive"
    await db.commit()
    return {"message": "报价已禁用"}


# ═══════════════════════════════════════════════════════
# PurchaseOrder 采购订单
# ═══════════════════════════════════════════════════════

@router.get("/purchase-orders", response_model=PurchaseOrderListOut)
async def list_purchase_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    supplier_id: Optional[str] = Query(None, alias="supplierId"),
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(PurchaseOrder)
    if status_filter:
        query = query.where(PurchaseOrder.status == status_filter)
    if supplier_id:
        query = query.where(PurchaseOrder.supplierId == supplier_id)
    if store_id:
        query = query.where(PurchaseOrder.storeId == store_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.options(selectinload(PurchaseOrder.lines))
    query = query.order_by(PurchaseOrder.createdAt.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    orders = result.scalars().all()

    items = [
        PurchaseOrderOut(
            **{k: getattr(o, k) for k in PurchaseOrderOut.model_fields if k != "lines"},
            lines=[PurchaseOrderLineOut.model_validate(ln) for ln in (o.lines or [])],
        )
        for o in orders
    ]
    return PurchaseOrderListOut(total=total, items=items, page=page, page_size=page_size)


@router.post("/purchase-orders", response_model=PurchaseOrderOut)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order_id = _gen_id()
    total = 0
    lines = []
    for line_data in data.lines:
        subtotal = round(line_data.quantity * line_data.unitPrice, 2)
        total += subtotal
        line = PurchaseOrderLine(
            lineId=_gen_id(),
            purchaseOrderId=order_id,
            productId=line_data.productId,
            quantity=line_data.quantity,
            unitPrice=line_data.unitPrice,
            subtotal=subtotal,
            remark=line_data.remark,
        )
        lines.append(line)

    order = PurchaseOrder(
        purchaseOrderId=order_id,
        storeId=data.storeId,
        supplierId=data.supplierId,
        orderNumber=_gen_order_number("PO"),
        totalAmount=round(total, 2),
        status="Draft",
        lines=lines,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return PurchaseOrderOut(
        **{k: getattr(order, k) for k in PurchaseOrderOut.model_fields if k != "lines"},
        lines=[PurchaseOrderLineOut.model_validate(ln) for ln in (order.lines or [])],
    )


@router.get("/purchase-orders/{order_id}", response_model=PurchaseOrderOut)
async def get_purchase_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    r = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.purchaseOrderId == order_id)
        .options(selectinload(PurchaseOrder.lines))
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "采购订单不存在")
    return PurchaseOrderOut(
        **{k: getattr(order, k) for k in PurchaseOrderOut.model_fields if k != "lines"},
        lines=[PurchaseOrderLineOut.model_validate(ln) for ln in (order.lines or [])],
    )


@router.put("/purchase-orders/{order_id}", response_model=PurchaseOrderOut)
async def update_purchase_order(
    order_id: str,
    data: PurchaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.purchaseOrderId == order_id)
        .options(selectinload(PurchaseOrder.lines))
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "采购订单不存在")

    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "status":
            # Set timestamps on status transitions
            if v == "Ordered" and not order.orderedAt:
                order.orderedAt = datetime.utcnow()
            elif v == "Received" and not order.receivedAt:
                order.receivedAt = datetime.utcnow()
        setattr(order, k, v)

    await db.commit()
    await db.refresh(order)
    return PurchaseOrderOut(
        **{k: getattr(order, k) for k in PurchaseOrderOut.model_fields if k != "lines"},
        lines=[PurchaseOrderLineOut.model_validate(ln) for ln in (order.lines or [])],
    )


@router.delete("/purchase-orders/{order_id}")
async def delete_purchase_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.purchaseOrderId == order_id)
        .options(selectinload(PurchaseOrder.lines))
    )
    order = r.scalar_one_or_none()
    if not order:
        raise HTTPException(404, "采购订单不存在")
    if order.status not in ("Draft", "Cancelled"):
        raise HTTPException(400, "只能删除草稿或已取消的订单")
    order.status = "Cancelled"
    await db.commit()
    return {"message": "采购订单已取消"}


# ═══════════════════════════════════════════════════════
# Warehouse 仓库
# ═══════════════════════════════════════════════════════

@router.get("/warehouses", response_model=list[WarehouseOut])
async def list_warehouses(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(Warehouse).where(Warehouse.status == "Active")
    if store_id:
        query = query.where(Warehouse.storeId == store_id)
    query = query.order_by(Warehouse.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/warehouses", response_model=WarehouseOut)
async def create_warehouse(
    data: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    wh = Warehouse(warehouseId=_gen_id(), **data.model_dump())
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseOut)
async def update_warehouse(
    warehouse_id: str,
    data: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Warehouse).where(Warehouse.warehouseId == warehouse_id))
    wh = r.scalar_one_or_none()
    if not wh:
        raise HTTPException(404, "仓库不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(wh, k, v)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.delete("/warehouses/{warehouse_id}")
async def delete_warehouse(
    warehouse_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(Warehouse).where(Warehouse.warehouseId == warehouse_id))
    wh = r.scalar_one_or_none()
    if not wh:
        raise HTTPException(404, "仓库不存在")
    wh.status = "Inactive"
    await db.commit()
    return {"message": "仓库已禁用"}


# ═══════════════════════════════════════════════════════
# InventoryOnHand 实时库存
# ═══════════════════════════════════════════════════════

@router.get("/inventory", response_model=InventoryOnHandListOut)
async def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[str] = Query(None, alias="warehouseId"),
    product_id: Optional[str] = Query(None, alias="productId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(InventoryOnHand)
    if warehouse_id:
        query = query.where(InventoryOnHand.warehouseId == warehouse_id)
    if product_id:
        query = query.where(InventoryOnHand.productId == product_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(InventoryOnHand.productId).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return InventoryOnHandListOut(total=total, items=items, page=page, page_size=page_size)


@router.put("/inventory/adjust")
async def adjust_inventory(
    data: InventoryAdjust,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Adjust inventory quantity to an absolute value."""
    r = await db.execute(
        select(InventoryOnHand).where(
            InventoryOnHand.warehouseId == data.warehouseId,
            InventoryOnHand.productId == data.productId,
        )
    )
    inv = r.scalar_one_or_none()
    if inv:
        inv.quantity = data.quantity
        inv.lastCountDate = date.today()
    else:
        inv = InventoryOnHand(
            inventoryId=_gen_id(),
            warehouseId=data.warehouseId,
            productId=data.productId,
            quantity=data.quantity,
            lastCountDate=date.today(),
        )
        db.add(inv)
    await db.commit()
    await db.refresh(inv)
    return InventoryOnHandOut.model_validate(inv)


# ═══════════════════════════════════════════════════════
# InventoryLot 批次库存
# ═══════════════════════════════════════════════════════

@router.get("/inventory-lots", response_model=InventoryLotListOut)
async def list_inventory_lots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[str] = Query(None, alias="warehouseId"),
    product_id: Optional[str] = Query(None, alias="productId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(InventoryLot)
    if warehouse_id:
        query = query.where(InventoryLot.warehouseId == warehouse_id)
    if product_id:
        query = query.where(InventoryLot.productId == product_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(InventoryLot.createdAt.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()
    return InventoryLotListOut(total=total, items=items, page=page, page_size=page_size)


@router.post("/inventory-lots", response_model=InventoryLotOut)
async def create_inventory_lot(
    data: InventoryLotCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lot = InventoryLot(lotId=_gen_id(), **data.model_dump())
    db.add(lot)
    await db.commit()
    await db.refresh(lot)
    return lot


@router.put("/inventory-lots/{lot_id}", response_model=InventoryLotOut)
async def update_inventory_lot(
    lot_id: str,
    data: InventoryLotUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(select(InventoryLot).where(InventoryLot.lotId == lot_id))
    lot = r.scalar_one_or_none()
    if not lot:
        raise HTTPException(404, "批次不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(lot, k, v)
    await db.commit()
    await db.refresh(lot)
    return lot


# ═══════════════════════════════════════════════════════
# InventoryTransfer 库存调拨
# ═══════════════════════════════════════════════════════

@router.get("/inventory-transfers", response_model=list[InventoryTransferOut])
async def list_inventory_transfers(
    warehouse_id: Optional[str] = Query(None, alias="warehouseId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(InventoryTransfer).order_by(InventoryTransfer.createdAt.desc())
    if warehouse_id:
        query = query.where(
            or_(InventoryTransfer.fromWarehouseId == warehouse_id,
                InventoryTransfer.toWarehouseId == warehouse_id)
        )
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/inventory-transfers", response_model=InventoryTransferOut)
async def create_inventory_transfer(
    data: InventoryTransferCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    transfer = InventoryTransfer(
        transferId=_gen_id(),
        **data.model_dump(),
        transferredAt=datetime.utcnow(),
    )
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    return transfer


# ═══════════════════════════════════════════════════════
# TransferRequest 调拨申请
# ═══════════════════════════════════════════════════════

@router.get("/transfer-requests", response_model=list[TransferRequestOut])
async def list_transfer_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(TransferRequest).order_by(TransferRequest.createdAt.desc())
    if status_filter:
        query = query.where(TransferRequest.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/transfer-requests", response_model=TransferRequestOut)
async def create_transfer_request(
    data: TransferRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tr = TransferRequest(transferRequestId=_gen_id(), **data.model_dump())
    db.add(tr)
    await db.commit()
    await db.refresh(tr)
    return tr


@router.put("/transfer-requests/{transfer_id}", response_model=TransferRequestOut)
async def update_transfer_request(
    transfer_id: str,
    data: TransferRequestUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(TransferRequest).where(TransferRequest.transferRequestId == transfer_id)
    )
    tr = r.scalar_one_or_none()
    if not tr:
        raise HTTPException(404, "调拨申请不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(tr, k, v)
    await db.commit()
    await db.refresh(tr)
    return tr


# ═══════════════════════════════════════════════════════
# InternalSettlement 内部结算
# ═══════════════════════════════════════════════════════

@router.get("/internal-settlements", response_model=list[InternalSettlementOut])
async def list_internal_settlements(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(InternalSettlement).order_by(InternalSettlement.createdAt.desc())
    if status_filter:
        query = query.where(InternalSettlement.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


# ═══════════════════════════════════════════════════════
# StockCount 盘点
# ═══════════════════════════════════════════════════════

@router.get("/stock-counts", response_model=StockCountListOut)
async def list_stock_counts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    warehouse_id: Optional[str] = Query(None, alias="warehouseId"),
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    query = select(StockCount)
    if status_filter:
        query = query.where(StockCount.status == status_filter)
    if warehouse_id:
        query = query.where(StockCount.warehouseId == warehouse_id)

    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.options(selectinload(StockCount.lines))
    query = query.order_by(StockCount.createdAt.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    counts = result.scalars().all()

    items = [
        StockCountOut(
            **{k: getattr(c, k) for k in StockCountOut.model_fields if k != "lines"},
            lines=[StockCountLineOut.model_validate(ln) for ln in (c.lines or [])],
        )
        for c in counts
    ]
    return StockCountListOut(total=total, items=items, page=page, page_size=page_size)


@router.post("/stock-counts", response_model=StockCountOut)
async def create_stock_count(
    data: StockCountCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    count_id = _gen_id()
    lines = []
    for line_data in data.lines:
        diff_qty = line_data.actualQuantity - line_data.bookQuantity
        diff_amt = round(diff_qty * line_data.unitPrice, 2)
        line = StockCountLine(
            lineId=_gen_id(),
            countId=count_id,
            productId=line_data.productId,
            bookQuantity=line_data.bookQuantity,
            actualQuantity=line_data.actualQuantity,
            differenceQuantity=diff_qty,
            unitPrice=line_data.unitPrice,
            differenceAmount=diff_amt,
            remark=line_data.remark,
        )
        lines.append(line)

    sc = StockCount(
        countId=count_id,
        warehouseId=data.warehouseId,
        storeId=data.storeId,
        countNumber=_gen_order_number("SC"),
        type=data.type,
        countedBy=data.countedBy,
        countDate=data.countDate or date.today(),
        lines=lines,
    )
    db.add(sc)
    await db.commit()
    await db.refresh(sc)
    return StockCountOut(
        **{k: getattr(sc, k) for k in StockCountOut.model_fields if k != "lines"},
        lines=[StockCountLineOut.model_validate(ln) for ln in (sc.lines or [])],
    )


@router.get("/stock-counts/{count_id}", response_model=StockCountOut)
async def get_stock_count(
    count_id: str,
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    r = await db.execute(
        select(StockCount).where(StockCount.countId == count_id)
        .options(selectinload(StockCount.lines))
    )
    sc = r.scalar_one_or_none()
    if not sc:
        raise HTTPException(404, "盘点单不存在")
    return StockCountOut(
        **{k: getattr(sc, k) for k in StockCountOut.model_fields if k != "lines"},
        lines=[StockCountLineOut.model_validate(ln) for ln in (sc.lines or [])],
    )


@router.put("/stock-counts/{count_id}", response_model=StockCountOut)
async def update_stock_count(
    count_id: str,
    data: StockCountUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(StockCount).where(StockCount.countId == count_id)
        .options(selectinload(StockCount.lines))
    )
    sc = r.scalar_one_or_none()
    if not sc:
        raise HTTPException(404, "盘点单不存在")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(sc, k, v)

    # If approved, sync InventoryOnHand
    if data.status == "Approved":
        for line in sc.lines:
            inv_r = await db.execute(
                select(InventoryOnHand).where(
                    InventoryOnHand.warehouseId == sc.warehouseId,
                    InventoryOnHand.productId == line.productId,
                )
            )
            inv = inv_r.scalar_one_or_none()
            if inv:
                inv.quantity = line.actualQuantity
                inv.lastCountDate = date.today()
            else:
                inv = InventoryOnHand(
                    inventoryId=_gen_id(),
                    warehouseId=sc.warehouseId,
                    productId=line.productId,
                    quantity=line.actualQuantity,
                    lastCountDate=date.today(),
                )
                db.add(inv)

    await db.commit()
    await db.refresh(sc)
    return StockCountOut(
        **{k: getattr(sc, k) for k in StockCountOut.model_fields if k != "lines"},
        lines=[StockCountLineOut.model_validate(ln) for ln in (sc.lines or [])],
    )


@router.delete("/stock-counts/{count_id}")
async def delete_stock_count(
    count_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = await db.execute(
        select(StockCount).where(StockCount.countId == count_id)
        .options(selectinload(StockCount.lines))
    )
    sc = r.scalar_one_or_none()
    if not sc:
        raise HTTPException(404, "盘点单不存在")
    if sc.status not in ("Draft",):
        raise HTTPException(400, "只能删除草稿状态的盘点单")
    await db.delete(sc)
    await db.commit()
    return {"message": "盘点单已删除"}
