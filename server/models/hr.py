"""D07 人力资源域 — Department, Position, Employee, ExternalStaff, Schedule, Attendance, Payroll 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    departmentId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    name = Column(String(50), nullable=False)
    parentId = Column(String(32), ForeignKey("departments.departmentId"), nullable=True)
    sortOrder = Column(Integer, default=0)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    positionId = Column(String(32), unique=True, nullable=False, index=True)
    departmentId = Column(String(32), ForeignKey("departments.departmentId"), nullable=False)
    name = Column(String(50), nullable=False)
    jobLevel = Column(String(20))
    description = Column(String(200))
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jobId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class SalaryGrade(Base):
    __tablename__ = "salary_grades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    gradeId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    minSalary = Column(Float, nullable=False)
    maxSalary = Column(Float, nullable=False)
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class PromotionRecord(Base):
    __tablename__ = "promotion_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    promotionId = Column(String(32), unique=True, nullable=False, index=True)
    employeeId = Column(String(32), nullable=False)
    fromPositionId = Column(String(32), ForeignKey("positions.positionId"), nullable=True)
    toPositionId = Column(String(32), ForeignKey("positions.positionId"), nullable=False)
    fromSalaryGradeId = Column(String(32), ForeignKey("salary_grades.gradeId"), nullable=True)
    toSalaryGradeId = Column(String(32), ForeignKey("salary_grades.gradeId"), nullable=True)
    effectiveDate = Column(Date, nullable=False)
    reason = Column(String(500))
    approvedBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    employeeId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    departmentId = Column(String(32), ForeignKey("departments.departmentId"), nullable=True)
    positionId = Column(String(32), ForeignKey("positions.positionId"), nullable=True)
    jobId = Column(String(32), ForeignKey("jobs.jobId"), nullable=True)
    salaryGradeId = Column(String(32), ForeignKey("salary_grades.gradeId"), nullable=True)
    employeeNumber = Column(String(20), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    idCard = Column(String(18))
    gender = Column(String(10))
    birthday = Column(Date)
    hireDate = Column(Date, nullable=False)
    type = Column(String(20), default="FullTime")  # FullTime/PartTime/Contract/Temporary
    education = Column(String(20))
    bankName = Column(String(100))
    bankAccount = Column(String(50))
    status = Column(String(20), default="Active")  # Active/Resigned/Suspended
    resignedDate = Column(Date)
    createdAt = Column(DateTime, server_default=func.now())


class ExternalStaff(Base):
    __tablename__ = "external_staff"
    id = Column(Integer, primary_key=True, autoincrement=True)
    staffId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    company = Column(String(100))
    name = Column(String(50), nullable=False)
    phone = Column(String(20))
    idCard = Column(String(18))
    serviceType = Column(String(20), nullable=False)  # Cleaning/Security/Maintenance/Other
    contractStartDate = Column(Date)
    contractEndDate = Column(Date)
    status = Column(String(20), default="Active")  # Active/Inactive
    createdAt = Column(DateTime, server_default=func.now())


class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    scheduleId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    employeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    workDate = Column(Date, nullable=False)
    startTime = Column(String(10), nullable=False)
    endTime = Column(String(10), nullable=False)
    scheduleType = Column(String(10), default="Morning")  # Morning/Evening/Night/Off
    isHoliday = Column(Boolean, default=False)
    createdBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class ScheduleSwap(Base):
    __tablename__ = "schedule_swaps"
    id = Column(Integer, primary_key=True, autoincrement=True)
    swapId = Column(String(32), unique=True, nullable=False, index=True)
    fromEmployeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    toEmployeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    scheduleId = Column(String(32), ForeignKey("schedules.scheduleId"), nullable=False)
    swapDate = Column(Date, nullable=False)
    reason = Column(String(200))
    status = Column(String(20), default="Pending")  # Pending/Approved/Rejected
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class Attendance(Base):
    __tablename__ = "attendances"
    id = Column(Integer, primary_key=True, autoincrement=True)
    attendanceId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    employeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    date = Column(Date, nullable=False)
    clockIn = Column(String(10))
    clockOut = Column(String(10))
    status = Column(String(10), default="Normal")  # Normal/Late/Early/Absent/Overtime
    remark = Column(String(200))
    createdAt = Column(DateTime, server_default=func.now())


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, autoincrement=True)
    leaveId = Column(String(32), unique=True, nullable=False, index=True)
    employeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    leaveType = Column(String(20), nullable=False)  # Annual/Sick/Personal/Maternity
    startDate = Column(Date, nullable=False)
    endDate = Column(Date, nullable=False)
    duration = Column(Float, nullable=False)
    reason = Column(String(500))
    status = Column(String(20), default="Pending")  # Pending/Approved/Rejected/Cancelled
    approvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class Payroll(Base):
    __tablename__ = "payrolls"
    id = Column(Integer, primary_key=True, autoincrement=True)
    payrollId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    employeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    yearMonth = Column(String(7), nullable=False)  # YYYY-MM
    totalAmount = Column(Float, nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Confirmed/Paid
    paidAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())

    items = relationship("PayrollItem", back_populates="payroll", cascade="all, delete-orphan")


class PayrollItem(Base):
    __tablename__ = "payroll_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    itemId = Column(String(32), unique=True, nullable=False, index=True)
    payrollId = Column(String(32), ForeignKey("payrolls.payrollId"), nullable=False)
    category = Column(String(20), nullable=False)  # Base/Overtime/Bonus/Penalty/Insurance/Tax
    amount = Column(Float, nullable=False)
    remark = Column(String(200))

    payroll = relationship("Payroll", back_populates="items")


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reviewId = Column(String(32), unique=True, nullable=False, index=True)
    employeeId = Column(String(32), ForeignKey("employees.employeeId"), nullable=False)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    reviewDate = Column(Date, nullable=False)
    score = Column(Float)
    rating = Column(String(10))  # A/B/C/D
    reviewContent = Column(Text)
    reviewerId = Column(String(32), nullable=False)
    status = Column(String(20), default="Draft")  # Draft/Submitted/Approved
    createdAt = Column(DateTime, server_default=func.now())


class CleanerAssessment(Base):
    __tablename__ = "cleaner_assessments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessmentId = Column(String(32), unique=True, nullable=False, index=True)
    storeId = Column(String(32), ForeignKey("stores.storeId"), nullable=False)
    staffId = Column(String(32), ForeignKey("external_staff.staffId"), nullable=False)
    reviewDate = Column(Date, nullable=False)
    score = Column(Float)
    rating = Column(String(10))  # A/B/C/D
    detailItems = Column(Text)  # JSON
    reviewerId = Column(String(32), nullable=False)
    remark = Column(String(500))
    createdAt = Column(DateTime, server_default=func.now())
