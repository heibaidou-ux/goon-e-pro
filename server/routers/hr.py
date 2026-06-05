"""D07 人力资源域 API — 部门/岗位/员工/排班/考勤/薪资/绩效"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from datetime import datetime, date

from database import get_db
from models.hr import (
    Department, Position, Job, SalaryGrade, PromotionRecord,
    Employee, ExternalStaff, Schedule, ScheduleSwap,
    Attendance, LeaveRequest, Payroll, PayrollItem,
    PerformanceReview, CleanerAssessment,
)
from models.store_dev import Store
from models.user import User
from schemas.hr import (
    DepartmentCreate, DepartmentUpdate, DepartmentOut, DepartmentListOut, DepartmentTreeOut,
    PositionCreate, PositionUpdate, PositionOut, PositionListOut,
    JobCreate, JobUpdate, JobOut, JobListOut,
    SalaryGradeCreate, SalaryGradeUpdate, SalaryGradeOut, SalaryGradeListOut,
    PromotionRecordCreate, PromotionRecordOut, PromotionRecordListOut,
    EmployeeCreate, EmployeeUpdate, EmployeeOut, EmployeeListOut,
    ExternalStaffCreate, ExternalStaffUpdate, ExternalStaffOut, ExternalStaffListOut,
    ScheduleCreate, ScheduleUpdate, ScheduleOut, ScheduleListOut,
    ScheduleSwapCreate, ScheduleSwapUpdate, ScheduleSwapOut, ScheduleSwapListOut,
    AttendanceCreate, AttendanceUpdate, AttendanceOut, AttendanceListOut,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestOut, LeaveRequestListOut,
    PayrollCreate, PayrollUpdate, PayrollOut, PayrollListOut, PayrollItemOut,
    PerformanceReviewCreate, PerformanceReviewUpdate, PerformanceReviewOut, PerformanceReviewListOut,
    CleanerAssessmentCreate, CleanerAssessmentUpdate, CleanerAssessmentOut, CleanerAssessmentListOut,
)
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/hr", tags=["人力资源管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


async def _get_store_name(db: AsyncSession, store_id: str) -> Optional[str]:
    if not store_id:
        return None
    r = await db.execute(select(Store.name).where(Store.storeId == store_id))
    return r.scalar_one_or_none()


async def _get_employee_name(db: AsyncSession, employee_id: str) -> Optional[str]:
    if not employee_id:
        return None
    r = await db.execute(select(Employee.name).where(Employee.employeeId == employee_id))
    return r.scalar_one_or_none()


async def _get_department_name(db: AsyncSession, department_id: str) -> Optional[str]:
    if not department_id:
        return None
    r = await db.execute(select(Department.name).where(Department.departmentId == department_id))
    return r.scalar_one_or_none()


async def _get_position_name(db: AsyncSession, position_id: str) -> Optional[str]:
    if not position_id:
        return None
    r = await db.execute(select(Position.name).where(Position.positionId == position_id))
    return r.scalar_one_or_none()


async def _get_job_name(db: AsyncSession, job_id: str) -> Optional[str]:
    if not job_id:
        return None
    r = await db.execute(select(Job.name).where(Job.jobId == job_id))
    return r.scalar_one_or_none()


async def _get_salary_grade_name(db: AsyncSession, grade_id: str) -> Optional[str]:
    if not grade_id:
        return None
    r = await db.execute(select(SalaryGrade.name).where(SalaryGrade.gradeId == grade_id))
    return r.scalar_one_or_none()


# ═══════════════════════════════════════════
# Department 部门
# ═══════════════════════════════════════════

@router.get("/departments", response_model=DepartmentListOut)
async def list_departments(
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Department)
    if store_id:
        q = q.where(Department.storeId == store_id)
    if status:
        q = q.where(Department.status == status)
    q = q.order_by(Department.sortOrder.asc(), Department.createdAt.desc())

    count_q = select(func.count(Department.departmentId)).select_from(Department)
    if store_id:
        count_q = count_q.where(Department.storeId == store_id)
    if status:
        count_q = count_q.where(Department.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        result.append(DepartmentOut(
            departmentId=item.departmentId, storeId=item.storeId, storeName=store_name,
            name=item.name, parentId=item.parentId, sortOrder=item.sortOrder,
            status=item.status, createdAt=item.createdAt,
        ))

    return DepartmentListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/departments/{department_id}", response_model=DepartmentOut)
async def get_department(department_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Department).where(Department.departmentId == department_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "部门不存在")
    store_name = await _get_store_name(db, item.storeId)
    return DepartmentOut(
        departmentId=item.departmentId, storeId=item.storeId, storeName=store_name,
        name=item.name, parentId=item.parentId, sortOrder=item.sortOrder,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/departments", response_model=DepartmentOut, status_code=201)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Department(
        departmentId=_gen_id(), storeId=data.storeId, name=data.name,
        parentId=data.parentId, sortOrder=data.sortOrder, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    return DepartmentOut(
        departmentId=item.departmentId, storeId=item.storeId, storeName=store_name,
        name=item.name, parentId=item.parentId, sortOrder=item.sortOrder,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/departments/{department_id}", response_model=DepartmentOut)
async def update_department(
    department_id: str,
    data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Department).where(Department.departmentId == department_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "部门不存在")
    if data.name is not None:
        item.name = data.name
    if data.parentId is not None:
        item.parentId = data.parentId
    if data.sortOrder is not None:
        item.sortOrder = data.sortOrder
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    return DepartmentOut(
        departmentId=item.departmentId, storeId=item.storeId, storeName=store_name,
        name=item.name, parentId=item.parentId, sortOrder=item.sortOrder,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/departments/{department_id}")
async def delete_department(department_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Department).where(Department.departmentId == department_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "部门不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "部门已删除"}


@router.get("/departments/tree", response_model=list[DepartmentTreeOut])
async def department_tree(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Get department tree structure."""
    q = select(Department)
    if store_id:
        q = q.where(Department.storeId == store_id)
    q = q.order_by(Department.sortOrder.asc())
    r = await db.execute(q)
    all_depts = r.scalars().all()

    dept_map = {}
    for d in all_depts:
        dept_map[d.departmentId] = DepartmentTreeOut(
            departmentId=d.departmentId, name=d.name,
            parentId=d.parentId, sortOrder=d.sortOrder,
            status=d.status, children=[],
        )

    roots = []
    for d in all_depts:
        node = dept_map[d.departmentId]
        if d.parentId and d.parentId in dept_map:
            dept_map[d.parentId].children.append(node)
        else:
            roots.append(node)

    return roots


# ═══════════════════════════════════════════
# Position 岗位
# ═══════════════════════════════════════════

