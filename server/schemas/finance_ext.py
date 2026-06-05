"""D06 财务域（扩展）— AccountSubject, FiscalCalendar, JournalEntry, Ledger, Budget, Advance, Reimburse, Payment, Payable, Depreciation, BankAccount, Invoice"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── AccountSubject 会计科目 ──

class AccountSubjectCreate(BaseModel):
    code: str
    name: str
    parentId: Optional[str] = None
    level: int
    type: str  # Asset/Liability/Equity/Revenue/Expense
    direction: str  # Debit/Credit
    isLeaf: bool = True
    status: str = "Active"


class AccountSubjectUpdate(BaseModel):
    name: Optional[str] = None
    parentId: Optional[str] = None
    level: Optional[int] = None
    type: Optional[str] = None
    direction: Optional[str] = None
    isLeaf: Optional[bool] = None
    status: Optional[str] = None


class AccountSubjectOut(BaseModel):
    subjectId: str
    code: str
    name: str
    parentId: Optional[str] = None
    level: int
    type: str
    direction: str
    isLeaf: bool = True
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountSubjectListOut(BaseModel):
    total: int
    items: List[AccountSubjectOut]
    page: int = 1
    page_size: int = 20


class AccountSubjectTreeNode(BaseModel):
    subjectId: str
    code: str
    name: str
    parentId: Optional[str] = None
    level: int
    type: str
    direction: str
    isLeaf: bool = True
    status: str = "Active"
    children: List["AccountSubjectTreeNode"] = []

    class Config:
        from_attributes = True


# ── FiscalCalendar 会计日历 ──

class FiscalCalendarCreate(BaseModel):
    year: int
    periodStart: date
    periodEnd: date
    isClosed: bool = False
    closedBy: Optional[str] = None


class FiscalCalendarUpdate(BaseModel):
    periodStart: Optional[date] = None
    periodEnd: Optional[date] = None
    isClosed: Optional[bool] = None
    closedBy: Optional[str] = None
    closedAt: Optional[datetime] = None


class FiscalCalendarOut(BaseModel):
    calendarId: str
    year: int
    periodStart: date
    periodEnd: date
    isClosed: bool = False
    closedBy: Optional[str] = None
    closedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class FiscalCalendarListOut(BaseModel):
    total: int
    items: List[FiscalCalendarOut]
    page: int = 1
    page_size: int = 20


# ── JournalEntry 记账凭证 ──

class JournalEntryLineCreate(BaseModel):
    subjectId: str
    direction: str  # Debit/Credit
    amount: float
    summary: Optional[str] = None


class JournalEntryLineUpdate(BaseModel):
    subjectId: Optional[str] = None
    direction: Optional[str] = None
    amount: Optional[float] = None
    summary: Optional[str] = None


class JournalEntryLineOut(BaseModel):
    lineId: str
    entryId: str
    subjectId: str
    direction: str
    amount: float
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class JournalEntryCreate(BaseModel):
    periodId: str
    entryNumber: str
    entryDate: date
    summary: Optional[str] = None
    attachmentCount: int = 0
    createdBy: str
    lines: List[JournalEntryLineCreate]


class JournalEntryUpdate(BaseModel):
    summary: Optional[str] = None
    attachmentCount: Optional[int] = None
    status: Optional[str] = None
    approvedBy: Optional[str] = None
    lines: Optional[List[JournalEntryLineCreate]] = None


class JournalEntryOut(BaseModel):
    entryId: str
    periodId: str
    entryNumber: str
    entryDate: date
    summary: Optional[str] = None
    attachmentCount: int = 0
    status: str = "Draft"
    createdBy: str
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None
    lines: List[JournalEntryLineOut] = []

    class Config:
        from_attributes = True


class JournalEntryListOut(BaseModel):
    total: int
    items: List[JournalEntryOut]
    page: int = 1
    page_size: int = 20


# ── Ledger 分类账 ──

class LedgerCreate(BaseModel):
    subjectId: str
    periodId: str
    openingBalance: float = 0
    debitAmount: float = 0
    creditAmount: float = 0
    closingBalance: float = 0


class LedgerUpdate(BaseModel):
    openingBalance: Optional[float] = None
    debitAmount: Optional[float] = None
    creditAmount: Optional[float] = None
    closingBalance: Optional[float] = None


class LedgerOut(BaseModel):
    ledgerId: str
    subjectId: str
    periodId: str
    openingBalance: float = 0
    debitAmount: float = 0
    creditAmount: float = 0
    closingBalance: float = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class LedgerListOut(BaseModel):
    total: int
    items: List[LedgerOut]
    page: int = 1
    page_size: int = 20


# ── Budget 预算 ──

class BudgetCreate(BaseModel):
    orgId: Optional[str] = None
    storeId: Optional[str] = None
    year: int
    month: Optional[int] = None
    category: str  # Operating/Labor/Marketing/Admin
    budgetAmount: float
    actualAmount: float = 0


class BudgetUpdate(BaseModel):
    budgetAmount: Optional[float] = None
    actualAmount: Optional[float] = None
    category: Optional[str] = None


class BudgetOut(BaseModel):
    budgetId: str
    orgId: Optional[str] = None
    storeId: Optional[str] = None
    year: int
    month: Optional[int] = None
    category: str
    budgetAmount: float
    actualAmount: float = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetListOut(BaseModel):
    total: int
    items: List[BudgetOut]
    page: int = 1
    page_size: int = 20


class BudgetComparisonItem(BaseModel):
    budgetId: str
    category: str
    budgetAmount: float
    actualAmount: float
    variance: float
    varianceRate: float  # percentage


class BudgetComparisonOut(BaseModel):
    year: int
    storeId: Optional[str] = None
    storeName: Optional[str] = None
    items: List[BudgetComparisonItem]
    totalBudget: float
    totalActual: float
    totalVariance: float


# ── AdvanceRequest 预支申请 ──

class AdvanceRequestCreate(BaseModel):
    storeId: str
    employeeId: str
    amount: float
    purpose: Optional[str] = None
    expectedRepayDate: Optional[date] = None


class AdvanceRequestUpdate(BaseModel):
    amount: Optional[float] = None
    purpose: Optional[str] = None
    expectedRepayDate: Optional[date] = None
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class AdvanceRequestOut(BaseModel):
    advanceId: str
    storeId: str
    storeName: Optional[str] = None
    employeeId: str
    employeeName: Optional[str] = None
    amount: float
    purpose: Optional[str] = None
    expectedRepayDate: Optional[date] = None
    status: str = "Pending"
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AdvanceRequestListOut(BaseModel):
    total: int
    items: List[AdvanceRequestOut]
    page: int = 1
    page_size: int = 20


# ── Reimbursement 报销 ──

class ReimbursementCreate(BaseModel):
    storeId: str
    employeeId: str
    amount: float
    expenseType: str
    description: Optional[str] = None
    receiptUrls: Optional[str] = None


class ReimbursementUpdate(BaseModel):
    amount: Optional[float] = None
    expenseType: Optional[str] = None
    description: Optional[str] = None
    receiptUrls: Optional[str] = None
    status: Optional[str] = None
    approvedBy: Optional[str] = None
    paidAt: Optional[datetime] = None


class ReimbursementOut(BaseModel):
    reimbursementId: str
    storeId: str
    storeName: Optional[str] = None
    employeeId: str
    employeeName: Optional[str] = None
    amount: float
    expenseType: str
    description: Optional[str] = None
    receiptUrls: Optional[str] = None
    status: str = "Draft"
    approvedBy: Optional[str] = None
    paidAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ReimbursementListOut(BaseModel):
    total: int
    items: List[ReimbursementOut]
    page: int = 1
    page_size: int = 20


# ── Payment 付款 ──

class PaymentCreate(BaseModel):
    storeId: str
    payeeType: str  # Supplier/Employee/Other
    payeeId: str
    amount: float
    paymentMethod: str
    bankAccountId: Optional[str] = None
    transactionId: Optional[str] = None


class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    paymentMethod: Optional[str] = None
    bankAccountId: Optional[str] = None
    transactionId: Optional[str] = None
    status: Optional[str] = None
    paidAt: Optional[datetime] = None


class PaymentOut(BaseModel):
    paymentId: str
    storeId: str
    storeName: Optional[str] = None
    payeeType: str
    payeeId: str
    amount: float
    paymentMethod: str
    bankAccountId: Optional[str] = None
    transactionId: Optional[str] = None
    status: str = "Pending"
    paidAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentListOut(BaseModel):
    total: float  # sum of amounts
    items: List[PaymentOut]
    page: int = 1
    page_size: int = 20


# ── AccountsPayable 应付账款 ──

class AccountsPayableCreate(BaseModel):
    supplierId: str
    storeId: str
    purchaseOrderId: Optional[str] = None
    amount: float
    paidAmount: float = 0
    dueDate: date


class AccountsPayableUpdate(BaseModel):
    paidAmount: Optional[float] = None
    status: Optional[str] = None


class AccountsPayableOut(BaseModel):
    payableId: str
    supplierId: str
    supplierName: Optional[str] = None
    storeId: str
    storeName: Optional[str] = None
    purchaseOrderId: Optional[str] = None
    amount: float
    paidAmount: float = 0
    dueDate: date
    status: str = "Unpaid"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountsPayableListOut(BaseModel):
    total: float  # sum of amounts
    items: List[AccountsPayableOut]
    page: int = 1
    page_size: int = 20


class AccountsPayableAgingItem(BaseModel):
    payableId: str
    supplierId: str
    supplierName: Optional[str] = None
    amount: float
    paidAmount: float
    balance: float
    dueDate: date
    agingDays: int
    agingBucket: str  # 0-30 / 31-60 / 61-90 / 90+


class AccountsPayableAgingOut(BaseModel):
    storeId: Optional[str] = None
    storeName: Optional[str] = None
    items: List[AccountsPayableAgingItem]
    totalBalance: float


# ── DepreciationRecord 折旧记录 ──

class DepreciationRecordCreate(BaseModel):
    assetId: str
    period: str  # YYYY-MM
    depreciationAmount: float
    accumulatedDepreciation: float
    netValue: float


class DepreciationRecordUpdate(BaseModel):
    depreciationAmount: Optional[float] = None
    accumulatedDepreciation: Optional[float] = None
    netValue: Optional[float] = None


class DepreciationRecordOut(BaseModel):
    depreciationId: str
    assetId: str
    assetName: Optional[str] = None
    period: str
    depreciationAmount: float
    accumulatedDepreciation: float
    netValue: float
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepreciationRecordListOut(BaseModel):
    total: int
    items: List[DepreciationRecordOut]
    page: int = 1
    page_size: int = 20


# ── BankAccount 银行账户 ──

class BankAccountCreate(BaseModel):
    legalEntityId: str
    bankName: str
    branchName: Optional[str] = None
    accountName: str
    accountNumber: str
    type: str = "Basic"  # Basic/General/Special
    status: str = "Active"


class BankAccountUpdate(BaseModel):
    bankName: Optional[str] = None
    branchName: Optional[str] = None
    accountName: Optional[str] = None
    accountNumber: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None


class BankAccountOut(BaseModel):
    accountId: str
    legalEntityId: str
    legalEntityName: Optional[str] = None
    bankName: str
    branchName: Optional[str] = None
    accountName: str
    accountNumber: str
    type: str = "Basic"
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class BankAccountListOut(BaseModel):
    total: int
    items: List[BankAccountOut]
    page: int = 1
    page_size: int = 20


# ── Invoice 发票 ──

class InvoiceCreate(BaseModel):
    storeId: str
    invoiceNumber: str
    invoiceCode: Optional[str] = None
    amount: float
    type: str  # Special/General/Electric
    direction: str  # Input/Output
    customerTaxId: Optional[str] = None
    issueDate: date


class InvoiceUpdate(BaseModel):
    invoiceCode: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    customerTaxId: Optional[str] = None
    status: Optional[str] = None


class InvoiceOut(BaseModel):
    invoiceId: str
    storeId: str
    storeName: Optional[str] = None
    invoiceNumber: str
    invoiceCode: Optional[str] = None
    amount: float
    type: str
    direction: str
    customerTaxId: Optional[str] = None
    issueDate: date
    status: str = "Issued"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class InvoiceListOut(BaseModel):
    total: int
    items: List[InvoiceOut]
    page: int = 1
    page_size: int = 20
