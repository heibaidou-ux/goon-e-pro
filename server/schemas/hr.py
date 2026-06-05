"""D07 人力资源域 — Pydantic schemas"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ── Department ──

class DepartmentCreate(BaseModel):
    storeId: str
    name: str
    parentId: Optional[str] = None
    sortOrder: int = 0
    status: str = "Active"


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parentId: Optional[str] = None
    sortOrder: Optional[int] = None
    status: Optional[str] = None


class DepartmentOut(BaseModel):
    departmentId: str
    storeId: str
    storeName: Optional[str] = None
    name: str
    parentId: Optional[str] = None
    sortOrder: int = 0
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class DepartmentTreeOut(BaseModel):
    departmentId: str
    name: str
    parentId: Optional[str] = None
    sortOrder: int = 0
    status: str = "Active"
    children: List["DepartmentTreeOut"] = []

    class Config:
        from_attributes = True


class DepartmentListOut(BaseModel):
    total: int
    items: List[DepartmentOut]
    page: int = 1
    page_size: int = 20


# ── Position ──

class PositionCreate(BaseModel):
    departmentId: str
    name: str
    jobLevel: Optional[str] = None
    description: Optional[str] = None
    status: str = "Active"


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    jobLevel: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class PositionOut(BaseModel):
    positionId: str
    departmentId: str
    departmentName: Optional[str] = None
    name: str
    jobLevel: Optional[str] = None
    description: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PositionListOut(BaseModel):
    total: int
    items: List[PositionOut]
    page: int = 1
    page_size: int = 20


# ── Job ──

class JobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "Active"


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class JobOut(BaseModel):
    jobId: str
    name: str
    description: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobListOut(BaseModel):
    total: int
    items: List[JobOut]
    page: int = 1
    page_size: int = 20


# ── SalaryGrade ──

class SalaryGradeCreate(BaseModel):
    name: str
    minSalary: float
    maxSalary: float
    status: str = "Active"


class SalaryGradeUpdate(BaseModel):
    name: Optional[str] = None
    minSalary: Optional[float] = None
    maxSalary: Optional[float] = None
    status: Optional[str] = None


class SalaryGradeOut(BaseModel):
    gradeId: str
    name: str
    minSalary: float
    maxSalary: float
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SalaryGradeListOut(BaseModel):
    total: int
    items: List[SalaryGradeOut]
    page: int = 1
    page_size: int = 20


# ── PromotionRecord ──

class PromotionRecordCreate(BaseModel):
    employeeId: str
    fromPositionId: Optional[str] = None
    toPositionId: str
    fromSalaryGradeId: Optional[str] = None
    toSalaryGradeId: Optional[str] = None
    effectiveDate: date
    reason: Optional[str] = None
    approvedBy: str


class PromotionRecordOut(BaseModel):
    promotionId: str
    employeeId: str
    employeeName: Optional[str] = None
    fromPositionId: Optional[str] = None
    fromPositionName: Optional[str] = None
    toPositionId: str
    toPositionName: Optional[str] = None
    fromSalaryGradeId: Optional[str] = None
    fromSalaryGradeName: Optional[str] = None
    toSalaryGradeId: Optional[str] = None
    toSalaryGradeName: Optional[str] = None
    effectiveDate: date
    reason: Optional[str] = None
    approvedBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PromotionRecordListOut(BaseModel):
    total: int
    items: List[PromotionRecordOut]
    page: int = 1
    page_size: int = 20


# ── Employee ──

class EmployeeCreate(BaseModel):
    storeId: str
    departmentId: Optional[str] = None
    positionId: Optional[str] = None
    jobId: Optional[str] = None
    salaryGradeId: Optional[str] = None
    employeeNumber: str
    name: str
    phone: Optional[str] = None
    idCard: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    hireDate: date
    type: str = "FullTime"
    education: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    status: str = "Active"


class EmployeeUpdate(BaseModel):
    departmentId: Optional[str] = None
    positionId: Optional[str] = None
    jobId: Optional[str] = None
    salaryGradeId: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    idCard: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    hireDate: Optional[date] = None
    type: Optional[str] = None
    education: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    status: Optional[str] = None
    resignedDate: Optional[date] = None


class EmployeeOut(BaseModel):
    employeeId: str
    storeId: str
    storeName: Optional[str] = None
    departmentId: Optional[str] = None
    departmentName: Optional[str] = None
    positionId: Optional[str] = None
    positionName: Optional[str] = None
    jobId: Optional[str] = None
    jobName: Optional[str] = None
    salaryGradeId: Optional[str] = None
    salaryGradeName: Optional[str] = None
    employeeNumber: str
    name: str
    phone: Optional[str] = None
    idCard: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[date] = None
    hireDate: date
    type: str = "FullTime"
    education: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    status: str = "Active"
    resignedDate: Optional[date] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeListOut(BaseModel):
    total: int
    items: List[EmployeeOut]
    page: int = 1
    page_size: int = 20


# ── ExternalStaff ──

class ExternalStaffCreate(BaseModel):
    storeId: str
    company: Optional[str] = None
    name: str
    phone: Optional[str] = None
    idCard: Optional[str] = None
    serviceType: str
    contractStartDate: Optional[date] = None
    contractEndDate: Optional[date] = None
    status: str = "Active"


class ExternalStaffUpdate(BaseModel):
    company: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    idCard: Optional[str] = None
    serviceType: Optional[str] = None
    contractStartDate: Optional[date] = None
    contractEndDate: Optional[date] = None
    status: Optional[str] = None


class ExternalStaffOut(BaseModel):
    staffId: str
    storeId: str
    storeName: Optional[str] = None
    company: Optional[str] = None
    name: str
    phone: Optional[str] = None
    idCard: Optional[str] = None
    serviceType: str
    contractStartDate: Optional[date] = None
    contractEndDate: Optional[date] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExternalStaffListOut(BaseModel):
    total: int
    items: List[ExternalStaffOut]
    page: int = 1
    page_size: int = 20


# ── Schedule ──

class ScheduleCreate(BaseModel):
    storeId: str
    employeeId: str
    workDate: date
    startTime: str
    endTime: str
    scheduleType: str = "Morning"
    isHoliday: bool = False
    createdBy: str


class ScheduleUpdate(BaseModel):
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    scheduleType: Optional[str] = None
    isHoliday: Optional[bool] = None


class ScheduleOut(BaseModel):
    scheduleId: str
    storeId: str
    storeName: Optional[str] = None
    employeeId: str
    employeeName: Optional[str] = None
    workDate: date
    startTime: str
    endTime: str
    scheduleType: str = "Morning"
    isHoliday: bool = False
    createdBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScheduleListOut(BaseModel):
    total: int
    items: List[ScheduleOut]
    page: int = 1
    page_size: int = 20


# ── ScheduleSwap ──

class ScheduleSwapCreate(BaseModel):
    fromEmployeeId: str
    toEmployeeId: str
    scheduleId: str
    swapDate: date
    reason: Optional[str] = None


class ScheduleSwapUpdate(BaseModel):
    status: Optional[str] = None
    approvedBy: Optional[str] = None


class ScheduleSwapOut(BaseModel):
    swapId: str
    fromEmployeeId: str
    fromEmployeeName: Optional[str] = None
    toEmployeeId: str
    toEmployeeName: Optional[str] = None
    scheduleId: str
    swapDate: date
    reason: Optional[str] = None
    status: str = "Pending"
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScheduleSwapListOut(BaseModel):
    total: int
    items: List[ScheduleSwapOut]
    page: int = 1
    page_size: int = 20


# ── Attendance ──

class AttendanceCreate(BaseModel):
    storeId: str
    employeeId: str
    date: date
    clockIn: Optional[str] = None
    clockOut: Optional[str] = None
    status: str = "Normal"
    remark: Optional[str] = None


class AttendanceUpdate(BaseModel):
    clockIn: Optional[str] = None
    clockOut: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None


class AttendanceOut(BaseModel):
    attendanceId: str
    storeId: str
    storeName: Optional[str] = None
    employeeId: str
    employeeName: Optional[str] = None
    date: date
    clockIn: Optional[str] = None
    clockOut: Optional[str] = None
    status: str = "Normal"
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceListOut(BaseModel):
    total: int
    items: List[AttendanceOut]
    page: int = 1
    page_size: int = 20


# ── LeaveRequest ──

class LeaveRequestCreate(BaseModel):
    employeeId: str
    leaveType: str
    startDate: date
    endDate: date
    duration: float
    reason: Optional[str] = None


class LeaveRequestUpdate(BaseModel):
    status: Optional[str] = None
    approvedBy: Optional[str] = None
    reason: Optional[str] = None


class LeaveRequestOut(BaseModel):
    leaveId: str
    employeeId: str
    employeeName: Optional[str] = None
    leaveType: str
    startDate: date
    endDate: date
    duration: float
    reason: Optional[str] = None
    status: str = "Pending"
    approvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class LeaveRequestListOut(BaseModel):
    total: int
    items: List[LeaveRequestOut]
    page: int = 1
    page_size: int = 20


# ── Payroll ──

class PayrollItemCreate(BaseModel):
    category: str
    amount: float
    remark: Optional[str] = None


class PayrollCreate(BaseModel):
    storeId: str
    employeeId: str
    yearMonth: str
    totalAmount: float
    status: str = "Draft"
    items: Optional[List[PayrollItemCreate]] = None


class PayrollUpdate(BaseModel):
    totalAmount: Optional[float] = None
    status: Optional[str] = None
    paidAt: Optional[datetime] = None


class PayrollItemOut(BaseModel):
    itemId: str
    payrollId: str
    category: str
    amount: float
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class PayrollOut(BaseModel):
    payrollId: str
    storeId: str
    storeName: Optional[str] = None
    employeeId: str
    employeeName: Optional[str] = None
    yearMonth: str
    totalAmount: float
    status: str = "Draft"
    paidAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    items: List[PayrollItemOut] = []

    class Config:
        from_attributes = True


class PayrollListOut(BaseModel):
    total: int
    items: List[PayrollOut]
    page: int = 1
    page_size: int = 20


# ── PerformanceReview ──

class PerformanceReviewCreate(BaseModel):
    employeeId: str
    storeId: str
    reviewDate: date
    score: Optional[float] = None
    rating: Optional[str] = None
    reviewContent: Optional[str] = None
    reviewerId: str
    status: str = "Draft"


class PerformanceReviewUpdate(BaseModel):
    score: Optional[float] = None
    rating: Optional[str] = None
    reviewContent: Optional[str] = None
    status: Optional[str] = None


class PerformanceReviewOut(BaseModel):
    reviewId: str
    employeeId: str
    employeeName: Optional[str] = None
    storeId: str
    storeName: Optional[str] = None
    reviewDate: date
    score: Optional[float] = None
    rating: Optional[str] = None
    reviewContent: Optional[str] = None
    reviewerId: str
    reviewerName: Optional[str] = None
    status: str = "Draft"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PerformanceReviewListOut(BaseModel):
    total: int
    items: List[PerformanceReviewOut]
    page: int = 1
    page_size: int = 20


# ── CleanerAssessment ──

class CleanerAssessmentCreate(BaseModel):
    storeId: str
    staffId: str
    reviewDate: date
    score: Optional[float] = None
    rating: Optional[str] = None
    detailItems: Optional[str] = None
    reviewerId: str
    remark: Optional[str] = None


class CleanerAssessmentUpdate(BaseModel):
    score: Optional[float] = None
    rating: Optional[str] = None
    detailItems: Optional[str] = None
    remark: Optional[str] = None


class CleanerAssessmentOut(BaseModel):
    assessmentId: str
    storeId: str
    storeName: Optional[str] = None
    staffId: str
    staffName: Optional[str] = None
    reviewDate: date
    score: Optional[float] = None
    rating: Optional[str] = None
    detailItems: Optional[str] = None
    reviewerId: str
    reviewerName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CleanerAssessmentListOut(BaseModel):
    total: int
    items: List[CleanerAssessmentOut]
    page: int = 1
    page_size: int = 20
