"""记账功能 API — 收入/支出/日结/月结/对账/分红/固定资产"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from datetime import datetime, date

from database import get_db
from models.finance import (
    RevenueFlow, ExpenseRecord, DailySettlement, MonthlySettlement,
    ReconciliationTicket, DividendRecord, FixedAsset,
)
from models.store_dev import Store
from models.user import User
from schemas.finance import (
    RevenueFlowCreate, RevenueFlowUpdate, RevenueFlowOut, RevenueFlowListOut,
    ExpenseRecordCreate, ExpenseRecordUpdate, ExpenseRecordOut, ExpenseRecordListOut,
    DailySettlementCreate, DailySettlementOut,
    MonthlySettlementOut,
    ReconciliationTicketCreate, ReconciliationTicketOut,
    DividendRecordOut,
    FixedAssetCreate, FixedAssetUpdate, FixedAssetOut, FixedAssetListOut,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/finance", tags=["记账管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ═══════════════════════════════════════════
# Revenue Flow 收入
# ═══════════════════════════════════════════

@router.get("/revenue", response_model=RevenueFlowListOut)
async def list_revenue(
    store_id: Optional[str] = Query(None, alias="storeId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List revenue flows with optional filters."""
    q = select(RevenueFlow)

    if store_id:
        q = q.where(RevenueFlow.storeId == store_id)
    if start_date:
        q = q.where(RevenueFlow.receivedAt >= start_date)
    if end_date:
        q = q.where(RevenueFlow.receivedAt <= end_date + " 23:59:59")
    if type:
        q = q.where(RevenueFlow.type == type)

    q = q.order_by(RevenueFlow.receivedAt.desc())

    # Total sum for the filtered set
    sum_q = select(func.coalesce(func.sum(RevenueFlow.amount), 0))
    if store_id:
        sum_q = sum_q.where(RevenueFlow.storeId == store_id)
    if start_date:
        sum_q = sum_q.where(RevenueFlow.receivedAt >= start_date)
    if end_date:
        sum_q = sum_q.where(RevenueFlow.receivedAt <= end_date + " 23:59:59")
    if type:
        sum_q = sum_q.where(RevenueFlow.type == type)

    total_sum = (await db.execute(sum_q)).scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    # Enrich with store name
    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(RevenueFlowOut(
            revenueId=item.revenueId,
            storeId=item.storeId,
            storeName=store_name,
            orderId=item.orderId,
            amount=item.amount,
            paymentMethod=item.paymentMethod,
            type=item.type,
            channel=item.channel,
            receivedAt=item.receivedAt,
            createdAt=item.createdAt,
        ))

    return RevenueFlowListOut(total=total_sum, items=result, page=page, page_size=page_size)


