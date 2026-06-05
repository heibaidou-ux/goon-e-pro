"""D06 财务域（扩展）API — AccountSubject, FiscalCalendar, JournalEntry, Ledger, Budget, Advance, Reimburse, Payment, Payable, Depreciation, BankAccount, Invoice"""
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc, and_
from datetime import datetime, date

from database import get_db
from models.finance import (
    AccountSubject, FiscalCalendar, JournalEntry, JournalEntryLine,
    Ledger, Budget, AdvanceRequest, Reimbursement, Payment,
    AccountsPayable, DepreciationRecord, BankAccount, Invoice, FixedAsset,
)
from models.store_dev import Store, LegalEntity
from models.supply_chain import Supplier
from schemas.finance_ext import (
    AccountSubjectCreate, AccountSubjectUpdate, AccountSubjectOut, AccountSubjectListOut, AccountSubjectTreeNode,
    FiscalCalendarCreate, FiscalCalendarUpdate, FiscalCalendarOut, FiscalCalendarListOut,
    JournalEntryCreate, JournalEntryUpdate, JournalEntryOut, JournalEntryLineOut, JournalEntryListOut,
    LedgerCreate, LedgerUpdate, LedgerOut, LedgerListOut,
    BudgetCreate, BudgetUpdate, BudgetOut, BudgetListOut, BudgetComparisonItem, BudgetComparisonOut,
    AdvanceRequestCreate, AdvanceRequestUpdate, AdvanceRequestOut, AdvanceRequestListOut,
    ReimbursementCreate, ReimbursementUpdate, ReimbursementOut, ReimbursementListOut,
    PaymentCreate, PaymentUpdate, PaymentOut, PaymentListOut,
    AccountsPayableCreate, AccountsPayableUpdate, AccountsPayableOut, AccountsPayableListOut,
    AccountsPayableAgingItem, AccountsPayableAgingOut,
    DepreciationRecordCreate, DepreciationRecordUpdate, DepreciationRecordOut, DepreciationRecordListOut,
    BankAccountCreate, BankAccountUpdate, BankAccountOut, BankAccountListOut,
    InvoiceCreate, InvoiceUpdate, InvoiceOut, InvoiceListOut,
)

