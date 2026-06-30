"""市场营销管理 API — 活动/优惠券/线索/商机/营销列表/客户细分/第三方活动/渠道"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, date

from database import get_db
from services.auth_service import get_current_user, get_optional_user
from models.marketing import (
    Campaign, CouponTemplate, Coupon, Lead, Opportunity,
    MarketingList, CustomerSegment, ThirdPartyActivity, CampaignEffect, Channel,
)
from models.store_dev import Store
from schemas.marketing import (
    CampaignCreate, CampaignUpdate, CampaignOut, CampaignListOut,
    CouponTemplateCreate, CouponTemplateUpdate, CouponTemplateOut, CouponTemplateListOut,
    CouponCreate, CouponUpdate, CouponOut, CouponListOut,
    LeadCreate, LeadUpdate, LeadOut, LeadListOut,
    OpportunityCreate, OpportunityUpdate, OpportunityOut, OpportunityListOut,
    MarketingListCreate, MarketingListUpdate, MarketingListOut, MarketingListListOut,
    CustomerSegmentCreate, CustomerSegmentUpdate, CustomerSegmentOut, CustomerSegmentListOut,
    ThirdPartyActivityCreate, ThirdPartyActivityUpdate, ThirdPartyActivityOut, ThirdPartyActivityListOut,
    CampaignEffectCreate, CampaignEffectUpdate, CampaignEffectOut, CampaignEffectListOut,
    ChannelCreate, ChannelUpdate, ChannelOut, ChannelListOut,
)

router = APIRouter(prefix="/api/marketing", tags=["市场营销管理"], dependencies=[Depends(get_optional_user)])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


def _get_store_name(store_id: str | None) -> str | None:
    """Placeholder — store name is resolved inside each endpoint via async DB call."""
    return None


# ═══════════════════════════════════════════
# Campaign 营销活动
# ═══════════════════════════════════════════

@router.get("/campaigns", response_model=CampaignListOut)
async def list_campaigns(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List marketing campaigns with optional filters."""
    q = select(Campaign)
    if store_id:
        q = q.where(Campaign.storeId == store_id)
    if status:
        q = q.where(Campaign.status == status)
    if type:
        q = q.where(Campaign.type == type)
    if start_date:
        q = q.where(Campaign.startDate >= start_date)
    if end_date:
        q = q.where(Campaign.endDate <= end_date)
    q = q.order_by(Campaign.createdAt.desc())

    # Count total
    count_q = select(func.count(Campaign.campaignId)).select_from(Campaign)
    if store_id:
        count_q = count_q.where(Campaign.storeId == store_id)
    if status:
        count_q = count_q.where(Campaign.status == status)
    if type:
        count_q = count_q.where(Campaign.type == type)
    if start_date:
        count_q = count_q.where(Campaign.startDate >= start_date)
    if end_date:
        count_q = count_q.where(Campaign.endDate <= end_date)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(CampaignOut(
            campaignId=item.campaignId, name=item.name, type=item.type,
            storeId=item.storeId, storeName=store_name,
            startDate=item.startDate, endDate=item.endDate,
            budget=item.budget, usedAmount=item.usedAmount,
            status=item.status, description=item.description,
            createdBy=item.createdBy, createdAt=item.createdAt,
        ))

    return CampaignListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/campaigns/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Campaign).where(Campaign.campaignId == campaign_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "营销活动不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return CampaignOut(
        campaignId=item.campaignId, name=item.name, type=item.type,
        storeId=item.storeId, storeName=store_name,
        startDate=item.startDate, endDate=item.endDate,
        budget=item.budget, usedAmount=item.usedAmount,
        status=item.status, description=item.description,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.post("/campaigns", response_model=CampaignOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Campaign(
        campaignId=_gen_id(), name=data.name, type=data.type,
        storeId=data.storeId, startDate=data.startDate, endDate=data.endDate,
        budget=data.budget, description=data.description, createdBy=data.createdBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return CampaignOut(
        campaignId=item.campaignId, name=item.name, type=item.type,
        storeId=item.storeId, storeName=store_name,
        startDate=item.startDate, endDate=item.endDate,
        budget=item.budget, usedAmount=item.usedAmount,
        status=item.status, description=item.description,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.put("/campaigns/{campaign_id}", response_model=CampaignOut, dependencies=[Depends(get_current_user)])
async def update_campaign(
    campaign_id: str,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Campaign).where(Campaign.campaignId == campaign_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "营销活动不存在")
    if data.name is not None:
        item.name = data.name
    if data.type is not None:
        item.type = data.type
    if data.storeId is not None:
        item.storeId = data.storeId
    if data.startDate is not None:
        item.startDate = data.startDate
    if data.endDate is not None:
        item.endDate = data.endDate
    if data.budget is not None:
        item.budget = data.budget
    if data.usedAmount is not None:
        item.usedAmount = data.usedAmount
    if data.status is not None:
        item.status = data.status
    if data.description is not None:
        item.description = data.description
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return CampaignOut(
        campaignId=item.campaignId, name=item.name, type=item.type,
        storeId=item.storeId, storeName=store_name,
        startDate=item.startDate, endDate=item.endDate,
        budget=item.budget, usedAmount=item.usedAmount,
        status=item.status, description=item.description,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Campaign Effects (nested under campaigns)
# ═══════════════════════════════════════════

@router.get("/campaigns/{campaign_id}/effects", response_model=list[CampaignEffectOut])
async def list_campaign_effects(
    campaign_id: str,
    metric_name: Optional[str] = Query(None, alias="metricName"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
):
    """Get all effect records for a specific campaign."""
    # Verify campaign exists
    cr = await db.execute(select(Campaign).where(Campaign.campaignId == campaign_id))
    if not cr.scalar_one_or_none():
        raise HTTPException(404, "营销活动不存在")

    q = select(CampaignEffect).where(CampaignEffect.campaignId == campaign_id)
    if metric_name:
        q = q.where(CampaignEffect.metricName == metric_name)
    if start_date:
        q = q.where(CampaignEffect.date >= start_date)
    if end_date:
        q = q.where(CampaignEffect.date <= end_date)
    q = q.order_by(CampaignEffect.date.desc())

    r = await db.execute(q)
    items = r.scalars().all()
    return [
        CampaignEffectOut(
            effectId=item.effectId, campaignId=item.campaignId,
            metricName=item.metricName, metricValue=item.metricValue,
            date=item.date, createdAt=item.createdAt,
        )
        for item in items
    ]


# ═══════════════════════════════════════════
# CouponTemplate 优惠券模板
# ═══════════════════════════════════════════

@router.get("/coupon-templates", response_model=CouponTemplateListOut)
async def list_coupon_templates(
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List coupon templates with optional filters."""
    q = select(CouponTemplate)
    if status:
        q = q.where(CouponTemplate.status == status)
    if type:
        q = q.where(CouponTemplate.type == type)
    if search:
        q = q.where(CouponTemplate.name.contains(search))
    q = q.order_by(CouponTemplate.createdAt.desc())

    count_q = select(func.count(CouponTemplate.templateId)).select_from(CouponTemplate)
    if status:
        count_q = count_q.where(CouponTemplate.status == status)
    if type:
        count_q = count_q.where(CouponTemplate.type == type)
    if search:
        count_q = count_q.where(CouponTemplate.name.contains(search))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CouponTemplateListOut(
        total=total,
        items=[
            CouponTemplateOut(
                templateId=item.templateId, name=item.name, type=item.type,
                value=item.value, condition=item.condition,
                totalCount=item.totalCount, perLimit=item.perLimit,
                startTime=item.startTime, endTime=item.endTime,
                applicableStoreIds=item.applicableStoreIds,
                status=item.status, createdBy=item.createdBy, createdAt=item.createdAt,
            )
            for item in items
        ],
        page=page, page_size=page_size,
    )


@router.get("/coupon-templates/{template_id}", response_model=CouponTemplateOut)
async def get_coupon_template(template_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CouponTemplate).where(CouponTemplate.templateId == template_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "优惠券模板不存在")
    return CouponTemplateOut(
        templateId=item.templateId, name=item.name, type=item.type,
        value=item.value, condition=item.condition,
        totalCount=item.totalCount, perLimit=item.perLimit,
        startTime=item.startTime, endTime=item.endTime,
        applicableStoreIds=item.applicableStoreIds,
        status=item.status, createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.post("/coupon-templates", response_model=CouponTemplateOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_coupon_template(
    data: CouponTemplateCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CouponTemplate(
        templateId=_gen_id(), name=data.name, type=data.type,
        value=data.value, condition=data.condition,
        totalCount=data.totalCount, perLimit=data.perLimit,
        startTime=data.startTime, endTime=data.endTime,
        applicableStoreIds=data.applicableStoreIds,
        createdBy=data.createdBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CouponTemplateOut(
        templateId=item.templateId, name=item.name, type=item.type,
        value=item.value, condition=item.condition,
        totalCount=item.totalCount, perLimit=item.perLimit,
        startTime=item.startTime, endTime=item.endTime,
        applicableStoreIds=item.applicableStoreIds,
        status=item.status, createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.put("/coupon-templates/{template_id}", response_model=CouponTemplateOut, dependencies=[Depends(get_current_user)])
async def update_coupon_template(
    template_id: str,
    data: CouponTemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CouponTemplate).where(CouponTemplate.templateId == template_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "优惠券模板不存在")
    if data.name is not None:
        item.name = data.name
    if data.type is not None:
        item.type = data.type
    if data.value is not None:
        item.value = data.value
    if data.condition is not None:
        item.condition = data.condition
    if data.totalCount is not None:
        item.totalCount = data.totalCount
    if data.perLimit is not None:
        item.perLimit = data.perLimit
    if data.startTime is not None:
        item.startTime = data.startTime
    if data.endTime is not None:
        item.endTime = data.endTime
    if data.applicableStoreIds is not None:
        item.applicableStoreIds = data.applicableStoreIds
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return CouponTemplateOut(
        templateId=item.templateId, name=item.name, type=item.type,
        value=item.value, condition=item.condition,
        totalCount=item.totalCount, perLimit=item.perLimit,
        startTime=item.startTime, endTime=item.endTime,
        applicableStoreIds=item.applicableStoreIds,
        status=item.status, createdBy=item.createdBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Coupon 优惠券实例
# ═══════════════════════════════════════════

@router.get("/coupons/verify")
async def verify_coupon(
    code: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Verify a coupon by its unique code. Checks status and expiration."""
    r = await db.execute(select(Coupon).where(Coupon.code == code))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "优惠券不存在")

    # Resolve template name
    template_name = None
    if item.templateId:
        tr = await db.execute(select(CouponTemplate.name).where(CouponTemplate.templateId == item.templateId))
        template_name = tr.scalar_one_or_none()

    # Determine validity
    now = datetime.utcnow()
    is_valid = True
    message = "优惠券可用"
    if item.status == "Used":
        is_valid = False
        message = "优惠券已使用"
    elif item.status == "Expired" or (item.expiredAt and item.expiredAt < now):
        is_valid = False
        message = "优惠券已过期"
    elif item.status == "Frozen":
        is_valid = False
        message = "优惠券已冻结"

    return {
        "valid": is_valid,
        "message": message,
        "coupon": CouponOut(
            couponId=item.couponId, templateId=item.templateId,
            templateName=template_name,
            customerId=item.customerId, orderId=item.orderId,
            code=item.code, status=item.status,
            usedAt=item.usedAt, expiredAt=item.expiredAt,
            createdAt=item.createdAt,
        ),
    }


@router.get("/coupons/by-customer/{customer_id}", response_model=list[CouponOut])
async def get_coupons_by_customer(
    customer_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all coupons belonging to a specific customer."""
    q = select(Coupon).where(Coupon.customerId == customer_id)
    if status:
        q = q.where(Coupon.status == status)
    q = q.order_by(Coupon.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        template_name = None
        if item.templateId:
            tr = await db.execute(select(CouponTemplate.name).where(CouponTemplate.templateId == item.templateId))
            template_name = tr.scalar_one_or_none()
        result.append(CouponOut(
            couponId=item.couponId, templateId=item.templateId,
            templateName=template_name,
            customerId=item.customerId, orderId=item.orderId,
            code=item.code, status=item.status,
            usedAt=item.usedAt, expiredAt=item.expiredAt,
            createdAt=item.createdAt,
        ))
    return result


@router.get("/coupons", response_model=CouponListOut)
async def list_coupons(
    status: Optional[str] = None,
    template_id: Optional[str] = Query(None, alias="templateId"),
    customer_id: Optional[str] = Query(None, alias="customerId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List coupon instances with optional filters."""
    q = select(Coupon)
    if status:
        q = q.where(Coupon.status == status)
    if template_id:
        q = q.where(Coupon.templateId == template_id)
    if customer_id:
        q = q.where(Coupon.customerId == customer_id)
    q = q.order_by(Coupon.createdAt.desc())

    count_q = select(func.count(Coupon.couponId)).select_from(Coupon)
    if status:
        count_q = count_q.where(Coupon.status == status)
    if template_id:
        count_q = count_q.where(Coupon.templateId == template_id)
    if customer_id:
        count_q = count_q.where(Coupon.customerId == customer_id)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        template_name = None
        if item.templateId:
            tr = await db.execute(select(CouponTemplate.name).where(CouponTemplate.templateId == item.templateId))
            template_name = tr.scalar_one_or_none()
        result.append(CouponOut(
            couponId=item.couponId, templateId=item.templateId,
            templateName=template_name,
            customerId=item.customerId, orderId=item.orderId,
            code=item.code, status=item.status,
            usedAt=item.usedAt, expiredAt=item.expiredAt,
            createdAt=item.createdAt,
        ))

    return CouponListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/coupons/{coupon_id}", response_model=CouponOut)
async def get_coupon(coupon_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Coupon).where(Coupon.couponId == coupon_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "优惠券不存在")
    template_name = None
    if item.templateId:
        tr = await db.execute(select(CouponTemplate.name).where(CouponTemplate.templateId == item.templateId))
        template_name = tr.scalar_one_or_none()
    return CouponOut(
        couponId=item.couponId, templateId=item.templateId,
        templateName=template_name,
        customerId=item.customerId, orderId=item.orderId,
        code=item.code, status=item.status,
        usedAt=item.usedAt, expiredAt=item.expiredAt,
        createdAt=item.createdAt,
    )


@router.post("/coupons", response_model=CouponOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_coupon(
    data: CouponCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check code uniqueness
    cr = await db.execute(select(Coupon).where(Coupon.code == data.code))
    if cr.scalar_one_or_none():
        raise HTTPException(409, "优惠券编码已存在")

    # Verify template exists
    tr = await db.execute(select(CouponTemplate).where(CouponTemplate.templateId == data.templateId))
    template = tr.scalar_one_or_none()
    if not template:
        raise HTTPException(404, "优惠券模板不存在")

    item = Coupon(
        couponId=_gen_id(), templateId=data.templateId,
        customerId=data.customerId, orderId=data.orderId,
        code=data.code, expiredAt=data.expiredAt,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CouponOut(
        couponId=item.couponId, templateId=item.templateId,
        templateName=template.name,
        customerId=item.customerId, orderId=item.orderId,
        code=item.code, status=item.status,
        usedAt=item.usedAt, expiredAt=item.expiredAt,
        createdAt=item.createdAt,
    )


@router.put("/coupons/{coupon_id}", response_model=CouponOut, dependencies=[Depends(get_current_user)])
async def update_coupon(
    coupon_id: str,
    data: CouponUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Coupon).where(Coupon.couponId == coupon_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "优惠券不存在")
    if data.status is not None:
        item.status = data.status
    if data.orderId is not None:
        item.orderId = data.orderId
    if data.usedAt is not None:
        item.usedAt = data.usedAt
    if data.expiredAt is not None:
        item.expiredAt = data.expiredAt
    await db.commit()
    await db.refresh(item)
    template_name = None
    if item.templateId:
        tr = await db.execute(select(CouponTemplate.name).where(CouponTemplate.templateId == item.templateId))
        template_name = tr.scalar_one_or_none()
    return CouponOut(
        couponId=item.couponId, templateId=item.templateId,
        templateName=template_name,
        customerId=item.customerId, orderId=item.orderId,
        code=item.code, status=item.status,
        usedAt=item.usedAt, expiredAt=item.expiredAt,
        createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Lead 线索
# ═══════════════════════════════════════════

@router.get("/leads", response_model=LeadListOut)
async def list_leads(
    store_id: Optional[str] = Query(None, alias="storeId"),
    source: Optional[str] = None,
    status: Optional[str] = None,
    intention: Optional[str] = None,
    assignee_id: Optional[str] = Query(None, alias="assigneeId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List leads with optional filters."""
    q = select(Lead)
    if store_id:
        q = q.where(Lead.storeId == store_id)
    if source:
        q = q.where(Lead.source == source)
    if status:
        q = q.where(Lead.status == status)
    if intention:
        q = q.where(Lead.intention == intention)
    if assignee_id:
        q = q.where(Lead.assigneeId == assignee_id)
    if start_date:
        q = q.where(Lead.createdAt >= start_date)
    if end_date:
        q = q.where(Lead.createdAt <= end_date + " 23:59:59")
    q = q.order_by(Lead.createdAt.desc())

    count_q = select(func.count(Lead.leadId)).select_from(Lead)
    if store_id:
        count_q = count_q.where(Lead.storeId == store_id)
    if source:
        count_q = count_q.where(Lead.source == source)
    if status:
        count_q = count_q.where(Lead.status == status)
    if intention:
        count_q = count_q.where(Lead.intention == intention)
    if assignee_id:
        count_q = count_q.where(Lead.assigneeId == assignee_id)
    if start_date:
        count_q = count_q.where(Lead.createdAt >= start_date)
    if end_date:
        count_q = count_q.where(Lead.createdAt <= end_date + " 23:59:59")
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(LeadOut(
            leadId=item.leadId, customerId=item.customerId,
            source=item.source, storeId=item.storeId, storeName=store_name,
            intention=item.intention, status=item.status,
            assigneeId=item.assigneeId, description=item.description,
            createdAt=item.createdAt,
        ))

    return LeadListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/leads/{lead_id}", response_model=LeadOut)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Lead).where(Lead.leadId == lead_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "线索不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return LeadOut(
        leadId=item.leadId, customerId=item.customerId,
        source=item.source, storeId=item.storeId, storeName=store_name,
        intention=item.intention, status=item.status,
        assigneeId=item.assigneeId, description=item.description,
        createdAt=item.createdAt,
    )


@router.post("/leads", response_model=LeadOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_lead(
    data: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Lead(
        leadId=_gen_id(), customerId=data.customerId,
        source=data.source, storeId=data.storeId,
        intention=data.intention, assigneeId=data.assigneeId,
        description=data.description,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return LeadOut(
        leadId=item.leadId, customerId=item.customerId,
        source=item.source, storeId=item.storeId, storeName=store_name,
        intention=item.intention, status=item.status,
        assigneeId=item.assigneeId, description=item.description,
        createdAt=item.createdAt,
    )


@router.put("/leads/{lead_id}", response_model=LeadOut, dependencies=[Depends(get_current_user)])
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Lead).where(Lead.leadId == lead_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "线索不存在")
    if data.source is not None:
        item.source = data.source
    if data.storeId is not None:
        item.storeId = data.storeId
    if data.intention is not None:
        item.intention = data.intention
    if data.status is not None:
        item.status = data.status
    if data.assigneeId is not None:
        item.assigneeId = data.assigneeId
    if data.description is not None:
        item.description = data.description
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return LeadOut(
        leadId=item.leadId, customerId=item.customerId,
        source=item.source, storeId=item.storeId, storeName=store_name,
        intention=item.intention, status=item.status,
        assigneeId=item.assigneeId, description=item.description,
        createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Opportunity 商机
# ═══════════════════════════════════════════

@router.get("/opportunities", response_model=OpportunityListOut)
async def list_opportunities(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    lead_id: Optional[str] = Query(None, alias="leadId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List opportunities with optional filters."""
    q = select(Opportunity)
    if store_id:
        q = q.where(Opportunity.storeId == store_id)
    if status:
        q = q.where(Opportunity.status == status)
    if lead_id:
        q = q.where(Opportunity.leadId == lead_id)
    if start_date:
        q = q.where(Opportunity.createdAt >= start_date)
    if end_date:
        q = q.where(Opportunity.createdAt <= end_date + " 23:59:59")
    q = q.order_by(Opportunity.createdAt.desc())

    count_q = select(func.count(Opportunity.opportunityId)).select_from(Opportunity)
    if store_id:
        count_q = count_q.where(Opportunity.storeId == store_id)
    if status:
        count_q = count_q.where(Opportunity.status == status)
    if lead_id:
        count_q = count_q.where(Opportunity.leadId == lead_id)
    if start_date:
        count_q = count_q.where(Opportunity.createdAt >= start_date)
    if end_date:
        count_q = count_q.where(Opportunity.createdAt <= end_date + " 23:59:59")
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(OpportunityOut(
            opportunityId=item.opportunityId, leadId=item.leadId,
            customerId=item.customerId, storeId=item.storeId,
            storeName=store_name,
            expectedAmount=item.expectedAmount, probability=item.probability,
            expectedCloseDate=item.expectedCloseDate, status=item.status,
            remark=item.remark, createdAt=item.createdAt,
        ))

    return OpportunityListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityOut)
async def get_opportunity(opportunity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Opportunity).where(Opportunity.opportunityId == opportunity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "商机不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return OpportunityOut(
        opportunityId=item.opportunityId, leadId=item.leadId,
        customerId=item.customerId, storeId=item.storeId,
        storeName=store_name,
        expectedAmount=item.expectedAmount, probability=item.probability,
        expectedCloseDate=item.expectedCloseDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


@router.post("/opportunities", response_model=OpportunityOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Opportunity(
        opportunityId=_gen_id(), leadId=data.leadId,
        customerId=data.customerId, storeId=data.storeId,
        expectedAmount=data.expectedAmount, probability=data.probability,
        expectedCloseDate=data.expectedCloseDate, remark=data.remark,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return OpportunityOut(
        opportunityId=item.opportunityId, leadId=item.leadId,
        customerId=item.customerId, storeId=item.storeId,
        storeName=store_name,
        expectedAmount=item.expectedAmount, probability=item.probability,
        expectedCloseDate=item.expectedCloseDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityOut, dependencies=[Depends(get_current_user)])
async def update_opportunity(
    opportunity_id: str,
    data: OpportunityUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Opportunity).where(Opportunity.opportunityId == opportunity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "商机不存在")
    if data.expectedAmount is not None:
        item.expectedAmount = data.expectedAmount
    if data.probability is not None:
        item.probability = data.probability
    if data.expectedCloseDate is not None:
        item.expectedCloseDate = data.expectedCloseDate
    if data.status is not None:
        item.status = data.status
    if data.remark is not None:
        item.remark = data.remark
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return OpportunityOut(
        opportunityId=item.opportunityId, leadId=item.leadId,
        customerId=item.customerId, storeId=item.storeId,
        storeName=store_name,
        expectedAmount=item.expectedAmount, probability=item.probability,
        expectedCloseDate=item.expectedCloseDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# MarketingList 营销列表
# ═══════════════════════════════════════════

@router.get("/marketing-lists", response_model=MarketingListListOut)
async def list_marketing_lists(
    store_id: Optional[str] = Query(None, alias="storeId"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(MarketingList)
    if store_id:
        q = q.where(MarketingList.storeId == store_id)
    if search:
        q = q.where(MarketingList.name.contains(search))
    q = q.order_by(MarketingList.createdAt.desc())

    count_q = select(func.count(MarketingList.listId)).select_from(MarketingList)
    if store_id:
        count_q = count_q.where(MarketingList.storeId == store_id)
    if search:
        count_q = count_q.where(MarketingList.name.contains(search))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(MarketingListOut(
            listId=item.listId, storeId=item.storeId, storeName=store_name,
            name=item.name, description=item.description,
            customerCount=item.customerCount,
            generatedBy=item.generatedBy, createdAt=item.createdAt,
        ))

    return MarketingListListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/marketing-lists/{list_id}", response_model=MarketingListOut)
async def get_marketing_list(list_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(MarketingList).where(MarketingList.listId == list_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "营销列表不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return MarketingListOut(
        listId=item.listId, storeId=item.storeId, storeName=store_name,
        name=item.name, description=item.description,
        customerCount=item.customerCount,
        generatedBy=item.generatedBy, createdAt=item.createdAt,
    )


@router.post("/marketing-lists", response_model=MarketingListOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_marketing_list(
    data: MarketingListCreate,
    db: AsyncSession = Depends(get_db),
):
    item = MarketingList(
        listId=_gen_id(), storeId=data.storeId, name=data.name,
        description=data.description, generatedBy=data.generatedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return MarketingListOut(
        listId=item.listId, storeId=item.storeId, storeName=store_name,
        name=item.name, description=item.description,
        customerCount=item.customerCount,
        generatedBy=item.generatedBy, createdAt=item.createdAt,
    )


@router.put("/marketing-lists/{list_id}", response_model=MarketingListOut, dependencies=[Depends(get_current_user)])
async def update_marketing_list(
    list_id: str,
    data: MarketingListUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(MarketingList).where(MarketingList.listId == list_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "营销列表不存在")
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.customerCount is not None:
        item.customerCount = data.customerCount
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return MarketingListOut(
        listId=item.listId, storeId=item.storeId, storeName=store_name,
        name=item.name, description=item.description,
        customerCount=item.customerCount,
        generatedBy=item.generatedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# CustomerSegment 客户细分
# ═══════════════════════════════════════════

@router.get("/customer-segments", response_model=CustomerSegmentListOut)
async def list_customer_segments(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CustomerSegment)
    if search:
        q = q.where(CustomerSegment.name.contains(search))
    q = q.order_by(CustomerSegment.createdAt.desc())

    count_q = select(func.count(CustomerSegment.segmentId)).select_from(CustomerSegment)
    if search:
        count_q = count_q.where(CustomerSegment.name.contains(search))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CustomerSegmentListOut(
        total=total,
        items=[
            CustomerSegmentOut(
                segmentId=item.segmentId, name=item.name,
                description=item.description, conditions=item.conditions,
                customerCount=item.customerCount, createdAt=item.createdAt,
            )
            for item in items
        ],
        page=page, page_size=page_size,
    )


@router.get("/customer-segments/{segment_id}", response_model=CustomerSegmentOut)
async def get_customer_segment(segment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CustomerSegment).where(CustomerSegment.segmentId == segment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "客户细分不存在")
    return CustomerSegmentOut(
        segmentId=item.segmentId, name=item.name,
        description=item.description, conditions=item.conditions,
        customerCount=item.customerCount, createdAt=item.createdAt,
    )


@router.post("/customer-segments", response_model=CustomerSegmentOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_customer_segment(
    data: CustomerSegmentCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CustomerSegment(
        segmentId=_gen_id(), name=data.name,
        description=data.description, conditions=data.conditions,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CustomerSegmentOut(
        segmentId=item.segmentId, name=item.name,
        description=item.description, conditions=item.conditions,
        customerCount=item.customerCount, createdAt=item.createdAt,
    )


@router.put("/customer-segments/{segment_id}", response_model=CustomerSegmentOut, dependencies=[Depends(get_current_user)])
async def update_customer_segment(
    segment_id: str,
    data: CustomerSegmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CustomerSegment).where(CustomerSegment.segmentId == segment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "客户细分不存在")
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.conditions is not None:
        item.conditions = data.conditions
    if data.customerCount is not None:
        item.customerCount = data.customerCount
    await db.commit()
    await db.refresh(item)
    return CustomerSegmentOut(
        segmentId=item.segmentId, name=item.name,
        description=item.description, conditions=item.conditions,
        customerCount=item.customerCount, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# ThirdPartyActivity 第三方活动
# ═══════════════════════════════════════════

@router.get("/third-party-activities", response_model=ThirdPartyActivityListOut)
async def list_third_party_activities(
    store_id: Optional[str] = Query(None, alias="storeId"),
    platform: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ThirdPartyActivity)
    if store_id:
        q = q.where(ThirdPartyActivity.storeId == store_id)
    if platform:
        q = q.where(ThirdPartyActivity.platform == platform)
    if status:
        q = q.where(ThirdPartyActivity.status == status)
    if start_date:
        q = q.where(ThirdPartyActivity.startDate >= start_date)
    if end_date:
        q = q.where(ThirdPartyActivity.endDate <= end_date)
    q = q.order_by(ThirdPartyActivity.createdAt.desc())

    count_q = select(func.count(ThirdPartyActivity.activityId)).select_from(ThirdPartyActivity)
    if store_id:
        count_q = count_q.where(ThirdPartyActivity.storeId == store_id)
    if platform:
        count_q = count_q.where(ThirdPartyActivity.platform == platform)
    if status:
        count_q = count_q.where(ThirdPartyActivity.status == status)
    if start_date:
        count_q = count_q.where(ThirdPartyActivity.startDate >= start_date)
    if end_date:
        count_q = count_q.where(ThirdPartyActivity.endDate <= end_date)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(ThirdPartyActivityOut(
            activityId=item.activityId, storeId=item.storeId, storeName=store_name,
            platform=item.platform, activityName=item.activityName,
            activityBudget=item.activityBudget, actualCost=item.actualCost,
            salesAmount=item.salesAmount, startDate=item.startDate,
            endDate=item.endDate, status=item.status,
            remark=item.remark, createdAt=item.createdAt,
        ))

    return ThirdPartyActivityListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/third-party-activities/{activity_id}", response_model=ThirdPartyActivityOut)
async def get_third_party_activity(activity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ThirdPartyActivity).where(ThirdPartyActivity.activityId == activity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "第三方活动不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ThirdPartyActivityOut(
        activityId=item.activityId, storeId=item.storeId, storeName=store_name,
        platform=item.platform, activityName=item.activityName,
        activityBudget=item.activityBudget, actualCost=item.actualCost,
        salesAmount=item.salesAmount, startDate=item.startDate,
        endDate=item.endDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


@router.post("/third-party-activities", response_model=ThirdPartyActivityOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_third_party_activity(
    data: ThirdPartyActivityCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ThirdPartyActivity(
        activityId=_gen_id(), storeId=data.storeId,
        platform=data.platform, activityName=data.activityName,
        activityBudget=data.activityBudget,
        startDate=data.startDate, endDate=data.endDate,
        remark=data.remark,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ThirdPartyActivityOut(
        activityId=item.activityId, storeId=item.storeId, storeName=store_name,
        platform=item.platform, activityName=item.activityName,
        activityBudget=item.activityBudget, actualCost=item.actualCost,
        salesAmount=item.salesAmount, startDate=item.startDate,
        endDate=item.endDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


@router.put("/third-party-activities/{activity_id}", response_model=ThirdPartyActivityOut, dependencies=[Depends(get_current_user)])
async def update_third_party_activity(
    activity_id: str,
    data: ThirdPartyActivityUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ThirdPartyActivity).where(ThirdPartyActivity.activityId == activity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "第三方活动不存在")
    if data.storeId is not None:
        item.storeId = data.storeId
    if data.platform is not None:
        item.platform = data.platform
    if data.activityName is not None:
        item.activityName = data.activityName
    if data.activityBudget is not None:
        item.activityBudget = data.activityBudget
    if data.actualCost is not None:
        item.actualCost = data.actualCost
    if data.salesAmount is not None:
        item.salesAmount = data.salesAmount
    if data.startDate is not None:
        item.startDate = data.startDate
    if data.endDate is not None:
        item.endDate = data.endDate
    if data.status is not None:
        item.status = data.status
    if data.remark is not None:
        item.remark = data.remark
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ThirdPartyActivityOut(
        activityId=item.activityId, storeId=item.storeId, storeName=store_name,
        platform=item.platform, activityName=item.activityName,
        activityBudget=item.activityBudget, actualCost=item.actualCost,
        salesAmount=item.salesAmount, startDate=item.startDate,
        endDate=item.endDate, status=item.status,
        remark=item.remark, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# CampaignEffect 活动效果
# ═══════════════════════════════════════════

@router.get("/campaign-effects", response_model=CampaignEffectListOut)
async def list_campaign_effects(
    campaign_id: Optional[str] = Query(None, alias="campaignId"),
    metric_name: Optional[str] = Query(None, alias="metricName"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CampaignEffect)
    if campaign_id:
        q = q.where(CampaignEffect.campaignId == campaign_id)
    if metric_name:
        q = q.where(CampaignEffect.metricName == metric_name)
    if start_date:
        q = q.where(CampaignEffect.date >= start_date)
    if end_date:
        q = q.where(CampaignEffect.date <= end_date)
    q = q.order_by(CampaignEffect.createdAt.desc())

    count_q = select(func.count(CampaignEffect.effectId)).select_from(CampaignEffect)
    if campaign_id:
        count_q = count_q.where(CampaignEffect.campaignId == campaign_id)
    if metric_name:
        count_q = count_q.where(CampaignEffect.metricName == metric_name)
    if start_date:
        count_q = count_q.where(CampaignEffect.date >= start_date)
    if end_date:
        count_q = count_q.where(CampaignEffect.date <= end_date)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CampaignEffectListOut(
        total=total,
        items=[
            CampaignEffectOut(
                effectId=item.effectId, campaignId=item.campaignId,
                metricName=item.metricName, metricValue=item.metricValue,
                date=item.date, createdAt=item.createdAt,
            )
            for item in items
        ],
        page=page, page_size=page_size,
    )


@router.get("/campaign-effects/{effect_id}", response_model=CampaignEffectOut)
async def get_campaign_effect(effect_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CampaignEffect).where(CampaignEffect.effectId == effect_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "活动效果记录不存在")
    return CampaignEffectOut(
        effectId=item.effectId, campaignId=item.campaignId,
        metricName=item.metricName, metricValue=item.metricValue,
        date=item.date, createdAt=item.createdAt,
    )


@router.post("/campaign-effects", response_model=CampaignEffectOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_campaign_effect(
    data: CampaignEffectCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CampaignEffect(
        effectId=_gen_id(), campaignId=data.campaignId,
        metricName=data.metricName, metricValue=data.metricValue,
        date=data.date,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CampaignEffectOut(
        effectId=item.effectId, campaignId=item.campaignId,
        metricName=item.metricName, metricValue=item.metricValue,
        date=item.date, createdAt=item.createdAt,
    )


@router.put("/campaign-effects/{effect_id}", response_model=CampaignEffectOut, dependencies=[Depends(get_current_user)])
async def update_campaign_effect(
    effect_id: str,
    data: CampaignEffectUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CampaignEffect).where(CampaignEffect.effectId == effect_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "活动效果记录不存在")
    if data.metricName is not None:
        item.metricName = data.metricName
    if data.metricValue is not None:
        item.metricValue = data.metricValue
    if data.date is not None:
        item.date = data.date
    await db.commit()
    await db.refresh(item)
    return CampaignEffectOut(
        effectId=item.effectId, campaignId=item.campaignId,
        metricName=item.metricName, metricValue=item.metricValue,
        date=item.date, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Channel 渠道
# ═══════════════════════════════════════════

@router.get("/channels", response_model=ChannelListOut)
async def list_channels(
    type: Optional[str] = None,
    platform: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Channel)
    if type:
        q = q.where(Channel.type == type)
    if platform:
        q = q.where(Channel.platform == platform)
    if status:
        q = q.where(Channel.status == status)
    q = q.order_by(Channel.createdAt.desc())

    count_q = select(func.count(Channel.channelId)).select_from(Channel)
    if type:
        count_q = count_q.where(Channel.type == type)
    if platform:
        count_q = count_q.where(Channel.platform == platform)
    if status:
        count_q = count_q.where(Channel.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return ChannelListOut(
        total=total,
        items=[
            ChannelOut(
                channelId=item.channelId, name=item.name,
                type=item.type, platform=item.platform,
                commissionRate=item.commissionRate,
                status=item.status, createdAt=item.createdAt,
            )
            for item in items
        ],
        page=page, page_size=page_size,
    )


@router.get("/channels/{channel_id}", response_model=ChannelOut)
async def get_channel(channel_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Channel).where(Channel.channelId == channel_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "渠道不存在")
    return ChannelOut(
        channelId=item.channelId, name=item.name,
        type=item.type, platform=item.platform,
        commissionRate=item.commissionRate,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/channels", response_model=ChannelOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_channel(
    data: ChannelCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Channel(
        channelId=_gen_id(), name=data.name, type=data.type,
        platform=data.platform, commissionRate=data.commissionRate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ChannelOut(
        channelId=item.channelId, name=item.name,
        type=item.type, platform=item.platform,
        commissionRate=item.commissionRate,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/channels/{channel_id}", response_model=ChannelOut, dependencies=[Depends(get_current_user)])
async def update_channel(
    channel_id: str,
    data: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Channel).where(Channel.channelId == channel_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "渠道不存在")
    if data.name is not None:
        item.name = data.name
    if data.type is not None:
        item.type = data.type
    if data.platform is not None:
        item.platform = data.platform
    if data.commissionRate is not None:
        item.commissionRate = data.commissionRate
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return ChannelOut(
        channelId=item.channelId, name=item.name,
        type=item.type, platform=item.platform,
        commissionRate=item.commissionRate,
        status=item.status, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Marketing Analytics Summary 营销分析总览
# ═══════════════════════════════════════════

@router.get("/analytics/summary")
async def marketing_analytics_summary(
    store_id: Optional[str] = Query(None, alias="storeId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated marketing analytics across campaigns, leads, opportunities, coupons, and third-party activities."""
    now = datetime.utcnow()

    # ── Campaign stats ──
    campaign_q = select(
        func.count(Campaign.campaignId),
        func.coalesce(func.sum(Campaign.budget), 0),
        func.coalesce(func.sum(Campaign.usedAmount), 0),
    )
    if store_id:
        campaign_q = campaign_q.where(Campaign.storeId == store_id)
    if start_date:
        campaign_q = campaign_q.where(Campaign.startDate >= start_date)
    if end_date:
        campaign_q = campaign_q.where(Campaign.endDate <= end_date)
    campaign_row = (await db.execute(campaign_q)).one()
    campaign_count = int(campaign_row[0])
    total_budget = float(campaign_row[1])
    total_used = float(campaign_row[2])

    # ── Lead stats by status ──
    lead_status_data = {}
    for status_val in ["New", "Contacted", "Converted", "Abandoned"]:
        q = select(func.count(Lead.leadId)).where(Lead.status == status_val)
        if store_id:
            q = q.where(Lead.storeId == store_id)
        if start_date:
            q = q.where(Lead.createdAt >= start_date)
        if end_date:
            q = q.where(Lead.createdAt <= end_date + " 23:59:59")
        cnt = (await db.execute(q)).scalar() or 0
        lead_status_data[status_val] = cnt

    # Total leads
    total_leads_q = select(func.count(Lead.leadId))
    if store_id:
        total_leads_q = total_leads_q.where(Lead.storeId == store_id)
    if start_date:
        total_leads_q = total_leads_q.where(Lead.createdAt >= start_date)
    if end_date:
        total_leads_q = total_leads_q.where(Lead.createdAt <= end_date + " 23:59:59")
    total_leads = (await db.execute(total_leads_q)).scalar() or 0

    # ── Opportunity stats ──
    opp_q = select(
        func.count(Opportunity.opportunityId),
        func.coalesce(func.sum(Opportunity.expectedAmount), 0),
    )
    if store_id:
        opp_q = opp_q.where(Opportunity.storeId == store_id)
    if start_date:
        opp_q = opp_q.where(Opportunity.createdAt >= start_date)
    if end_date:
        opp_q = opp_q.where(Opportunity.createdAt <= end_date + " 23:59:59")
    opp_row = (await db.execute(opp_q)).one()
    total_opportunities = int(opp_row[0])
    total_expected_amount = float(opp_row[1])

    # Won opportunities amount
    won_q = select(func.coalesce(func.sum(Opportunity.expectedAmount), 0)).where(
        Opportunity.status == "Won"
    )
    if store_id:
        won_q = won_q.where(Opportunity.storeId == store_id)
    if start_date:
        won_q = won_q.where(Opportunity.createdAt >= start_date)
    if end_date:
        won_q = won_q.where(Opportunity.createdAt <= end_date + " 23:59:59")
    won_amount = (await db.execute(won_q)).scalar() or 0

    # ── Coupon stats ──
    total_coupons_q = select(func.count(Coupon.couponId))
    if start_date:
        total_coupons_q = total_coupons_q.where(Coupon.createdAt >= start_date)
    if end_date:
        total_coupons_q = total_coupons_q.where(Coupon.createdAt <= end_date + " 23:59:59")
    total_coupons = (await db.execute(total_coupons_q)).scalar() or 0

    used_coupons_q = select(func.count(Coupon.couponId)).where(Coupon.status == "Used")
    if start_date:
        used_coupons_q = used_coupons_q.where(Coupon.createdAt >= start_date)
    if end_date:
        used_coupons_q = used_coupons_q.where(Coupon.createdAt <= end_date + " 23:59:59")
    used_coupons = (await db.execute(used_coupons_q)).scalar() or 0

    # ── Third-party activity stats ──
    tpa_q = select(
        func.count(ThirdPartyActivity.activityId),
        func.coalesce(func.sum(ThirdPartyActivity.actualCost), 0),
        func.coalesce(func.sum(ThirdPartyActivity.salesAmount), 0),
    )
    if store_id:
        tpa_q = tpa_q.where(ThirdPartyActivity.storeId == store_id)
    if start_date:
        tpa_q = tpa_q.where(ThirdPartyActivity.startDate >= start_date)
    if end_date:
        tpa_q = tpa_q.where(ThirdPartyActivity.endDate <= end_date)
    tpa_row = (await db.execute(tpa_q)).one()
    tpa_count = int(tpa_row[0])
    tpa_total_cost = float(tpa_row[1])
    tpa_total_sales = float(tpa_row[2])

    return {
        "campaigns": {
            "total": campaign_count,
            "totalBudget": total_budget,
            "totalUsed": total_used,
            "budgetUtilization": round(total_used / total_budget * 100, 2) if total_budget > 0 else 0,
        },
        "leads": {
            "total": total_leads,
            "byStatus": lead_status_data,
        },
        "opportunities": {
            "total": total_opportunities,
            "totalExpectedAmount": total_expected_amount,
            "wonAmount": won_amount,
        },
        "coupons": {
            "totalIssued": total_coupons,
            "totalUsed": used_coupons,
            "redemptionRate": round(used_coupons / total_coupons * 100, 2) if total_coupons > 0 else 0,
        },
        "thirdPartyActivities": {
            "total": tpa_count,
            "totalCost": tpa_total_cost,
            "totalSales": tpa_total_sales,
            "roi": round((tpa_total_sales - tpa_total_cost) / tpa_total_cost * 100, 2) if tpa_total_cost > 0 else 0,
        },
        "reportPeriod": {
            "startDate": start_date,
            "endDate": end_date,
        },
    }