@router.get("/positions", response_model=PositionListOut)
async def list_positions(
    department_id: Optional[str] = Query(None, alias="departmentId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Position)
    if department_id:
        q = q.where(Position.departmentId == department_id)
    if status:
        q = q.where(Position.status == status)
    q = q.order_by(Position.createdAt.desc())

    count_q = select(func.count(Position.positionId)).select_from(Position)
    if department_id:
        count_q = count_q.where(Position.departmentId == department_id)
    if status:
        count_q = count_q.where(Position.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        dept_name = await _get_department_name(db, item.departmentId)
        result.append(PositionOut(
            positionId=item.positionId, departmentId=item.departmentId, departmentName=dept_name,
            name=item.name, jobLevel=item.jobLevel, description=item.description,
            status=item.status, createdAt=item.createdAt,
        ))

    return PositionListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/positions/{position_id}", response_model=PositionOut)
async def get_position(position_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Position).where(Position.positionId == position_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "岗位不存在")
    dept_name = await _get_department_name(db, item.departmentId)
    return PositionOut(
        positionId=item.positionId, departmentId=item.departmentId, departmentName=dept_name,
        name=item.name, jobLevel=item.jobLevel, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/positions", response_model=PositionOut, status_code=201)
async def create_position(
    data: PositionCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Position(
        positionId=_gen_id(), departmentId=data.departmentId, name=data.name,
        jobLevel=data.jobLevel, description=data.description, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    dept_name = await _get_department_name(db, item.departmentId)
    return PositionOut(
        positionId=item.positionId, departmentId=item.departmentId, departmentName=dept_name,
        name=item.name, jobLevel=item.jobLevel, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/positions/{position_id}", response_model=PositionOut)
async def update_position(
    position_id: str,
    data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Position).where(Position.positionId == position_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "岗位不存在")
    if data.name is not None:
        item.name = data.name
    if data.jobLevel is not None:
        item.jobLevel = data.jobLevel
    if data.description is not None:
        item.description = data.description
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    dept_name = await _get_department_name(db, item.departmentId)
    return PositionOut(
        positionId=item.positionId, departmentId=item.departmentId, departmentName=dept_name,
        name=item.name, jobLevel=item.jobLevel, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/positions/{position_id}")
async def delete_position(position_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Position).where(Position.positionId == position_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "岗位不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "岗位已删除"}


# ═══════════════════════════════════════════
# Job 职务
# ═══════════════════════════════════════════

@router.get("/jobs", response_model=JobListOut)
async def list_jobs(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Job)
    if status:
        q = q.where(Job.status == status)
    q = q.order_by(Job.createdAt.desc())

    count_q = select(func.count(Job.jobId)).select_from(Job)
    if status:
        count_q = count_q.where(Job.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [JobOut(
        jobId=item.jobId, name=item.name, description=item.description,
        status=item.status, createdAt=item.createdAt,
    ) for item in items]

    return JobListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Job).where(Job.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "职务不存在")
    return JobOut(
        jobId=item.jobId, name=item.name, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/jobs", response_model=JobOut, status_code=201)
async def create_job(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Job(
        jobId=_gen_id(), name=data.name, description=data.description, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return JobOut(
        jobId=item.jobId, name=item.name, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/jobs/{job_id}", response_model=JobOut)
async def update_job(
    job_id: str,
    data: JobUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Job).where(Job.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "职务不存在")
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return JobOut(
        jobId=item.jobId, name=item.name, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Job).where(Job.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "职务不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "职务已删除"}


# ═══════════════════════════════════════════
# SalaryGrade 薪资等级
# ═══════════════════════════════════════════

@router.get("/salary-grades", response_model=SalaryGradeListOut)
async def list_salary_grades(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(SalaryGrade)
    if status:
        q = q.where(SalaryGrade.status == status)
    q = q.order_by(SalaryGrade.minSalary.asc())

    count_q = select(func.count(SalaryGrade.gradeId)).select_from(SalaryGrade)
    if status:
        count_q = count_q.where(SalaryGrade.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = [SalaryGradeOut(
        gradeId=item.gradeId, name=item.name, minSalary=item.minSalary,
        maxSalary=item.maxSalary, status=item.status, createdAt=item.createdAt,
    ) for item in items]

    return SalaryGradeListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/salary-grades/{grade_id}", response_model=SalaryGradeOut)
async def get_salary_grade(grade_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SalaryGrade).where(SalaryGrade.gradeId == grade_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资等级不存在")
    return SalaryGradeOut(
        gradeId=item.gradeId, name=item.name, minSalary=item.minSalary,
        maxSalary=item.maxSalary, status=item.status, createdAt=item.createdAt,
    )


@router.post("/salary-grades", response_model=SalaryGradeOut, status_code=201)
async def create_salary_grade(
    data: SalaryGradeCreate,
    db: AsyncSession = Depends(get_db),
):
    item = SalaryGrade(
        gradeId=_gen_id(), name=data.name, minSalary=data.minSalary,
        maxSalary=data.maxSalary, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SalaryGradeOut(
        gradeId=item.gradeId, name=item.name, minSalary=item.minSalary,
        maxSalary=item.maxSalary, status=item.status, createdAt=item.createdAt,
    )


@router.put("/salary-grades/{grade_id}", response_model=SalaryGradeOut)
async def update_salary_grade(
    grade_id: str,
    data: SalaryGradeUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(SalaryGrade).where(SalaryGrade.gradeId == grade_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资等级不存在")
    if data.name is not None:
        item.name = data.name
    if data.minSalary is not None:
        item.minSalary = data.minSalary
    if data.maxSalary is not None:
        item.maxSalary = data.maxSalary
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return SalaryGradeOut(
        gradeId=item.gradeId, name=item.name, minSalary=item.minSalary,
        maxSalary=item.maxSalary, status=item.status, createdAt=item.createdAt,
    )


@router.delete("/salary-grades/{grade_id}")
async def delete_salary_grade(grade_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SalaryGrade).where(SalaryGrade.gradeId == grade_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资等级不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "薪资等级已删除"}


# ═══════════════════════════════════════════
# PromotionRecord 晋升记录
# ═══════════════════════════════════════════

@router.get("/promotions", response_model=PromotionRecordListOut)
async def list_promotions(
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(PromotionRecord)
    if employee_id:
        q = q.where(PromotionRecord.employeeId == employee_id)
    q = q.order_by(PromotionRecord.effectiveDate.desc())

    count_q = select(func.count(PromotionRecord.promotionId)).select_from(PromotionRecord)
    if employee_id:
        count_q = count_q.where(PromotionRecord.employeeId == employee_id)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        emp_name = await _get_employee_name(db, item.employeeId)
        from_pos = await _get_position_name(db, item.fromPositionId)
        to_pos = await _get_position_name(db, item.toPositionId)
        from_grade = await _get_salary_grade_name(db, item.fromSalaryGradeId)
        to_grade = await _get_salary_grade_name(db, item.toSalaryGradeId)
        result.append(PromotionRecordOut(
            promotionId=item.promotionId, employeeId=item.employeeId, employeeName=emp_name,
            fromPositionId=item.fromPositionId, fromPositionName=from_pos,
            toPositionId=item.toPositionId, toPositionName=to_pos,
            fromSalaryGradeId=item.fromSalaryGradeId, fromSalaryGradeName=from_grade,
            toSalaryGradeId=item.toSalaryGradeId, toSalaryGradeName=to_grade,
            effectiveDate=item.effectiveDate, reason=item.reason,
            approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return PromotionRecordListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/promotions/{promotion_id}", response_model=PromotionRecordOut)
async def get_promotion(promotion_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(PromotionRecord).where(PromotionRecord.promotionId == promotion_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "晋升记录不存在")
    emp_name = await _get_employee_name(db, item.employeeId)
    from_pos = await _get_position_name(db, item.fromPositionId)
    to_pos = await _get_position_name(db, item.toPositionId)
    from_grade = await _get_salary_grade_name(db, item.fromSalaryGradeId)
    to_grade = await _get_salary_grade_name(db, item.toSalaryGradeId)
    return PromotionRecordOut(
        promotionId=item.promotionId, employeeId=item.employeeId, employeeName=emp_name,
        fromPositionId=item.fromPositionId, fromPositionName=from_pos,
        toPositionId=item.toPositionId, toPositionName=to_pos,
        fromSalaryGradeId=item.fromSalaryGradeId, fromSalaryGradeName=from_grade,
        toSalaryGradeId=item.toSalaryGradeId, toSalaryGradeName=to_grade,
        effectiveDate=item.effectiveDate, reason=item.reason,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.post("/promotions", response_model=PromotionRecordOut, status_code=201)
async def create_promotion(
    data: PromotionRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    item = PromotionRecord(
        promotionId=_gen_id(), employeeId=data.employeeId,
        fromPositionId=data.fromPositionId, toPositionId=data.toPositionId,
        fromSalaryGradeId=data.fromSalaryGradeId, toSalaryGradeId=data.toSalaryGradeId,
        effectiveDate=data.effectiveDate, reason=data.reason, approvedBy=data.approvedBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    emp_name = await _get_employee_name(db, item.employeeId)
    from_pos = await _get_position_name(db, item.fromPositionId)
    to_pos = await _get_position_name(db, item.toPositionId)
    from_grade = await _get_salary_grade_name(db, item.fromSalaryGradeId)
    to_grade = await _get_salary_grade_name(db, item.toSalaryGradeId)
    return PromotionRecordOut(
        promotionId=item.promotionId, employeeId=item.employeeId, employeeName=emp_name,
        fromPositionId=item.fromPositionId, fromPositionName=from_pos,
        toPositionId=item.toPositionId, toPositionName=to_pos,
        fromSalaryGradeId=item.fromSalaryGradeId, fromSalaryGradeName=from_grade,
        toSalaryGradeId=item.toSalaryGradeId, toSalaryGradeName=to_grade,
        effectiveDate=item.effectiveDate, reason=item.reason,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# Employee 员工（核心数据）
# ═══════════════════════════════════════════

@router.get("/employees/search", response_model=list[EmployeeOut])
async def search_employees(
    store_id: Optional[str] = Query(None, alias="storeId"),
    name: Optional[str] = None,
    phone: Optional[str] = None,
    employee_number: Optional[str] = Query(None, alias="employeeNumber"),
    db: AsyncSession = Depends(get_db),
):
    """Search employees by store, name, phone, or employee number."""
    q = select(Employee)
    if store_id:
        q = q.where(Employee.storeId == store_id)
    if name:
        q = q.where(Employee.name.contains(name))
    if phone:
        q = q.where(Employee.phone.contains(phone))
    if employee_number:
        q = q.where(Employee.employeeNumber.contains(employee_number))
    q = q.order_by(Employee.createdAt.desc())
    q = q.limit(50)

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        dept_name = await _get_department_name(db, item.departmentId)
        pos_name = await _get_position_name(db, item.positionId)
        job_name = await _get_job_name(db, item.jobId)
        grade_name = await _get_salary_grade_name(db, item.salaryGradeId)
        result.append(EmployeeOut(
            employeeId=item.employeeId, storeId=item.storeId, storeName=store_name,
            departmentId=item.departmentId, departmentName=dept_name,
            positionId=item.positionId, positionName=pos_name,
            jobId=item.jobId, jobName=job_name,
            salaryGradeId=item.salaryGradeId, salaryGradeName=grade_name,
            employeeNumber=item.employeeNumber, name=item.name,
            phone=item.phone, idCard=item.idCard, gender=item.gender,
            birthday=item.birthday, hireDate=item.hireDate, type=item.type,
            education=item.education, bankName=item.bankName,
            bankAccount=item.bankAccount, status=item.status,
            resignedDate=item.resignedDate, createdAt=item.createdAt,
        ))

    return result


@router.get("/employees", response_model=EmployeeListOut)
async def list_employees(
    store_id: Optional[str] = Query(None, alias="storeId"),
    department_id: Optional[str] = Query(None, alias="departmentId"),
    status: Optional[str] = None,
    type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Employee)
    if store_id:
        q = q.where(Employee.storeId == store_id)
    if department_id:
        q = q.where(Employee.departmentId == department_id)
    if status:
        q = q.where(Employee.status == status)
    if type:
        q = q.where(Employee.type == type)
    if search:
        q = q.where(or_(
            Employee.name.contains(search),
            Employee.employeeNumber.contains(search),
            Employee.phone.contains(search),
        ))
    q = q.order_by(Employee.createdAt.desc())

    count_q = select(func.count(Employee.employeeId)).select_from(Employee)
    if store_id:
        count_q = count_q.where(Employee.storeId == store_id)
    if department_id:
        count_q = count_q.where(Employee.departmentId == department_id)
    if status:
        count_q = count_q.where(Employee.status == status)
    if type:
        count_q = count_q.where(Employee.type == type)
    if search:
        count_q = count_q.where(or_(
            Employee.name.contains(search),
            Employee.employeeNumber.contains(search),
            Employee.phone.contains(search),
        ))
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        dept_name = await _get_department_name(db, item.departmentId)
        pos_name = await _get_position_name(db, item.positionId)
        job_name = await _get_job_name(db, item.jobId)
        grade_name = await _get_salary_grade_name(db, item.salaryGradeId)
        result.append(EmployeeOut(
            employeeId=item.employeeId, storeId=item.storeId, storeName=store_name,
            departmentId=item.departmentId, departmentName=dept_name,
            positionId=item.positionId, positionName=pos_name,
            jobId=item.jobId, jobName=job_name,
            salaryGradeId=item.salaryGradeId, salaryGradeName=grade_name,
            employeeNumber=item.employeeNumber, name=item.name,
            phone=item.phone, idCard=item.idCard, gender=item.gender,
            birthday=item.birthday, hireDate=item.hireDate, type=item.type,
            education=item.education, bankName=item.bankName,
            bankAccount=item.bankAccount, status=item.status,
            resignedDate=item.resignedDate, createdAt=item.createdAt,
        ))

    return EmployeeListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/employees/{employee_id}", response_model=EmployeeOut)
async def get_employee(employee_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Employee).where(Employee.employeeId == employee_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "员工不存在")
    store_name = await _get_store_name(db, item.storeId)
    dept_name = await _get_department_name(db, item.departmentId)
    pos_name = await _get_position_name(db, item.positionId)
    job_name = await _get_job_name(db, item.jobId)
    grade_name = await _get_salary_grade_name(db, item.salaryGradeId)
    return EmployeeOut(
        employeeId=item.employeeId, storeId=item.storeId, storeName=store_name,
        departmentId=item.departmentId, departmentName=dept_name,
        positionId=item.positionId, positionName=pos_name,
        jobId=item.jobId, jobName=job_name,
        salaryGradeId=item.salaryGradeId, salaryGradeName=grade_name,
        employeeNumber=item.employeeNumber, name=item.name,
        phone=item.phone, idCard=item.idCard, gender=item.gender,
        birthday=item.birthday, hireDate=item.hireDate, type=item.type,
        education=item.education, bankName=item.bankName,
        bankAccount=item.bankAccount, status=item.status,
        resignedDate=item.resignedDate, createdAt=item.createdAt,
    )


@router.post("/employees", response_model=EmployeeOut, status_code=201)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check employee number uniqueness
    r = await db.execute(select(Employee).where(Employee.employeeNumber == data.employeeNumber))
    if r.scalar_one_or_none():
        raise HTTPException(409, "员工编号已存在")

    item = Employee(
        employeeId=_gen_id(), storeId=data.storeId,
        departmentId=data.departmentId, positionId=data.positionId,
        jobId=data.jobId, salaryGradeId=data.salaryGradeId,
        employeeNumber=data.employeeNumber, name=data.name,
        phone=data.phone, idCard=data.idCard, gender=data.gender,
        birthday=data.birthday, hireDate=data.hireDate, type=data.type,
        education=data.education, bankName=data.bankName,
        bankAccount=data.bankAccount, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    dept_name = await _get_department_name(db, item.departmentId)
    pos_name = await _get_position_name(db, item.positionId)
    job_name = await _get_job_name(db, item.jobId)
    grade_name = await _get_salary_grade_name(db, item.salaryGradeId)
    return EmployeeOut(
        employeeId=item.employeeId, storeId=item.storeId, storeName=store_name,
        departmentId=item.departmentId, departmentName=dept_name,
        positionId=item.positionId, positionName=pos_name,
        jobId=item.jobId, jobName=job_name,
        salaryGradeId=item.salaryGradeId, salaryGradeName=grade_name,
        employeeNumber=item.employeeNumber, name=item.name,
        phone=item.phone, idCard=item.idCard, gender=item.gender,
        birthday=item.birthday, hireDate=item.hireDate, type=item.type,
        education=item.education, bankName=item.bankName,
        bankAccount=item.bankAccount, status=item.status,
        resignedDate=item.resignedDate, createdAt=item.createdAt,
    )


@router.put("/employees/{employee_id}", response_model=EmployeeOut)
async def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Employee).where(Employee.employeeId == employee_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "员工不存在")
    if data.departmentId is not None:
        item.departmentId = data.departmentId
    if data.positionId is not None:
        item.positionId = data.positionId
    if data.jobId is not None:
        item.jobId = data.jobId
    if data.salaryGradeId is not None:
        item.salaryGradeId = data.salaryGradeId
    if data.name is not None:
        item.name = data.name
    if data.phone is not None:
        item.phone = data.phone
    if data.idCard is not None:
        item.idCard = data.idCard
    if data.gender is not None:
        item.gender = data.gender
    if data.birthday is not None:
        item.birthday = data.birthday
    if data.hireDate is not None:
        item.hireDate = data.hireDate
    if data.type is not None:
        item.type = data.type
    if data.education is not None:
        item.education = data.education
    if data.bankName is not None:
        item.bankName = data.bankName
    if data.bankAccount is not None:
        item.bankAccount = data.bankAccount
    if data.status is not None:
        item.status = data.status
    if data.resignedDate is not None:
        item.resignedDate = data.resignedDate
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    dept_name = await _get_department_name(db, item.departmentId)
    pos_name = await _get_position_name(db, item.positionId)
    job_name = await _get_job_name(db, item.jobId)
    grade_name = await _get_salary_grade_name(db, item.salaryGradeId)
    return EmployeeOut(
        employeeId=item.employeeId, storeId=item.storeId, storeName=store_name,
        departmentId=item.departmentId, departmentName=dept_name,
        positionId=item.positionId, positionName=pos_name,
        jobId=item.jobId, jobName=job_name,
        salaryGradeId=item.salaryGradeId, salaryGradeName=grade_name,
        employeeNumber=item.employeeNumber, name=item.name,
        phone=item.phone, idCard=item.idCard, gender=item.gender,
        birthday=item.birthday, hireDate=item.hireDate, type=item.type,
        education=item.education, bankName=item.bankName,
        bankAccount=item.bankAccount, status=item.status,
        resignedDate=item.resignedDate, createdAt=item.createdAt,
    )


@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Employee).where(Employee.employeeId == employee_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "员工不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "员工已删除"}


# ═══════════════════════════════════════════
# ExternalStaff 外协人员
# ═══════════════════════════════════════════

@router.get("/external-staff", response_model=ExternalStaffListOut)
async def list_external_staff(
    store_id: Optional[str] = Query(None, alias="storeId"),
    service_type: Optional[str] = Query(None, alias="serviceType"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ExternalStaff)
    if store_id:
        q = q.where(ExternalStaff.storeId == store_id)
    if service_type:
        q = q.where(ExternalStaff.serviceType == service_type)
    if status:
        q = q.where(ExternalStaff.status == status)
    q = q.order_by(ExternalStaff.createdAt.desc())

    count_q = select(func.count(ExternalStaff.staffId)).select_from(ExternalStaff)
    if store_id:
        count_q = count_q.where(ExternalStaff.storeId == store_id)
    if service_type:
        count_q = count_q.where(ExternalStaff.serviceType == service_type)
    if status:
        count_q = count_q.where(ExternalStaff.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        result.append(ExternalStaffOut(
            staffId=item.staffId, storeId=item.storeId, storeName=store_name,
            company=item.company, name=item.name, phone=item.phone,
            idCard=item.idCard, serviceType=item.serviceType,
            contractStartDate=item.contractStartDate,
            contractEndDate=item.contractEndDate,
            status=item.status, createdAt=item.createdAt,
        ))

    return ExternalStaffListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/external-staff/{staff_id}", response_model=ExternalStaffOut)
async def get_external_staff(staff_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ExternalStaff).where(ExternalStaff.staffId == staff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "外协人员不存在")
    store_name = await _get_store_name(db, item.storeId)
    return ExternalStaffOut(
        staffId=item.staffId, storeId=item.storeId, storeName=store_name,
        company=item.company, name=item.name, phone=item.phone,
        idCard=item.idCard, serviceType=item.serviceType,
        contractStartDate=item.contractStartDate,
        contractEndDate=item.contractEndDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.post("/external-staff", response_model=ExternalStaffOut, status_code=201)
async def create_external_staff(
    data: ExternalStaffCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ExternalStaff(
        staffId=_gen_id(), storeId=data.storeId, company=data.company,
        name=data.name, phone=data.phone, idCard=data.idCard,
        serviceType=data.serviceType, contractStartDate=data.contractStartDate,
        contractEndDate=data.contractEndDate, status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    return ExternalStaffOut(
        staffId=item.staffId, storeId=item.storeId, storeName=store_name,
        company=item.company, name=item.name, phone=item.phone,
        idCard=item.idCard, serviceType=item.serviceType,
        contractStartDate=item.contractStartDate,
        contractEndDate=item.contractEndDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/external-staff/{staff_id}", response_model=ExternalStaffOut)
async def update_external_staff(
    staff_id: str,
    data: ExternalStaffUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ExternalStaff).where(ExternalStaff.staffId == staff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "外协人员不存在")
    if data.company is not None:
        item.company = data.company
    if data.name is not None:
        item.name = data.name
    if data.phone is not None:
        item.phone = data.phone
    if data.idCard is not None:
        item.idCard = data.idCard
    if data.serviceType is not None:
        item.serviceType = data.serviceType
    if data.contractStartDate is not None:
        item.contractStartDate = data.contractStartDate
    if data.contractEndDate is not None:
        item.contractEndDate = data.contractEndDate
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    return ExternalStaffOut(
        staffId=item.staffId, storeId=item.storeId, storeName=store_name,
        company=item.company, name=item.name, phone=item.phone,
        idCard=item.idCard, serviceType=item.serviceType,
        contractStartDate=item.contractStartDate,
        contractEndDate=item.contractEndDate,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/external-staff/{staff_id}")
async def delete_external_staff(staff_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ExternalStaff).where(ExternalStaff.staffId == staff_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "外协人员不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "外协人员已删除"}


# ═══════════════════════════════════════════
# Schedule 排班
# ═══════════════════════════════════════════

@router.get("/schedules", response_model=ScheduleListOut)
async def list_schedules(
    store_id: Optional[str] = Query(None, alias="storeId"),
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Schedule)
    if store_id:
        q = q.where(Schedule.storeId == store_id)
    if employee_id:
        q = q.where(Schedule.employeeId == employee_id)
    if start_date:
        q = q.where(Schedule.workDate >= start_date)
    if end_date:
        q = q.where(Schedule.workDate <= end_date)
    q = q.order_by(Schedule.workDate.desc(), Schedule.startTime.asc())

    count_q = select(func.count(Schedule.scheduleId)).select_from(Schedule)
    if store_id:
        count_q = count_q.where(Schedule.storeId == store_id)
    if employee_id:
        count_q = count_q.where(Schedule.employeeId == employee_id)
    if start_date:
        count_q = count_q.where(Schedule.workDate >= start_date)
    if end_date:
        count_q = count_q.where(Schedule.workDate <= end_date)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(ScheduleOut(
            scheduleId=item.scheduleId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            workDate=item.workDate, startTime=item.startTime, endTime=item.endTime,
            scheduleType=item.scheduleType, isHoliday=item.isHoliday,
            createdBy=item.createdBy, createdAt=item.createdAt,
        ))

    return ScheduleListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/schedules/weekly", response_model=list[ScheduleOut])
async def weekly_schedule(
    store_id: Optional[str] = Query(None, alias="storeId"),
    week_start: Optional[str] = Query(None, alias="weekStart"),
    db: AsyncSession = Depends(get_db),
):
    """Get schedule for a specific week."""
    q = select(Schedule)
    if store_id:
        q = q.where(Schedule.storeId == store_id)
    if week_start:
        from datetime import timedelta
        ws = datetime.strptime(week_start, "%Y-%m-%d").date()
        week_end = ws + timedelta(days=6)
        q = q.where(Schedule.workDate >= ws, Schedule.workDate <= week_end)
    q = q.order_by(Schedule.workDate.asc(), Schedule.startTime.asc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(ScheduleOut(
            scheduleId=item.scheduleId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            workDate=item.workDate, startTime=item.startTime, endTime=item.endTime,
            scheduleType=item.scheduleType, isHoliday=item.isHoliday,
            createdBy=item.createdBy, createdAt=item.createdAt,
        ))

    return result


@router.get("/schedules/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Schedule).where(Schedule.scheduleId == schedule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班记录不存在")
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return ScheduleOut(
        scheduleId=item.scheduleId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        workDate=item.workDate, startTime=item.startTime, endTime=item.endTime,
        scheduleType=item.scheduleType, isHoliday=item.isHoliday,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.post("/schedules", response_model=ScheduleOut, status_code=201)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Schedule(
        scheduleId=_gen_id(), storeId=data.storeId, employeeId=data.employeeId,
        workDate=data.workDate, startTime=data.startTime, endTime=data.endTime,
        scheduleType=data.scheduleType, isHoliday=data.isHoliday,
        createdBy=data.createdBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return ScheduleOut(
        scheduleId=item.scheduleId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        workDate=item.workDate, startTime=item.startTime, endTime=item.endTime,
        scheduleType=item.scheduleType, isHoliday=item.isHoliday,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.put("/schedules/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: str,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Schedule).where(Schedule.scheduleId == schedule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班记录不存在")
    if data.startTime is not None:
        item.startTime = data.startTime
    if data.endTime is not None:
        item.endTime = data.endTime
    if data.scheduleType is not None:
        item.scheduleType = data.scheduleType
    if data.isHoliday is not None:
        item.isHoliday = data.isHoliday
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return ScheduleOut(
        scheduleId=item.scheduleId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        workDate=item.workDate, startTime=item.startTime, endTime=item.endTime,
        scheduleType=item.scheduleType, isHoliday=item.isHoliday,
        createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Schedule).where(Schedule.scheduleId == schedule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "排班已删除"}


# ═══════════════════════════════════════════
# ScheduleSwap 排班调换
# ═══════════════════════════════════════════

@router.get("/schedule-swaps", response_model=ScheduleSwapListOut)
async def list_schedule_swaps(
    from_employee_id: Optional[str] = Query(None, alias="fromEmployeeId"),
    to_employee_id: Optional[str] = Query(None, alias="toEmployeeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ScheduleSwap)
    if from_employee_id:
        q = q.where(ScheduleSwap.fromEmployeeId == from_employee_id)
    if to_employee_id:
        q = q.where(ScheduleSwap.toEmployeeId == to_employee_id)
    if status:
        q = q.where(ScheduleSwap.status == status)
    q = q.order_by(ScheduleSwap.createdAt.desc())

    count_q = select(func.count(ScheduleSwap.swapId)).select_from(ScheduleSwap)
    if from_employee_id:
        count_q = count_q.where(ScheduleSwap.fromEmployeeId == from_employee_id)
    if to_employee_id:
        count_q = count_q.where(ScheduleSwap.toEmployeeId == to_employee_id)
    if status:
        count_q = count_q.where(ScheduleSwap.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        from_name = await _get_employee_name(db, item.fromEmployeeId)
        to_name = await _get_employee_name(db, item.toEmployeeId)
        result.append(ScheduleSwapOut(
            swapId=item.swapId, fromEmployeeId=item.fromEmployeeId, fromEmployeeName=from_name,
            toEmployeeId=item.toEmployeeId, toEmployeeName=to_name,
            scheduleId=item.scheduleId, swapDate=item.swapDate,
            reason=item.reason, status=item.status,
            approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return ScheduleSwapListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/schedule-swaps/{swap_id}", response_model=ScheduleSwapOut)
async def get_schedule_swap(swap_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ScheduleSwap).where(ScheduleSwap.swapId == swap_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班调换记录不存在")
    from_name = await _get_employee_name(db, item.fromEmployeeId)
    to_name = await _get_employee_name(db, item.toEmployeeId)
    return ScheduleSwapOut(
        swapId=item.swapId, fromEmployeeId=item.fromEmployeeId, fromEmployeeName=from_name,
        toEmployeeId=item.toEmployeeId, toEmployeeName=to_name,
        scheduleId=item.scheduleId, swapDate=item.swapDate,
        reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.post("/schedule-swaps", response_model=ScheduleSwapOut, status_code=201)
async def create_schedule_swap(
    data: ScheduleSwapCreate,
    db: AsyncSession = Depends(get_db),
):
    item = ScheduleSwap(
        swapId=_gen_id(), fromEmployeeId=data.fromEmployeeId,
        toEmployeeId=data.toEmployeeId, scheduleId=data.scheduleId,
        swapDate=data.swapDate, reason=data.reason,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    from_name = await _get_employee_name(db, item.fromEmployeeId)
    to_name = await _get_employee_name(db, item.toEmployeeId)
    return ScheduleSwapOut(
        swapId=item.swapId, fromEmployeeId=item.fromEmployeeId, fromEmployeeName=from_name,
        toEmployeeId=item.toEmployeeId, toEmployeeName=to_name,
        scheduleId=item.scheduleId, swapDate=item.swapDate,
        reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.put("/schedule-swaps/{swap_id}", response_model=ScheduleSwapOut)
async def update_schedule_swap(
    swap_id: str,
    data: ScheduleSwapUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(ScheduleSwap).where(ScheduleSwap.swapId == swap_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班调换记录不存在")
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy
    await db.commit()
    await db.refresh(item)
    from_name = await _get_employee_name(db, item.fromEmployeeId)
    to_name = await _get_employee_name(db, item.toEmployeeId)
    return ScheduleSwapOut(
        swapId=item.swapId, fromEmployeeId=item.fromEmployeeId, fromEmployeeName=from_name,
        toEmployeeId=item.toEmployeeId, toEmployeeName=to_name,
        scheduleId=item.scheduleId, swapDate=item.swapDate,
        reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.delete("/schedule-swaps/{swap_id}")
async def delete_schedule_swap(swap_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ScheduleSwap).where(ScheduleSwap.swapId == swap_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "排班调换记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "排班调换已删除"}


# ═══════════════════════════════════════════
# Attendance 考勤
# ═══════════════════════════════════════════

@router.get("/attendances", response_model=AttendanceListOut)
async def list_attendances(
    store_id: Optional[str] = Query(None, alias="storeId"),
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Attendance)
    if store_id:
        q = q.where(Attendance.storeId == store_id)
    if employee_id:
        q = q.where(Attendance.employeeId == employee_id)
    if start_date:
        q = q.where(Attendance.date >= start_date)
    if end_date:
        q = q.where(Attendance.date <= end_date)
    if status:
        q = q.where(Attendance.status == status)
    q = q.order_by(Attendance.date.desc())

    count_q = select(func.count(Attendance.attendanceId)).select_from(Attendance)
    if store_id:
        count_q = count_q.where(Attendance.storeId == store_id)
    if employee_id:
        count_q = count_q.where(Attendance.employeeId == employee_id)
    if start_date:
        count_q = count_q.where(Attendance.date >= start_date)
    if end_date:
        count_q = count_q.where(Attendance.date <= end_date)
    if status:
        count_q = count_q.where(Attendance.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(AttendanceOut(
            attendanceId=item.attendanceId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            date=item.date, clockIn=item.clockIn, clockOut=item.clockOut,
            status=item.status, remark=item.remark, createdAt=item.createdAt,
        ))

    return AttendanceListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/attendances/today", response_model=list[AttendanceOut])
async def today_attendance(
    store_id: Optional[str] = Query(None, alias="storeId"),
    db: AsyncSession = Depends(get_db),
):
    """Get today's attendance records."""
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    q = select(Attendance).where(Attendance.date == today_str)
    if store_id:
        q = q.where(Attendance.storeId == store_id)
    q = q.order_by(Attendance.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(AttendanceOut(
            attendanceId=item.attendanceId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            date=item.date, clockIn=item.clockIn, clockOut=item.clockOut,
            status=item.status, remark=item.remark, createdAt=item.createdAt,
        ))

    return result


@router.get("/attendances/{attendance_id}", response_model=AttendanceOut)
async def get_attendance(attendance_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Attendance).where(Attendance.attendanceId == attendance_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "考勤记录不存在")
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return AttendanceOut(
        attendanceId=item.attendanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        date=item.date, clockIn=item.clockIn, clockOut=item.clockOut,
        status=item.status, remark=item.remark, createdAt=item.createdAt,
    )


@router.post("/attendances", response_model=AttendanceOut, status_code=201)
async def create_attendance(
    data: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Attendance(
        attendanceId=_gen_id(), storeId=data.storeId, employeeId=data.employeeId,
        date=data.date, clockIn=data.clockIn, clockOut=data.clockOut,
        status=data.status, remark=data.remark,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return AttendanceOut(
        attendanceId=item.attendanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        date=item.date, clockIn=item.clockIn, clockOut=item.clockOut,
        status=item.status, remark=item.remark, createdAt=item.createdAt,
    )


@router.put("/attendances/{attendance_id}", response_model=AttendanceOut)
async def update_attendance(
    attendance_id: str,
    data: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Attendance).where(Attendance.attendanceId == attendance_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "考勤记录不存在")
    if data.clockIn is not None:
        item.clockIn = data.clockIn
    if data.clockOut is not None:
        item.clockOut = data.clockOut
    if data.status is not None:
        item.status = data.status
    if data.remark is not None:
        item.remark = data.remark
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    return AttendanceOut(
        attendanceId=item.attendanceId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        date=item.date, clockIn=item.clockIn, clockOut=item.clockOut,
        status=item.status, remark=item.remark, createdAt=item.createdAt,
    )


@router.delete("/attendances/{attendance_id}")
async def delete_attendance(attendance_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Attendance).where(Attendance.attendanceId == attendance_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "考勤记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "考勤记录已删除"}


# ═══════════════════════════════════════════
# LeaveRequest 请假
# ═══════════════════════════════════════════

@router.get("/leave-requests", response_model=LeaveRequestListOut)
async def list_leave_requests(
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    status: Optional[str] = None,
    leave_type: Optional[str] = Query(None, alias="leaveType"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(LeaveRequest)
    if employee_id:
        q = q.where(LeaveRequest.employeeId == employee_id)
    if status:
        q = q.where(LeaveRequest.status == status)
    if leave_type:
        q = q.where(LeaveRequest.leaveType == leave_type)
    if start_date:
        q = q.where(LeaveRequest.startDate >= start_date)
    if end_date:
        q = q.where(LeaveRequest.endDate <= end_date)
    q = q.order_by(LeaveRequest.createdAt.desc())

    count_q = select(func.count(LeaveRequest.leaveId)).select_from(LeaveRequest)
    if employee_id:
        count_q = count_q.where(LeaveRequest.employeeId == employee_id)
    if status:
        count_q = count_q.where(LeaveRequest.status == status)
    if leave_type:
        count_q = count_q.where(LeaveRequest.leaveType == leave_type)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(LeaveRequestOut(
            leaveId=item.leaveId, employeeId=item.employeeId, employeeName=emp_name,
            leaveType=item.leaveType, startDate=item.startDate, endDate=item.endDate,
            duration=item.duration, reason=item.reason, status=item.status,
            approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return LeaveRequestListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/leave-requests/pending", response_model=list[LeaveRequestOut])
async def pending_leave_requests(
    db: AsyncSession = Depends(get_db),
):
    """Get all pending leave requests."""
    q = select(LeaveRequest).where(LeaveRequest.status == "Pending")
    q = q.order_by(LeaveRequest.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        emp_name = await _get_employee_name(db, item.employeeId)
        result.append(LeaveRequestOut(
            leaveId=item.leaveId, employeeId=item.employeeId, employeeName=emp_name,
            leaveType=item.leaveType, startDate=item.startDate, endDate=item.endDate,
            duration=item.duration, reason=item.reason, status=item.status,
            approvedBy=item.approvedBy, createdAt=item.createdAt,
        ))

    return result


@router.get("/leave-requests/{leave_id}", response_model=LeaveRequestOut)
async def get_leave_request(leave_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(LeaveRequest).where(LeaveRequest.leaveId == leave_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "请假记录不存在")
    emp_name = await _get_employee_name(db, item.employeeId)
    return LeaveRequestOut(
        leaveId=item.leaveId, employeeId=item.employeeId, employeeName=emp_name,
        leaveType=item.leaveType, startDate=item.startDate, endDate=item.endDate,
        duration=item.duration, reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.post("/leave-requests", response_model=LeaveRequestOut, status_code=201)
async def create_leave_request(
    data: LeaveRequestCreate,
    db: AsyncSession = Depends(get_db),
):
    item = LeaveRequest(
        leaveId=_gen_id(), employeeId=data.employeeId, leaveType=data.leaveType,
        startDate=data.startDate, endDate=data.endDate, duration=data.duration,
        reason=data.reason,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    emp_name = await _get_employee_name(db, item.employeeId)
    return LeaveRequestOut(
        leaveId=item.leaveId, employeeId=item.employeeId, employeeName=emp_name,
        leaveType=item.leaveType, startDate=item.startDate, endDate=item.endDate,
        duration=item.duration, reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.put("/leave-requests/{leave_id}", response_model=LeaveRequestOut)
async def update_leave_request(
    leave_id: str,
    data: LeaveRequestUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(LeaveRequest).where(LeaveRequest.leaveId == leave_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "请假记录不存在")
    if data.status is not None:
        item.status = data.status
    if data.approvedBy is not None:
        item.approvedBy = data.approvedBy
    if data.reason is not None:
        item.reason = data.reason
    await db.commit()
    await db.refresh(item)
    emp_name = await _get_employee_name(db, item.employeeId)
    return LeaveRequestOut(
        leaveId=item.leaveId, employeeId=item.employeeId, employeeName=emp_name,
        leaveType=item.leaveType, startDate=item.startDate, endDate=item.endDate,
        duration=item.duration, reason=item.reason, status=item.status,
        approvedBy=item.approvedBy, createdAt=item.createdAt,
    )


@router.delete("/leave-requests/{leave_id}")
async def delete_leave_request(leave_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(LeaveRequest).where(LeaveRequest.leaveId == leave_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "请假记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "请假记录已删除"}


# ═══════════════════════════════════════════
# Payroll 薪资
# ═══════════════════════════════════════════

@router.get("/payrolls", response_model=PayrollListOut)
async def list_payrolls(
    store_id: Optional[str] = Query(None, alias="storeId"),
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    year_month: Optional[str] = Query(None, alias="yearMonth"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Payroll)
    if store_id:
        q = q.where(Payroll.storeId == store_id)
    if employee_id:
        q = q.where(Payroll.employeeId == employee_id)
    if year_month:
        q = q.where(Payroll.yearMonth == year_month)
    if status:
        q = q.where(Payroll.status == status)
    q = q.order_by(Payroll.yearMonth.desc(), Payroll.createdAt.desc())

    count_q = select(func.count(Payroll.payrollId)).select_from(Payroll)
    if store_id:
        count_q = count_q.where(Payroll.storeId == store_id)
    if employee_id:
        count_q = count_q.where(Payroll.employeeId == employee_id)
    if year_month:
        count_q = count_q.where(Payroll.yearMonth == year_month)
    if status:
        count_q = count_q.where(Payroll.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        # Load items
        items_r = await db.execute(
            select(PayrollItem).where(PayrollItem.payrollId == item.payrollId)
        )
        payroll_items = items_r.scalars().all()
        result.append(PayrollOut(
            payrollId=item.payrollId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            yearMonth=item.yearMonth, totalAmount=item.totalAmount,
            status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
            items=[PayrollItemOut(
                itemId=pi.itemId, payrollId=pi.payrollId, category=pi.category,
                amount=pi.amount, remark=pi.remark,
            ) for pi in payroll_items],
        ))

    return PayrollListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/payrolls/by-month", response_model=list[PayrollOut])
async def payroll_by_month(
    store_id: Optional[str] = Query(None, alias="storeId"),
    year_month: Optional[str] = Query(None, alias="yearMonth"),
    db: AsyncSession = Depends(get_db),
):
    """Get payroll records for a specific month."""
    q = select(Payroll)
    if store_id:
        q = q.where(Payroll.storeId == store_id)
    if year_month:
        q = q.where(Payroll.yearMonth == year_month)
    q = q.order_by(Payroll.createdAt.desc())

    r = await db.execute(q)
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        emp_name = await _get_employee_name(db, item.employeeId)
        items_r = await db.execute(
            select(PayrollItem).where(PayrollItem.payrollId == item.payrollId)
        )
        payroll_items = items_r.scalars().all()
        result.append(PayrollOut(
            payrollId=item.payrollId, storeId=item.storeId, storeName=store_name,
            employeeId=item.employeeId, employeeName=emp_name,
            yearMonth=item.yearMonth, totalAmount=item.totalAmount,
            status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
            items=[PayrollItemOut(
                itemId=pi.itemId, payrollId=pi.payrollId, category=pi.category,
                amount=pi.amount, remark=pi.remark,
            ) for pi in payroll_items],
        ))

    return result


@router.get("/payrolls/{payroll_id}", response_model=PayrollOut)
async def get_payroll(payroll_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Payroll).where(Payroll.payrollId == payroll_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资记录不存在")
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    items_r = await db.execute(
        select(PayrollItem).where(PayrollItem.payrollId == item.payrollId)
    )
    payroll_items = items_r.scalars().all()
    return PayrollOut(
        payrollId=item.payrollId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        yearMonth=item.yearMonth, totalAmount=item.totalAmount,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
        items=[PayrollItemOut(
            itemId=pi.itemId, payrollId=pi.payrollId, category=pi.category,
            amount=pi.amount, remark=pi.remark,
        ) for pi in payroll_items],
    )


@router.post("/payrolls", response_model=PayrollOut, status_code=201)
async def create_payroll(
    data: PayrollCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Payroll(
        payrollId=_gen_id(), storeId=data.storeId, employeeId=data.employeeId,
        yearMonth=data.yearMonth, totalAmount=data.totalAmount, status=data.status,
    )
    db.add(item)
    await db.flush()

    # Create items if provided
    if data.items:
        for item_data in data.items:
            pi = PayrollItem(
                itemId=_gen_id(), payrollId=item.payrollId,
                category=item_data.category, amount=item_data.amount,
                remark=item_data.remark,
            )
            db.add(pi)

    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    items_r = await db.execute(
        select(PayrollItem).where(PayrollItem.payrollId == item.payrollId)
    )
    payroll_items = items_r.scalars().all()
    return PayrollOut(
        payrollId=item.payrollId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        yearMonth=item.yearMonth, totalAmount=item.totalAmount,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
        items=[PayrollItemOut(
            itemId=pi.itemId, payrollId=pi.payrollId, category=pi.category,
            amount=pi.amount, remark=pi.remark,
        ) for pi in payroll_items],
    )


@router.put("/payrolls/{payroll_id}", response_model=PayrollOut)
async def update_payroll(
    payroll_id: str,
    data: PayrollUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Payroll).where(Payroll.payrollId == payroll_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资记录不存在")
    if data.totalAmount is not None:
        item.totalAmount = data.totalAmount
    if data.status is not None:
        item.status = data.status
    if data.paidAt is not None:
        item.paidAt = data.paidAt
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    emp_name = await _get_employee_name(db, item.employeeId)
    items_r = await db.execute(
        select(PayrollItem).where(PayrollItem.payrollId == item.payrollId)
    )
    payroll_items = items_r.scalars().all()
    return PayrollOut(
        payrollId=item.payrollId, storeId=item.storeId, storeName=store_name,
        employeeId=item.employeeId, employeeName=emp_name,
        yearMonth=item.yearMonth, totalAmount=item.totalAmount,
        status=item.status, paidAt=item.paidAt, createdAt=item.createdAt,
        items=[PayrollItemOut(
            itemId=pi.itemId, payrollId=pi.payrollId, category=pi.category,
            amount=pi.amount, remark=pi.remark,
        ) for pi in payroll_items],
    )


@router.delete("/payrolls/{payroll_id}")
async def delete_payroll(payroll_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Payroll).where(Payroll.payrollId == payroll_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "薪资记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "薪资记录已删除"}


# ═══════════════════════════════════════════
# PerformanceReview 绩效考评
# ═══════════════════════════════════════════

@router.get("/performance-reviews", response_model=PerformanceReviewListOut)
async def list_performance_reviews(
    employee_id: Optional[str] = Query(None, alias="employeeId"),
    store_id: Optional[str] = Query(None, alias="storeId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(PerformanceReview)
    if employee_id:
        q = q.where(PerformanceReview.employeeId == employee_id)
    if store_id:
        q = q.where(PerformanceReview.storeId == store_id)
    if status:
        q = q.where(PerformanceReview.status == status)
    q = q.order_by(PerformanceReview.reviewDate.desc())

    count_q = select(func.count(PerformanceReview.reviewId)).select_from(PerformanceReview)
    if employee_id:
        count_q = count_q.where(PerformanceReview.employeeId == employee_id)
    if store_id:
        count_q = count_q.where(PerformanceReview.storeId == store_id)
    if status:
        count_q = count_q.where(PerformanceReview.status == status)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        emp_name = await _get_employee_name(db, item.employeeId)
        store_name = await _get_store_name(db, item.storeId)
        reviewer_name = await _get_employee_name(db, item.reviewerId)
        result.append(PerformanceReviewOut(
            reviewId=item.reviewId, employeeId=item.employeeId, employeeName=emp_name,
            storeId=item.storeId, storeName=store_name,
            reviewDate=item.reviewDate, score=item.score, rating=item.rating,
            reviewContent=item.reviewContent, reviewerId=item.reviewerId,
            reviewerName=reviewer_name, status=item.status, createdAt=item.createdAt,
        ))

    return PerformanceReviewListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/performance-reviews/{review_id}", response_model=PerformanceReviewOut)
async def get_performance_review(review_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(PerformanceReview).where(PerformanceReview.reviewId == review_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "绩效考评记录不存在")
    emp_name = await _get_employee_name(db, item.employeeId)
    store_name = await _get_store_name(db, item.storeId)
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return PerformanceReviewOut(
        reviewId=item.reviewId, employeeId=item.employeeId, employeeName=emp_name,
        storeId=item.storeId, storeName=store_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        reviewContent=item.reviewContent, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, status=item.status, createdAt=item.createdAt,
    )


@router.post("/performance-reviews", response_model=PerformanceReviewOut, status_code=201)
async def create_performance_review(
    data: PerformanceReviewCreate,
    db: AsyncSession = Depends(get_db),
):
    item = PerformanceReview(
        reviewId=_gen_id(), employeeId=data.employeeId, storeId=data.storeId,
        reviewDate=data.reviewDate, score=data.score, rating=data.rating,
        reviewContent=data.reviewContent, reviewerId=data.reviewerId,
        status=data.status,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    emp_name = await _get_employee_name(db, item.employeeId)
    store_name = await _get_store_name(db, item.storeId)
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return PerformanceReviewOut(
        reviewId=item.reviewId, employeeId=item.employeeId, employeeName=emp_name,
        storeId=item.storeId, storeName=store_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        reviewContent=item.reviewContent, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, status=item.status, createdAt=item.createdAt,
    )


@router.put("/performance-reviews/{review_id}", response_model=PerformanceReviewOut)
async def update_performance_review(
    review_id: str,
    data: PerformanceReviewUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(PerformanceReview).where(PerformanceReview.reviewId == review_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "绩效考评记录不存在")
    if data.score is not None:
        item.score = data.score
    if data.rating is not None:
        item.rating = data.rating
    if data.reviewContent is not None:
        item.reviewContent = data.reviewContent
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    emp_name = await _get_employee_name(db, item.employeeId)
    store_name = await _get_store_name(db, item.storeId)
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return PerformanceReviewOut(
        reviewId=item.reviewId, employeeId=item.employeeId, employeeName=emp_name,
        storeId=item.storeId, storeName=store_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        reviewContent=item.reviewContent, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, status=item.status, createdAt=item.createdAt,
    )


@router.delete("/performance-reviews/{review_id}")
async def delete_performance_review(review_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(PerformanceReview).where(PerformanceReview.reviewId == review_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "绩效考评记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "绩效考评已删除"}


# ═══════════════════════════════════════════
# CleanerAssessment 保洁考核
# ═══════════════════════════════════════════

@router.get("/cleaner-assessments", response_model=CleanerAssessmentListOut)
async def list_cleaner_assessments(
    store_id: Optional[str] = Query(None, alias="storeId"),
    staff_id: Optional[str] = Query(None, alias="staffId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CleanerAssessment)
    if store_id:
        q = q.where(CleanerAssessment.storeId == store_id)
    if staff_id:
        q = q.where(CleanerAssessment.staffId == staff_id)
    q = q.order_by(CleanerAssessment.reviewDate.desc())

    count_q = select(func.count(CleanerAssessment.assessmentId)).select_from(CleanerAssessment)
    if store_id:
        count_q = count_q.where(CleanerAssessment.storeId == store_id)
    if staff_id:
        count_q = count_q.where(CleanerAssessment.staffId == staff_id)
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    result = []
    for item in items:
        store_name = await _get_store_name(db, item.storeId)
        staff_name = None
        if item.staffId:
            sr = await db.execute(select(ExternalStaff.name).where(ExternalStaff.staffId == item.staffId))
            staff_name = sr.scalar_one_or_none()
        reviewer_name = await _get_employee_name(db, item.reviewerId)
        result.append(CleanerAssessmentOut(
            assessmentId=item.assessmentId, storeId=item.storeId, storeName=store_name,
            staffId=item.staffId, staffName=staff_name,
            reviewDate=item.reviewDate, score=item.score, rating=item.rating,
            detailItems=item.detailItems, reviewerId=item.reviewerId,
            reviewerName=reviewer_name, remark=item.remark, createdAt=item.createdAt,
        ))

    return CleanerAssessmentListOut(total=total, items=result, page=page, page_size=page_size)


@router.get("/cleaner-assessments/{assessment_id}", response_model=CleanerAssessmentOut)
async def get_cleaner_assessment(assessment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CleanerAssessment).where(CleanerAssessment.assessmentId == assessment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "保洁考核记录不存在")
    store_name = await _get_store_name(db, item.storeId)
    staff_name = None
    if item.staffId:
        sr = await db.execute(select(ExternalStaff.name).where(ExternalStaff.staffId == item.staffId))
        staff_name = sr.scalar_one_or_none()
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return CleanerAssessmentOut(
        assessmentId=item.assessmentId, storeId=item.storeId, storeName=store_name,
        staffId=item.staffId, staffName=staff_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        detailItems=item.detailItems, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, remark=item.remark, createdAt=item.createdAt,
    )


@router.post("/cleaner-assessments", response_model=CleanerAssessmentOut, status_code=201)
async def create_cleaner_assessment(
    data: CleanerAssessmentCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CleanerAssessment(
        assessmentId=_gen_id(), storeId=data.storeId, staffId=data.staffId,
        reviewDate=data.reviewDate, score=data.score, rating=data.rating,
        detailItems=data.detailItems, reviewerId=data.reviewerId, remark=data.remark,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    staff_name = None
    if item.staffId:
        sr = await db.execute(select(ExternalStaff.name).where(ExternalStaff.staffId == item.staffId))
        staff_name = sr.scalar_one_or_none()
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return CleanerAssessmentOut(
        assessmentId=item.assessmentId, storeId=item.storeId, storeName=store_name,
        staffId=item.staffId, staffName=staff_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        detailItems=item.detailItems, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, remark=item.remark, createdAt=item.createdAt,
    )


@router.put("/cleaner-assessments/{assessment_id}", response_model=CleanerAssessmentOut)
async def update_cleaner_assessment(
    assessment_id: str,
    data: CleanerAssessmentUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CleanerAssessment).where(CleanerAssessment.assessmentId == assessment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "保洁考核记录不存在")
    if data.score is not None:
        item.score = data.score
    if data.rating is not None:
        item.rating = data.rating
    if data.detailItems is not None:
        item.detailItems = data.detailItems
    if data.remark is not None:
        item.remark = data.remark
    await db.commit()
    await db.refresh(item)
    store_name = await _get_store_name(db, item.storeId)
    staff_name = None
    if item.staffId:
        sr = await db.execute(select(ExternalStaff.name).where(ExternalStaff.staffId == item.staffId))
        staff_name = sr.scalar_one_or_none()
    reviewer_name = await _get_employee_name(db, item.reviewerId)
    return CleanerAssessmentOut(
        assessmentId=item.assessmentId, storeId=item.storeId, storeName=store_name,
        staffId=item.staffId, staffName=staff_name,
        reviewDate=item.reviewDate, score=item.score, rating=item.rating,
        detailItems=item.detailItems, reviewerId=item.reviewerId,
        reviewerName=reviewer_name, remark=item.remark, createdAt=item.createdAt,
    )


@router.delete("/cleaner-assessments/{assessment_id}")
async def delete_cleaner_assessment(assessment_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CleanerAssessment).where(CleanerAssessment.assessmentId == assessment_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "保洁考核记录不存在")
    await db.delete(item)
    await db.commit()
    return {"message": "保洁考核已删除"}