@router.get("/revenue/stats")
async def revenue_stats(
    store_id: Optional[str] = Query(None, alias="storeId"),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Revenue statistics grouped by day for charts."""
    from sqlalchemy import cast, Date
    since = datetime.utcnow().date().isoformat()
    # approximate: just subtract days
    import datetime as dt
    since_date = (datetime.utcnow() - dt.timedelta(days=days)).strftime("%Y-%m-%d")

    q = select(
        cast(RevenueFlow.receivedAt, Date).label("day"),
        func.sum(RevenueFlow.amount).label("total"),
        func.count(RevenueFlow.revenueId).label("count"),
    ).where(RevenueFlow.receivedAt >= since_date)

    if store_id:
        q = q.where(RevenueFlow.storeId == store_id)
    q = q.group_by(cast(RevenueFlow.receivedAt, Date)).order_by(cast(RevenueFlow.receivedAt, Date))

    r = await db.execute(q)
    rows = r.all()

    # Breakdown by type
    type_q = select(
        RevenueFlow.type,
        func.sum(RevenueFlow.amount).label("total"),
    )
    if store_id:
        type_q = type_q.where(RevenueFlow.storeId == store_id)
    type_q = type_q.group_by(RevenueFlow.type)
    type_r = await db.execute(type_q)
    type_rows = type_r.all()

    return {
        "daily": [{"date": str(row.day), "totalAmount": float(row.total), "orderCount": int(row.count)} for row in rows],
        "byType": [{"type": row.type, "total": float(row.total)} for row in type_rows],
        "totalRevenue": float(sum(r.total for r in rows)),
    }


@router.get("/revenue/{revenue_id}", response_model=RevenueFlowOut)
async def get_revenue(revenue_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RevenueFlow).where(RevenueFlow.revenueId == revenue_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "收入记录不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return RevenueFlowOut(
        revenueId=item.revenueId, storeId=item.storeId, storeName=store_name,
        orderId=item.orderId, amount=item.amount, paymentMethod=item.paymentMethod,
        type=item.type, channel=item.channel, receivedAt=item.receivedAt, createdAt=item.createdAt,
    )


@router.post("/revenue", response_model=RevenueFlowOut, status_code=201)
async def create_revenue(
    data: RevenueFlowCreate,
    db: AsyncSession = Depends(get_db),
):
    item = RevenueFlow(
        revenueId=_gen_id(), storeId=data.storeId, orderId=data.orderId,
        amount=data.amount, paymentMethod=data.paymentMethod, type=data.type,
        channel=data.channel, receivedAt=data.receivedAt or datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return RevenueFlowOut(
        revenueId=item.revenueId, storeId=item.storeId, storeName=store_name,
        orderId=item.orderId, amount=item.amount, paymentMethod=item.paymentMethod,
        type=item.type, channel=item.channel, receivedAt=item.receivedAt, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Expense 支出
# ═══════════════════════════════════════════

@router.get("/expenses", response_model=ExpenseRecordListOut)
async def list_expenses(
    store_id: Optional[str] = Query(None, alias="storeId"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ExpenseRecord)
    if store_id:
        q = q.where(ExpenseRecord.storeId == store_id)
    if category:
        q = q.where(ExpenseRecord.category == category)
    if status:
        q = q.where(ExpenseRecord.status == status)
    if start_date:
        q = q.where(ExpenseRecord.incurredDate >= start_date)
    if end_date:
        q = q.where(ExpenseRecord.incurredDate <= end_date)
    q = q.order_by(ExpenseRecord.createdAt.desc())

    # Total sum
    sum_q = select(func.coalesce(func.sum(ExpenseRecord.amount), 0))
    if store_id:
        sum_q = sum_q.where(ExpenseRecord.storeId == store_id)
    if category:
        sum_q = sum_q.where(ExpenseRecord.category == category)
    if status:
        sum_q = sum_q.where(ExpenseRecord.status == status)
    if start_date:
        sum_q = sum_q.where(ExpenseRecord.incurredDate >= start_date)
    if end_date:
        sum_q = sum_q.where(ExpenseRecord.incurredDate <= end_date)

    total_sum = (await db.execute(sum_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(ExpenseRecordOut(
            expenseId=item.expenseId, storeId=item.storeId, storeName=store_name,
            category=item.category, amount=item.amount, description=item.description,
            incurredDate=item.incurredDate, status=item.status,
            applicantId=item.applicantId, approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return ExpenseRecordListOut(total=total_sum, items=result, page=page, page_size=page_size)


@router.post("/expenses", response_model=ExpenseRecordOut, status_code=201)
async def create_expense(
    data: ExpenseRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ExpenseRecord(
        expenseId=_gen_id(), storeId=data.storeId, category=data.category,
        amount=data.amount, description=data.description,
        incurredDate=data.incurredDate, applicantId=data.applicantId,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ExpenseRecordOut(
        expenseId=item.expenseId, storeId=item.storeId, storeName=store_name,
        category=item.category, amount=item.amount, description=item.description,
        incurredDate=item.incurredDate, status=item.status,
        applicantId=item.applicantId, approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.put("/expenses/{expense_id}", response_model=ExpenseRecordOut)
async def update_expense(
    expense_id: str,
    data: ExpenseRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ExpenseRecord).where(ExpenseRecord.expenseId == expense_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "支出记录不存在")
    if data.category is not None:
        item.category = data.category
    if data.amount is not None:
        item.amount = data.amount
    if data.description is not None:
        item.description = data.description
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ExpenseRecordOut(
        expenseId=item.expenseId, storeId=item.storeId, storeName=store_name,
        category=item.category, amount=item.amount, description=item.description,
        incurredDate=item.incurredDate, status=item.status,
        applicantId=item.applicantId, approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Daily Settlement 日结
# ═══════════════════════════════════════════

@router.get("/settlements/daily", response_model=list[DailySettlementOut])
async def list_daily_settlements(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(DailySettlement)
    if store_id:
        q = q.where(DailySettlement.storeId == store_id)
    if status:
        q = q.where(DailySettlement.status == status)
    q = q.order_by(DailySettlement.settlementDate.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(DailySettlementOut(
            settlementId=item.settlementId, storeId=item.storeId, storeName=store_name,
            settlementDate=item.settlementDate,
            totalRevenue=item.totalRevenue, totalExpense=item.totalExpense,
            cashAmount=item.cashAmount, cardAmount=item.cardAmount,
            transferAmount=item.transferAmount, onlineAmount=item.onlineAmount,
            netAmount=item.netAmount, status=item.status,
            closedBy=item.closedBy, createdAt=item.createdAt,
        ))
    return result


@router.post("/settlements/daily", response_model=DailySettlementOut, status_code=201)
async def create_daily_settlement(
    data: DailySettlementCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check if settlement already exists for this store+date
    r = await db.execute(
        select(DailySettlement).where(
            DailySettlement.storeId == data.storeId,
            DailySettlement.settlementDate == data.settlementDate,
        )
    )
    if r.scalar_one_or_none():
        raise HTTPException(409, "该门店当日已存在日结记录")

    # Auto-calculate from revenue and expense records
    rev_sum = (await db.execute(
        select(func.coalesce(func.sum(RevenueFlow.amount), 0)).where(
            RevenueFlow.storeId == data.storeId,
            func.date(RevenueFlow.receivedAt) == data.settlementDate,
        )
    )).scalar() or 0

    exp_sum = (await db.execute(
        select(func.coalesce(func.sum(ExpenseRecord.amount), 0)).where(
            ExpenseRecord.storeId == data.storeId,
            ExpenseRecord.incurredDate == data.settlementDate,
        )
    )).scalar() or 0

    item = DailySettlement(
        settlementId=_gen_id(), storeId=data.storeId,
        settlementDate=data.settlementDate,
        totalRevenue=rev_sum, totalExpense=exp_sum,
        netAmount=round(rev_sum - exp_sum, 2),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return DailySettlementOut(
        settlementId=item.settlementId, storeId=item.storeId, storeName=store_name,
        settlementDate=item.settlementDate,
        totalRevenue=item.totalRevenue, totalExpense=item.totalExpense,
        cashAmount=item.cashAmount, cardAmount=item.cardAmount,
        transferAmount=item.transferAmount, onlineAmount=item.onlineAmount,
        netAmount=item.netAmount, status=item.status,
        closedBy=item.closedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Monthly Settlement 月结
# ═══════════════════════════════════════════

@router.get("/settlements/monthly", response_model=list[MonthlySettlementOut])
async def list_monthly_settlements(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    q = select(MonthlySettlement)
    if store_id:
        q = q.where(MonthlySettlement.storeId == store_id)
    q = q.order_by(MonthlySettlement.yearMonth.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(MonthlySettlementOut(
            settlementId=item.settlementId, storeId=item.storeId, storeName=store_name,
            yearMonth=item.yearMonth, totalRevenue=item.totalRevenue,
            totalExpense=item.totalExpense, netAmount=item.netAmount,
            dividendAmount=item.dividendAmount, status=item.status,
            closedBy=item.closedBy, createdAt=item.createdAt,
        ))
    return result


@router.post("/settlements/monthly/run", response_model=MonthlySettlementOut)
async def run_monthly_settlement(
    store_id: str = Query(..., alias="storeId"),
    year_month: str = Query(..., alias="yearMonth"),
    db: AsyncSession = Depends(get_db),
):
    """Trigger monthly settlement calculation for a store."""
    # Calculate from daily settlements
    rev_sum = (await db.execute(
        select(func.coalesce(func.sum(DailySettlement.totalRevenue), 0)).where(
            DailySettlement.storeId == store_id,
        )
    )).scalar() or 0

    exp_sum = (await db.execute(
        select(func.coalesce(func.sum(DailySettlement.totalExpense), 0)).where(
            DailySettlement.storeId == store_id,
        )
    )).scalar() or 0

    # Check existing
    r = await db.execute(
        select(MonthlySettlement).where(
            MonthlySettlement.storeId == store_id,
            MonthlySettlement.yearMonth == year_month,
        )
    )
    existing = r.scalar_one_or_none()
    if existing:
        existing.totalRevenue = rev_sum
        existing.totalExpense = exp_sum
        existing.netAmount = round(rev_sum - exp_sum, 2)
        existing.status = "Closed"
        item = existing
    else:
        item = MonthlySettlement(
            settlementId=_gen_id(), storeId=store_id, yearMonth=year_month,
            totalRevenue=rev_sum, totalExpense=exp_sum,
            netAmount=round(rev_sum - exp_sum, 2), status="Closed",
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return MonthlySettlementOut(
        settlementId=item.settlementId, storeId=item.storeId, storeName=store_name,
        yearMonth=item.yearMonth, totalRevenue=item.totalRevenue,
        totalExpense=item.totalExpense, netAmount=item.netAmount,
        dividendAmount=item.dividendAmount, status=item.status,
        closedBy=item.closedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Reconciliation 对账
# ═══════════════════════════════════════════

@router.get("/reconciliation/tickets", response_model=list[ReconciliationTicketOut])
async def list_reconciliation_tickets(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(ReconciliationTicket)
    if store_id:
        q = q.where(ReconciliationTicket.storeId == store_id)
    if status:
        q = q.where(ReconciliationTicket.status == status)
    q = q.order_by(ReconciliationTicket.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(ReconciliationTicketOut(
            ticketId=item.ticketId, storeId=item.storeId, storeName=store_name,
            period=item.period, totalRevenue=item.totalRevenue,
            totalExpense=item.totalExpense, netAmount=item.netAmount,
            status=item.status, createdBy=item.createdBy,
            confirmedBy=item.confirmedBy, createdAt=item.createdAt,
        ))
    return result


@router.post("/reconciliation/tickets", response_model=ReconciliationTicketOut, status_code=201)
async def create_reconciliation_ticket(
    data: ReconciliationTicketCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ReconciliationTicket(
        ticketId=_gen_id(), storeId=data.storeId, period=data.period,
        createdBy=data.createdBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ReconciliationTicketOut(
        ticketId=item.ticketId, storeId=item.storeId, storeName=store_name,
        period=item.period, totalRevenue=item.totalRevenue,
        totalExpense=item.totalExpense, netAmount=item.netAmount,
        status=item.status, createdBy=item.createdBy,
        confirmedBy=item.confirmedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Dividends 分红
# ═══════════════════════════════════════════

@router.get("/dividends", response_model=list[DividendRecordOut])
async def list_dividends(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(DividendRecord)
    if store_id:
        q = q.where(DividendRecord.storeId == store_id)
    if status:
        q = q.where(DividendRecord.status == status)
    q = q.order_by(DividendRecord.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(DividendRecordOut(
            dividendId=item.dividendId, monthlySettlementId=item.monthlySettlementId,
            shareholderId=item.shareholderId, storeId=item.storeId,
            storeName=store_name, amount=item.amount, ratio=item.ratio,
            paidAt=item.paidAt, status=item.status, createdAt=item.createdAt,
        ))
    return result


# ═══════════════════════════════════════════
# Fixed Assets 固定资产
# ═══════════════════════════════════════════

@router.get("/assets", response_model=FixedAssetListOut)
async def list_fixed_assets(
    store_id: Optional[str] = Query(None, alias="storeId"),
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(FixedAsset)
    if store_id:
        q = q.where(FixedAsset.storeId == store_id)
    if category:
        q = q.where(FixedAsset.category == category)
    if status:
        q = q.where(FixedAsset.status == status)
    if search:
        q = q.where(FixedAsset.name.contains(search))
    q = q.order_by(FixedAsset.createdAt.desc())

    # Count total
    count_q = select(func.count(FixedAsset.assetId)).select_from(FixedAsset)
    if store_id:
        count_q = count_q.where(FixedAsset.storeId == store_id)
    if category:
        count_q = count_q.where(FixedAsset.category == category)
    if status:
        count_q = count_q.where(FixedAsset.status == status)
    if search:
        count_q = count_q.where(FixedAsset.name.contains(search))

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
        result.append(FixedAssetOut(
            assetId=item.assetId, storeId=item.storeId, storeName=store_name,
            name=item.name, category=item.category,
            originalValue=item.originalValue, currentValue=item.currentValue,
            purchaseDate=item.purchaseDate, depreciationMethod=item.depreciationMethod,
            status=item.status, createdAt=item.createdAt,
        ))

    return FixedAssetListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/assets/{asset_id}", response_model=FixedAssetOut)
async def get_fixed_asset(asset_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(FixedAsset).where(FixedAsset.assetId == asset_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "资产不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return FixedAssetOut(
        assetId=item.assetId, storeId=item.storeId, storeName=store_name,
        name=item.name, category=item.category,
        originalValue=item.originalValue, currentValue=item.currentValue,
        purchaseDate=item.purchaseDate, depreciationMethod=item.depreciationMethod,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/assets", response_model=FixedAssetOut, status_code=201)
async def create_fixed_asset(
    data: FixedAssetCreate,
    db: AsyncSession = Depends(get_db),
):
    item = FixedAsset(
        assetId=_gen_id(), storeId=data.storeId, name=data.name,
        category=data.category, originalValue=data.originalValue,
        currentValue=data.originalValue,  # Initially equals original value
        purchaseDate=data.purchaseDate, depreciationMethod=data.depreciationMethod,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return FixedAssetOut(
        assetId=item.assetId, storeId=item.storeId, storeName=store_name,
        name=item.name, category=item.category,
        originalValue=item.originalValue, currentValue=item.currentValue,
        purchaseDate=item.purchaseDate, depreciationMethod=item.depreciationMethod,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/assets/{asset_id}", response_model=FixedAssetOut)
async def update_fixed_asset(
    asset_id: str,
    data: FixedAssetUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(FixedAsset).where(FixedAsset.assetId == asset_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "资产不存在")
    if data.name is not None:
        item.name = data.name
    if data.category is not None:
        item.category = data.category
    if data.originalValue is not None:
        item.originalValue = data.originalValue
    if data.currentValue is not None:
        item.currentValue = data.currentValue
    if data.purchaseDate is not None:
        item.purchaseDate = data.purchaseDate
    if data.depreciationMethod is not None:
        item.depreciationMethod = data.depreciationMethod
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return FixedAssetOut(
        assetId=item.assetId, storeId=item.storeId, storeName=store_name,
        name=item.name, category=item.category,
        originalValue=item.originalValue, currentValue=item.currentValue,
        purchaseDate=item.purchaseDate, depreciationMethod=item.depreciationMethod,
        status=item.status, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Dashboard Stats 记账总览
# ═══════════════════════════════════════════

@router.get("/dashboard")
async def finance_dashboard(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated finance stats for dashboard."""
    # Current month
    now = datetime.utcnow()
    month_start = now.strftime("%Y-%m") + "-01"
    next_month = f"{now.year}-{now.month + 1:02d}-01" if now.month < 12 else f"{now.year + 1}-01-01"

    # Revenue this month
    rev_q = select(func.coalesce(func.sum(RevenueFlow.amount), 0)).where(
        RevenueFlow.receivedAt >= month_start,
        RevenueFlow.receivedAt < next_month,
    )
    if store_id:
        rev_q = rev_q.where(RevenueFlow.storeId == store_id)
    month_revenue = (await db.execute(rev_q)).scalar() or 0

    # Expense this month
    exp_q = select(func.coalesce(func.sum(ExpenseRecord.amount), 0)).where(
        ExpenseRecord.incurredDate >= month_start,
        ExpenseRecord.incurredDate < next_month,
    )
    if store_id:
        exp_q = exp_q.where(ExpenseRecord.storeId == store_id)
    month_expense = (await db.execute(exp_q)).scalar() or 0

    # Pending expense count
    pending_q = select(func.count(ExpenseRecord.expenseId)).where(
        ExpenseRecord.status.in_(["Draft", "Submitted"])
    )
    if store_id:
        pending_q = pending_q.where(ExpenseRecord.storeId == store_id)
    pending_expenses = (await db.execute(pending_q)).scalar() or 0

    return {
        "monthRevenue": float(month_revenue),
        "monthExpense": float(month_expense),
        "monthNet": float(month_revenue - month_expense),
        "pendingExpenses": pending_expenses,
        "reportPeriod": now.strftime("%Y-%m"),
    }
