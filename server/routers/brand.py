"""D01 品牌运营域 API — 组织/经营目标/目标指标/品牌资产/合同/股东/投资/里程碑"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from datetime import datetime, date

from database import get_db
from models.brand import (
    Organization, BusinessGoal, GoalMetric, BrandAsset, Contract,
    Shareholder, Investment, Milestone,
)
from models.store_dev import Store
from schemas.brand import (
    OrganizationCreate, OrganizationUpdate, OrganizationOut, OrganizationListOut,
    BusinessGoalCreate, BusinessGoalUpdate, BusinessGoalOut, BusinessGoalListOut,
    GoalMetricCreate, GoalMetricUpdate, GoalMetricOut, GoalMetricListOut,
    BrandAssetCreate, BrandAssetUpdate, BrandAssetOut, BrandAssetListOut,
    ContractCreate, ContractUpdate, ContractOut, ContractListOut,
    ShareholderCreate, ShareholderUpdate, ShareholderOut, ShareholderListOut,
    InvestmentCreate, InvestmentUpdate, InvestmentOut, InvestmentListOut,
    MilestoneCreate, MilestoneUpdate, MilestoneOut, MilestoneListOut,
)
from services.auth_service import get_current_user, get_optional_user

router = APIRouter(prefix="/api/brand", tags=["品牌运营管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ═══════════════════════════════════════════
# Organization 组织
# ═══════════════════════════════════════════

@router.get("/orgs", response_model=OrganizationListOut, dependencies=[Depends(get_optional_user)])
async def list_organizations(
    parent_org_id: Optional[str] = Query(None, alias="parentOrgId"),
    type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List organizations with optional filters."""
    q = select(Organization)
    count_q = select(func.count(Organization.id)).select_from(Organization)

    if parent_org_id is not None:
        q = q.where(Organization.parentOrgId == parent_org_id)
        count_q = count_q.where(Organization.parentOrgId == parent_org_id)
    if type:
        q = q.where(Organization.type == type)
        count_q = count_q.where(Organization.type == type)
    if status:
        q = q.where(Organization.status == status)
        count_q = count_q.where(Organization.status == status)
    if search:
        q = q.where(Organization.name.contains(search))
        count_q = count_q.where(Organization.name.contains(search))

    q = q.order_by(Organization.createdAt.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [OrganizationOut(
        orgId=item.orgId, parentOrgId=item.parentOrgId, name=item.name,
        shortName=item.shortName, type=item.type, creditCode=item.creditCode,
        legalRep=item.legalRep, registeredAddress=item.registeredAddress,
        contactPhone=item.contactPhone, logo=item.logo, status=item.status,
        establishedDate=item.establishedDate, createdAt=item.createdAt,
        updatedAt=item.updatedAt,
    ) for item in items]

    return OrganizationListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/orgs/tree", dependencies=[Depends(get_optional_user)])
async def get_org_tree(
    db: AsyncSession = Depends(get_db),
):
    """Get the full organization tree structure (nested by parentOrgId)."""
    r = await db.execute(select(Organization).order_by(Organization.createdAt))
    all_orgs = r.scalars().all()

    org_map = {}
    for org in all_orgs:
        org_map[org.orgId] = {
            "orgId": org.orgId,
            "parentOrgId": org.parentOrgId,
            "name": org.name,
            "shortName": org.shortName,
            "type": org.type,
            "status": org.status,
            "establishedDate": str(org.establishedDate) if org.establishedDate else None,
            "children": [],
        }

    roots = []
    for org_id, node in org_map.items():
        pid = node["parentOrgId"]
        if pid and pid in org_map:
            org_map[pid]["children"].append(node)
        else:
            roots.append(node)

    return roots


@router.get("/orgs/{org_id}", response_model=OrganizationOut, dependencies=[Depends(get_optional_user)])
async def get_organization(org_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Organization).where(Organization.orgId == org_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "组织不存在")
    return OrganizationOut(
        orgId=item.orgId, parentOrgId=item.parentOrgId, name=item.name,
        shortName=item.shortName, type=item.type, creditCode=item.creditCode,
        legalRep=item.legalRep, registeredAddress=item.registeredAddress,
        contactPhone=item.contactPhone, logo=item.logo, status=item.status,
        establishedDate=item.establishedDate, createdAt=item.createdAt,
        updatedAt=item.updatedAt,
    )


@router.post("/orgs", response_model=OrganizationOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Organization(
        orgId=_gen_id(), parentOrgId=data.parentOrgId, name=data.name,
        shortName=data.shortName, type=data.type, creditCode=data.creditCode,
        legalRep=data.legalRep, registeredAddress=data.registeredAddress,
        contactPhone=data.contactPhone, logo=data.logo,
        status=data.status or "Active", establishedDate=data.establishedDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return OrganizationOut(
        orgId=item.orgId, parentOrgId=item.parentOrgId, name=item.name,
        shortName=item.shortName, type=item.type, creditCode=item.creditCode,
        legalRep=item.legalRep, registeredAddress=item.registeredAddress,
        contactPhone=item.contactPhone, logo=item.logo, status=item.status,
        establishedDate=item.establishedDate, createdAt=item.createdAt,
        updatedAt=item.updatedAt,
    )


@router.put("/orgs/{org_id}", response_model=OrganizationOut, dependencies=[Depends(get_current_user)])
async def update_organization(
    org_id: str,
    data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Organization).where(Organization.orgId == org_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "组织不存在")
    if data.parentOrgId is not None:
        item.parentOrgId = data.parentOrgId
    if data.name is not None:
        item.name = data.name
    if data.shortName is not None:
        item.shortName = data.shortName
    if data.type is not None:
        item.type = data.type
    if data.creditCode is not None:
        item.creditCode = data.creditCode
    if data.legalRep is not None:
        item.legalRep = data.legalRep
    if data.registeredAddress is not None:
        item.registeredAddress = data.registeredAddress
    if data.contactPhone is not None:
        item.contactPhone = data.contactPhone
    if data.logo is not None:
        item.logo = data.logo
    if data.status is not None:
        item.status = data.status
    if data.establishedDate is not None:
        item.establishedDate = data.establishedDate
    await db.commit()
    await db.refresh(item)
    return OrganizationOut(
        orgId=item.orgId, parentOrgId=item.parentOrgId, name=item.name,
        shortName=item.shortName, type=item.type, creditCode=item.creditCode,
        legalRep=item.legalRep, registeredAddress=item.registeredAddress,
        contactPhone=item.contactPhone, logo=item.logo, status=item.status,
        establishedDate=item.establishedDate, createdAt=item.createdAt,
        updatedAt=item.updatedAt,
    )


@router.delete("/orgs/{org_id}", dependencies=[Depends(get_current_user)])
async def delete_organization(org_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Organization).where(Organization.orgId == org_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "组织不存在")
    # Check if has children
    children_r = await db.execute(
        select(func.count(Organization.id)).where(Organization.parentOrgId == org_id)
    )
    child_count = children_r.scalar() or 0
    if child_count > 0:
        raise HTTPException(400, f"该组织有 {child_count} 个子组织，请先删除子组织")
    await db.delete(item)
    await db.commit()
    return {"message": "组织已删除"}


# ═══════════════════════════════════════════
# BusinessGoal 经营目标
# ═══════════════════════════════════════════

@router.get("/goals", response_model=BusinessGoalListOut, dependencies=[Depends(get_optional_user)])
async def list_business_goals(
    org_id: Optional[str] = Query(None, alias="orgId"),
    year: Optional[int] = None,
    quarter: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List business goals with filtering by orgId, year, quarter, status."""
    q = select(BusinessGoal)
    count_q = select(func.count(BusinessGoal.id)).select_from(BusinessGoal)

    if org_id:
        q = q.where(BusinessGoal.orgId == org_id)
        count_q = count_q.where(BusinessGoal.orgId == org_id)
    if year is not None:
        q = q.where(BusinessGoal.year == year)
        count_q = count_q.where(BusinessGoal.year == year)
    if quarter is not None:
        q = q.where(BusinessGoal.quarter == quarter)
        count_q = count_q.where(BusinessGoal.quarter == quarter)
    if status:
        q = q.where(BusinessGoal.status == status)
        count_q = count_q.where(BusinessGoal.status == status)

    q = q.order_by(BusinessGoal.year.desc(), BusinessGoal.quarter.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        org_name = None
        if item.orgId:
            sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
            org_name = sr.scalar_one_or_none()
        result.append(BusinessGoalOut(
            goalId=item.goalId, orgId=item.orgId, orgName=org_name,
            year=item.year, quarter=item.quarter,
            revenueTarget=item.revenueTarget, profitTarget=item.profitTarget,
            storeCountTarget=item.storeCountTarget,
            memberGrowthTarget=item.memberGrowthTarget,
            status=item.status, createdAt=item.createdAt,
        ))

    return BusinessGoalListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/goals/{goal_id}", response_model=BusinessGoalOut, dependencies=[Depends(get_optional_user)])
async def get_business_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BusinessGoal).where(BusinessGoal.goalId == goal_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "经营目标不存在")
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BusinessGoalOut(
        goalId=item.goalId, orgId=item.orgId, orgName=org_name,
        year=item.year, quarter=item.quarter,
        revenueTarget=item.revenueTarget, profitTarget=item.profitTarget,
        storeCountTarget=item.storeCountTarget,
        memberGrowthTarget=item.memberGrowthTarget,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/goals", response_model=BusinessGoalOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_business_goal(
    data: BusinessGoalCreate,
    db: AsyncSession = Depends(get_db),
):
    item = BusinessGoal(
        goalId=_gen_id(), orgId=data.orgId, year=data.year,
        quarter=data.quarter, revenueTarget=data.revenueTarget,
        profitTarget=data.profitTarget, storeCountTarget=data.storeCountTarget,
        memberGrowthTarget=data.memberGrowthTarget,
        status=data.status or "Draft",
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BusinessGoalOut(
        goalId=item.goalId, orgId=item.orgId, orgName=org_name,
        year=item.year, quarter=item.quarter,
        revenueTarget=item.revenueTarget, profitTarget=item.profitTarget,
        storeCountTarget=item.storeCountTarget,
        memberGrowthTarget=item.memberGrowthTarget,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/goals/{goal_id}", response_model=BusinessGoalOut, dependencies=[Depends(get_current_user)])
async def update_business_goal(
    goal_id: str,
    data: BusinessGoalUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(BusinessGoal).where(BusinessGoal.goalId == goal_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "经营目标不存在")
    if data.year is not None:
        item.year = data.year
    if data.quarter is not None:
        item.quarter = data.quarter
    if data.revenueTarget is not None:
        item.revenueTarget = data.revenueTarget
    if data.profitTarget is not None:
        item.profitTarget = data.profitTarget
    if data.storeCountTarget is not None:
        item.storeCountTarget = data.storeCountTarget
    if data.memberGrowthTarget is not None:
        item.memberGrowthTarget = data.memberGrowthTarget
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BusinessGoalOut(
        goalId=item.goalId, orgId=item.orgId, orgName=org_name,
        year=item.year, quarter=item.quarter,
        revenueTarget=item.revenueTarget, profitTarget=item.profitTarget,
        storeCountTarget=item.storeCountTarget,
        memberGrowthTarget=item.memberGrowthTarget,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/goals/{goal_id}", dependencies=[Depends(get_current_user)])
async def delete_business_goal(goal_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BusinessGoal).where(BusinessGoal.goalId == goal_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "经营目标不存在")
    # Check for related metrics
    metrics_r = await db.execute(
        select(func.count(GoalMetric.id)).where(GoalMetric.goalId == goal_id)
    )
    if metrics_r.scalar() > 0:
        raise HTTPException(400, "该目标下存在指标数据，请先删除指标")
    await db.delete(item)
    await db.commit()
    return {"message": "经营目标已删除"}


# ═══════════════════════════════════════════
# GoalMetric 目标指标
# ═══════════════════════════════════════════

@router.get("/goals/{goal_id}/metrics", response_model=GoalMetricListOut, dependencies=[Depends(get_optional_user)])
async def list_goal_metrics(
    goal_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List metrics for a specific business goal."""
    q = select(GoalMetric).where(GoalMetric.goalId == goal_id)
    count_q = select(func.count(GoalMetric.id)).select_from(GoalMetric).where(
        GoalMetric.goalId == goal_id
    )
    q = q.order_by(GoalMetric.updatedAt.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [GoalMetricOut(
        metricId=item.metricId, goalId=item.goalId,
        metricName=item.metricName, targetValue=item.targetValue,
        actualValue=item.actualValue, unit=item.unit,
        updatedAt=item.updatedAt,
    ) for item in items]

    return GoalMetricListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/metrics/{metric_id}", response_model=GoalMetricOut, dependencies=[Depends(get_optional_user)])
async def get_goal_metric(metric_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(GoalMetric).where(GoalMetric.metricId == metric_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "指标不存在")
    return GoalMetricOut(
        metricId=item.metricId, goalId=item.goalId,
        metricName=item.metricName, targetValue=item.targetValue,
        actualValue=item.actualValue, unit=item.unit,
        updatedAt=item.updatedAt,
    )


@router.post("/metrics", response_model=GoalMetricOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_goal_metric(
    data: GoalMetricCreate,
    db: AsyncSession = Depends(get_db),
):
    item = GoalMetric(
        metricId=_gen_id(), goalId=data.goalId,
        metricName=data.metricName, targetValue=data.targetValue,
        actualValue=data.actualValue, unit=data.unit,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return GoalMetricOut(
        metricId=item.metricId, goalId=item.goalId,
        metricName=item.metricName, targetValue=item.targetValue,
        actualValue=item.actualValue, unit=item.unit,
        updatedAt=item.updatedAt,
    )


@router.put("/metrics/{metric_id}", response_model=GoalMetricOut, dependencies=[Depends(get_current_user)])
async def update_goal_metric(
    metric_id: str,
    data: GoalMetricUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(GoalMetric).where(GoalMetric.metricId == metric_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "指标不存在")
    if data.metricName is not None:
        item.metricName = data.metricName
    if data.targetValue is not None:
        item.targetValue = data.targetValue
    if data.actualValue is not None:
        item.actualValue = data.actualValue
    if data.unit is not None:
        item.unit = data.unit
    await db.commit()
    await db.refresh(item)
    return GoalMetricOut(
        metricId=item.metricId, goalId=item.goalId,
        metricName=item.metricName, targetValue=item.targetValue,
        actualValue=item.actualValue, unit=item.unit,
        updatedAt=item.updatedAt,
    )


@router.delete("/metrics/{metric_id}", dependencies=[Depends(get_current_user)])
async def delete_goal_metric(metric_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(GoalMetric).where(GoalMetric.metricId == metric_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "指标不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "指标已删除"}


# ═══════════════════════════════════════════
# BrandAsset 品牌资产
# ═══════════════════════════════════════════

@router.get("/assets", response_model=BrandAssetListOut, dependencies=[Depends(get_optional_user)])
async def list_brand_assets(
    org_id: Optional[str] = Query(None, alias="orgId"),
    asset_type: Optional[str] = Query(None, alias="assetType"),
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List brand assets with optional filters."""
    q = select(BrandAsset)
    count_q = select(func.count(BrandAsset.id)).select_from(BrandAsset)

    if org_id:
        q = q.where(BrandAsset.orgId == org_id)
        count_q = count_q.where(BrandAsset.orgId == org_id)
    if asset_type:
        q = q.where(BrandAsset.assetType == asset_type)
        count_q = count_q.where(BrandAsset.assetType == asset_type)
    if status:
        q = q.where(BrandAsset.status == status)
        count_q = count_q.where(BrandAsset.status == status)
    if search:
        q = q.where(BrandAsset.name.contains(search))
        count_q = count_q.where(BrandAsset.name.contains(search))

    q = q.order_by(BrandAsset.uploadedAt.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        org_name = None
        if item.orgId:
            sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
            org_name = sr.scalar_one_or_none()
        result.append(BrandAssetOut(
            assetId=item.assetId, orgId=item.orgId, orgName=org_name,
            assetType=item.assetType, name=item.name,
            fileName=item.fileName, fileSize=item.fileSize,
            version=item.version, tags=item.tags,
            status=item.status, uploadedBy=item.uploadedBy,
            uploadedAt=item.uploadedAt,
        ))

    return BrandAssetListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/assets/{asset_id}", response_model=BrandAssetOut, dependencies=[Depends(get_optional_user)])
async def get_brand_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BrandAsset).where(BrandAsset.assetId == asset_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "品牌资产不存在")
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BrandAssetOut(
        assetId=item.assetId, orgId=item.orgId, orgName=org_name,
        assetType=item.assetType, name=item.name,
        fileName=item.fileName, fileSize=item.fileSize,
        version=item.version, tags=item.tags,
        status=item.status, uploadedBy=item.uploadedBy,
        uploadedAt=item.uploadedAt,
    )


@router.post("/assets", response_model=BrandAssetOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_brand_asset(
    data: BrandAssetCreate,
    db: AsyncSession = Depends(get_db),
):
    item = BrandAsset(
        assetId=_gen_id(), orgId=data.orgId, assetType=data.assetType,
        name=data.name, fileName=data.fileName, fileSize=data.fileSize,
        version=data.version, tags=data.tags,
        status=data.status or "Active", uploadedBy=data.uploadedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BrandAssetOut(
        assetId=item.assetId, orgId=item.orgId, orgName=org_name,
        assetType=item.assetType, name=item.name,
        fileName=item.fileName, fileSize=item.fileSize,
        version=item.version, tags=item.tags,
        status=item.status, uploadedBy=item.uploadedBy,
        uploadedAt=item.uploadedAt,
    )


@router.put("/assets/{asset_id}", response_model=BrandAssetOut, dependencies=[Depends(get_current_user)])
async def update_brand_asset(
    asset_id: str,
    data: BrandAssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(BrandAsset).where(BrandAsset.assetId == asset_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "品牌资产不存在")
    if data.name is not None:
        item.name = data.name
    if data.fileName is not None:
        item.fileName = data.fileName
    if data.fileSize is not None:
        item.fileSize = data.fileSize
    if data.version is not None:
        item.version = data.version
    if data.tags is not None:
        item.tags = data.tags
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    org_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    return BrandAssetOut(
        assetId=item.assetId, orgId=item.orgId, orgName=org_name,
        assetType=item.assetType, name=item.name,
        fileName=item.fileName, fileSize=item.fileSize,
        version=item.version, tags=item.tags,
        status=item.status, uploadedBy=item.uploadedBy,
        uploadedAt=item.uploadedAt,
    )


@router.delete("/assets/{asset_id}", dependencies=[Depends(get_current_user)])
async def delete_brand_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BrandAsset).where(BrandAsset.assetId == asset_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "品牌资产不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "品牌资产已删除"}


# ═══════════════════════════════════════════
# Contract 合同
# ═══════════════════════════════════════════

@router.get("/contracts", response_model=ContractListOut, dependencies=[Depends(get_optional_user)])
async def list_contracts(
    org_id: Optional[str] = Query(None, alias="orgId"),
    counterparty_id: Optional[str] = Query(None, alias="counterpartyId"),
    status: Optional[str] = None,
    contract_type: Optional[str] = Query(None, alias="contractType"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List contracts with filtering by orgId, counterpartyId, status, type."""
    q = select(Contract)
    count_q = select(func.count(Contract.id)).select_from(Contract)

    if org_id:
        q = q.where(Contract.orgId == org_id)
        count_q = count_q.where(Contract.orgId == org_id)
    if counterparty_id:
        q = q.where(Contract.counterpartyId == counterparty_id)
        count_q = count_q.where(Contract.counterpartyId == counterparty_id)
    if status:
        q = q.where(Contract.status == status)
        count_q = count_q.where(Contract.status == status)
    if contract_type:
        q = q.where(Contract.contractType == contract_type)
        count_q = count_q.where(Contract.contractType == contract_type)
    if search:
        q = q.where(Contract.contractNumber.contains(search))
        count_q = count_q.where(Contract.contractNumber.contains(search))

    q = q.order_by(Contract.startDate.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        org_name = None
        counterparty_name = None
        store_name = None
        if item.orgId:
            sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
            org_name = sr.scalar_one_or_none()
        if item.counterpartyId:
            sr = await db.execute(select(Organization.name).where(Organization.orgId == item.counterpartyId))
            counterparty_name = sr.scalar_one_or_none()
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(ContractOut(
            contractId=item.contractId, contractNumber=item.contractNumber,
            orgId=item.orgId, orgName=org_name,
            counterpartyId=item.counterpartyId, counterpartyName=counterparty_name,
            storeId=item.storeId, storeName=store_name,
            contractType=item.contractType, startDate=item.startDate,
            endDate=item.endDate, amount=item.amount,
            paymentTerms=item.paymentTerms, attachmentUrls=item.attachmentUrls,
            status=item.status, signedAt=item.signedAt,
        ))

    return ContractListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/contracts/{contract_id}", response_model=ContractOut, dependencies=[Depends(get_optional_user)])
async def get_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Contract).where(Contract.contractId == contract_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "合同不存在")
    org_name = None
    counterparty_name = None
    store_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    if item.counterpartyId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.counterpartyId))
        counterparty_name = sr.scalar_one_or_none()
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ContractOut(
        contractId=item.contractId, contractNumber=item.contractNumber,
        orgId=item.orgId, orgName=org_name,
        counterpartyId=item.counterpartyId, counterpartyName=counterparty_name,
        storeId=item.storeId, storeName=store_name,
        contractType=item.contractType, startDate=item.startDate,
        endDate=item.endDate, amount=item.amount,
        paymentTerms=item.paymentTerms, attachmentUrls=item.attachmentUrls,
        status=item.status, signedAt=item.signedAt,
    )


@router.post("/contracts", response_model=ContractOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_contract(
    data: ContractCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Contract(
        contractId=_gen_id(), contractNumber=data.contractNumber,
        orgId=data.orgId, counterpartyId=data.counterpartyId,
        storeId=data.storeId, contractType=data.contractType,
        startDate=data.startDate, endDate=data.endDate,
        amount=data.amount, paymentTerms=data.paymentTerms,
        attachmentUrls=data.attachmentUrls, status=data.status or "Draft",
        signedAt=data.signedAt,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    org_name = None
    counterparty_name = None
    store_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    if item.counterpartyId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.counterpartyId))
        counterparty_name = sr.scalar_one_or_none()
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ContractOut(
        contractId=item.contractId, contractNumber=item.contractNumber,
        orgId=item.orgId, orgName=org_name,
        counterpartyId=item.counterpartyId, counterpartyName=counterparty_name,
        storeId=item.storeId, storeName=store_name,
        contractType=item.contractType, startDate=item.startDate,
        endDate=item.endDate, amount=item.amount,
        paymentTerms=item.paymentTerms, attachmentUrls=item.attachmentUrls,
        status=item.status, signedAt=item.signedAt,
    )


@router.put("/contracts/{contract_id}", response_model=ContractOut, dependencies=[Depends(get_current_user)])
async def update_contract(
    contract_id: str,
    data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Contract).where(Contract.contractId == contract_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "合同不存在")
    if data.contractNumber is not None:
        item.contractNumber = data.contractNumber
    if data.startDate is not None:
        item.startDate = data.startDate
    if data.endDate is not None:
        item.endDate = data.endDate
    if data.amount is not None:
        item.amount = data.amount
    if data.paymentTerms is not None:
        item.paymentTerms = data.paymentTerms
    if data.attachmentUrls is not None:
        item.attachmentUrls = data.attachmentUrls
    if data.status is not None:
        item.status = data.status
    if data.signedAt is not None:
        item.signedAt = data.signedAt
    await db.commit()
    await db.refresh(item)
    org_name = None
    counterparty_name = None
    store_name = None
    if item.orgId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.orgId))
        org_name = sr.scalar_one_or_none()
    if item.counterpartyId:
        sr = await db.execute(select(Organization.name).where(Organization.orgId == item.counterpartyId))
        counterparty_name = sr.scalar_one_or_none()
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ContractOut(
        contractId=item.contractId, contractNumber=item.contractNumber,
        orgId=item.orgId, orgName=org_name,
        counterpartyId=item.counterpartyId, counterpartyName=counterparty_name,
        storeId=item.storeId, storeName=store_name,
        contractType=item.contractType, startDate=item.startDate,
        endDate=item.endDate, amount=item.amount,
        paymentTerms=item.paymentTerms, attachmentUrls=item.attachmentUrls,
        status=item.status, signedAt=item.signedAt,
    )


@router.delete("/contracts/{contract_id}", dependencies=[Depends(get_current_user)])
async def delete_contract(contract_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Contract).where(Contract.contractId == contract_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "合同不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "合同已删除"}


# ═══════════════════════════════════════════
# Shareholder 股东
# ═══════════════════════════════════════════

@router.get("/shareholders", response_model=ShareholderListOut, dependencies=[Depends(get_optional_user)])
async def list_shareholders(
    type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List shareholders with optional filters and total dividend stats."""
    q = select(Shareholder)
    count_q = select(func.count(Shareholder.id)).select_from(Shareholder)
    sum_q = select(func.coalesce(func.sum(Shareholder.totalDividend), 0))

    if type:
        q = q.where(Shareholder.type == type)
        count_q = count_q.where(Shareholder.type == type)
        sum_q = sum_q.where(Shareholder.type == type)
    if status:
        q = q.where(Shareholder.status == status)
        count_q = count_q.where(Shareholder.status == status)
        sum_q = sum_q.where(Shareholder.status == status)
    if search:
        q = q.where(Shareholder.name.contains(search))
        count_q = count_q.where(Shareholder.name.contains(search))
        sum_q = sum_q.where(Shareholder.name.contains(search))

    q = q.order_by(Shareholder.createdAt.desc())

    total = (await db.execute(count_q)).scalar() or 0
    total_dividend = (await db.execute(sum_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [ShareholderOut(
        shareholderId=item.shareholderId, shareholderNumber=item.shareholderNumber,
        name=item.name, type=item.type, idType=item.idType,
        idNumber=item.idNumber, phone=item.phone, address=item.address,
        bankName=item.bankName, bankAccountName=item.bankAccountName,
        bankAccountNumber=item.bankAccountNumber,
        totalDividend=item.totalDividend or 0,
        status=item.status, exitDate=item.exitDate, exitReason=item.exitReason,
        createdAt=item.createdAt, updatedAt=item.updatedAt,
    ) for item in items]

    return ShareholderListOut(
        total=total, totalDividend=total_dividend,
        items=result, page=page, page_size=page_size,
    )


@router.get("/shareholders/{shareholder_id}", response_model=ShareholderOut, dependencies=[Depends(get_optional_user)])
async def get_shareholder(shareholder_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Shareholder).where(Shareholder.shareholderId == shareholder_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "股东不存在")
    return ShareholderOut(
        shareholderId=item.shareholderId, shareholderNumber=item.shareholderNumber,
        name=item.name, type=item.type, idType=item.idType,
        idNumber=item.idNumber, phone=item.phone, address=item.address,
        bankName=item.bankName, bankAccountName=item.bankAccountName,
        bankAccountNumber=item.bankAccountNumber,
        totalDividend=item.totalDividend or 0,
        status=item.status, exitDate=item.exitDate, exitReason=item.exitReason,
        createdAt=item.createdAt, updatedAt=item.updatedAt,
    )


@router.post("/shareholders", response_model=ShareholderOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_shareholder(
    data: ShareholderCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Shareholder(
        shareholderId=_gen_id(), shareholderNumber=data.shareholderNumber,
        name=data.name, type=data.type, idType=data.idType,
        idNumber=data.idNumber, phone=data.phone, address=data.address,
        bankName=data.bankName, bankAccountName=data.bankAccountName,
        bankAccountNumber=data.bankAccountNumber,
        totalDividend=data.totalDividend or 0,
        status=data.status or "Active",
        exitDate=data.exitDate, exitReason=data.exitReason,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return ShareholderOut(
        shareholderId=item.shareholderId, shareholderNumber=item.shareholderNumber,
        name=item.name, type=item.type, idType=item.idType,
        idNumber=item.idNumber, phone=item.phone, address=item.address,
        bankName=item.bankName, bankAccountName=item.bankAccountName,
        bankAccountNumber=item.bankAccountNumber,
        totalDividend=item.totalDividend or 0,
        status=item.status, exitDate=item.exitDate, exitReason=item.exitReason,
        createdAt=item.createdAt, updatedAt=item.updatedAt,
    )


@router.put("/shareholders/{shareholder_id}", response_model=ShareholderOut, dependencies=[Depends(get_current_user)])
async def update_shareholder(
    shareholder_id: str,
    data: ShareholderUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Shareholder).where(Shareholder.shareholderId == shareholder_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "股东不存在")
    if data.name is not None:
        item.name = data.name
    if data.type is not None:
        item.type = data.type
    if data.idType is not None:
        item.idType = data.idType
    if data.idNumber is not None:
        item.idNumber = data.idNumber
    if data.phone is not None:
        item.phone = data.phone
    if data.address is not None:
        item.address = data.address
    if data.bankName is not None:
        item.bankName = data.bankName
    if data.bankAccountName is not None:
        item.bankAccountName = data.bankAccountName
    if data.bankAccountNumber is not None:
        item.bankAccountNumber = data.bankAccountNumber
    if data.totalDividend is not None:
        item.totalDividend = data.totalDividend
    if data.status is not None:
        item.status = data.status
    if data.exitDate is not None:
        item.exitDate = data.exitDate
    if data.exitReason is not None:
        item.exitReason = data.exitReason
    await db.commit()
    await db.refresh(item)
    return ShareholderOut(
        shareholderId=item.shareholderId, shareholderNumber=item.shareholderNumber,
        name=item.name, type=item.type, idType=item.idType,
        idNumber=item.idNumber, phone=item.phone, address=item.address,
        bankName=item.bankName, bankAccountName=item.bankAccountName,
        bankAccountNumber=item.bankAccountNumber,
        totalDividend=item.totalDividend or 0,
        status=item.status, exitDate=item.exitDate, exitReason=item.exitReason,
        createdAt=item.createdAt, updatedAt=item.updatedAt,
    )


@router.delete("/shareholders/{shareholder_id}", dependencies=[Depends(get_current_user)])
async def delete_shareholder(shareholder_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Shareholder).where(Shareholder.shareholderId == shareholder_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "股东不存在")
    # Check for related investments
    inv_r = await db.execute(
        select(func.count(Investment.id)).where(Investment.shareholderId == shareholder_id)
    )
    if inv_r.scalar() > 0:
        raise HTTPException(400, "该股东存在投资记录，请先删除投资记录")
    await db.delete(item)
    await db.commit()
    return {"message": "股东已删除"}


# ═══════════════════════════════════════════
# Investment 投资
# ═══════════════════════════════════════════

@router.get("/investments", response_model=InvestmentListOut, dependencies=[Depends(get_optional_user)])
async def list_investments(
    shareholder_id: Optional[str] = Query(None, alias="shareholderId"),
    target_type: Optional[str] = Query(None, alias="targetType"),
    target_id: Optional[str] = Query(None, alias="targetId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List investments with optional filters."""
    q = select(Investment)
    count_q = select(func.count(Investment.id)).select_from(Investment)

    if shareholder_id:
        q = q.where(Investment.shareholderId == shareholder_id)
        count_q = count_q.where(Investment.shareholderId == shareholder_id)
    if target_type:
        q = q.where(Investment.targetType == target_type)
        count_q = count_q.where(Investment.targetType == target_type)
    if target_id:
        q = q.where(Investment.targetId == target_id)
        count_q = count_q.where(Investment.targetId == target_id)
    if status:
        q = q.where(Investment.status == status)
        count_q = count_q.where(Investment.status == status)

    q = q.order_by(Investment.investmentDate.desc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        shareholder_name = None
        if item.shareholderId:
            sr = await db.execute(
                select(Shareholder.name).where(Shareholder.shareholderId == item.shareholderId)
            )
            shareholder_name = sr.scalar_one_or_none()
        result.append(InvestmentOut(
            investmentId=item.investmentId, shareholderId=item.shareholderId,
            shareholderName=shareholder_name,
            targetType=item.targetType, targetId=item.targetId,
            shareRatio=item.shareRatio, investmentAmount=item.investmentAmount,
            investmentDate=item.investmentDate, exitDate=item.exitDate,
            status=item.status, changeLogs=item.changeLogs,
        ))

    return InvestmentListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/investments/{investment_id}", response_model=InvestmentOut, dependencies=[Depends(get_optional_user)])
async def get_investment(investment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Investment).where(Investment.investmentId == investment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "投资记录不存在")
    shareholder_name = None
    if item.shareholderId:
        sr = await db.execute(
            select(Shareholder.name).where(Shareholder.shareholderId == item.shareholderId)
        )
        shareholder_name = sr.scalar_one_or_none()
    return InvestmentOut(
        investmentId=item.investmentId, shareholderId=item.shareholderId,
        shareholderName=shareholder_name,
        targetType=item.targetType, targetId=item.targetId,
        shareRatio=item.shareRatio, investmentAmount=item.investmentAmount,
        investmentDate=item.investmentDate, exitDate=item.exitDate,
        status=item.status, changeLogs=item.changeLogs,
    )


@router.post("/investments", response_model=InvestmentOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_investment(
    data: InvestmentCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Investment(
        investmentId=_gen_id(), shareholderId=data.shareholderId,
        targetType=data.targetType, targetId=data.targetId,
        shareRatio=data.shareRatio, investmentAmount=data.investmentAmount,
        investmentDate=data.investmentDate, exitDate=data.exitDate,
        status=data.status or "Active", changeLogs=data.changeLogs,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    shareholder_name = None
    if item.shareholderId:
        sr = await db.execute(
            select(Shareholder.name).where(Shareholder.shareholderId == item.shareholderId)
        )
        shareholder_name = sr.scalar_one_or_none()
    return InvestmentOut(
        investmentId=item.investmentId, shareholderId=item.shareholderId,
        shareholderName=shareholder_name,
        targetType=item.targetType, targetId=item.targetId,
        shareRatio=item.shareRatio, investmentAmount=item.investmentAmount,
        investmentDate=item.investmentDate, exitDate=item.exitDate,
        status=item.status, changeLogs=item.changeLogs,
    )


@router.put("/investments/{investment_id}", response_model=InvestmentOut, dependencies=[Depends(get_current_user)])
async def update_investment(
    investment_id: str,
    data: InvestmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Investment).where(Investment.investmentId == investment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "投资记录不存在")
    if data.shareRatio is not None:
        item.shareRatio = data.shareRatio
    if data.investmentAmount is not None:
        item.investmentAmount = data.investmentAmount
    if data.investmentDate is not None:
        item.investmentDate = data.investmentDate
    if data.exitDate is not None:
        item.exitDate = data.exitDate
    if data.status is not None:
        item.status = data.status
    if data.changeLogs is not None:
        item.changeLogs = data.changeLogs
    await db.commit()
    await db.refresh(item)
    shareholder_name = None
    if item.shareholderId:
        sr = await db.execute(
            select(Shareholder.name).where(Shareholder.shareholderId == item.shareholderId)
        )
        shareholder_name = sr.scalar_one_or_none()
    return InvestmentOut(
        investmentId=item.investmentId, shareholderId=item.shareholderId,
        shareholderName=shareholder_name,
        targetType=item.targetType, targetId=item.targetId,
        shareRatio=item.shareRatio, investmentAmount=item.investmentAmount,
        investmentDate=item.investmentDate, exitDate=item.exitDate,
        status=item.status, changeLogs=item.changeLogs,
    )


@router.delete("/investments/{investment_id}", dependencies=[Depends(get_current_user)])
async def delete_investment(investment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Investment).where(Investment.investmentId == investment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "投资记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "投资记录已删除"}


# ═══════════════════════════════════════════
# Milestone 里程碑
# ═══════════════════════════════════════════

@router.get("/goals/{goal_id}/milestones", response_model=MilestoneListOut, dependencies=[Depends(get_optional_user)])
async def list_milestones(
    goal_id: str,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List milestones for a specific business goal."""
    q = select(Milestone).where(Milestone.goalId == goal_id)
    count_q = select(func.count(Milestone.id)).select_from(Milestone).where(
        Milestone.goalId == goal_id
    )

    if status:
        q = q.where(Milestone.status == status)
        count_q = count_q.where(Milestone.status == status)

    q = q.order_by(Milestone.sortOrder.asc().nullslast(), Milestone.plannedDate.asc())

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [MilestoneOut(
        milestoneId=item.milestoneId, goalId=item.goalId,
        name=item.name, description=item.description,
        plannedDate=item.plannedDate, actualDate=item.actualDate,
        status=item.status, sortOrder=item.sortOrder,
    ) for item in items]

    return MilestoneListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/milestones/{milestone_id}", response_model=MilestoneOut, dependencies=[Depends(get_optional_user)])
async def get_milestone(milestone_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Milestone).where(Milestone.milestoneId == milestone_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "里程碑不存在")
    return MilestoneOut(
        milestoneId=item.milestoneId, goalId=item.goalId,
        name=item.name, description=item.description,
        plannedDate=item.plannedDate, actualDate=item.actualDate,
        status=item.status, sortOrder=item.sortOrder,
    )


@router.post("/milestones", response_model=MilestoneOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_milestone(
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Milestone(
        milestoneId=_gen_id(), goalId=data.goalId,
        name=data.name, description=data.description,
        plannedDate=data.plannedDate, actualDate=data.actualDate,
        status=data.status or "Planned", sortOrder=data.sortOrder,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return MilestoneOut(
        milestoneId=item.milestoneId, goalId=item.goalId,
        name=item.name, description=item.description,
        plannedDate=item.plannedDate, actualDate=item.actualDate,
        status=item.status, sortOrder=item.sortOrder,
    )


@router.put("/milestones/{milestone_id}", response_model=MilestoneOut, dependencies=[Depends(get_current_user)])
async def update_milestone(
    milestone_id: str,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Milestone).where(Milestone.milestoneId == milestone_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "里程碑不存在")
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.plannedDate is not None:
        item.plannedDate = data.plannedDate
    if data.actualDate is not None:
        item.actualDate = data.actualDate
    if data.status is not None:
        item.status = data.status
    if data.sortOrder is not None:
        item.sortOrder = data.sortOrder
    await db.commit()
    await db.refresh(item)
    return MilestoneOut(
        milestoneId=item.milestoneId, goalId=item.goalId,
        name=item.name, description=item.description,
        plannedDate=item.plannedDate, actualDate=item.actualDate,
        status=item.status, sortOrder=item.sortOrder,
    )


@router.delete("/milestones/{milestone_id}", dependencies=[Depends(get_current_user)])
async def delete_milestone(milestone_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Milestone).where(Milestone.milestoneId == milestone_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "里程碑不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "里程碑已删除"}
