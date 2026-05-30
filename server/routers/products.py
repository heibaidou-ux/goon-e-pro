import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from database import get_db
from models.product import Product, ProductCategory, ProductImage
from models.user import User
from schemas.product import (
    ProductCreate, ProductUpdate, ProductOut, ProductListOut,
    ProductCategoryCreate, ProductCategoryOut, ProductImageOut,
)
from services.auth_service import get_current_user
from services.image_service import image_service

router = APIRouter(prefix="/api/products", tags=["商品管理"])


# ── Categories ──

@router.get("/categories", response_model=list[ProductCategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProductCategory).order_by(ProductCategory.sort_order)
    )
    categories = result.scalars().all()
    out = []
    for c in categories:
        subs = json.loads(c.subcategories) if isinstance(c.subcategories, str) else (c.subcategories or [])
        out.append(ProductCategoryOut(
            id=c.id, name=c.name, subcategories=subs,
            sort_order=c.sort_order, created_at=c.created_at
        ))
    return out


@router.post("/categories", response_model=ProductCategoryOut)
async def create_category(data: ProductCategoryCreate,
                          db: AsyncSession = Depends(get_db),
                          user: User = Depends(get_current_user)):
    cat = ProductCategory(
        name=data.name,
        subcategories=json.dumps(data.subcategories, ensure_ascii=False),
        sort_order=data.sort_order,
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return ProductCategoryOut(
        id=cat.id, name=cat.name,
        subcategories=data.subcategories,
        sort_order=cat.sort_order, created_at=cat.created_at
    )


# ── Products ──

@router.get("", response_model=ProductListOut)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.is_active == True)

    if search:
        query = query.where(
            or_(Product.name.ilike(f"%{search}%"), Product.code.ilike(f"%{search}%"))
        )
    if category:
        query = query.where(Product.category == category)
    if status:
        query = query.where(Product.status == status)

    # Eagerly load images
    query = query.options(selectinload(Product.images))

    # Total count
    count_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginated
    offset = (page - 1) * page_size
    query = query.order_by(Product.updated_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    products = result.scalars().all()

    return ProductListOut(total=total, items=list(products), page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Product).where(Product.id == product_id).options(selectinload(Product.images))
    result = await db.execute(query)
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


@router.post("", response_model=ProductOut)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check code uniqueness
    result = await db.execute(select(Product).where(Product.code == data.code))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="商品编码已存在")

    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.commit()
    await db.refresh(product)
    # Re-fetch with images
    q2 = select(Product).where(Product.id == product_id).options(selectinload(Product.images))
    result2 = await db.execute(q2)
    return result2.scalar_one()


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # Soft delete
    product.is_active = False
    await db.commit()
    return {"message": "已删除"}


# ── Product Images ──

@router.post("/{product_id}/images", response_model=list[ProductImageOut])
async def upload_product_images(
    product_id: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # Get current max sort_order
    img_result = await db.execute(
        select(func.max(ProductImage.sort_order))
        .where(ProductImage.product_id == product_id)
    )
    max_order = img_result.scalar() or -1

    created_images = []
    for i, file in enumerate(files):
        content = await file.read()
        ext = f".{file.filename.split('.')[-1]}" if file.filename else ".jpg"

        try:
            urls = image_service.process_product_image(content, product_id, ext)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check if this should be the cover image
        is_cover = (max_order + i) == 0

        img = ProductImage(
            product_id=product_id,
            url_original=urls["original"],
            url_thumbnail=urls.get(240),
            url_medium=urls.get(480),
            url_large=urls.get(800),
            is_cover=is_cover,
            sort_order=max_order + 1 + i,
        )
        db.add(img)
        created_images.append(img)

    await db.commit()
    for img in created_images:
        await db.refresh(img)

    return created_images


@router.delete("/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ProductImage).where(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id,
        )
    )
    img = result.scalar_one_or_none()
    if not img:
        raise HTTPException(status_code=404, detail="图片不存在")

    await db.delete(img)
    await db.commit()
    return {"message": "图片已删除"}
