"""门店拓展管理 API — D02 剩余实体 CRUD"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from database import get_db
from services.auth_service import get_current_user, get_optional_user
from models.store_dev import (
    LegalEntity, Territory, StoreSiteSelection, StoreConstruction,
    ConstructionCost, DesignDrawing, RoomPricing, RoomPersonPricing,
    TimeSlotCoefficient, HolidayCalendar, ActivityCalendar,
    DurationDiscountRule, NightPackage, Store,
)
from schemas.store_dev import (
    LegalEntityCreate, LegalEntityUpdate, LegalEntityOut, LegalEntityListOut,
    TerritoryCreate, TerritoryUpdate, TerritoryOut, TerritoryListOut,
    StoreSiteSelectionCreate, StoreSiteSelectionUpdate, StoreSiteSelectionOut, StoreSiteSelectionListOut,
    StoreConstructionCreate, StoreConstructionUpdate, StoreConstructionOut, StoreConstructionListOut,
    ConstructionCostCreate, ConstructionCostUpdate, ConstructionCostOut, ConstructionCostListOut,
    DesignDrawingCreate, DesignDrawingUpdate, DesignDrawingOut, DesignDrawingListOut,
    RoomPricingCreate, RoomPricingUpdate, RoomPricingOut, RoomPricingListOut,
    RoomPersonPricingCreate, RoomPersonPricingUpdate, RoomPersonPricingOut, RoomPersonPricingListOut,
    TimeSlotCoefficientCreate, TimeSlotCoefficientUpdate, TimeSlotCoefficientOut, TimeSlotCoefficientListOut,
    HolidayCalendarCreate, HolidayCalendarUpdate, HolidayCalendarOut, HolidayCalendarListOut,
    ActivityCalendarCreate, ActivityCalendarUpdate, ActivityCalendarOut, ActivityCalendarListOut,
    DurationDiscountRuleCreate, DurationDiscountRuleUpdate, DurationDiscountRuleOut, DurationDiscountRuleListOut,
    NightPackageCreate, NightPackageUpdate, NightPackageOut, NightPackageListOut,
)

router = APIRouter(prefix="/api/store-dev", tags=["门店拓展管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


async def _resolve_store_name(db: AsyncSession, store_id: str) -> Optional[str]:
    if not store_id:
        return None
    r = await db.execute(select(Store.name).where(Store.storeId == store_id))
    return r.scalar_one_or_none()


# ═══════════════════════════════════════════
# LegalEntity 法律主体
# ═══════════════════════════════════════════

@router.get("/legal-entities", response_model=LegalEntityListOut, dependencies=[Depends(get_optional_user)])
async def list_legal_entities(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(LegalEntity)
    if status:
        q = q.where(LegalEntity.status == status)
    if search:
        q = q.where(LegalEntity.name.contains(search))
    q = q.order_by(LegalEntity.id.desc())

    count_q = select(func.count(LegalEntity.legalEntityId)).select_from(LegalEntity)
    if status:
        count_q = count_q.where(LegalEntity.status == status)
    if search:
        count_q = count_q.where(LegalEntity.name.contains(search))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return LegalEntityListOut(
        total=total,
        items=[LegalEntityOut(
            legalEntityId=item.legalEntityId, name=item.name, type=item.type,
            creditCode=item.creditCode, legalRep=item.legalRep,
            registeredCapital=item.registeredCapital, registeredAddress=item.registeredAddress,
            businessScope=item.businessScope, establishedDate=item.establishedDate,
            status=item.status,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/legal-entities/{legal_entity_id}", response_model=LegalEntityOut, dependencies=[Depends(get_optional_user)])
async def get_legal_entity(legal_entity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(LegalEntity).where(LegalEntity.legalEntityId == legal_entity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "法律主体不存在")
    return LegalEntityOut(
        legalEntityId=item.legalEntityId, name=item.name, type=item.type,
        creditCode=item.creditCode, legalRep=item.legalRep,
        registeredCapital=item.registeredCapital, registeredAddress=item.registeredAddress,
        businessScope=item.businessScope, establishedDate=item.establishedDate,
        status=item.status,
    )


@router.post("/legal-entities", response_model=LegalEntityOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_legal_entity(
    data: LegalEntityCreate,
    db: AsyncSession = Depends(get_db),
):
    if data.creditCode:
        exist = await db.execute(select(LegalEntity).where(LegalEntity.creditCode == data.creditCode))
        if exist.scalar_one_or_none():
            raise HTTPException(409, "统一社会信用代码已存在")
    item = LegalEntity(
        legalEntityId=_gen_id(), name=data.name, type=data.type,
        creditCode=data.creditCode, legalRep=data.legalRep,
        registeredCapital=data.registeredCapital, registeredAddress=data.registeredAddress,
        businessScope=data.businessScope, establishedDate=data.establishedDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return LegalEntityOut(
        legalEntityId=item.legalEntityId, name=item.name, type=item.type,
        creditCode=item.creditCode, legalRep=item.legalRep,
        registeredCapital=item.registeredCapital, registeredAddress=item.registeredAddress,
        businessScope=item.businessScope, establishedDate=item.establishedDate,
        status=item.status,
    )


@router.put("/legal-entities/{legal_entity_id}", response_model=LegalEntityOut, dependencies=[Depends(get_current_user)])
async def update_legal_entity(
    legal_entity_id: str,
    data: LegalEntityUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(LegalEntity).where(LegalEntity.legalEntityId == legal_entity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "法律主体不存在")
    if data.name is not None:
        item.name = data.name
    if data.type is not None:
        item.type = data.type
    if data.creditCode is not None:
        item.creditCode = data.creditCode
    if data.legalRep is not None:
        item.legalRep = data.legalRep
    if data.registeredCapital is not None:
        item.registeredCapital = data.registeredCapital
    if data.registeredAddress is not None:
        item.registeredAddress = data.registeredAddress
    if data.businessScope is not None:
        item.businessScope = data.businessScope
    if data.establishedDate is not None:
        item.establishedDate = data.establishedDate
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return LegalEntityOut(
        legalEntityId=item.legalEntityId, name=item.name, type=item.type,
        creditCode=item.creditCode, legalRep=item.legalRep,
        registeredCapital=item.registeredCapital, registeredAddress=item.registeredAddress,
        businessScope=item.businessScope, establishedDate=item.establishedDate,
        status=item.status,
    )


@router.delete("/legal-entities/{legal_entity_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_legal_entity(legal_entity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(LegalEntity).where(LegalEntity.legalEntityId == legal_entity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "法律主体不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# Territory 行政区划
# ═══════════════════════════════════════════

@router.get("/territories", response_model=TerritoryListOut, dependencies=[Depends(get_optional_user)])
async def list_territories(
    parent_id: Optional[str] = Query(None, alias="parentId"),
    level: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Territory)
    if parent_id:
        q = q.where(Territory.parentId == parent_id)
    if level is not None:
        q = q.where(Territory.level == level)
    if status:
        q = q.where(Territory.status == status)
    q = q.order_by(Territory.id.desc())

    count_q = select(func.count(Territory.territoryId)).select_from(Territory)
    if parent_id:
        count_q = count_q.where(Territory.parentId == parent_id)
    if level is not None:
        count_q = count_q.where(Territory.level == level)
    if status:
        count_q = count_q.where(Territory.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return TerritoryListOut(
        total=total,
        items=[TerritoryOut(
            territoryId=item.territoryId, parentId=item.parentId,
            name=item.name, level=item.level, status=item.status,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/territories/{territory_id}", response_model=TerritoryOut, dependencies=[Depends(get_optional_user)])
async def get_territory(territory_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Territory).where(Territory.territoryId == territory_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "行政区划不存在")
    return TerritoryOut(
        territoryId=item.territoryId, parentId=item.parentId,
        name=item.name, level=item.level, status=item.status,
    )


@router.post("/territories", response_model=TerritoryOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_territory(
    data: TerritoryCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Territory(
        territoryId=_gen_id(), parentId=data.parentId,
        name=data.name, level=data.level,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return TerritoryOut(
        territoryId=item.territoryId, parentId=item.parentId,
        name=item.name, level=item.level, status=item.status,
    )


@router.put("/territories/{territory_id}", response_model=TerritoryOut, dependencies=[Depends(get_current_user)])
async def update_territory(
    territory_id: str,
    data: TerritoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Territory).where(Territory.territoryId == territory_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "行政区划不存在")
    if data.name is not None:
        item.name = data.name
    if data.level is not None:
        item.level = data.level
    if data.parentId is not None:
        item.parentId = data.parentId
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return TerritoryOut(
        territoryId=item.territoryId, parentId=item.parentId,
        name=item.name, level=item.level, status=item.status,
    )


@router.delete("/territories/{territory_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_territory(territory_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Territory).where(Territory.territoryId == territory_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "行政区划不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# StoreSiteSelection 门店选址
# ═══════════════════════════════════════════

@router.get("/site-selections", response_model=StoreSiteSelectionListOut, dependencies=[Depends(get_optional_user)])
async def list_site_selections(
    source: Optional[str] = None,
    approval_status: Optional[str] = Query(None, alias="approvalStatus"),
    submitted_by: Optional[str] = Query(None, alias="submittedBy"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(StoreSiteSelection)
    if source:
        q = q.where(StoreSiteSelection.source == source)
    if approval_status:
        q = q.where(StoreSiteSelection.approvalStatus == approval_status)
    if submitted_by:
        q = q.where(StoreSiteSelection.submittedBy == submitted_by)
    q = q.order_by(StoreSiteSelection.createdAt.desc())

    count_q = select(func.count(StoreSiteSelection.selectionId)).select_from(StoreSiteSelection)
    if source:
        count_q = count_q.where(StoreSiteSelection.source == source)
    if approval_status:
        count_q = count_q.where(StoreSiteSelection.approvalStatus == approval_status)
    if submitted_by:
        count_q = count_q.where(StoreSiteSelection.submittedBy == submitted_by)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        result_store_name = None
        if item.resultStoreId:
            result_store_name = await _resolve_store_name(db, item.resultStoreId)
        result.append(StoreSiteSelectionOut(
            selectionId=item.selectionId, source=item.source,
            region=item.region, address=item.address, area=item.area,
            rent=item.rent, environmentAssessment=item.environmentAssessment,
            recommendationReason=item.recommendationReason,
            investorFeedback=item.investorFeedback,
            investorConfirmed=item.investorConfirmed,
            investorAmount=item.investorAmount,
            approvalStatus=item.approvalStatus, approvalFlowId=item.approvalFlowId,
            resultStoreId=item.resultStoreId, resultStoreName=result_store_name,
            submittedBy=item.submittedBy, createdAt=item.createdAt,
        ))
    return StoreSiteSelectionListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/site-selections/{selection_id}", response_model=StoreSiteSelectionOut, dependencies=[Depends(get_optional_user)])
async def get_site_selection(selection_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(StoreSiteSelection).where(StoreSiteSelection.selectionId == selection_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "选址记录不存在")
    result_store_name = None
    if item.resultStoreId:
        result_store_name = await _resolve_store_name(db, item.resultStoreId)
    return StoreSiteSelectionOut(
        selectionId=item.selectionId, source=item.source,
        region=item.region, address=item.address, area=item.area,
        rent=item.rent, environmentAssessment=item.environmentAssessment,
        recommendationReason=item.recommendationReason,
        investorFeedback=item.investorFeedback,
        investorConfirmed=item.investorConfirmed,
        investorAmount=item.investorAmount,
        approvalStatus=item.approvalStatus, approvalFlowId=item.approvalFlowId,
        resultStoreId=item.resultStoreId, resultStoreName=result_store_name,
        submittedBy=item.submittedBy, createdAt=item.createdAt,
    )


@router.post("/site-selections", response_model=StoreSiteSelectionOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_site_selection(
    data: StoreSiteSelectionCreate,
    db: AsyncSession = Depends(get_db),
):
    item = StoreSiteSelection(
        selectionId=_gen_id(), source=data.source, region=data.region,
        address=data.address, area=data.area, rent=data.rent,
        environmentAssessment=data.environmentAssessment,
        recommendationReason=data.recommendationReason,
        investorFeedback=data.investorFeedback,
        investorConfirmed=data.investorConfirmed or False,
        investorAmount=data.investorAmount,
        approvalFlowId=data.approvalFlowId,
        resultStoreId=data.resultStoreId,
        submittedBy=data.submittedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    result_store_name = None
    if item.resultStoreId:
        result_store_name = await _resolve_store_name(db, item.resultStoreId)
    return StoreSiteSelectionOut(
        selectionId=item.selectionId, source=item.source,
        region=item.region, address=item.address, area=item.area,
        rent=item.rent, environmentAssessment=item.environmentAssessment,
        recommendationReason=item.recommendationReason,
        investorFeedback=item.investorFeedback,
        investorConfirmed=item.investorConfirmed,
        investorAmount=item.investorAmount,
        approvalStatus=item.approvalStatus, approvalFlowId=item.approvalFlowId,
        resultStoreId=item.resultStoreId, resultStoreName=result_store_name,
        submittedBy=item.submittedBy, createdAt=item.createdAt,
    )


@router.put("/site-selections/{selection_id}", response_model=StoreSiteSelectionOut, dependencies=[Depends(get_current_user)])
async def update_site_selection(
    selection_id: str,
    data: StoreSiteSelectionUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(StoreSiteSelection).where(StoreSiteSelection.selectionId == selection_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "选址记录不存在")
    if data.source is not None:
        item.source = data.source
    if data.region is not None:
        item.region = data.region
    if data.address is not None:
        item.address = data.address
    if data.area is not None:
        item.area = data.area
    if data.rent is not None:
        item.rent = data.rent
    if data.environmentAssessment is not None:
        item.environmentAssessment = data.environmentAssessment
    if data.recommendationReason is not None:
        item.recommendationReason = data.recommendationReason
    if data.investorFeedback is not None:
        item.investorFeedback = data.investorFeedback
    if data.investorConfirmed is not None:
        item.investorConfirmed = data.investorConfirmed
    if data.investorAmount is not None:
        item.investorAmount = data.investorAmount
    if data.approvalStatus is not None:
        item.approvalStatus = data.approvalStatus
    if data.approvalFlowId is not None:
        item.approvalFlowId = data.approvalFlowId
    if data.resultStoreId is not None:
        item.resultStoreId = data.resultStoreId
    await db.commit()
    await db.refresh(item)
    result_store_name = None
    if item.resultStoreId:
        result_store_name = await _resolve_store_name(db, item.resultStoreId)
    return StoreSiteSelectionOut(
        selectionId=item.selectionId, source=item.source,
        region=item.region, address=item.address, area=item.area,
        rent=item.rent, environmentAssessment=item.environmentAssessment,
        recommendationReason=item.recommendationReason,
        investorFeedback=item.investorFeedback,
        investorConfirmed=item.investorConfirmed,
        investorAmount=item.investorAmount,
        approvalStatus=item.approvalStatus, approvalFlowId=item.approvalFlowId,
        resultStoreId=item.resultStoreId, resultStoreName=result_store_name,
        submittedBy=item.submittedBy, createdAt=item.createdAt,
    )


@router.delete("/site-selections/{selection_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_site_selection(selection_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(StoreSiteSelection).where(StoreSiteSelection.selectionId == selection_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "选址记录不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# StoreConstruction 门店建设
# ═══════════════════════════════════════════

@router.get("/constructions", response_model=StoreConstructionListOut, dependencies=[Depends(get_optional_user)])
async def list_constructions(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(StoreConstruction)
    if store_id:
        q = q.where(StoreConstruction.storeId == store_id)
    if status:
        q = q.where(StoreConstruction.status == status)
    q = q.order_by(StoreConstruction.id.desc())

    count_q = select(func.count(StoreConstruction.constructionId)).select_from(StoreConstruction)
    if store_id:
        count_q = count_q.where(StoreConstruction.storeId == store_id)
    if status:
        count_q = count_q.where(StoreConstruction.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(StoreConstructionOut(
            constructionId=item.constructionId, storeId=item.storeId,
            storeName=store_name,
            planStartDate=item.planStartDate, planEndDate=item.planEndDate,
            actualStartDate=item.actualStartDate, actualEndDate=item.actualEndDate,
            totalCost=item.totalCost, status=item.status,
            sealedAt=item.sealedAt, sealedBy=item.sealedBy,
        ))
    return StoreConstructionListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/constructions/{construction_id}", response_model=StoreConstructionOut, dependencies=[Depends(get_optional_user)])
async def get_construction(construction_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(StoreConstruction).where(StoreConstruction.constructionId == construction_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设记录不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return StoreConstructionOut(
        constructionId=item.constructionId, storeId=item.storeId,
        storeName=store_name,
        planStartDate=item.planStartDate, planEndDate=item.planEndDate,
        actualStartDate=item.actualStartDate, actualEndDate=item.actualEndDate,
        totalCost=item.totalCost, status=item.status,
        sealedAt=item.sealedAt, sealedBy=item.sealedBy,
    )


@router.post("/constructions", response_model=StoreConstructionOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_construction(
    data: StoreConstructionCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify store exists
    sr = await db.execute(select(Store.storeId).where(Store.storeId == data.storeId))
    if not sr.scalar_one_or_none():
        raise HTTPException(404, "门店不存在")
    item = StoreConstruction(
        constructionId=_gen_id(), storeId=data.storeId,
        planStartDate=data.planStartDate, planEndDate=data.planEndDate,
        actualStartDate=data.actualStartDate, actualEndDate=data.actualEndDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return StoreConstructionOut(
        constructionId=item.constructionId, storeId=item.storeId,
        storeName=store_name,
        planStartDate=item.planStartDate, planEndDate=item.planEndDate,
        actualStartDate=item.actualStartDate, actualEndDate=item.actualEndDate,
        totalCost=item.totalCost, status=item.status,
        sealedAt=item.sealedAt, sealedBy=item.sealedBy,
    )


@router.put("/constructions/{construction_id}", response_model=StoreConstructionOut, dependencies=[Depends(get_current_user)])
async def update_construction(
    construction_id: str,
    data: StoreConstructionUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(StoreConstruction).where(StoreConstruction.constructionId == construction_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设记录不存在")
    if data.planStartDate is not None:
        item.planStartDate = data.planStartDate
    if data.planEndDate is not None:
        item.planEndDate = data.planEndDate
    if data.actualStartDate is not None:
        item.actualStartDate = data.actualStartDate
    if data.actualEndDate is not None:
        item.actualEndDate = data.actualEndDate
    if data.totalCost is not None:
        item.totalCost = data.totalCost
    if data.status is not None:
        item.status = data.status
    if data.sealedBy is not None:
        item.sealedBy = data.sealedBy
        if data.status == "Sealed":
            from datetime import datetime
            item.sealedAt = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return StoreConstructionOut(
        constructionId=item.constructionId, storeId=item.storeId,
        storeName=store_name,
        planStartDate=item.planStartDate, planEndDate=item.planEndDate,
        actualStartDate=item.actualStartDate, actualEndDate=item.actualEndDate,
        totalCost=item.totalCost, status=item.status,
        sealedAt=item.sealedAt, sealedBy=item.sealedBy,
    )


@router.delete("/constructions/{construction_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_construction(construction_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(StoreConstruction).where(StoreConstruction.constructionId == construction_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设记录不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# ConstructionCost 建设成本
# ═══════════════════════════════════════════

@router.get("/construction-costs", response_model=ConstructionCostListOut, dependencies=[Depends(get_optional_user)])
async def list_construction_costs(
    construction_id: Optional[str] = Query(None, alias="constructionId"),
    category: Optional[str] = None,
    supplier_id: Optional[str] = Query(None, alias="supplierId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ConstructionCost)
    if construction_id:
        q = q.where(ConstructionCost.constructionId == construction_id)
    if category:
        q = q.where(ConstructionCost.category == category)
    if supplier_id:
        q = q.where(ConstructionCost.supplierId == supplier_id)
    q = q.order_by(ConstructionCost.incurredDate.desc())

    count_q = select(func.coalesce(func.sum(ConstructionCost.amount), 0))
    if construction_id:
        count_q = count_q.where(ConstructionCost.constructionId == construction_id)
    if category:
        count_q = count_q.where(ConstructionCost.category == category)
    if supplier_id:
        count_q = count_q.where(ConstructionCost.supplierId == supplier_id)
    total_sum = (await db.execute(count_q)).scalar() or 0

    count_rows_q = select(func.count(ConstructionCost.costId)).select_from(ConstructionCost)
    if construction_id:
        count_rows_q = count_rows_q.where(ConstructionCost.constructionId == construction_id)
    if category:
        count_rows_q = count_rows_q.where(ConstructionCost.category == category)
    if supplier_id:
        count_rows_q = count_rows_q.where(ConstructionCost.supplierId == supplier_id)
    total_rows = (await db.execute(count_rows_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return ConstructionCostListOut(
        total=total_sum,
        items=[ConstructionCostOut(
            costId=item.costId, constructionId=item.constructionId,
            category=item.category, description=item.description,
            amount=item.amount, supplierId=item.supplierId,
            voucherUrl=item.voucherUrl, incurredDate=item.incurredDate,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/construction-costs/{cost_id}", response_model=ConstructionCostOut, dependencies=[Depends(get_optional_user)])
async def get_construction_cost(cost_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ConstructionCost).where(ConstructionCost.costId == cost_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设成本记录不存在")
    return ConstructionCostOut(
        costId=item.costId, constructionId=item.constructionId,
        category=item.category, description=item.description,
        amount=item.amount, supplierId=item.supplierId,
        voucherUrl=item.voucherUrl, incurredDate=item.incurredDate,
    )


@router.post("/construction-costs", response_model=ConstructionCostOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_construction_cost(
    data: ConstructionCostCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify construction exists
    cr = await db.execute(select(StoreConstruction.constructionId).where(
        StoreConstruction.constructionId == data.constructionId))
    if not cr.scalar_one_or_none():
        raise HTTPException(404, "建设记录不存在")
    item = ConstructionCost(
        costId=_gen_id(), constructionId=data.constructionId,
        category=data.category, description=data.description,
        amount=data.amount, supplierId=data.supplierId,
        voucherUrl=data.voucherUrl, incurredDate=data.incurredDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ConstructionCostOut(
        costId=item.costId, constructionId=item.constructionId,
        category=item.category, description=item.description,
        amount=item.amount, supplierId=item.supplierId,
        voucherUrl=item.voucherUrl, incurredDate=item.incurredDate,
    )


@router.put("/construction-costs/{cost_id}", response_model=ConstructionCostOut, dependencies=[Depends(get_current_user)])
async def update_construction_cost(
    cost_id: str,
    data: ConstructionCostUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ConstructionCost).where(ConstructionCost.costId == cost_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设成本记录不存在")
    if data.category is not None:
        item.category = data.category
    if data.description is not None:
        item.description = data.description
    if data.amount is not None:
        item.amount = data.amount
    if data.supplierId is not None:
        item.supplierId = data.supplierId
    if data.voucherUrl is not None:
        item.voucherUrl = data.voucherUrl
    if data.incurredDate is not None:
        item.incurredDate = data.incurredDate
    await db.commit()
    await db.refresh(item)
    return ConstructionCostOut(
        costId=item.costId, constructionId=item.constructionId,
        category=item.category, description=item.description,
        amount=item.amount, supplierId=item.supplierId,
        voucherUrl=item.voucherUrl, incurredDate=item.incurredDate,
    )


@router.delete("/construction-costs/{cost_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_construction_cost(cost_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ConstructionCost).where(ConstructionCost.costId == cost_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "建设成本记录不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# DesignDrawing 设计图纸
# ═══════════════════════════════════════════

@router.get("/drawings", response_model=DesignDrawingListOut, dependencies=[Depends(get_optional_user)])
async def list_drawings(
    store_id: Optional[str] = Query(None, alias="storeId"),
    construction_id: Optional[str] = Query(None, alias="constructionId"),
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(DesignDrawing)
    if store_id:
        q = q.where(DesignDrawing.storeId == store_id)
    if construction_id:
        q = q.where(DesignDrawing.constructionId == construction_id)
    if type:
        q = q.where(DesignDrawing.type == type)
    if status:
        q = q.where(DesignDrawing.status == status)
    q = q.order_by(DesignDrawing.id.desc())

    count_q = select(func.count(DesignDrawing.drawingId)).select_from(DesignDrawing)
    if store_id:
        count_q = count_q.where(DesignDrawing.storeId == store_id)
    if construction_id:
        count_q = count_q.where(DesignDrawing.constructionId == construction_id)
    if type:
        count_q = count_q.where(DesignDrawing.type == type)
    if status:
        count_q = count_q.where(DesignDrawing.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(DesignDrawingOut(
            drawingId=item.drawingId, storeId=item.storeId,
            storeName=store_name,
            constructionId=item.constructionId, type=item.type,
            name=item.name, fileName=item.fileName,
            fileFormat=item.fileFormat, version=item.version,
            status=item.status, uploadedBy=item.uploadedBy,
            approvedBy=item.approvedBy,
        ))
    return DesignDrawingListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/drawings/{drawing_id}", response_model=DesignDrawingOut, dependencies=[Depends(get_optional_user)])
async def get_drawing(drawing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DesignDrawing).where(DesignDrawing.drawingId == drawing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "图纸不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return DesignDrawingOut(
        drawingId=item.drawingId, storeId=item.storeId,
        storeName=store_name,
        constructionId=item.constructionId, type=item.type,
        name=item.name, fileName=item.fileName,
        fileFormat=item.fileFormat, version=item.version,
        status=item.status, uploadedBy=item.uploadedBy,
        approvedBy=item.approvedBy,
    )


@router.post("/drawings", response_model=DesignDrawingOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_drawing(
    data: DesignDrawingCreate,
    db: AsyncSession = Depends(get_db),
):
    # Verify store exists
    sr = await db.execute(select(Store.storeId).where(Store.storeId == data.storeId))
    if not sr.scalar_one_or_none():
        raise HTTPException(404, "门店不存在")
    if data.constructionId:
        cr = await db.execute(select(StoreConstruction.constructionId).where(
            StoreConstruction.constructionId == data.constructionId))
        if not cr.scalar_one_or_none():
            raise HTTPException(404, "建设记录不存在")
    item = DesignDrawing(
        drawingId=_gen_id(), storeId=data.storeId,
        constructionId=data.constructionId, type=data.type,
        name=data.name, fileName=data.fileName,
        fileFormat=data.fileFormat, version=data.version,
        uploadedBy=data.uploadedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return DesignDrawingOut(
        drawingId=item.drawingId, storeId=item.storeId,
        storeName=store_name,
        constructionId=item.constructionId, type=item.type,
        name=item.name, fileName=item.fileName,
        fileFormat=item.fileFormat, version=item.version,
        status=item.status, uploadedBy=item.uploadedBy,
        approvedBy=item.approvedBy,
    )


@router.put("/drawings/{drawing_id}", response_model=DesignDrawingOut, dependencies=[Depends(get_current_user)])
async def update_drawing(
    drawing_id: str,
    data: DesignDrawingUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(DesignDrawing).where(DesignDrawing.drawingId == drawing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "图纸不存在")
    if data.type is not None:
        item.type = data.type
    if data.name is not None:
        item.name = data.name
    if data.fileName is not None:
        item.fileName = data.fileName
    if data.fileFormat is not None:
        item.fileFormat = data.fileFormat
    if data.version is not None:
        item.version = data.version
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return DesignDrawingOut(
        drawingId=item.drawingId, storeId=item.storeId,
        storeName=store_name,
        constructionId=item.constructionId, type=item.type,
        name=item.name, fileName=item.fileName,
        fileFormat=item.fileFormat, version=item.version,
        status=item.status, uploadedBy=item.uploadedBy,
        approvedBy=item.approvedBy,
    )


@router.delete("/drawings/{drawing_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_drawing(drawing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DesignDrawing).where(DesignDrawing.drawingId == drawing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "图纸不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# RoomPricing 房间定价
# ═══════════════════════════════════════════

@router.get("/room-pricings", response_model=RoomPricingListOut, dependencies=[Depends(get_optional_user)])
async def list_room_pricings(
    room_id: Optional[str] = Query(None, alias="roomId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RoomPricing)
    if room_id:
        q = q.where(RoomPricing.roomId == room_id)
    if status:
        q = q.where(RoomPricing.status == status)
    q = q.order_by(RoomPricing.id.desc())

    count_q = select(func.count(RoomPricing.pricingId)).select_from(RoomPricing)
    if room_id:
        count_q = count_q.where(RoomPricing.roomId == room_id)
    if status:
        count_q = count_q.where(RoomPricing.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return RoomPricingListOut(
        total=total,
        items=[RoomPricingOut(
            pricingId=item.pricingId, roomId=item.roomId,
            basePrice=item.basePrice, unit=item.unit,
            effectiveDate=item.effectiveDate, expiryDate=item.expiryDate,
            status=item.status,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/room-pricings/{pricing_id}", response_model=RoomPricingOut, dependencies=[Depends(get_optional_user)])
async def get_room_pricing(pricing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomPricing).where(RoomPricing.pricingId == pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间定价不存在")
    return RoomPricingOut(
        pricingId=item.pricingId, roomId=item.roomId,
        basePrice=item.basePrice, unit=item.unit,
        effectiveDate=item.effectiveDate, expiryDate=item.expiryDate,
        status=item.status,
    )


@router.post("/room-pricings", response_model=RoomPricingOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_room_pricing(
    data: RoomPricingCreate,
    db: AsyncSession = Depends(get_db),
):
    item = RoomPricing(
        pricingId=_gen_id(), roomId=data.roomId,
        basePrice=data.basePrice, unit=data.unit,
        effectiveDate=data.effectiveDate, expiryDate=data.expiryDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RoomPricingOut(
        pricingId=item.pricingId, roomId=item.roomId,
        basePrice=item.basePrice, unit=item.unit,
        effectiveDate=item.effectiveDate, expiryDate=item.expiryDate,
        status=item.status,
    )


@router.put("/room-pricings/{pricing_id}", response_model=RoomPricingOut, dependencies=[Depends(get_current_user)])
async def update_room_pricing(
    pricing_id: str,
    data: RoomPricingUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RoomPricing).where(RoomPricing.pricingId == pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间定价不存在")
    if data.basePrice is not None:
        item.basePrice = data.basePrice
    if data.unit is not None:
        item.unit = data.unit
    if data.effectiveDate is not None:
        item.effectiveDate = data.effectiveDate
    if data.expiryDate is not None:
        item.expiryDate = data.expiryDate
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return RoomPricingOut(
        pricingId=item.pricingId, roomId=item.roomId,
        basePrice=item.basePrice, unit=item.unit,
        effectiveDate=item.effectiveDate, expiryDate=item.expiryDate,
        status=item.status,
    )


@router.delete("/room-pricings/{pricing_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_room_pricing(pricing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomPricing).where(RoomPricing.pricingId == pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间定价不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# RoomPersonPricing 房间按人定价
# ═══════════════════════════════════════════

@router.get("/room-person-pricings", response_model=RoomPersonPricingListOut, dependencies=[Depends(get_optional_user)])
async def list_room_person_pricings(
    room_id: Optional[str] = Query(None, alias="roomId"),
    person_count: Optional[int] = Query(None, alias="personCount"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RoomPersonPricing)
    if room_id:
        q = q.where(RoomPersonPricing.roomId == room_id)
    if person_count is not None:
        q = q.where(RoomPersonPricing.personCount == person_count)
    if status:
        q = q.where(RoomPersonPricing.status == status)
    q = q.order_by(RoomPersonPricing.id.desc())

    count_q = select(func.count(RoomPersonPricing.personPricingId)).select_from(RoomPersonPricing)
    if room_id:
        count_q = count_q.where(RoomPersonPricing.roomId == room_id)
    if person_count is not None:
        count_q = count_q.where(RoomPersonPricing.personCount == person_count)
    if status:
        count_q = count_q.where(RoomPersonPricing.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return RoomPersonPricingListOut(
        total=total,
        items=[RoomPersonPricingOut(
            personPricingId=item.personPricingId, roomId=item.roomId,
            personCount=item.personCount, pricePerHour=item.pricePerHour,
            status=item.status,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/room-person-pricings/{person_pricing_id}", response_model=RoomPersonPricingOut, dependencies=[Depends(get_optional_user)])
async def get_room_person_pricing(person_pricing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomPersonPricing).where(RoomPersonPricing.personPricingId == person_pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间按人定价不存在")
    return RoomPersonPricingOut(
        personPricingId=item.personPricingId, roomId=item.roomId,
        personCount=item.personCount, pricePerHour=item.pricePerHour,
        status=item.status,
    )


@router.post("/room-person-pricings", response_model=RoomPersonPricingOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_room_person_pricing(
    data: RoomPersonPricingCreate,
    db: AsyncSession = Depends(get_db),
):
    item = RoomPersonPricing(
        personPricingId=_gen_id(), roomId=data.roomId,
        personCount=data.personCount, pricePerHour=data.pricePerHour,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RoomPersonPricingOut(
        personPricingId=item.personPricingId, roomId=item.roomId,
        personCount=item.personCount, pricePerHour=item.pricePerHour,
        status=item.status,
    )


@router.put("/room-person-pricings/{person_pricing_id}", response_model=RoomPersonPricingOut, dependencies=[Depends(get_current_user)])
async def update_room_person_pricing(
    person_pricing_id: str,
    data: RoomPersonPricingUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RoomPersonPricing).where(RoomPersonPricing.personPricingId == person_pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间按人定价不存在")
    if data.personCount is not None:
        item.personCount = data.personCount
    if data.pricePerHour is not None:
        item.pricePerHour = data.pricePerHour
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return RoomPersonPricingOut(
        personPricingId=item.personPricingId, roomId=item.roomId,
        personCount=item.personCount, pricePerHour=item.pricePerHour,
        status=item.status,
    )


@router.delete("/room-person-pricings/{person_pricing_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_room_person_pricing(person_pricing_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomPersonPricing).where(RoomPersonPricing.personPricingId == person_pricing_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间按人定价不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# TimeSlotCoefficient 时段系数
# ═══════════════════════════════════════════

@router.get("/time-slot-coefficients", response_model=TimeSlotCoefficientListOut, dependencies=[Depends(get_optional_user)])
async def list_time_slot_coefficients(
    store_id: Optional[str] = Query(None, alias="storeId"),
    day_type: Optional[str] = Query(None, alias="dayType"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(TimeSlotCoefficient)
    if store_id:
        q = q.where(TimeSlotCoefficient.storeId == store_id)
    if day_type:
        q = q.where(TimeSlotCoefficient.dayType == day_type)
    q = q.order_by(TimeSlotCoefficient.id.desc())

    count_q = select(func.count(TimeSlotCoefficient.coeffId)).select_from(TimeSlotCoefficient)
    if store_id:
        count_q = count_q.where(TimeSlotCoefficient.storeId == store_id)
    if day_type:
        count_q = count_q.where(TimeSlotCoefficient.dayType == day_type)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(TimeSlotCoefficientOut(
            coeffId=item.coeffId, storeId=item.storeId,
            storeName=store_name,
            dayType=item.dayType, timeRange=item.timeRange,
            coefficient=item.coefficient, description=item.description,
        ))
    return TimeSlotCoefficientListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/time-slot-coefficients/{coeff_id}", response_model=TimeSlotCoefficientOut, dependencies=[Depends(get_optional_user)])
async def get_time_slot_coefficient(coeff_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(TimeSlotCoefficient).where(TimeSlotCoefficient.coeffId == coeff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时段系数不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return TimeSlotCoefficientOut(
        coeffId=item.coeffId, storeId=item.storeId,
        storeName=store_name,
        dayType=item.dayType, timeRange=item.timeRange,
        coefficient=item.coefficient, description=item.description,
    )


@router.post("/time-slot-coefficients", response_model=TimeSlotCoefficientOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_time_slot_coefficient(
    data: TimeSlotCoefficientCreate,
    db: AsyncSession = Depends(get_db),
):
    item = TimeSlotCoefficient(
        coeffId=_gen_id(), storeId=data.storeId,
        dayType=data.dayType, timeRange=data.timeRange,
        coefficient=data.coefficient, description=data.description,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return TimeSlotCoefficientOut(
        coeffId=item.coeffId, storeId=item.storeId,
        storeName=store_name,
        dayType=item.dayType, timeRange=item.timeRange,
        coefficient=item.coefficient, description=item.description,
    )


@router.put("/time-slot-coefficients/{coeff_id}", response_model=TimeSlotCoefficientOut, dependencies=[Depends(get_current_user)])
async def update_time_slot_coefficient(
    coeff_id: str,
    data: TimeSlotCoefficientUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(TimeSlotCoefficient).where(TimeSlotCoefficient.coeffId == coeff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时段系数不存在")
    if data.dayType is not None:
        item.dayType = data.dayType
    if data.timeRange is not None:
        item.timeRange = data.timeRange
    if data.coefficient is not None:
        item.coefficient = data.coefficient
    if data.description is not None:
        item.description = data.description
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return TimeSlotCoefficientOut(
        coeffId=item.coeffId, storeId=item.storeId,
        storeName=store_name,
        dayType=item.dayType, timeRange=item.timeRange,
        coefficient=item.coefficient, description=item.description,
    )


@router.delete("/time-slot-coefficients/{coeff_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_time_slot_coefficient(coeff_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(TimeSlotCoefficient).where(TimeSlotCoefficient.coeffId == coeff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时段系数不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# HolidayCalendar 节假日日历
# ═══════════════════════════════════════════

@router.get("/holiday-calendars", response_model=HolidayCalendarListOut, dependencies=[Depends(get_optional_user)])
async def list_holiday_calendars(
    status: Optional[str] = None,
    year: Optional[int] = Query(None, alias="year"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(HolidayCalendar)
    if status:
        q = q.where(HolidayCalendar.status == status)
    if year is not None:
        from sqlalchemy import extract
        q = q.where(extract("year", HolidayCalendar.startDate) == year)
    q = q.order_by(HolidayCalendar.startDate.desc())

    count_q = select(func.count(HolidayCalendar.holidayId)).select_from(HolidayCalendar)
    if status:
        count_q = count_q.where(HolidayCalendar.status == status)
    if year is not None:
        from sqlalchemy import extract
        count_q = count_q.where(extract("year", HolidayCalendar.startDate) == year)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return HolidayCalendarListOut(
        total=total,
        items=[HolidayCalendarOut(
            holidayId=item.holidayId, name=item.name,
            startDate=item.startDate, endDate=item.endDate,
            coefficient=item.coefficient, recurrence=item.recurrence,
            status=item.status,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/holiday-calendars/{holiday_id}", response_model=HolidayCalendarOut, dependencies=[Depends(get_optional_user)])
async def get_holiday_calendar(holiday_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(HolidayCalendar).where(HolidayCalendar.holidayId == holiday_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "节假日记录不存在")
    return HolidayCalendarOut(
        holidayId=item.holidayId, name=item.name,
        startDate=item.startDate, endDate=item.endDate,
        coefficient=item.coefficient, recurrence=item.recurrence,
        status=item.status,
    )


@router.post("/holiday-calendars", response_model=HolidayCalendarOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_holiday_calendar(
    data: HolidayCalendarCreate,
    db: AsyncSession = Depends(get_db),
):
    item = HolidayCalendar(
        holidayId=_gen_id(), name=data.name,
        startDate=data.startDate, endDate=data.endDate,
        coefficient=data.coefficient, recurrence=data.recurrence,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return HolidayCalendarOut(
        holidayId=item.holidayId, name=item.name,
        startDate=item.startDate, endDate=item.endDate,
        coefficient=item.coefficient, recurrence=item.recurrence,
        status=item.status,
    )


@router.put("/holiday-calendars/{holiday_id}", response_model=HolidayCalendarOut, dependencies=[Depends(get_current_user)])
async def update_holiday_calendar(
    holiday_id: str,
    data: HolidayCalendarUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(HolidayCalendar).where(HolidayCalendar.holidayId == holiday_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "节假日记录不存在")
    if data.name is not None:
        item.name = data.name
    if data.startDate is not None:
        item.startDate = data.startDate
    if data.endDate is not None:
        item.endDate = data.endDate
    if data.coefficient is not None:
        item.coefficient = data.coefficient
    if data.recurrence is not None:
        item.recurrence = data.recurrence
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return HolidayCalendarOut(
        holidayId=item.holidayId, name=item.name,
        startDate=item.startDate, endDate=item.endDate,
        coefficient=item.coefficient, recurrence=item.recurrence,
        status=item.status,
    )


@router.delete("/holiday-calendars/{holiday_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_holiday_calendar(holiday_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(HolidayCalendar).where(HolidayCalendar.holidayId == holiday_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "节假日记录不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# ActivityCalendar 活动日历
# ═══════════════════════════════════════════

@router.get("/activity-calendars", response_model=ActivityCalendarListOut, dependencies=[Depends(get_optional_user)])
async def list_activity_calendars(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ActivityCalendar)
    if store_id:
        q = q.where(ActivityCalendar.storeId == store_id)
    if status:
        q = q.where(ActivityCalendar.status == status)
    q = q.order_by(ActivityCalendar.startDate.desc())

    count_q = select(func.count(ActivityCalendar.activityId)).select_from(ActivityCalendar)
    if store_id:
        count_q = count_q.where(ActivityCalendar.storeId == store_id)
    if status:
        count_q = count_q.where(ActivityCalendar.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(ActivityCalendarOut(
            activityId=item.activityId, storeId=item.storeId,
            storeName=store_name,
            name=item.name, startDate=item.startDate,
            endDate=item.endDate, coefficient=item.coefficient,
            status=item.status,
        ))
    return ActivityCalendarListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/activity-calendars/{activity_id}", response_model=ActivityCalendarOut, dependencies=[Depends(get_optional_user)])
async def get_activity_calendar(activity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ActivityCalendar).where(ActivityCalendar.activityId == activity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "活动记录不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return ActivityCalendarOut(
        activityId=item.activityId, storeId=item.storeId,
        storeName=store_name,
        name=item.name, startDate=item.startDate,
        endDate=item.endDate, coefficient=item.coefficient,
        status=item.status,
    )


@router.post("/activity-calendars", response_model=ActivityCalendarOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_activity_calendar(
    data: ActivityCalendarCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ActivityCalendar(
        activityId=_gen_id(), storeId=data.storeId,
        name=data.name, startDate=data.startDate,
        endDate=data.endDate, coefficient=data.coefficient,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return ActivityCalendarOut(
        activityId=item.activityId, storeId=item.storeId,
        storeName=store_name,
        name=item.name, startDate=item.startDate,
        endDate=item.endDate, coefficient=item.coefficient,
        status=item.status,
    )


@router.put("/activity-calendars/{activity_id}", response_model=ActivityCalendarOut, dependencies=[Depends(get_current_user)])
async def update_activity_calendar(
    activity_id: str,
    data: ActivityCalendarUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ActivityCalendar).where(ActivityCalendar.activityId == activity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "活动记录不存在")
    if data.name is not None:
        item.name = data.name
    if data.startDate is not None:
        item.startDate = data.startDate
    if data.endDate is not None:
        item.endDate = data.endDate
    if data.coefficient is not None:
        item.coefficient = data.coefficient
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return ActivityCalendarOut(
        activityId=item.activityId, storeId=item.storeId,
        storeName=store_name,
        name=item.name, startDate=item.startDate,
        endDate=item.endDate, coefficient=item.coefficient,
        status=item.status,
    )


@router.delete("/activity-calendars/{activity_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_activity_calendar(activity_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ActivityCalendar).where(ActivityCalendar.activityId == activity_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "活动记录不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# DurationDiscountRule 时长折扣规则
# ═══════════════════════════════════════════

@router.get("/duration-discount-rules", response_model=DurationDiscountRuleListOut, dependencies=[Depends(get_optional_user)])
async def list_duration_discount_rules(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(DurationDiscountRule)
    if store_id:
        q = q.where(DurationDiscountRule.storeId == store_id)
    if status:
        q = q.where(DurationDiscountRule.status == status)
    q = q.order_by(DurationDiscountRule.id.desc())

    count_q = select(func.count(DurationDiscountRule.ruleId)).select_from(DurationDiscountRule)
    if store_id:
        count_q = count_q.where(DurationDiscountRule.storeId == store_id)
    if status:
        count_q = count_q.where(DurationDiscountRule.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(DurationDiscountRuleOut(
            ruleId=item.ruleId, storeId=item.storeId,
            storeName=store_name,
            minDuration=item.minDuration, maxDuration=item.maxDuration,
            discountRate=item.discountRate, status=item.status,
        ))
    return DurationDiscountRuleListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/duration-discount-rules/{rule_id}", response_model=DurationDiscountRuleOut, dependencies=[Depends(get_optional_user)])
async def get_duration_discount_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DurationDiscountRule).where(DurationDiscountRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时长折扣规则不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return DurationDiscountRuleOut(
        ruleId=item.ruleId, storeId=item.storeId,
        storeName=store_name,
        minDuration=item.minDuration, maxDuration=item.maxDuration,
        discountRate=item.discountRate, status=item.status,
    )


@router.post("/duration-discount-rules", response_model=DurationDiscountRuleOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_duration_discount_rule(
    data: DurationDiscountRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    item = DurationDiscountRule(
        ruleId=_gen_id(), storeId=data.storeId,
        minDuration=data.minDuration, maxDuration=data.maxDuration,
        discountRate=data.discountRate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return DurationDiscountRuleOut(
        ruleId=item.ruleId, storeId=item.storeId,
        storeName=store_name,
        minDuration=item.minDuration, maxDuration=item.maxDuration,
        discountRate=item.discountRate, status=item.status,
    )


@router.put("/duration-discount-rules/{rule_id}", response_model=DurationDiscountRuleOut, dependencies=[Depends(get_current_user)])
async def update_duration_discount_rule(
    rule_id: str,
    data: DurationDiscountRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(DurationDiscountRule).where(DurationDiscountRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时长折扣规则不存在")
    if data.minDuration is not None:
        item.minDuration = data.minDuration
    if data.maxDuration is not None:
        item.maxDuration = data.maxDuration
    if data.discountRate is not None:
        item.discountRate = data.discountRate
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return DurationDiscountRuleOut(
        ruleId=item.ruleId, storeId=item.storeId,
        storeName=store_name,
        minDuration=item.minDuration, maxDuration=item.maxDuration,
        discountRate=item.discountRate, status=item.status,
    )


@router.delete("/duration-discount-rules/{rule_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_duration_discount_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DurationDiscountRule).where(DurationDiscountRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "时长折扣规则不存在")
    await db.delete(item)
    await db.commit()


# ═══════════════════════════════════════════
# NightPackage 夜间/过夜套餐
# ═══════════════════════════════════════════

@router.get("/night-packages", response_model=NightPackageListOut, dependencies=[Depends(get_optional_user)])
async def list_night_packages(
    store_id: Optional[str] = Query(None, alias="storeId"),
    package_type: Optional[str] = Query(None, alias="packageType"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(NightPackage)
    if store_id:
        q = q.where(NightPackage.storeId == store_id)
    if package_type:
        q = q.where(NightPackage.packageType == package_type)
    if status:
        q = q.where(NightPackage.status == status)
    q = q.order_by(NightPackage.id.desc())

    count_q = select(func.count(NightPackage.packageId)).select_from(NightPackage)
    if store_id:
        count_q = count_q.where(NightPackage.storeId == store_id)
    if package_type:
        count_q = count_q.where(NightPackage.packageType == package_type)
    if status:
        count_q = count_q.where(NightPackage.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _resolve_store_name(db, item.storeId)
        result.append(NightPackageOut(
            packageId=item.packageId, storeId=item.storeId,
            storeName=store_name,
            packageType=item.packageType, price=item.price,
            durationMinutes=item.durationMinutes,
            applicableTimeRange=item.applicableTimeRange,
            status=item.status,
        ))
    return NightPackageListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/night-packages/{package_id}", response_model=NightPackageOut, dependencies=[Depends(get_optional_user)])
async def get_night_package(package_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(NightPackage).where(NightPackage.packageId == package_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "夜间套餐不存在")
    store_name = await _resolve_store_name(db, item.storeId)
    return NightPackageOut(
        packageId=item.packageId, storeId=item.storeId,
        storeName=store_name,
        packageType=item.packageType, price=item.price,
        durationMinutes=item.durationMinutes,
        applicableTimeRange=item.applicableTimeRange,
        status=item.status,
    )


@router.post("/night-packages", response_model=NightPackageOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_night_package(
    data: NightPackageCreate,
    db: AsyncSession = Depends(get_db),
):
    item = NightPackage(
        packageId=_gen_id(), storeId=data.storeId,
        packageType=data.packageType, price=data.price,
        durationMinutes=data.durationMinutes,
        applicableTimeRange=data.applicableTimeRange,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return NightPackageOut(
        packageId=item.packageId, storeId=item.storeId,
        storeName=store_name,
        packageType=item.packageType, price=item.price,
        durationMinutes=item.durationMinutes,
        applicableTimeRange=item.applicableTimeRange,
        status=item.status,
    )


@router.put("/night-packages/{package_id}", response_model=NightPackageOut, dependencies=[Depends(get_current_user)])
async def update_night_package(
    package_id: str,
    data: NightPackageUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(NightPackage).where(NightPackage.packageId == package_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "夜间套餐不存在")
    if data.packageType is not None:
        item.packageType = data.packageType
    if data.price is not None:
        item.price = data.price
    if data.durationMinutes is not None:
        item.durationMinutes = data.durationMinutes
    if data.applicableTimeRange is not None:
        item.applicableTimeRange = data.applicableTimeRange
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = await _resolve_store_name(db, item.storeId)
    return NightPackageOut(
        packageId=item.packageId, storeId=item.storeId,
        storeName=store_name,
        packageType=item.packageType, price=item.price,
        durationMinutes=item.durationMinutes,
        applicableTimeRange=item.applicableTimeRange,
        status=item.status,
    )


@router.delete("/night-packages/{package_id}", status_code=204, dependencies=[Depends(get_current_user)])
async def delete_night_package(package_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(NightPackage).where(NightPackage.packageId == package_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "夜间套餐不存在")
    await db.delete(item)
    await db.commit()
