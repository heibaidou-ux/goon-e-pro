"""D06 财务域 — AccountSubject, JournalEntry, Ledger, Budget, Revenue, Expense, Settlement, Dividend, FixedAsset 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class AccountSubject(Base):
    __tablename__ = "account_subjects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    subjectId = Column(String(32), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    parentId = Column(String(32), ForeignKey("account_subjects.subjectId"), nullable=True)
    level = Column(Integer, nullable=False)
    type = Column(String(20), nullable=False)  # Asset/Liability/Equity/Revenue/Expense
    direction = Column(String(10), nullable=False)  # Debit/Credit
    isLeaf = Column(Boolean, default=True)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class FiscalCalendar(Base):
    __tablename__ = "fiscal_calendars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    calendarId = Column(String(32), unique=True, nullable=False, index=True)
    year = Column(Integer, nullable=False)
    periodStart = Column(Date, nullable=False)
    periodEnd = Column(Date, nullable=False)
    isClosed = Column(Boolean, default=False)
    closedBy = Column(String(32))
    closedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True, autoincrement=True)
    entryId = Column(String(32), unique=True, nullable=False, index=True)
    periodId = Column(String(32), ForeignKey("fiscal_calendars.calendarId"), nullable=False)
    entryNumber = Column(String(30), unique=True, nullable=False)
    entryDate = Column(Date, nullable=False)
    summary = Column(String(500))
    attachmentCount = Column(Integer, default=0)
    status = Column(String(20), default="Draft")  # Draft/Posted/Reversed
    createdBy = Column(String(32), nullable=False)
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())

    lines = relationship("JournalEntryLine", back_populates="journalEntry", cascade="all, delete-orphan")


class JournalEntryLine(Base):
    __tablename__ = "journal_entry_lines"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lineId = Column(String(32), unique=True, nullable=False, index=True)
    entryId = Column(String(32), ForeignKey("journal_entries.entryId"), nullable=False)
    subjectId = Column(String(32), ForeignKey("account_subjects.subjectId"), nullable=False)
    direction = Column(String(10), nullable=False)  # Debit/Credit
    amount = Column(Float, nullable=False)
    summary = Column(String(200))

    journalEntry = relationship("JournalEntry", back_populates="lines")


class Ledger(Base):
    __tablename__ = "ledgers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ledgerId = Column(String(32), unique=True, nullable=False, index=True)
    subjectId = Column(String(32), ForeignKey("account_subjects.subjectId"), nullable=False)
    periodId = Column(String(32), ForeignKey("fiscal_calendars.calendarId"), nullable=False)
    openingBalance = Column(Float, default=0)
    debitAmount = Column(Float, default=0)
    creditAmount = Column(Float, default=0)
    closingBalance = Column(Float, default=0)
    createdAt = Column(DateTime, server_default=func.now())


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    budgetId = Column(String(32), unique=True, nullable=False, index=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer)
    category = Column(String(30), nullable=False)  # Operating/Labor/Marketing/Admin
    budgetAmount = Column(Float, nullable=False)
    actualAmount = Column(Float, default=0)
    createdAt = Column(DateTime, server_default=func.now())


class RevenueFlow(Base):
    __tablename__ = "revenue_flows"
    id = Column(Integer, primary_key=True, autoincrement=True)
    revenueId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    orderId = Column(String(32), ForeignKey("orders.orderId"), nullable=True)
    amount = Column(Float, nullable=False)
    paymentMethod = Column(String(20), nullable=False)
    type = Column(String(30), nullable=False)  # RoomRental/ProductSales/Recharge/Deposit
    channel = Column(String(20))
    receivedAt = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class ExpenseRecord(Base):
    __tablename__ = "expense_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    expenseId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    category = Column(String(30), nullable=False)  # Rent/Utility/Labor/Repair/Marketing/Other
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    incurredDate = Column(Date, nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Submitted/Approved/Rejected
    applicantId = Column(String(32), nullable=False)
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class AdvanceRequest(Base):
    __tablename__ = "advance_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    advanceId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    employeeId = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    purpose = Column(String(500))
    expectedRepayDate = Column(Date)
    status = Column(String(20), default="Pending")  # Pending/Approved/Paid/Repaid/Settled
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class Reimbursement(Base):
    __tablename__ = "reimbursements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reimbursementId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    employeeId = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    expenseType = Column(String(30), nullable=False)
    description = Column(String(500))
    receiptUrls = Column(Text)
    status = Column(String(20), default="Draft")  # Draft/Submitted/Approved/Paid/Rejected
    approvedBy = Column(String(32))
    paidAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    paymentId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    payeeType = Column(String(20), nullable=False)  # Supplier/Employee/Other
    payeeId = Column(String(32), nullable=False)
    amount = Column(Float, nullable=False)
    paymentMethod = Column(String(20), nullable=False)
    bankAccountId = Column(String(32), nullable=True)
    transactionId = Column(String(64))
    status = Column(String(20), default="Pending")  # Pending/Completed/Failed
    paidAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class AccountsPayable(Base):
    __tablename__ = "accounts_payable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    payableId = Column(String(32), unique=True, nullable=False, index=True)
    supplierId = Column(String(32), ForeignKey("suppliers.supplierId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    purchaseOrderId = Column(String(32), ForeignKey("purchase_orders.purchaseOrderId"), nullable=True)
    amount = Column(Float, nullable=False)
    paidAmount = Column(Float, default=0)
    dueDate = Column(Date, nullable=False)
    status = Column(String(20), default="Unpaid")  # Unpaid/PartialPaid/Paid/Overdue
    createdAt = Column(DateTime, server_default=func.now())


class ReconciliationTicket(Base):
    __tablename__ = "reconciliation_tickets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ticketId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    period = Column(String(20), nullable=False)
    totalRevenue = Column(Float, default=0)
    totalExpense = Column(Float, default=0)
    netAmount = Column(Float, default=0)
    status = Column(String(20), default="Draft")  # Draft/Confirmed/Disputed/Approved
    createdBy = Column(String(32), nullable=False)
    confirmedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class DailySettlement(Base):
    __tablename__ = "daily_settlements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    settlementId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    settlementDate = Column(Date, nullable=False)
    totalRevenue = Column(Float, default=0)
    totalExpense = Column(Float, default=0)
    cashAmount = Column(Float, default=0)
    cardAmount = Column(Float, default=0)
    transferAmount = Column(Float, default=0)
    onlineAmount = Column(Float, default=0)
    netAmount = Column(Float, default=0)
    status = Column(String(20), default="Open")  # Open/Closed/Reviewed
    closedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class MonthlySettlement(Base):
    __tablename__ = "monthly_settlements"
    id = Column(Integer, primary_key=True, autoincrement=True)
    settlementId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    yearMonth = Column(String(7), nullable=False)  # YYYY-MM
    totalRevenue = Column(Float, default=0)
    totalExpense = Column(Float, default=0)
    netAmount = Column(Float, default=0)
    dividendAmount = Column(Float, default=0)
    status = Column(String(20), default="Open")  # Open/Closed/Reviewed
    closedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class DividendRecord(Base):
    __tablename__ = "dividend_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    dividendId = Column(String(32), unique=True, nullable=False, index=True)
    monthlySettlementId = Column(String(32), ForeignKey("monthly_settlements.settlementId"), nullable=False)
    shareholderId = Column(String(32), ForeignKey("shareholders.shareholderId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    amount = Column(Float, nullable=False)
    ratio = Column(Float, nullable=False)
    paidAt = Column(DateTime)
    status = Column(String(20), default="Pending")  # Pending/Paid
    createdAt = Column(DateTime, server_default=func.now())


class FixedAsset(Base):
    __tablename__ = "fixed_assets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assetId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(30), nullable=False)  # Decoration/Equipment/Furniture/Vehicle
    originalValue = Column(Float, nullable=False)
    currentValue = Column(Float, nullable=False)
    purchaseDate = Column(Date, nullable=False)
    depreciationMethod = Column(String(20), default="StraightLine")  # StraightLine/DoubleDeclining
    status = Column(String(20), default="InUse")  # InUse/Idle/Scrapped
    createdAt = Column(DateTime, server_default=func.now())


class DepreciationRecord(Base):
    __tablename__ = "depreciation_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    depreciationId = Column(String(32), unique=True, nullable=False, index=True)
    assetId = Column(String(32), ForeignKey("fixed_assets.assetId"), nullable=False)
    period = Column(String(7), nullable=False)  # YYYY-MM
    depreciationAmount = Column(Float, nullable=False)
    accumulatedDepreciation = Column(Float, nullable=False)
    netValue = Column(Float, nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class BankAccount(Base):
    __tablename__ = "bank_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    accountId = Column(String(32), unique=True, nullable=False, index=True)
    legalEntityId = Column(String(32), ForeignKey("legal_entities.legalEntityId"), nullable=False)
    bankName = Column(String(100), nullable=False)
    branchName = Column(String(100))
    accountName = Column(String(100), nullable=False)
    accountNumber = Column(String(50), nullable=False)
    type = Column(String(20), default="Basic")  # Basic/General/Special
    status = Column(String(20), default="Active")  # Active/Frozen/Closed
    createdAt = Column(DateTime, server_default=func.now())


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    invoiceId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    invoiceNumber = Column(String(50), unique=True, nullable=False)
    invoiceCode = Column(String(50))
    amount = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # Special/General/Electric
    direction = Column(String(10), nullable=False)  # Input/Output
    customerTaxId = Column(String(50))
    issueDate = Column(Date, nullable=False)
    status = Column(String(20), default="Issued")  # Issued/Invalid
    createdAt = Column(DateTime, server_default=func.now())