router = APIRouter(prefix="/api/finance-ext", tags=["财务管理（扩展）"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ═══════════════════════════════════════════════════════
# AccountSubject 会计科目
# ═══════════════════════════════════════════════════════

def _build_subject_tree(subjects: list[AccountSubject], parent_id: Optional[str] = None) -> list[dict]:
    """Recursively build account subject tree."""
    tree = []
    for s in subjects:
        if s.parentId == parent_id:
            node = AccountSubjectTreeNode(
                subjectId=s.subjectId, code=s.code, name=s.name,
                parentId=s.parentId, level=s.level, type=s.type,
                direction=s.direction, isLeaf=s.isLeaf, status=s.status,
            )
            children = _build_subject_tree(subjects, s.subjectId)
            node.children = children
            tree.append(node)
    return tree


@router.get("/account-subjects", response_model=AccountSubjectListOut)
async def list_account_subjects(
    type: Optional[str] = None,
    level: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AccountSubject)
    if type:
        q = q.where(AccountSubject.type == type)
    if level is not None:
        q = q.where(AccountSubject.level == level)
    if status:
        q = q.where(AccountSubject.status == status)
    if search:
        q = q.where(or_(
            AccountSubject.name.contains(search),
            AccountSubject.code.contains(search),
        ))
    q = q.order_by(AccountSubject.code.asc())

    count_q = select(func.count(AccountSubject.subjectId)).select_from(AccountSubject)
    if type:
        count_q = count_q.where(AccountSubject.type == type)
    if level is not None:
        count_q = count_q.where(AccountSubject.level == level)
    if status:
        count_q = count_q.where(AccountSubject.status == status)
    if search:
        count_q = count_q.where(or_(
            AccountSubject.name.contains(search),
            AccountSubject.code.contains(search),
        ))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return AccountSubjectListOut(
        total=total,
        items=[AccountSubjectOut.model_validate(s) for s in items],
        page=page, page_size=page_size,
    )


@router.get("/account-subjects/tree", response_model=List[AccountSubjectTreeNode])
async def get_account_subject_tree(
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get account subject tree structure."""
    q = select(AccountSubject).order_by(AccountSubject.code.asc())
    if type:
        q = q.where(AccountSubject.type == type)
    r = await db.execute(q)
    subjects = r.scalars().all()
    return _build_subject_tree(subjects)


@router.get("/account-subjects/{subject_id}", response_model=AccountSubjectOut)
async def get_account_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AccountSubject).where(AccountSubject.subjectId == subject_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计科目不存在")
    return AccountSubjectOut.model_validate(item)


@router.post("/account-subjects", response_model=AccountSubjectOut, status_code=201)
async def create_account_subject(
    data: AccountSubjectCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check code uniqueness
    r = await db.execute(select(AccountSubject).where(AccountSubject.code == data.code))
    if r.scalar_one_or_none():
        raise HTTPException(409, "科目编码已存在")

    # If parentId provided, update parent's isLeaf
    if data.parentId:
        pr = await db.execute(select(AccountSubject).where(AccountSubject.subjectId == data.parentId))
        parent = pr.scalar_one_or_none()
        if not parent:
            raise HTTPException(404, "父级科目不存在")
        if parent.isLeaf:
            parent.isLeaf = False

    item = AccountSubject(
        subjectId=_gen_id(), code=data.code, name=data.name,
        parentId=data.parentId, level=data.level, type=data.type,
        direction=data.direction, isLeaf=data.isLeaf, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return AccountSubjectOut.model_validate(item)


@router.put("/account-subjects/{subject_id}", response_model=AccountSubjectOut)
async def update_account_subject(
    subject_id: str,
    data: AccountSubjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(AccountSubject).where(AccountSubject.subjectId == subject_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计科目不存在")
    if data.name is not None:
        item.name = data.name
    if data.parentId is not None:
        item.parentId = data.parentId
    if data.level is not None:
        item.level = data.level
    if data.type is not None:
        item.type = data.type
    if data.direction is not None:
        item.direction = data.direction
    if data.isLeaf is not None:
        item.isLeaf = data.isLeaf
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return AccountSubjectOut.model_validate(item)


@router.delete("/account-subjects/{subject_id}")
async def delete_account_subject(subject_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AccountSubject).where(AccountSubject.subjectId == subject_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计科目不存在")
    # Check if has children
    child_r = await db.execute(select(AccountSubject).where(AccountSubject.parentId == subject_id).limit(1))
    if child_r.scalar_one_or_none():
        raise HTTPException(400, "该科目存在子科目，无法删除")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


# ═══════════════════════════════════════════════════════
# FiscalCalendar 会计日历
# ═══════════════════════════════════════════════════════

@router.get("/fiscal-calendars", response_model=FiscalCalendarListOut)
async def list_fiscal_calendars(
    year: Optional[int] = None,
    is_closed: Optional[bool] = Query(None, alias="isClosed"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(FiscalCalendar)
    if year is not None:
        q = q.where(FiscalCalendar.year == year)
    if is_closed is not None:
        q = q.where(FiscalCalendar.isClosed == is_closed)
    q = q.order_by(FiscalCalendar.year.desc(), FiscalCalendar.periodStart.desc())

    count_q = select(func.count(FiscalCalendar.calendarId)).select_from(FiscalCalendar)
    if year is not None:
        count_q = count_q.where(FiscalCalendar.year == year)
    if is_closed is not None:
        count_q = count_q.where(FiscalCalendar.isClosed == is_closed)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return FiscalCalendarListOut(
        total=total,
        items=[FiscalCalendarOut.model_validate(s) for s in items],
        page=page, page_size=page_size,
    )


@router.get("/fiscal-calendars/{calendar_id}", response_model=FiscalCalendarOut)
async def get_fiscal_calendar(calendar_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(FiscalCalendar).where(FiscalCalendar.calendarId == calendar_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计日历不存在")
    return FiscalCalendarOut.model_validate(item)


@router.post("/fiscal-calendars", response_model=FiscalCalendarOut, status_code=201)
async def create_fiscal_calendar(
    data: FiscalCalendarCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check overlapping periods for same year
    r = await db.execute(
        select(FiscalCalendar).where(
            FiscalCalendar.year == data.year,
            FiscalCalendar.periodStart <= data.periodEnd,
            FiscalCalendar.periodEnd >= data.periodStart,
        ).limit(1)
    )
    if r.scalar_one_or_none():
        raise HTTPException(409, "该年度存在重叠的会计期间")

    item = FiscalCalendar(
        calendarId=_gen_id(), year=data.year,
        periodStart=data.periodStart, periodEnd=data.periodEnd,
        isClosed=data.isClosed, closedBy=data.closedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return FiscalCalendarOut.model_validate(item)


@router.put("/fiscal-calendars/{calendar_id}", response_model=FiscalCalendarOut)
async def update_fiscal_calendar(
    calendar_id: str,
    data: FiscalCalendarUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(FiscalCalendar).where(FiscalCalendar.calendarId == calendar_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计日历不存在")
    if data.periodStart is not None:
        item.periodStart = data.periodStart
    if data.periodEnd is not None:
        item.periodEnd = data.periodEnd
    if data.isClosed is not None:
        item.isClosed = data.isClosed
    if data.closedBy is not None:
        item.closedBy = data.closedBy
    if data.closedAt is not None:
        item.closedAt = data.closedAt
    await db.commit()
    await db.refresh(item)
    return FiscalCalendarOut.model_validate(item)


@router.post("/fiscal-calendars/{calendar_id}/close")
async def close_fiscal_calendar(
    calendar_id: str,
    closed_by: str = Query(..., alias="closedBy"),
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(FiscalCalendar).where(FiscalCalendar.calendarId == calendar_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "会计日历不存在")
    if item.isClosed:
        raise HTTPException(400, "该会计期间已结账")
    item.isClosed = True
    item.closedBy = closed_by
    item.closedAt = datetime.utcnow()
    await db.commit()
    await db.refresh(item)
    return FiscalCalendarOut.model_validate(item)


# ═══════════════════════════════════════════════════════
# JournalEntry 记账凭证
# ═══════════════════════════════════════════════════════

@router.get("/journal-entries", response_model=JournalEntryListOut)
async def list_journal_entries(
    period_id: Optional[str] = Query(None, alias="periodId"),
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(JournalEntry)
    if period_id:
        q = q.where(JournalEntry.periodId == period_id)
    if status:
        q = q.where(JournalEntry.status == status)
    if start_date:
        q = q.where(JournalEntry.entryDate >= start_date)
    if end_date:
        q = q.where(JournalEntry.entryDate <= end_date)
    if search:
        q = q.where(or_(
            JournalEntry.entryNumber.contains(search),
            JournalEntry.summary.contains(search),
        ))
    q = q.order_by(JournalEntry.createdAt.desc())

    count_q = select(func.count(JournalEntry.entryId)).select_from(JournalEntry)
    if period_id:
        count_q = count_q.where(JournalEntry.periodId == period_id)
    if status:
        count_q = count_q.where(JournalEntry.status == status)
    if start_date:
        count_q = count_q.where(JournalEntry.entryDate >= start_date)
    if end_date:
        count_q = count_q.where(JournalEntry.entryDate <= end_date)
    if search:
        count_q = count_q.where(or_(
            JournalEntry.entryNumber.contains(search),
            JournalEntry.summary.contains(search),
        ))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        lines_r = await db.execute(
            select(JournalEntryLine).where(JournalEntryLine.entryId == item.entryId)
        )
        lines = lines_r.scalars().all()
        result.append(JournalEntryOut(
            entryId=item.entryId, periodId=item.periodId,
            entryNumber=item.entryNumber, entryDate=item.entryDate,
            summary=item.summary, attachmentCount=item.attachmentCount,
            status=item.status, createdBy=item.createdBy,
            approvedBy=item.approvedBy, createdAt=item.createdAt,
            lines=[JournalEntryLineOut(
                lineId=ln.lineId, entryId=ln.entryId, subjectId=ln.subjectId,
                direction=ln.direction, amount=ln.amount, summary=ln.summary,
            ) for ln in lines],
        ))

    return JournalEntryListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/journal-entries/{entry_id}", response_model=JournalEntryOut)
async def get_journal_entry(entry_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(JournalEntry).where(JournalEntry.entryId == entry_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "记账凭证不存在")

    lines_r = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.entryId == item.entryId)
    )
    lines = lines_r.scalars().all()

    return JournalEntryOut(
        entryId=item.entryId, periodId=item.periodId,
        entryNumber=item.entryNumber, entryDate=item.entryDate,
        summary=item.summary, attachmentCount=item.attachmentCount,
        status=item.status, createdBy=item.createdBy,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
        lines=[JournalEntryLineOut(
            lineId=ln.lineId, entryId=ln.entryId, subjectId=ln.subjectId,
            direction=ln.direction, amount=ln.amount, summary=ln.summary,
        ) for ln in lines],
    )


@router.post("/journal-entries", response_model=JournalEntryOut, status_code=201)
async def create_journal_entry(
    data: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    # Validate period exists
    pr = await db.execute(select(FiscalCalendar).where(FiscalCalendar.calendarId == data.periodId))
    if not pr.scalar_one_or_none():
        raise HTTPException(404, "会计期间不存在")

    # Validate entry number uniqueness
    nr = await db.execute(select(JournalEntry).where(JournalEntry.entryNumber == data.entryNumber))
    if nr.scalar_one_or_none():
        raise HTTPException(409, "凭证编号已存在")

    # Validate debit = credit
    total_debit = sum(ln.amount for ln in data.lines if ln.direction == "Debit")
    total_credit = sum(ln.amount for ln in data.lines if ln.direction == "Credit")
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(400, f"借贷不平衡：借方 {total_debit} ≠ 贷方 {total_credit}")

    # Validate at least one line with each direction
    if not data.lines:
        raise HTTPException(400, "凭证至少需要一条分录")

    # Create entry
    entry = JournalEntry(
        entryId=_gen_id(), periodId=data.periodId,
        entryNumber=data.entryNumber, entryDate=data.entryDate,
        summary=data.summary, attachmentCount=data.attachmentCount,
        status="Draft", createdBy=data.createdBy,
    )
    db.add(entry)
    await db.flush()

    # Create lines
    for ln_data in data.lines:
        # Validate subject exists
        sr = await db.execute(
            select(AccountSubject).where(AccountSubject.subjectId == ln_data.subjectId)
        )
        if not sr.scalar_one_or_none():
            raise HTTPException(404, f"会计科目 {ln_data.subjectId} 不存在")

        line = JournalEntryLine(
            lineId=_gen_id(), entryId=entry.entryId,
            subjectId=ln_data.subjectId, direction=ln_data.direction,
            amount=ln_data.amount, summary=ln_data.summary,
        )
        db.add(line)

    await db.commit()
    await db.refresh(entry)

    # Fetch lines
    lines_r = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.entryId == entry.entryId)
    )
    lines = lines_r.scalars().all()

    return JournalEntryOut(
        entryId=entry.entryId, periodId=entry.periodId,
        entryNumber=entry.entryNumber, entryDate=entry.entryDate,
        summary=entry.summary, attachmentCount=entry.attachmentCount,
        status=entry.status, createdBy=entry.createdBy,
        approvedBy=entry.approvedBy, createdAt=entry.createdAt,
        lines=[JournalEntryLineOut(
            lineId=ln.lineId, entryId=ln.entryId, subjectId=ln.subjectId,
            direction=ln.direction, amount=ln.amount, summary=ln.summary,
        ) for ln in lines],
    )


@router.put("/journal-entries/{entry_id}", response_model=JournalEntryOut)
async def update_journal_entry(
    entry_id: str,
    data: JournalEntryUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(JournalEntry).where(JournalEntry.entryId == entry_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "记账凭证不存在")
    if item.status == "Posted":
        raise HTTPException(400, "已过账凭证不可修改")

    if data.summary is not None:
        item.summary = data.summary
    if data.attachmentCount is not None:
        item.attachmentCount = data.attachmentCount
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy

    # If lines provided, replace all
    if data.lines is not None:
        # Delete existing lines
        old_lines = await db.execute(
            select(JournalEntryLine).where(JournalEntryLine.entryId == entry_id)
        )
        for old in old_lines.scalars().all():
            await db.delete(old)

        # Validate debit = credit
        total_debit = sum(ln.amount for ln in data.lines if ln.direction == "Debit")
        total_credit = sum(ln.amount for ln in data.lines if ln.direction == "Credit")
        if abs(total_debit - total_credit) > 0.01:
            raise HTTPException(400, f"借贷不平衡：借方 {total_debit} ≠ 贷方 {total_credit}")

        # Create new lines
        for ln_data in data.lines:
            line = JournalEntryLine(
                lineId=_gen_id(), entryId=entry_id,
                subjectId=ln_data.subjectId, direction=ln_data.direction,
                amount=ln_data.amount, summary=ln_data.summary,
            )
            db.add(line)

    await db.commit()
    await db.refresh(item)

    lines_r = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.entryId == item.entryId)
    )
    lines = lines_r.scalars().all()

    return JournalEntryOut(
        entryId=item.entryId, periodId=item.periodId,
        entryNumber=item.entryNumber, entryDate=item.entryDate,
        summary=item.summary, attachmentCount=item.attachmentCount,
        status=item.status, createdBy=item.createdBy,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
        lines=[JournalEntryLineOut(
            lineId=ln.lineId, entryId=ln.entryId, subjectId=ln.subjectId,
            direction=ln.direction, amount=ln.amount, summary=ln.summary,
        ) for ln in lines],
    )


@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(
    entry_id: str,
    approved_by: str = Query(..., alias="approvedBy"),
    db: AsyncSession = Depends(get_db),
):
    """Post a journal entry — validate debit=credit and update status to Posted."""
    r = await db.execute(select(JournalEntry).where(JournalEntry.entryId == entry_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "记账凭证不存在")
    if item.status != "Draft":
        raise HTTPException(400, f"当前状态为 {item.status}，仅草稿凭证可过账")

    # Fetch lines
    lines_r = await db.execute(
        select(JournalEntryLine).where(JournalEntryLine.entryId == entry_id)
    )
    lines = lines_r.scalars().all()
    if not lines:
        raise HTTPException(400, "凭证无分录，无法过账")

    total_debit = sum(ln.amount for ln in lines if ln.direction == "Debit")
    total_credit = sum(ln.amount for ln in lines if ln.direction == "Credit")
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(400, f"借贷不平衡（借方 {total_debit} ≠ 贷方 {total_credit}），无法过账")

    item.status = "Posted"
    item.approvedBy = approved_by
    await db.commit()
    await db.refresh(item)

    return JournalEntryOut(
        entryId=item.entryId, periodId=item.periodId,
        entryNumber=item.entryNumber, entryDate=item.entryDate,
        summary=item.summary, attachmentCount=item.attachmentCount,
        status=item.status, createdBy=item.createdBy,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
        lines=[JournalEntryLineOut(
            lineId=ln.lineId, entryId=ln.entryId, subjectId=ln.subjectId,
            direction=ln.direction, amount=ln.amount, summary=ln.summary,
        ) for ln in lines],
    )


@router.delete("/journal-entries/{entry_id}")
async def delete_journal_entry(entry_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(JournalEntry).where(JournalEntry.entryId == entry_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "记账凭证不存在")
    if item.status == "Posted":
        raise HTTPException(400, "已过账凭证不可删除")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


# ═══════════════════════════════════════════════════════
# Ledger 分类账
# ═══════════════════════════════════════════════════════

@router.get("/ledgers", response_model=LedgerListOut)
async def list_ledgers(
    subject_id: Optional[str] = Query(None, alias="subjectId"),
    period_id: Optional[str] = Query(None, alias="periodId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Ledger)
    if subject_id:
        q = q.where(Ledger.subjectId == subject_id)
    if period_id:
        q = q.where(Ledger.periodId == period_id)
    q = q.order_by(Ledger.createdAt.desc())

    count_q = select(func.count(Ledger.ledgerId)).select_from(Ledger)
    if subject_id:
        count_q = count_q.where(Ledger.subjectId == subject_id)
    if period_id:
        count_q = count_q.where(Ledger.periodId == period_id)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return LedgerListOut(
        total=total,
        items=[LedgerOut.model_validate(s) for s in items],
        page=page, page_size=page_size,
    )


@router.get("/ledgers/{ledger_id}", response_model=LedgerOut)
async def get_ledger(ledger_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Ledger).where(Ledger.ledgerId == ledger_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "分类账记录不存在")
    return LedgerOut.model_validate(item)


@router.post("/ledgers", response_model=LedgerOut, status_code=201)
async def create_ledger(
    data: LedgerCreate,
    db: AsyncSession = Depends(get_db),
):
    # Validate subject and period
    sr = await db.execute(select(AccountSubject).where(AccountSubject.subjectId == data.subjectId))
    if not sr.scalar_one_or_none():
        raise HTTPException(404, "会计科目不存在")
    pr = await db.execute(select(FiscalCalendar).where(FiscalCalendar.calendarId == data.periodId))
    if not pr.scalar_one_or_none():
        raise HTTPException(404, "会计期间不存在")

    item = Ledger(
        ledgerId=_gen_id(), subjectId=data.subjectId, periodId=data.periodId,
        openingBalance=data.openingBalance, debitAmount=data.debitAmount,
        creditAmount=data.creditAmount, closingBalance=data.closingBalance,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return LedgerOut.model_validate(item)


@router.put("/ledgers/{ledger_id}", response_model=LedgerOut)
async def update_ledger(
    ledger_id: str,
    data: LedgerUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Ledger).where(Ledger.ledgerId == ledger_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "分类账记录不存在")
    if data.openingBalance is not None:
        item.openingBalance = data.openingBalance
    if data.debitAmount is not None:
        item.debitAmount = data.debitAmount
    if data.creditAmount is not None:
        item.creditAmount = data.creditAmount
    if data.closingBalance is not None:
        item.closingBalance = data.closingBalance
    await db.commit()
    await db.refresh(item)
    return LedgerOut.model_validate(item)


# ═══════════════════════════════════════════════════════
# Budget 预算
# ═══════════════════════════════════════════════════════

@router.get("/budgets", response_model=BudgetListOut)
async def list_budgets(
    store_id: Optional[str] = Query(None, alias="storeId"),
    org_id: Optional[str] = Query(None, alias="orgId"),
    year: Optional[int] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Budget)
    if store_id:
        q = q.where(Budget.storeId == store_id)
    if org_id:
        q = q.where(Budget.orgId == org_id)
    if year is not None:
        q = q.where(Budget.year == year)
    if category:
        q = q.where(Budget.category == category)
    q = q.order_by(Budget.createdAt.desc())

    count_q = select(func.count(Budget.budgetId)).select_from(Budget)
    if store_id:
        count_q = count_q.where(Budget.storeId == store_id)
    if org_id:
        count_q = count_q.where(Budget.orgId == org_id)
    if year is not None:
        count_q = count_q.where(Budget.year == year)
    if category:
        count_q = count_q.where(Budget.category == category)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return BudgetListOut(
        total=total,
        items=[BudgetOut.model_validate(s) for s in items],
        page=page, page_size=page_size,
    )


@router.get("/budgets/comparison", response_model=BudgetComparisonOut)
async def budget_comparison(
    store_id: Optional[str] = Query(None, alias="storeId"),
    year: int = Query(..., ge=2000, le=2100),
    db: AsyncSession = Depends(get_db),
):
    """Budget vs actual comparison for a store/year."""
    q = select(Budget).where(Budget.year == year)
    if store_id:
        q = q.where(Budget.storeId == store_id)
    r = await db.execute(q)
    budgets = r.scalars().all()

    items = []
    total_budget = 0.0
    total_actual = 0.0
    for b in budgets:
        variance = b.budgetAmount - b.actualAmount
        variance_rate = round((variance / b.budgetAmount * 100), 2) if b.budgetAmount else 0
        items.append(BudgetComparisonItem(
            budgetId=b.budgetId, category=b.category,
            budgetAmount=b.budgetAmount, actualAmount=b.actualAmount,
            variance=round(variance, 2), varianceRate=variance_rate,
        ))
        total_budget += b.budgetAmount
        total_actual += b.actualAmount

    store_name = None
    if store_id:
        sr = await db.execute(select(Store.name).where(Store.storeId == store_id))
        store_name = sr.scalar_one_or_none()

    return BudgetComparisonOut(
        year=year, storeId=store_id, storeName=store_name,
        items=items, totalBudget=round(total_budget, 2),
        totalActual=round(total_actual, 2),
        totalVariance=round(total_budget - total_actual, 2),
    )


@router.get("/budgets/{budget_id}", response_model=BudgetOut)
async def get_budget(budget_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Budget).where(Budget.budgetId == budget_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预算记录不存在")
    return BudgetOut.model_validate(item)


@router.post("/budgets", response_model=BudgetOut, status_code=201)
async def create_budget(
    data: BudgetCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Budget(
        budgetId=_gen_id(), orgId=data.orgId, storeId=data.storeId,
        year=data.year, month=data.month, category=data.category,
        budgetAmount=data.budgetAmount, actualAmount=data.actualAmount,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return BudgetOut.model_validate(item)


@router.put("/budgets/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: str,
    data: BudgetUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Budget).where(Budget.budgetId == budget_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预算记录不存在")
    if data.budgetAmount is not None:
        item.budgetAmount = data.budgetAmount
    if data.actualAmount is not None:
        item.actualAmount = data.actualAmount
    if data.category is not None:
        item.category = data.category
    await db.commit()
    await db.refresh(item)
    return BudgetOut.model_validate(item)


@router.delete("/budgets/{budget_id}")
async def delete_budget(budget_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Budget).where(Budget.budgetId == budget_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预算记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


# ═══════════════════════════════════════════════════════
# AdvanceRequest 预支申请
# ═══════════════════════════════════════════════════════

@router.get("/advance-requests", response_model=AdvanceRequestListOut)
async def list_advance_requests(
    store_id: Optional[str] = Query(None, alias="storeId"),
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AdvanceRequest)
    if store_id:
        q = q.where(AdvanceRequest.storeId == store_id)
    if employee_id:
        q = q.where(AdvanceRequest.employeeId == employee_id)
    if status:
        q = q.where(AdvanceRequest.status == status)
    q = q.order_by(AdvanceRequest.createdAt.desc())

    count_q = select(func.count(AdvanceRequest.advanceId)).select_from(AdvanceRequest)
    if store_id:
        count_q = count_q.where(AdvanceRequest.storeId == store_id)
    if employee_id:
        count_q = count_q.where(AdvanceRequest.employeeId == employee_id)
    if status:
        count_q = count_q.where(AdvanceRequest.status == status)
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
        result.append(AdvanceRequestOut(
            advanceId=item.advanceId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, amount=item.amount,
            purpose=item.purpose, expectedRepayDate=item.expectedRepayDate,
            status=item.status, approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return AdvanceRequestListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/advance-requests/pending", response_model=List[AdvanceRequestOut])
async def get_pending_advance_requests(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Get all pending advance requests for approval."""
    q = select(AdvanceRequest).where(AdvanceRequest.status == "Pending")
    if store_id:
        q = q.where(AdvanceRequest.storeId == store_id)
    q = q.order_by(AdvanceRequest.createdAt.asc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = None
        if item.storeId:
            sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
            store_name = sr.scalar_one_or_none()
        result.append(AdvanceRequestOut(
            advanceId=item.advanceId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, amount=item.amount,
            purpose=item.purpose, expectedRepayDate=item.expectedRepayDate,
            status=item.status, approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))
    return result


@router.get("/advance-requests/{advance_id}", response_model=AdvanceRequestOut)
async def get_advance_request(advance_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AdvanceRequest).where(AdvanceRequest.advanceId == advance_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预支申请不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return AdvanceRequestOut(
        advanceId=item.advanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        purpose=item.purpose, expectedRepayDate=item.expectedRepayDate,
        status=item.status, approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.post("/advance-requests", response_model=AdvanceRequestOut, status_code=201)
async def create_advance_request(
    data: AdvanceRequestCreate,
    db: AsyncSession = Depends(get_db),
):
    item = AdvanceRequest(
        advanceId=_gen_id(), storeId=data.storeId, employeeId=data.employeeId,
        amount=data.amount, purpose=data.purpose,
        expectedRepayDate=data.expectedRepayDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return AdvanceRequestOut(
        advanceId=item.advanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        purpose=item.purpose, expectedRepayDate=item.expectedRepayDate,
        status=item.status, approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.put("/advance-requests/{advance_id}", response_model=AdvanceRequestOut)
async def update_advance_request(
    advance_id: str,
    data: AdvanceRequestUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(AdvanceRequest).where(AdvanceRequest.advanceId == advance_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "预支申请不存在")
    if data.amount is not None:
        item.amount = data.amount
    if data.purpose is not None:
        item.purpose = data.purpose
    if data.expectedRepayDate is not None:
        item.expectedRepayDate = data.expectedRepayDate
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
    return AdvanceRequestOut(
        advanceId=item.advanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        purpose=item.purpose, expectedRepayDate=item.expectedRepayDate,
        status=item.status, approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════
# Reimbursement 报销
# ═══════════════════════════════════════════════════════

@router.get("/reimbursements", response_model=ReimbursementListOut)
async def list_reimbursements(
    store_id: Optional[str] = Query(None, alias="storeId"),
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    status: Optional[str] = None,
    expense_type: Optional[str] = Query(None, alias="expenseType"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Reimbursement)
    if store_id:
        q = q.where(Reimbursement.storeId == store_id)
    if employee_id:
        q = q.where(Reimbursement.employeeId == employee_id)
    if status:
        q = q.where(Reimbursement.status == status)
    if expense_type:
        q = q.where(Reimbursement.expenseType == expense_type)
    q = q.order_by(Reimbursement.createdAt.desc())

    count_q = select(func.count(Reimbursement.reimbursementId)).select_from(Reimbursement)
    if store_id:
        count_q = count_q.where(Reimbursement.storeId == store_id)
    if employee_id:
        count_q = count_q.where(Reimbursement.employeeId == employee_id)
    if status:
        count_q = count_q.where(Reimbursement.status == status)
    if expense_type:
        count_q = count_q.where(Reimbursement.expenseType == expense_type)
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
        result.append(ReimbursementOut(
            reimbursementId=item.reimbursementId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, amount=item.amount,
            expenseType=item.expenseType, description=item.description,
            receiptUrls=item.receiptUrls, status=item.status,
            approvedBy=item.approvedBy, paidAt=item.paidAt, createdAt=item.createdAt,
        ))

    return ReimbursementListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/reimbursements/{reimbursement_id}", response_model=ReimbursementOut)
async def get_reimbursement(reimbursement_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Reimbursement).where(Reimbursement.reimbursementId == reimbursement_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "报销记录不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ReimbursementOut(
        reimbursementId=item.reimbursementId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        expenseType=item.expenseType, description=item.description,
        receiptUrls=item.receiptUrls, status=item.status,
        approvedBy=item.approvedBy, paidAt=item.paidAt, createdAt=item.createdAt,
    )


@router.post("/reimbursements", response_model=ReimbursementOut, status_code=201)
async def create_reimbursement(
    data: ReimbursementCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Reimbursement(
        reimbursementId=_gen_id(), storeId=data.storeId,
        employeeId=data.employeeId, amount=data.amount,
        expenseType=data.expenseType, description=data.description,
        receiptUrls=data.receiptUrls,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ReimbursementOut(
        reimbursementId=item.reimbursementId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        expenseType=item.expenseType, description=item.description,
        receiptUrls=item.receiptUrls, status=item.status,
        approvedBy=item.approvedBy, paidAt=item.paidAt, createdAt=item.createdAt,
    )


@router.put("/reimbursements/{reimbursement_id}", response_model=ReimbursementOut)
async def update_reimbursement(
    reimbursement_id: str,
    data: ReimbursementUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Reimbursement).where(Reimbursement.reimbursementId == reimbursement_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "报销记录不存在")
    if data.amount is not None:
        item.amount = data.amount
    if data.expenseType is not None:
        item.expenseType = data.expenseType
    if data.description is not None:
        item.description = data.description
    if data.receiptUrls is not None:
        item.receiptUrls = data.receiptUrls
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy
    if data.paidAt is not None:
        item.paidAt = data.paidAt
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return ReimbursementOut(
        reimbursementId=item.reimbursementId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, amount=item.amount,
        expenseType=item.expenseType, description=item.description,
        receiptUrls=item.receiptUrls, status=item.status,
        approvedBy=item.approvedBy, paidAt=item.paidAt, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════
# Payment 付款
# ═══════════════════════════════════════════════════════

@router.get("/payments", response_model=PaymentListOut)
async def list_payments(
    store_id: Optional[str] = Query(None, alias="storeId"),
    payee_type: Optional[str] = Query(None, alias="payeeType"),
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Payment)
    if store_id:
        q = q.where(Payment.storeId == store_id)
    if payee_type:
        q = q.where(Payment.payeeType == payee_type)
    if status:
        q = q.where(Payment.status == status)
    if start_date:
        q = q.where(Payment.createdAt >= start_date)
    if end_date:
        q = q.where(Payment.createdAt <= end_date + " 23:59:59")
    q = q.order_by(Payment.createdAt.desc())

    # Total sum
    sum_q = select(func.coalesce(func.sum(Payment.amount), 0))
    if store_id:
        sum_q = sum_q.where(Payment.storeId == store_id)
    if payee_type:
        sum_q = sum_q.where(Payment.payeeType == payee_type)
    if status:
        sum_q = sum_q.where(Payment.status == status)
    if start_date:
        sum_q = sum_q.where(Payment.createdAt >= start_date)
    if end_date:
        sum_q = sum_q.where(Payment.createdAt <= end_date + " 23:59:59")
    total_sum = (await db.execute(sum_q)).scalar() or 0

    count_q = select(func.count(Payment.paymentId)).select_from(Payment)
    if store_id:
        count_q = count_q.where(Payment.storeId == store_id)
    if payee_type:
        count_q = count_q.where(Payment.payeeType == payee_type)
    if status:
        count_q = count_q.where(Payment.status == status)
    if start_date:
        count_q = count_q.where(Payment.createdAt >= start_date)
    if end_date:
        count_q = count_q.where(Payment.createdAt <= end_date + " 23:59:59")
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
        result.append(PaymentOut(
            paymentId=item.paymentId, storeId=item.storeId, storeName=store_name,
            payeeType=item.payeeType, payeeId=item.payeeId,
            amount=item.amount, paymentMethod=item.paymentMethod,
            bankAccountId=item.bankAccountId, transactionId=item.transactionId,
            status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
        ))

    return PaymentListOut(total=total_sum, items=result, page=page, page_size=page_size)


@router.get("/payments/{payment_id}", response_model=PaymentOut)
async def get_payment(payment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Payment).where(Payment.paymentId == payment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "付款记录不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return PaymentOut(
        paymentId=item.paymentId, storeId=item.storeId, storeName=store_name,
        payeeType=item.payeeType, payeeId=item.payeeId,
        amount=item.amount, paymentMethod=item.paymentMethod,
        bankAccountId=item.bankAccountId, transactionId=item.transactionId,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
    )


@router.post("/payments", response_model=PaymentOut, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Payment(
        paymentId=_gen_id(), storeId=data.storeId,
        payeeType=data.payeeType, payeeId=data.payeeId,
        amount=data.amount, paymentMethod=data.paymentMethod,
        bankAccountId=data.bankAccountId, transactionId=data.transactionId,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return PaymentOut(
        paymentId=item.paymentId, storeId=item.storeId, storeName=store_name,
        payeeType=item.payeeType, payeeId=item.payeeId,
        amount=item.amount, paymentMethod=item.paymentMethod,
        bankAccountId=item.bankAccountId, transactionId=item.transactionId,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
    )


@router.put("/payments/{payment_id}", response_model=PaymentOut)
async def update_payment(
    payment_id: str,
    data: PaymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Payment).where(Payment.paymentId == payment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "付款记录不存在")
    if data.amount is not None:
        item.amount = data.amount
    if data.paymentMethod is not None:
        item.paymentMethod = data.paymentMethod
    if data.bankAccountId is not None:
        item.bankAccountId = data.bankAccountId
    if data.transactionId is not None:
        item.transactionId = data.transactionId
    if data.status is not None:
        item.status = data.status
    if data.paidAt is not None:
        item.paidAt = data.paidAt
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return PaymentOut(
        paymentId=item.paymentId, storeId=item.storeId, storeName=store_name,
        payeeType=item.payeeType, payeeId=item.payeeId,
        amount=item.amount, paymentMethod=item.paymentMethod,
        bankAccountId=item.bankAccountId, transactionId=item.transactionId,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════
# AccountsPayable 应付账款
# ═══════════════════════════════════════════════════════

@router.get("/accounts-payable", response_model=AccountsPayableListOut)
async def list_accounts_payable(
    store_id: Optional[str] = Query(None, alias="storeId"),
    supplier_id: Optional[str] = Query(None, alias="supplierId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AccountsPayable)
    if store_id:
        q = q.where(AccountsPayable.storeId == store_id)
    if supplier_id:
        q = q.where(AccountsPayable.supplierId == supplier_id)
    if status:
        q = q.where(AccountsPayable.status == status)
    q = q.order_by(AccountsPayable.createdAt.desc())

    sum_q = select(func.coalesce(func.sum(AccountsPayable.amount), 0))
    if store_id:
        sum_q = sum_q.where(AccountsPayable.storeId == store_id)
    if supplier_id:
        sum_q = sum_q.where(AccountsPayable.supplierId == supplier_id)
    if status:
        sum_q = sum_q.where(AccountsPayable.status == status)
    total_sum = (await db.execute(sum_q)).scalar() or 0

    count_q = select(func.count(AccountsPayable.payableId)).select_from(AccountsPayable)
    if store_id:
        count_q = count_q.where(AccountsPayable.storeId == store_id)
    if supplier_id:
        count_q = count_q.where(AccountsPayable.supplierId == supplier_id)
    if status:
        count_q = count_q.where(AccountsPayable.status == status)
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
        supplier_name = None
        if item.supplierId:
            spr = await db.execute(select(Supplier.name).where(Supplier.supplierId == item.supplierId))
            supplier_name = spr.scalar_one_or_none()
        result.append(AccountsPayableOut(
            payableId=item.payableId, supplierId=item.supplierId, supplierName=supplier_name,
            storeId=item.storeId, storeName=store_name,
            purchaseOrderId=item.purchaseOrderId, amount=item.amount,
            paidAmount=item.paidAmount, dueDate=item.dueDate,
            status=item.status, createdAt=item.createdAt,
        ))

    return AccountsPayableListOut(total=total_sum, items=result, page=page, page_size=page_size)


@router.get("/accounts-payable/aging", response_model=AccountsPayableAgingOut)
async def get_accounts_payable_aging(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Aging analysis for accounts payable."""
    q = select(AccountsPayable)
    if store_id:
        q = q.where(AccountsPayable.storeId == store_id)
    q = q.order_by(AccountsPayable.dueDate.asc())

    r = await db.execute(q)
    items = r.scalars().all()

    today = datetime.utcnow().date()
    aging_items = []
    total_balance = 0.0
    for item in items:
        balance = item.amount - item.paidAmount
        if balance <= 0:
            continue
        aging_days = (today - item.dueDate).days
        if aging_days <= 0:
            aging_bucket = "0-30"
        elif aging_days <= 30:
            aging_bucket = "0-30"
        elif aging_days <= 60:
            aging_bucket = "31-60"
        elif aging_days <= 90:
            aging_bucket = "61-90"
        else:
            aging_bucket = "90+"

        supplier_name = None
        if item.supplierId:
            spr = await db.execute(select(Supplier.name).where(Supplier.supplierId == item.supplierId))
            supplier_name = spr.scalar_one_or_none()

        total_balance += balance
        aging_items.append(AccountsPayableAgingItem(
            payableId=item.payableId, supplierId=item.supplierId,
            supplierName=supplier_name, amount=item.amount,
            paidAmount=item.paidAmount, balance=round(balance, 2),
            dueDate=item.dueDate, agingDays=max(0, aging_days),
            agingBucket=aging_bucket,
        ))

    store_name = None
    if store_id:
        sr = await db.execute(select(Store.name).where(Store.storeId == store_id))
        store_name = sr.scalar_one_or_none()

    return AccountsPayableAgingOut(
        storeId=store_id, storeName=store_name,
        items=aging_items, totalBalance=round(total_balance, 2),
    )


@router.get("/accounts-payable/{payable_id}", response_model=AccountsPayableOut)
async def get_accounts_payable(payable_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AccountsPayable).where(AccountsPayable.payableId == payable_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "应付账款记录不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    supplier_name = None
    if item.supplierId:
        spr = await db.execute(select(Supplier.name).where(Supplier.supplierId == item.supplierId))
        supplier_name = spr.scalar_one_or_none()
    return AccountsPayableOut(
        payableId=item.payableId, supplierId=item.supplierId, supplierName=supplier_name,
        storeId=item.storeId, storeName=store_name,
        purchaseOrderId=item.purchaseOrderId, amount=item.amount,
        paidAmount=item.paidAmount, dueDate=item.dueDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/accounts-payable", response_model=AccountsPayableOut, status_code=201)
async def create_accounts_payable(
    data: AccountsPayableCreate,
    db: AsyncSession = Depends(get_db),
):
    item = AccountsPayable(
        payableId=_gen_id(), supplierId=data.supplierId,
        storeId=data.storeId, purchaseOrderId=data.purchaseOrderId,
        amount=data.amount, paidAmount=data.paidAmount, dueDate=data.dueDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    supplier_name = None
    if item.supplierId:
        spr = await db.execute(select(Supplier.name).where(Supplier.supplierId == item.supplierId))
        supplier_name = spr.scalar_one_or_none()
    return AccountsPayableOut(
        payableId=item.payableId, supplierId=item.supplierId, supplierName=supplier_name,
        storeId=item.storeId, storeName=store_name,
        purchaseOrderId=item.purchaseOrderId, amount=item.amount,
        paidAmount=item.paidAmount, dueDate=item.dueDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/accounts-payable/{payable_id}", response_model=AccountsPayableOut)
async def update_accounts_payable(
    payable_id: str,
    data: AccountsPayableUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(AccountsPayable).where(AccountsPayable.payableId == payable_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "应付账款记录不存在")
    if data.paidAmount is not None:
        item.paidAmount = data.paidAmount
    # Auto-update status based on paid amount
    if item.paidAmount >= item.amount:
        item.status = "Paid"
    elif item.paidAmount > 0:
        item.status = "PartialPaid"
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    supplier_name = None
    if item.supplierId:
        spr = await db.execute(select(Supplier.name).where(Supplier.supplierId == item.supplierId))
        supplier_name = spr.scalar_one_or_none()
    return AccountsPayableOut(
        payableId=item.payableId, supplierId=item.supplierId, supplierName=supplier_name,
        storeId=item.storeId, storeName=store_name,
        purchaseOrderId=item.purchaseOrderId, amount=item.amount,
        paidAmount=item.paidAmount, dueDate=item.dueDate,
        status=item.status, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════
# DepreciationRecord 折旧记录
# ═══════════════════════════════════════════════════════

@router.get("/depreciation-records", response_model=DepreciationRecordListOut)
async def list_depreciation_records(
    asset_id: Optional[str] = Query(None, alias="assetId"),
    period: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(DepreciationRecord)
    if asset_id:
        q = q.where(DepreciationRecord.assetId == asset_id)
    if period:
        q = q.where(DepreciationRecord.period == period)
    q = q.order_by(DepreciationRecord.createdAt.desc())

    count_q = select(func.count(DepreciationRecord.depreciationId)).select_from(DepreciationRecord)
    if asset_id:
        count_q = count_q.where(DepreciationRecord.assetId == asset_id)
    if period:
        count_q = count_q.where(DepreciationRecord.period == period)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        asset_name = None
        if item.assetId:
            ar = await db.execute(select(FixedAsset.name).where(FixedAsset.assetId == item.assetId))
            asset_name = ar.scalar_one_or_none()
        result.append(DepreciationRecordOut(
            depreciationId=item.depreciationId, assetId=item.assetId,
            assetName=asset_name, period=item.period,
            depreciationAmount=item.depreciationAmount,
            accumulatedDepreciation=item.accumulatedDepreciation,
            netValue=item.netValue, createdAt=item.createdAt,
        ))

    return DepreciationRecordListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/depreciation-records/{depreciation_id}", response_model=DepreciationRecordOut)
async def get_depreciation_record(depreciation_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DepreciationRecord).where(DepreciationRecord.depreciationId == depreciation_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "折旧记录不存在")
    asset_name = None
    if item.assetId:
        ar = await db.execute(select(FixedAsset.name).where(FixedAsset.assetId == item.assetId))
        asset_name = ar.scalar_one_or_none()
    return DepreciationRecordOut(
        depreciationId=item.depreciationId, assetId=item.assetId,
        assetName=asset_name, period=item.period,
        depreciationAmount=item.depreciationAmount,
        accumulatedDepreciation=item.accumulatedDepreciation,
        netValue=item.netValue, createdAt=item.createdAt,
    )


@router.post("/depreciation-records", response_model=DepreciationRecordOut, status_code=201)
async def create_depreciation_record(
    data: DepreciationRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    # Validate asset exists
    ar = await db.execute(select(FixedAsset).where(FixedAsset.assetId == data.assetId))
    asset = ar.scalar_one_or_none()
    if not asset:
        raise HTTPException(404, "固定资产不存在")

    item = DepreciationRecord(
        depreciationId=_gen_id(), assetId=data.assetId,
        period=data.period, depreciationAmount=data.depreciationAmount,
        accumulatedDepreciation=data.accumulatedDepreciation,
        netValue=data.netValue,
    )
    db.add(item)

    # Update asset current value
    asset.currentValue = data.netValue
    db.add(asset)

    await db.commit()
    await db.refresh(item)
    return DepreciationRecordOut(
        depreciationId=item.depreciationId, assetId=item.assetId,
        assetName=asset.name, period=item.period,
        depreciationAmount=item.depreciationAmount,
        accumulatedDepreciation=item.accumulatedDepreciation,
        netValue=item.netValue, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════════════════
# BankAccount 银行账户
# ═══════════════════════════════════════════════════════

@router.get("/bank-accounts", response_model=BankAccountListOut)
async def list_bank_accounts(
    legal_entity_id: Optional[str] = Query(None, alias="legalEntityId"),
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(BankAccount)
    if legal_entity_id:
        q = q.where(BankAccount.legalEntityId == legal_entity_id)
    if type:
        q = q.where(BankAccount.type == type)
    if status:
        q = q.where(BankAccount.status == status)
    q = q.order_by(BankAccount.createdAt.desc())

    count_q = select(func.count(BankAccount.accountId)).select_from(BankAccount)
    if legal_entity_id:
        count_q = count_q.where(BankAccount.legalEntityId == legal_entity_id)
    if type:
        count_q = count_q.where(BankAccount.type == type)
    if status:
        count_q = count_q.where(BankAccount.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        legal_entity_name = None
        if item.legalEntityId:
            lr = await db.execute(select(LegalEntity.name).where(LegalEntity.legalEntityId == item.legalEntityId))
            legal_entity_name = lr.scalar_one_or_none()
        result.append(BankAccountOut(
            accountId=item.accountId, legalEntityId=item.legalEntityId,
            legalEntityName=legal_entity_name, bankName=item.bankName,
            branchName=item.branchName, accountName=item.accountName,
            accountNumber=item.accountNumber, type=item.type,
            status=item.status, createdAt=item.createdAt,
        ))

    return BankAccountListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/bank-accounts/{account_id}", response_model=BankAccountOut)
async def get_bank_account(account_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BankAccount).where(BankAccount.accountId == account_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "银行账户不存在")
    legal_entity_name = None
    if item.legalEntityId:
        lr = await db.execute(select(LegalEntity.name).where(LegalEntity.legalEntityId == item.legalEntityId))
        legal_entity_name = lr.scalar_one_or_none()
    return BankAccountOut(
        accountId=item.accountId, legalEntityId=item.legalEntityId,
        legalEntityName=legal_entity_name, bankName=item.bankName,
        branchName=item.branchName, accountName=item.accountName,
        accountNumber=item.accountNumber, type=item.type,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/bank-accounts", response_model=BankAccountOut, status_code=201)
async def create_bank_account(
    data: BankAccountCreate,
    db: AsyncSession = Depends(get_db),
):
    item = BankAccount(
        accountId=_gen_id(), legalEntityId=data.legalEntityId,
        bankName=data.bankName, branchName=data.branchName,
        accountName=data.accountName, accountNumber=data.accountNumber,
        type=data.type, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    legal_entity_name = None
    if item.legalEntityId:
        lr = await db.execute(select(LegalEntity.name).where(LegalEntity.legalEntityId == item.legalEntityId))
        legal_entity_name = lr.scalar_one_or_none()
    return BankAccountOut(
        accountId=item.accountId, legalEntityId=item.legalEntityId,
        legalEntityName=legal_entity_name, bankName=item.bankName,
        branchName=item.branchName, accountName=item.accountName,
        accountNumber=item.accountNumber, type=item.type,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/bank-accounts/{account_id}", response_model=BankAccountOut)
async def update_bank_account(
    account_id: str,
    data: BankAccountUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(BankAccount).where(BankAccount.accountId == account_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "银行账户不存在")
    if data.bankName is not None:
        item.bankName = data.bankName
    if data.branchName is not None:
        item.branchName = data.branchName
    if data.accountName is not None:
        item.accountName = data.accountName
    if data.accountNumber is not None:
        item.accountNumber = data.accountNumber
    if data.type is not None:
        item.type = data.type
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    legal_entity_name = None
    if item.legalEntityId:
        lr = await db.execute(select(LegalEntity.name).where(LegalEntity.legalEntityId == item.legalEntityId))
        legal_entity_name = lr.scalar_one_or_none()
    return BankAccountOut(
        accountId=item.accountId, legalEntityId=item.legalEntityId,
        legalEntityName=legal_entity_name, bankName=item.bankName,
        branchName=item.branchName, accountName=item.accountName,
        accountNumber=item.accountNumber, type=item.type,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/bank-accounts/{account_id}")
async def delete_bank_account(account_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BankAccount).where(BankAccount.accountId == account_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "银行账户不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}


# ═══════════════════════════════════════════════════════
# Invoice 发票
# ═══════════════════════════════════════════════════════

@router.get("/invoices", response_model=InvoiceListOut)
async def list_invoices(
    store_id: Optional[str] = Query(None, alias="storeId"),
    direction: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Invoice)
    if store_id:
        q = q.where(Invoice.storeId == store_id)
    if direction:
        q = q.where(Invoice.direction == direction)
    if type:
        q = q.where(Invoice.type == type)
    if status:
        q = q.where(Invoice.status == status)
    if start_date:
        q = q.where(Invoice.issueDate >= start_date)
    if end_date:
        q = q.where(Invoice.issueDate <= end_date)
    q = q.order_by(Invoice.createdAt.desc())

    count_q = select(func.count(Invoice.invoiceId)).select_from(Invoice)
    if store_id:
        count_q = count_q.where(Invoice.storeId == store_id)
    if direction:
        count_q = count_q.where(Invoice.direction == direction)
    if type:
        count_q = count_q.where(Invoice.type == type)
    if status:
        count_q = count_q.where(Invoice.status == status)
    if start_date:
        count_q = count_q.where(Invoice.issueDate >= start_date)
    if end_date:
        count_q = count_q.where(Invoice.issueDate <= end_date)
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
        result.append(InvoiceOut(
            invoiceId=item.invoiceId, storeId=item.storeId, storeName=store_name,
            invoiceNumber=item.invoiceNumber, invoiceCode=item.invoiceCode,
            amount=item.amount, type=item.type, direction=item.direction,
            customerTaxId=item.customerTaxId, issueDate=item.issueDate,
            status=item.status, createdAt=item.createdAt,
        ))

    return InvoiceListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(invoice_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Invoice).where(Invoice.invoiceId == invoice_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "发票不存在")
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InvoiceOut(
        invoiceId=item.invoiceId, storeId=item.storeId, storeName=store_name,
        invoiceNumber=item.invoiceNumber, invoiceCode=item.invoiceCode,
        amount=item.amount, type=item.type, direction=item.direction,
        customerTaxId=item.customerTaxId, issueDate=item.issueDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/invoices", response_model=InvoiceOut, status_code=201)
async def create_invoice(
    data: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check invoice number uniqueness
    nr = await db.execute(select(Invoice).where(Invoice.invoiceNumber == data.invoiceNumber))
    if nr.scalar_one_or_none():
        raise HTTPException(409, "发票号码已存在")

    item = Invoice(
        invoiceId=_gen_id(), storeId=data.storeId,
        invoiceNumber=data.invoiceNumber, invoiceCode=data.invoiceCode,
        amount=data.amount, type=data.type, direction=data.direction,
        customerTaxId=data.customerTaxId, issueDate=data.issueDate,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InvoiceOut(
        invoiceId=item.invoiceId, storeId=item.storeId, storeName=store_name,
        invoiceNumber=item.invoiceNumber, invoiceCode=item.invoiceCode,
        amount=item.amount, type=item.type, direction=item.direction,
        customerTaxId=item.customerTaxId, issueDate=item.issueDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/invoices/{invoice_id}", response_model=InvoiceOut)
async def update_invoice(
    invoice_id: str,
    data: InvoiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Invoice).where(Invoice.invoiceId == invoice_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "发票不存在")
    if data.invoiceCode is not None:
        item.invoiceCode = data.invoiceCode
    if data.amount is not None:
        item.amount = data.amount
    if data.type is not None:
        item.type = data.type
    if data.customerTaxId is not None:
        item.customerTaxId = data.customerTaxId
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = None
    if item.storeId:
        sr = await db.execute(select(Store.name).where(Store.storeId == item.storeId))
        store_name = sr.scalar_one_or_none()
    return InvoiceOut(
        invoiceId=item.invoiceId, storeId=item.storeId, storeName=store_name,
        invoiceNumber=item.invoiceNumber, invoiceCode=item.invoiceCode,
        amount=item.amount, type=item.type, direction=item.direction,
        customerTaxId=item.customerTaxId, issueDate=item.issueDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Invoice).where(Invoice.invoiceId == invoice_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "发票不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "删除成功"}
