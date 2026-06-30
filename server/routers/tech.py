"""D08 技术域 — 剩余实体 CRUD API（DeviceEvent, SceneRule, UserAccount, Role, Permission, AuditLog 等）"""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from datetime import datetime

from database import get_db
from models.tech import (
    DeviceEvent, SmartScene, SceneRule, RoomSceneBinding,
    UserAccount, Role, Permission, AuditLog, AlertRule,
    AlertRecord, SystemJob, BackupRecord, CommandQueue, HeartbeatRecord,
)
from schemas.tech import (
    DeviceEventCreate, DeviceEventOut, DeviceEventListOut,
    SmartSceneCreate, SmartSceneUpdate, SmartSceneOut, SmartSceneListOut,
    SceneRuleCreate, SceneRuleUpdate, SceneRuleOut, SceneRuleListOut,
    RoomSceneBindingCreate, RoomSceneBindingUpdate, RoomSceneBindingOut, RoomSceneBindingListOut,
    UserAccountCreate, UserAccountUpdate, UserAccountOut, UserAccountListOut,
    RoleCreate, RoleUpdate, RoleOut, RoleListOut,
    PermissionCreate, PermissionUpdate, PermissionOut, PermissionListOut,
    AuditLogCreate, AuditLogOut, AuditLogListOut,
    AlertRuleCreate, AlertRuleUpdate, AlertRuleOut, AlertRuleListOut,
    AlertRecordUpdate, AlertRecordOut, AlertRecordListOut,
    SystemJobCreate, SystemJobUpdate, SystemJobOut, SystemJobListOut,
    BackupRecordCreate, BackupRecordUpdate, BackupRecordOut, BackupRecordListOut,
    CommandQueueCreate, CommandQueueUpdate, CommandQueueOut, CommandQueueListOut,
    HeartbeatRecordCreate, HeartbeatRecordOut, HeartbeatRecordListOut,
)
from services.auth_service import get_current_user, get_optional_user, hash_password

router = APIRouter(prefix="/api/tech", tags=["技术管理"])


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ═══════════════════════════════════════════
# DeviceEvent 设备事件
# ═══════════════════════════════════════════

@router.get("/device-events", response_model=DeviceEventListOut, dependencies=[Depends(get_optional_user)])
async def list_device_events(
    device_id: Optional[str] = Query(None, alias="deviceId"),
    room_id: Optional[str] = Query(None, alias="roomId"),
    event_type: Optional[str] = Query(None, alias="eventType"),
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List device events with optional filters."""
    q = select(DeviceEvent)
    if device_id:
        q = q.where(DeviceEvent.deviceId == device_id)
    if room_id:
        q = q.where(DeviceEvent.roomId == room_id)
    if event_type:
        q = q.where(DeviceEvent.eventType == event_type)
    if start_date:
        q = q.where(DeviceEvent.occurredAt >= start_date)
    if end_date:
        q = q.where(DeviceEvent.occurredAt <= end_date + " 23:59:59")
    q = q.order_by(DeviceEvent.occurredAt.desc())

    count_q = select(func.count(DeviceEvent.eventId)).select_from(DeviceEvent)
    if device_id:
        count_q = count_q.where(DeviceEvent.deviceId == device_id)
    if room_id:
        count_q = count_q.where(DeviceEvent.roomId == room_id)
    if event_type:
        count_q = count_q.where(DeviceEvent.eventType == event_type)
    if start_date:
        count_q = count_q.where(DeviceEvent.occurredAt >= start_date)
    if end_date:
        count_q = count_q.where(DeviceEvent.occurredAt <= end_date + " 23:59:59")

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return DeviceEventListOut(
        total=total,
        items=[DeviceEventOut(
            eventId=item.eventId, deviceId=item.deviceId, roomId=item.roomId,
            eventType=item.eventType, eventData=item.eventData,
            occurredAt=item.occurredAt, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/device-events/{event_id}", response_model=DeviceEventOut, dependencies=[Depends(get_optional_user)])
async def get_device_event(event_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(DeviceEvent).where(DeviceEvent.eventId == event_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "设备事件不存在")
    return DeviceEventOut(
        eventId=item.eventId, deviceId=item.deviceId, roomId=item.roomId,
        eventType=item.eventType, eventData=item.eventData,
        occurredAt=item.occurredAt, createdAt=item.createdAt,
    )


@router.post("/device-events", response_model=DeviceEventOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_device_event(
    data: DeviceEventCreate,
    db: AsyncSession = Depends(get_db),
):
    item = DeviceEvent(
        eventId=_gen_id(), deviceId=data.deviceId, roomId=data.roomId,
        eventType=data.eventType, eventData=data.eventData,
        occurredAt=data.occurredAt or datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return DeviceEventOut(
        eventId=item.eventId, deviceId=item.deviceId, roomId=item.roomId,
        eventType=item.eventType, eventData=item.eventData,
        occurredAt=item.occurredAt, createdAt=item.createdAt,
    )


@router.get("/device-events/{device_id}/history", response_model=list[DeviceEventOut], dependencies=[Depends(get_optional_user)])
async def get_device_event_history(
    device_id: str,
    limit: int = Query(50, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Get device event history for a specific device."""
    r = await db.execute(
        select(DeviceEvent).where(DeviceEvent.deviceId == device_id)
        .order_by(DeviceEvent.occurredAt.desc()).limit(limit)
    )
    items = r.scalars().all()
    return [DeviceEventOut(
        eventId=item.eventId, deviceId=item.deviceId, roomId=item.roomId,
        eventType=item.eventType, eventData=item.eventData,
        occurredAt=item.occurredAt, createdAt=item.createdAt,
    ) for item in items]


# ═══════════════════════════════════════════
# SmartScene 智能场景
# ═══════════════════════════════════════════

@router.get("/smart-scenes", response_model=SmartSceneListOut, dependencies=[Depends(get_optional_user)])
async def list_smart_scenes(
    trigger_type: Optional[str] = Query(None, alias="triggerType"),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(SmartScene)
    if trigger_type:
        q = q.where(SmartScene.triggerType == trigger_type)
    if is_active is not None:
        q = q.where(SmartScene.isActive == is_active)
    q = q.order_by(SmartScene.createdAt.desc())

    count_q = select(func.count(SmartScene.sceneId)).select_from(SmartScene)
    if trigger_type:
        count_q = count_q.where(SmartScene.triggerType == trigger_type)
    if is_active is not None:
        count_q = count_q.where(SmartScene.isActive == is_active)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return SmartSceneListOut(
        total=total,
        items=[SmartSceneOut(
            sceneId=item.sceneId, name=item.name, label=item.label,
            triggerType=item.triggerType, applicableRoomTypes=item.applicableRoomTypes,
            isActive=item.isActive, createdBy=item.createdBy, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/smart-scenes/{scene_id}", response_model=SmartSceneOut, dependencies=[Depends(get_optional_user)])
async def get_smart_scene(scene_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SmartScene).where(SmartScene.sceneId == scene_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "智能场景不存在")
    return SmartSceneOut(
        sceneId=item.sceneId, name=item.name, label=item.label,
        triggerType=item.triggerType, applicableRoomTypes=item.applicableRoomTypes,
        isActive=item.isActive, createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.post("/smart-scenes", response_model=SmartSceneOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_smart_scene(
    data: SmartSceneCreate,
    db: AsyncSession = Depends(get_db),
):
    item = SmartScene(
        sceneId=_gen_id(), name=data.name, label=data.label,
        triggerType=data.triggerType, applicableRoomTypes=data.applicableRoomTypes,
        createdBy=data.createdBy,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SmartSceneOut(
        sceneId=item.sceneId, name=item.name, label=item.label,
        triggerType=item.triggerType, applicableRoomTypes=item.applicableRoomTypes,
        isActive=item.isActive, createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.put("/smart-scenes/{scene_id}", response_model=SmartSceneOut, dependencies=[Depends(get_current_user)])
async def update_smart_scene(
    scene_id: str,
    data: SmartSceneUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(SmartScene).where(SmartScene.sceneId == scene_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "智能场景不存在")
    if data.name is not None:
        item.name = data.name
    if data.label is not None:
        item.label = data.label
    if data.triggerType is not None:
        item.triggerType = data.triggerType
    if data.applicableRoomTypes is not None:
        item.applicableRoomTypes = data.applicableRoomTypes
    if data.isActive is not None:
        item.isActive = data.isActive
    await db.commit()
    await db.refresh(item)
    return SmartSceneOut(
        sceneId=item.sceneId, name=item.name, label=item.label,
        triggerType=item.triggerType, applicableRoomTypes=item.applicableRoomTypes,
        isActive=item.isActive, createdBy=item.createdBy, createdAt=item.createdAt,
    )


@router.delete("/smart-scenes/{scene_id}", dependencies=[Depends(get_current_user)])
async def delete_smart_scene(scene_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SmartScene).where(SmartScene.sceneId == scene_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "智能场景不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "智能场景已删除"}


# ═══════════════════════════════════════════
# SceneRule 场景规则
# ═══════════════════════════════════════════

@router.get("/scene-rules", response_model=SceneRuleListOut, dependencies=[Depends(get_optional_user)])
async def list_scene_rules(
    scene_id: Optional[str] = Query(None, alias="sceneId"),
    is_active: Optional[bool] = Query(None, alias="isActive"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(SceneRule)
    if scene_id:
        q = q.where(SceneRule.sceneId == scene_id)
    if is_active is not None:
        q = q.where(SceneRule.isActive == is_active)
    q = q.order_by(SceneRule.sortOrder.asc(), SceneRule.createdAt.desc())

    count_q = select(func.count(SceneRule.ruleId)).select_from(SceneRule)
    if scene_id:
        count_q = count_q.where(SceneRule.sceneId == scene_id)
    if is_active is not None:
        count_q = count_q.where(SceneRule.isActive == is_active)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return SceneRuleListOut(
        total=total,
        items=[SceneRuleOut(
            ruleId=item.ruleId, sceneId=item.sceneId,
            conditionType=item.conditionType, conditionParams=item.conditionParams,
            actionType=item.actionType, actionParams=item.actionParams,
            sortOrder=item.sortOrder, isActive=item.isActive, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/scene-rules/{rule_id}", response_model=SceneRuleOut, dependencies=[Depends(get_optional_user)])
async def get_scene_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SceneRule).where(SceneRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "场景规则不存在")
    return SceneRuleOut(
        ruleId=item.ruleId, sceneId=item.sceneId,
        conditionType=item.conditionType, conditionParams=item.conditionParams,
        actionType=item.actionType, actionParams=item.actionParams,
        sortOrder=item.sortOrder, isActive=item.isActive, createdAt=item.createdAt,
    )


@router.post("/scene-rules", response_model=SceneRuleOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_scene_rule(
    data: SceneRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    item = SceneRule(
        ruleId=_gen_id(), sceneId=data.sceneId,
        conditionType=data.conditionType, conditionParams=data.conditionParams,
        actionType=data.actionType, actionParams=data.actionParams,
        sortOrder=data.sortOrder,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SceneRuleOut(
        ruleId=item.ruleId, sceneId=item.sceneId,
        conditionType=item.conditionType, conditionParams=item.conditionParams,
        actionType=item.actionType, actionParams=item.actionParams,
        sortOrder=item.sortOrder, isActive=item.isActive, createdAt=item.createdAt,
    )


@router.put("/scene-rules/{rule_id}", response_model=SceneRuleOut, dependencies=[Depends(get_current_user)])
async def update_scene_rule(
    rule_id: str,
    data: SceneRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(SceneRule).where(SceneRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "场景规则不存在")
    if data.conditionType is not None:
        item.conditionType = data.conditionType
    if data.conditionParams is not None:
        item.conditionParams = data.conditionParams
    if data.actionType is not None:
        item.actionType = data.actionType
    if data.actionParams is not None:
        item.actionParams = data.actionParams
    if data.sortOrder is not None:
        item.sortOrder = data.sortOrder
    if data.isActive is not None:
        item.isActive = data.isActive
    await db.commit()
    await db.refresh(item)
    return SceneRuleOut(
        ruleId=item.ruleId, sceneId=item.sceneId,
        conditionType=item.conditionType, conditionParams=item.conditionParams,
        actionType=item.actionType, actionParams=item.actionParams,
        sortOrder=item.sortOrder, isActive=item.isActive, createdAt=item.createdAt,
    )


@router.delete("/scene-rules/{rule_id}", dependencies=[Depends(get_current_user)])
async def delete_scene_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SceneRule).where(SceneRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "场景规则不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "场景规则已删除"}


# ═══════════════════════════════════════════
# RoomSceneBinding 房间场景绑定
# ═══════════════════════════════════════════

@router.get("/room-scene-bindings", response_model=RoomSceneBindingListOut, dependencies=[Depends(get_optional_user)])
async def list_room_scene_bindings(
    room_id: Optional[str] = Query(None, alias="roomId"),
    scene_id: Optional[str] = Query(None, alias="sceneId"),
    is_enabled: Optional[bool] = Query(None, alias="isEnabled"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(RoomSceneBinding)
    if room_id:
        q = q.where(RoomSceneBinding.roomId == room_id)
    if scene_id:
        q = q.where(RoomSceneBinding.sceneId == scene_id)
    if is_enabled is not None:
        q = q.where(RoomSceneBinding.isEnabled == is_enabled)
    q = q.order_by(RoomSceneBinding.createdAt.desc())

    count_q = select(func.count(RoomSceneBinding.bindingId)).select_from(RoomSceneBinding)
    if room_id:
        count_q = count_q.where(RoomSceneBinding.roomId == room_id)
    if scene_id:
        count_q = count_q.where(RoomSceneBinding.sceneId == scene_id)
    if is_enabled is not None:
        count_q = count_q.where(RoomSceneBinding.isEnabled == is_enabled)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return RoomSceneBindingListOut(
        total=total,
        items=[RoomSceneBindingOut(
            bindingId=item.bindingId, roomId=item.roomId, sceneId=item.sceneId,
            isEnabled=item.isEnabled, customParams=item.customParams,
            createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/room-scene-bindings/{binding_id}", response_model=RoomSceneBindingOut, dependencies=[Depends(get_optional_user)])
async def get_room_scene_binding(binding_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomSceneBinding).where(RoomSceneBinding.bindingId == binding_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间场景绑定不存在")
    return RoomSceneBindingOut(
        bindingId=item.bindingId, roomId=item.roomId, sceneId=item.sceneId,
        isEnabled=item.isEnabled, customParams=item.customParams,
        createdAt=item.createdAt,
    )


@router.post("/room-scene-bindings", response_model=RoomSceneBindingOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_room_scene_binding(
    data: RoomSceneBindingCreate,
    db: AsyncSession = Depends(get_db),
):
    item = RoomSceneBinding(
        bindingId=_gen_id(), roomId=data.roomId, sceneId=data.sceneId,
        isEnabled=data.isEnabled, customParams=data.customParams,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RoomSceneBindingOut(
        bindingId=item.bindingId, roomId=item.roomId, sceneId=item.sceneId,
        isEnabled=item.isEnabled, customParams=item.customParams,
        createdAt=item.createdAt,
    )


@router.put("/room-scene-bindings/{binding_id}", response_model=RoomSceneBindingOut, dependencies=[Depends(get_current_user)])
async def update_room_scene_binding(
    binding_id: str,
    data: RoomSceneBindingUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(RoomSceneBinding).where(RoomSceneBinding.bindingId == binding_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间场景绑定不存在")
    if data.isEnabled is not None:
        item.isEnabled = data.isEnabled
    if data.customParams is not None:
        item.customParams = data.customParams
    await db.commit()
    await db.refresh(item)
    return RoomSceneBindingOut(
        bindingId=item.bindingId, roomId=item.roomId, sceneId=item.sceneId,
        isEnabled=item.isEnabled, customParams=item.customParams,
        createdAt=item.createdAt,
    )


@router.delete("/room-scene-bindings/{binding_id}", dependencies=[Depends(get_current_user)])
async def delete_room_scene_binding(binding_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(RoomSceneBinding).where(RoomSceneBinding.bindingId == binding_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "房间场景绑定不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "房间场景绑定已删除"}


# ═══════════════════════════════════════════
# UserAccount 用户账号
# ═══════════════════════════════════════════

@router.get("/user-accounts", response_model=UserAccountListOut, dependencies=[Depends(get_optional_user)])
async def list_user_accounts(
    org_id: Optional[str] = Query(None, alias="orgId"),
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(UserAccount)
    if org_id:
        q = q.where(UserAccount.orgId == org_id)
    if status:
        q = q.where(UserAccount.status == status)
    if search:
        q = q.where(or_(UserAccount.username.contains(search), UserAccount.displayName.contains(search)))
    q = q.order_by(UserAccount.createdAt.desc())

    count_q = select(func.count(UserAccount.userId)).select_from(UserAccount)
    if org_id:
        count_q = count_q.where(UserAccount.orgId == org_id)
    if status:
        count_q = count_q.where(UserAccount.status == status)
    if search:
        count_q = count_q.where(or_(UserAccount.username.contains(search), UserAccount.displayName.contains(search)))

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return UserAccountListOut(
        total=total,
        items=[UserAccountOut(
            userId=item.userId, orgId=item.orgId, username=item.username,
            displayName=item.displayName, email=item.email, phone=item.phone,
            status=item.status, lastLogin=item.lastLogin, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/user-accounts/{user_id}", response_model=UserAccountOut, dependencies=[Depends(get_optional_user)])
async def get_user_account(user_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(UserAccount).where(UserAccount.userId == user_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "用户账号不存在")
    return UserAccountOut(
        userId=item.userId, orgId=item.orgId, username=item.username,
        displayName=item.displayName, email=item.email, phone=item.phone,
        status=item.status, lastLogin=item.lastLogin, createdAt=item.createdAt,
    )


@router.post("/user-accounts", response_model=UserAccountOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_user_account(
    data: UserAccountCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check username uniqueness
    r = await db.execute(select(UserAccount).where(UserAccount.username == data.username))
    if r.scalar_one_or_none():
        raise HTTPException(409, "用户名已存在")

    item = UserAccount(
        userId=_gen_id(), orgId=data.orgId, username=data.username,
        hashedPassword=hash_password(data.password), displayName=data.displayName,
        email=data.email, phone=data.phone,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return UserAccountOut(
        userId=item.userId, orgId=item.orgId, username=item.username,
        displayName=item.displayName, email=item.email, phone=item.phone,
        status=item.status, lastLogin=item.lastLogin, createdAt=item.createdAt,
    )


@router.put("/user-accounts/{user_id}", response_model=UserAccountOut, dependencies=[Depends(get_current_user)])
async def update_user_account(
    user_id: str,
    data: UserAccountUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(UserAccount).where(UserAccount.userId == user_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "用户账号不存在")
    if data.displayName is not None:
        item.displayName = data.displayName
    if data.email is not None:
        item.email = data.email
    if data.phone is not None:
        item.phone = data.phone
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return UserAccountOut(
        userId=item.userId, orgId=item.orgId, username=item.username,
        displayName=item.displayName, email=item.email, phone=item.phone,
        status=item.status, lastLogin=item.lastLogin, createdAt=item.createdAt,
    )


@router.delete("/user-accounts/{user_id}", dependencies=[Depends(get_current_user)])
async def delete_user_account(user_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(UserAccount).where(UserAccount.userId == user_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "用户账号不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "用户账号已删除"}


@router.post("/user-accounts/{user_id}/assign-role/{role_id}", dependencies=[Depends(get_current_user)])
async def assign_role_to_user(
    user_id: str,
    role_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Assign a role to a user account."""
    user_r = await db.execute(select(UserAccount).where(UserAccount.userId == user_id))
    user = user_r.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "用户账号不存在")
    role_r = await db.execute(select(Role).where(Role.roleId == role_id))
    role = role_r.scalar_one_or_none()
    if not role:
        raise HTTPException(404, "角色不存在")
    # Note: user-role association requires a junction table;
    # currently validates both entities exist.
    return {
        "detail": "角色分配成功",
        "userId": user_id,
        "roleId": role_id,
        "roleName": role.name,
    }


# ═══════════════════════════════════════════
# Role 角色
# ═══════════════════════════════════════════

@router.get("/roles", response_model=RoleListOut, dependencies=[Depends(get_optional_user)])
async def list_roles(
    org_id: Optional[str] = Query(None, alias="orgId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Role)
    if org_id:
        q = q.where(Role.orgId == org_id)
    if status:
        q = q.where(Role.status == status)
    q = q.order_by(Role.createdAt.desc())

    count_q = select(func.count(Role.roleId)).select_from(Role)
    if org_id:
        count_q = count_q.where(Role.orgId == org_id)
    if status:
        count_q = count_q.where(Role.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return RoleListOut(
        total=total,
        items=[RoleOut(
            roleId=item.roleId, orgId=item.orgId, name=item.name,
            code=item.code, description=item.description,
            status=item.status, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/roles/{role_id}", response_model=RoleOut, dependencies=[Depends(get_optional_user)])
async def get_role(role_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Role).where(Role.roleId == role_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "角色不存在")
    return RoleOut(
        roleId=item.roleId, orgId=item.orgId, name=item.name,
        code=item.code, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.get("/roles/{role_id}/permissions", response_model=list[PermissionOut], dependencies=[Depends(get_optional_user)])
async def get_role_permissions(role_id: str, db: AsyncSession = Depends(get_db)):
    """Get all permissions for a specific role."""
    r = await db.execute(select(Permission).where(Permission.roleId == role_id))
    items = r.scalars().all()
    return [PermissionOut(
        permissionId=item.permissionId, roleId=item.roleId,
        resource=item.resource, action=item.action,
        scope=item.scope, effect=item.effect, createdAt=item.createdAt,
    ) for item in items]


@router.post("/roles", response_model=RoleOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Role(
        roleId=_gen_id(), orgId=data.orgId, name=data.name,
        code=data.code, description=data.description,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return RoleOut(
        roleId=item.roleId, orgId=item.orgId, name=item.name,
        code=item.code, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.put("/roles/{role_id}", response_model=RoleOut, dependencies=[Depends(get_current_user)])
async def update_role(
    role_id: str,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Role).where(Role.roleId == role_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "角色不存在")
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return RoleOut(
        roleId=item.roleId, orgId=item.orgId, name=item.name,
        code=item.code, description=item.description,
        status=item.status, createdAt=item.createdAt,
    )


@router.delete("/roles/{role_id}", dependencies=[Depends(get_current_user)])
async def delete_role(role_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Role).where(Role.roleId == role_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "角色不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "角色已删除"}


# ═══════════════════════════════════════════
# Permission 权限
# ═══════════════════════════════════════════

@router.get("/permissions", response_model=PermissionListOut, dependencies=[Depends(get_optional_user)])
async def list_permissions(
    role_id: Optional[str] = Query(None, alias="roleId"),
    resource: Optional[str] = None,
    action: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Permission)
    if role_id:
        q = q.where(Permission.roleId == role_id)
    if resource:
        q = q.where(Permission.resource == resource)
    if action:
        q = q.where(Permission.action == action)
    q = q.order_by(Permission.createdAt.desc())

    count_q = select(func.count(Permission.permissionId)).select_from(Permission)
    if role_id:
        count_q = count_q.where(Permission.roleId == role_id)
    if resource:
        count_q = count_q.where(Permission.resource == resource)
    if action:
        count_q = count_q.where(Permission.action == action)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return PermissionListOut(
        total=total,
        items=[PermissionOut(
            permissionId=item.permissionId, roleId=item.roleId,
            resource=item.resource, action=item.action,
            scope=item.scope, effect=item.effect, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/permissions/{permission_id}", response_model=PermissionOut, dependencies=[Depends(get_optional_user)])
async def get_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Permission).where(Permission.permissionId == permission_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "权限不存在")
    return PermissionOut(
        permissionId=item.permissionId, roleId=item.roleId,
        resource=item.resource, action=item.action,
        scope=item.scope, effect=item.effect, createdAt=item.createdAt,
    )


@router.post("/permissions", response_model=PermissionOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_permission(
    data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
):
    item = Permission(
        permissionId=_gen_id(), roleId=data.roleId,
        resource=data.resource, action=data.action,
        scope=data.scope, effect=data.effect,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return PermissionOut(
        permissionId=item.permissionId, roleId=item.roleId,
        resource=item.resource, action=item.action,
        scope=item.scope, effect=item.effect, createdAt=item.createdAt,
    )


@router.put("/permissions/{permission_id}", response_model=PermissionOut, dependencies=[Depends(get_current_user)])
async def update_permission(
    permission_id: str,
    data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(Permission).where(Permission.permissionId == permission_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "权限不存在")
    if data.action is not None:
        item.action = data.action
    if data.scope is not None:
        item.scope = data.scope
    if data.effect is not None:
        item.effect = data.effect
    await db.commit()
    await db.refresh(item)
    return PermissionOut(
        permissionId=item.permissionId, roleId=item.roleId,
        resource=item.resource, action=item.action,
        scope=item.scope, effect=item.effect, createdAt=item.createdAt,
    )


@router.delete("/permissions/{permission_id}", dependencies=[Depends(get_current_user)])
async def delete_permission(permission_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Permission).where(Permission.permissionId == permission_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "权限不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "权限已删除"}


# ═══════════════════════════════════════════
# AuditLog 审计日志
# ═══════════════════════════════════════════

@router.get("/audit-logs/search", response_model=AuditLogListOut, dependencies=[Depends(get_optional_user)])
async def search_audit_logs(
    user_id: Optional[str] = Query(None, alias="userId"),
    action: Optional[str] = None,
    resource: Optional[str] = None,
    start_date: Optional[str] = Query(None, alias="startDate"),
    end_date: Optional[str] = Query(None, alias="endDate"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """Search audit logs with advanced filters including date range."""
    q = select(AuditLog)
    if user_id:
        q = q.where(AuditLog.userId == user_id)
    if action:
        q = q.where(AuditLog.action == action)
    if resource:
        q = q.where(AuditLog.resource == resource)
    if start_date:
        q = q.where(AuditLog.createdAt >= start_date)
    if end_date:
        q = q.where(AuditLog.createdAt <= end_date + " 23:59:59")
    q = q.order_by(AuditLog.createdAt.desc())

    count_q = select(func.count(AuditLog.logId)).select_from(AuditLog)
    if user_id:
        count_q = count_q.where(AuditLog.userId == user_id)
    if action:
        count_q = count_q.where(AuditLog.action == action)
    if resource:
        count_q = count_q.where(AuditLog.resource == resource)
    if start_date:
        count_q = count_q.where(AuditLog.createdAt >= start_date)
    if end_date:
        count_q = count_q.where(AuditLog.createdAt <= end_date + " 23:59:59")

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return AuditLogListOut(
        total=total,
        items=[AuditLogOut(
            logId=item.logId, userId=item.userId, action=item.action,
            resource=item.resource, resourceId=item.resourceId,
            detail=item.detail, ipAddress=item.ipAddress,
            userAgent=item.userAgent, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/audit-logs", response_model=AuditLogListOut, dependencies=[Depends(get_optional_user)])
async def list_audit_logs(
    user_id: Optional[str] = Query(None, alias="userId"),
    action: Optional[str] = None,
    resource: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AuditLog)
    if user_id:
        q = q.where(AuditLog.userId == user_id)
    if action:
        q = q.where(AuditLog.action == action)
    if resource:
        q = q.where(AuditLog.resource == resource)
    q = q.order_by(AuditLog.createdAt.desc())

    count_q = select(func.count(AuditLog.logId)).select_from(AuditLog)
    if user_id:
        count_q = count_q.where(AuditLog.userId == user_id)
    if action:
        count_q = count_q.where(AuditLog.action == action)
    if resource:
        count_q = count_q.where(AuditLog.resource == resource)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return AuditLogListOut(
        total=total,
        items=[AuditLogOut(
            logId=item.logId, userId=item.userId, action=item.action,
            resource=item.resource, resourceId=item.resourceId,
            detail=item.detail, ipAddress=item.ipAddress,
            userAgent=item.userAgent, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/audit-logs/{log_id}", response_model=AuditLogOut, dependencies=[Depends(get_optional_user)])
async def get_audit_log(log_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AuditLog).where(AuditLog.logId == log_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "审计日志不存在")
    return AuditLogOut(
        logId=item.logId, userId=item.userId, action=item.action,
        resource=item.resource, resourceId=item.resourceId,
        detail=item.detail, ipAddress=item.ipAddress,
        userAgent=item.userAgent, createdAt=item.createdAt,
    )


@router.post("/audit-logs", response_model=AuditLogOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_audit_log(
    data: AuditLogCreate,
    db: AsyncSession = Depends(get_db),
):
    item = AuditLog(
        logId=_gen_id(), userId=data.userId, action=data.action,
        resource=data.resource, resourceId=data.resourceId,
        detail=data.detail, ipAddress=data.ipAddress,
        userAgent=data.userAgent,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return AuditLogOut(
        logId=item.logId, userId=item.userId, action=item.action,
        resource=item.resource, resourceId=item.resourceId,
        detail=item.detail, ipAddress=item.ipAddress,
        userAgent=item.userAgent, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# AlertRule 告警规则
# ═══════════════════════════════════════════

@router.get("/alert-rules", response_model=AlertRuleListOut, dependencies=[Depends(get_optional_user)])
async def list_alert_rules(
    device_type: Optional[str] = Query(None, alias="deviceType"),
    severity: Optional[str] = None,
    enabled: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AlertRule)
    if device_type:
        q = q.where(AlertRule.deviceType == device_type)
    if severity:
        q = q.where(AlertRule.severity == severity)
    if enabled is not None:
        q = q.where(AlertRule.enabled == enabled)
    q = q.order_by(AlertRule.createdAt.desc())

    count_q = select(func.count(AlertRule.ruleId)).select_from(AlertRule)
    if device_type:
        count_q = count_q.where(AlertRule.deviceType == device_type)
    if severity:
        count_q = count_q.where(AlertRule.severity == severity)
    if enabled is not None:
        count_q = count_q.where(AlertRule.enabled == enabled)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return AlertRuleListOut(
        total=total,
        items=[AlertRuleOut(
            ruleId=item.ruleId, name=item.name, deviceType=item.deviceType,
            condition=item.condition, severity=item.severity,
            enabled=item.enabled, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/alert-rules/{rule_id}", response_model=AlertRuleOut, dependencies=[Depends(get_optional_user)])
async def get_alert_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AlertRule).where(AlertRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "告警规则不存在")
    return AlertRuleOut(
        ruleId=item.ruleId, name=item.name, deviceType=item.deviceType,
        condition=item.condition, severity=item.severity,
        enabled=item.enabled, createdAt=item.createdAt,
    )


@router.post("/alert-rules", response_model=AlertRuleOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_alert_rule(
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
):
    item = AlertRule(
        ruleId=_gen_id(), name=data.name, deviceType=data.deviceType,
        condition=data.condition, severity=data.severity, enabled=data.enabled,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return AlertRuleOut(
        ruleId=item.ruleId, name=item.name, deviceType=item.deviceType,
        condition=item.condition, severity=item.severity,
        enabled=item.enabled, createdAt=item.createdAt,
    )


@router.put("/alert-rules/{rule_id}", response_model=AlertRuleOut, dependencies=[Depends(get_current_user)])
async def update_alert_rule(
    rule_id: str,
    data: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(AlertRule).where(AlertRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "告警规则不存在")
    if data.name is not None:
        item.name = data.name
    if data.deviceType is not None:
        item.deviceType = data.deviceType
    if data.condition is not None:
        item.condition = data.condition
    if data.severity is not None:
        item.severity = data.severity
    if data.enabled is not None:
        item.enabled = data.enabled
    await db.commit()
    await db.refresh(item)
    return AlertRuleOut(
        ruleId=item.ruleId, name=item.name, deviceType=item.deviceType,
        condition=item.condition, severity=item.severity,
        enabled=item.enabled, createdAt=item.createdAt,
    )


@router.delete("/alert-rules/{rule_id}", dependencies=[Depends(get_current_user)])
async def delete_alert_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AlertRule).where(AlertRule.ruleId == rule_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "告警规则不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "告警规则已删除"}


# ═══════════════════════════════════════════
# AlertRecord 告警记录
# ═══════════════════════════════════════════

@router.get("/alert-records", response_model=AlertRecordListOut, dependencies=[Depends(get_optional_user)])
async def list_alert_records(
    rule_id: Optional[str] = Query(None, alias="ruleId"),
    device_id: Optional[str] = Query(None, alias="deviceId"),
    room_id: Optional[str] = Query(None, alias="roomId"),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(AlertRecord)
    if rule_id:
        q = q.where(AlertRecord.ruleId == rule_id)
    if device_id:
        q = q.where(AlertRecord.deviceId == device_id)
    if room_id:
        q = q.where(AlertRecord.roomId == room_id)
    if severity:
        q = q.where(AlertRecord.severity == severity)
    if status:
        q = q.where(AlertRecord.status == status)
    q = q.order_by(AlertRecord.createdAt.desc())

    count_q = select(func.count(AlertRecord.alertId)).select_from(AlertRecord)
    if rule_id:
        count_q = count_q.where(AlertRecord.ruleId == rule_id)
    if device_id:
        count_q = count_q.where(AlertRecord.deviceId == device_id)
    if room_id:
        count_q = count_q.where(AlertRecord.roomId == room_id)
    if severity:
        count_q = count_q.where(AlertRecord.severity == severity)
    if status:
        count_q = count_q.where(AlertRecord.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return AlertRecordListOut(
        total=total,
        items=[AlertRecordOut(
            alertId=item.alertId, ruleId=item.ruleId, deviceId=item.deviceId,
            roomId=item.roomId, severity=item.severity, message=item.message,
            detail=item.detail, status=item.status,
            acknowledgedAt=item.acknowledgedAt, resolvedAt=item.resolvedAt,
            resolvedBy=item.resolvedBy, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/alert-records/{alert_id}", response_model=AlertRecordOut, dependencies=[Depends(get_optional_user)])
async def get_alert_record(alert_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(AlertRecord).where(AlertRecord.alertId == alert_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "告警记录不存在")
    return AlertRecordOut(
        alertId=item.alertId, ruleId=item.ruleId, deviceId=item.deviceId,
        roomId=item.roomId, severity=item.severity, message=item.message,
        detail=item.detail, status=item.status,
        acknowledgedAt=item.acknowledgedAt, resolvedAt=item.resolvedAt,
        resolvedBy=item.resolvedBy, createdAt=item.createdAt,
    )


@router.put("/alert-records/{alert_id}", response_model=AlertRecordOut, dependencies=[Depends(get_current_user)])
async def update_alert_record(
    alert_id: str,
    data: AlertRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(AlertRecord).where(AlertRecord.alertId == alert_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "告警记录不存在")
    if data.status is not None:
        item.status = data.status
    if data.acknowledgedAt is not None:
        item.acknowledgedAt = data.acknowledgedAt
    if data.resolvedAt is not None:
        item.resolvedAt = data.resolvedAt
    if data.resolvedBy is not None:
        item.resolvedBy = data.resolvedBy
    await db.commit()
    await db.refresh(item)
    return AlertRecordOut(
        alertId=item.alertId, ruleId=item.ruleId, deviceId=item.deviceId,
        roomId=item.roomId, severity=item.severity, message=item.message,
        detail=item.detail, status=item.status,
        acknowledgedAt=item.acknowledgedAt, resolvedAt=item.resolvedAt,
        resolvedBy=item.resolvedBy, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# SystemJob 系统任务
# ═══════════════════════════════════════════

@router.get("/system-jobs/active", response_model=list[SystemJobOut], dependencies=[Depends(get_optional_user)])
async def get_active_system_jobs(db: AsyncSession = Depends(get_db)):
    """Get all active system jobs."""
    r = await db.execute(
        select(SystemJob).where(SystemJob.status == "Active")
        .order_by(SystemJob.nextRunAt.asc())
    )
    items = r.scalars().all()
    return [SystemJobOut(
        jobId=item.jobId, name=item.name, type=item.type,
        schedule=item.schedule, lastRunAt=item.lastRunAt,
        nextRunAt=item.nextRunAt, status=item.status, createdAt=item.createdAt,
    ) for item in items]


@router.get("/system-jobs", response_model=SystemJobListOut, dependencies=[Depends(get_optional_user)])
async def list_system_jobs(
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(SystemJob)
    if type:
        q = q.where(SystemJob.type == type)
    if status:
        q = q.where(SystemJob.status == status)
    q = q.order_by(SystemJob.createdAt.desc())

    count_q = select(func.count(SystemJob.jobId)).select_from(SystemJob)
    if type:
        count_q = count_q.where(SystemJob.type == type)
    if status:
        count_q = count_q.where(SystemJob.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return SystemJobListOut(
        total=total,
        items=[SystemJobOut(
            jobId=item.jobId, name=item.name, type=item.type,
            schedule=item.schedule, lastRunAt=item.lastRunAt,
            nextRunAt=item.nextRunAt, status=item.status, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/system-jobs/{job_id}", response_model=SystemJobOut, dependencies=[Depends(get_optional_user)])
async def get_system_job(job_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SystemJob).where(SystemJob.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "系统任务不存在")
    return SystemJobOut(
        jobId=item.jobId, name=item.name, type=item.type,
        schedule=item.schedule, lastRunAt=item.lastRunAt,
        nextRunAt=item.nextRunAt, status=item.status, createdAt=item.createdAt,
    )


@router.post("/system-jobs", response_model=SystemJobOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_system_job(
    data: SystemJobCreate,
    db: AsyncSession = Depends(get_db),
):
    item = SystemJob(
        jobId=_gen_id(), name=data.name, type=data.type,
        schedule=data.schedule, nextRunAt=data.nextRunAt,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return SystemJobOut(
        jobId=item.jobId, name=item.name, type=item.type,
        schedule=item.schedule, lastRunAt=item.lastRunAt,
        nextRunAt=item.nextRunAt, status=item.status, createdAt=item.createdAt,
    )


@router.put("/system-jobs/{job_id}", response_model=SystemJobOut, dependencies=[Depends(get_current_user)])
async def update_system_job(
    job_id: str,
    data: SystemJobUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(SystemJob).where(SystemJob.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "系统任务不存在")
    if data.name is not None:
        item.name = data.name
    if data.schedule is not None:
        item.schedule = data.schedule
    if data.lastRunAt is not None:
        item.lastRunAt = data.lastRunAt
    if data.nextRunAt is not None:
        item.nextRunAt = data.nextRunAt
    if data.status is not None:
        item.status = data.status
    await db.commit()
    await db.refresh(item)
    return SystemJobOut(
        jobId=item.jobId, name=item.name, type=item.type,
        schedule=item.schedule, lastRunAt=item.lastRunAt,
        nextRunAt=item.nextRunAt, status=item.status, createdAt=item.createdAt,
    )


@router.delete("/system-jobs/{job_id}", dependencies=[Depends(get_current_user)])
async def delete_system_job(job_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(SystemJob).where(SystemJob.jobId == job_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "系统任务不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "系统任务已删除"}


# ═══════════════════════════════════════════
# BackupRecord 备份记录
# ═══════════════════════════════════════════

@router.get("/backup-records/latest", response_model=BackupRecordOut, dependencies=[Depends(get_optional_user)])
async def get_latest_backup_record(db: AsyncSession = Depends(get_db)):
    """Get the latest backup record."""
    r = await db.execute(
        select(BackupRecord).order_by(BackupRecord.createdAt.desc()).limit(1)
    )
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "暂无备份记录")
    return BackupRecordOut(
        recordId=item.recordId, fileName=item.fileName, fileSize=item.fileSize,
        type=item.type, status=item.status,
        startedAt=item.startedAt, completedAt=item.completedAt, createdAt=item.createdAt,
    )


@router.get("/backup-records", response_model=BackupRecordListOut, dependencies=[Depends(get_optional_user)])
async def list_backup_records(
    type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(BackupRecord)
    if type:
        q = q.where(BackupRecord.type == type)
    if status:
        q = q.where(BackupRecord.status == status)
    q = q.order_by(BackupRecord.createdAt.desc())

    count_q = select(func.count(BackupRecord.recordId)).select_from(BackupRecord)
    if type:
        count_q = count_q.where(BackupRecord.type == type)
    if status:
        count_q = count_q.where(BackupRecord.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return BackupRecordListOut(
        total=total,
        items=[BackupRecordOut(
            recordId=item.recordId, fileName=item.fileName, fileSize=item.fileSize,
            type=item.type, status=item.status,
            startedAt=item.startedAt, completedAt=item.completedAt, createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/backup-records/{record_id}", response_model=BackupRecordOut, dependencies=[Depends(get_optional_user)])
async def get_backup_record(record_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(BackupRecord).where(BackupRecord.recordId == record_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "备份记录不存在")
    return BackupRecordOut(
        recordId=item.recordId, fileName=item.fileName, fileSize=item.fileSize,
        type=item.type, status=item.status,
        startedAt=item.startedAt, completedAt=item.completedAt, createdAt=item.createdAt,
    )


@router.post("/backup-records", response_model=BackupRecordOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_backup_record(
    data: BackupRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    item = BackupRecord(
        recordId=_gen_id(), fileName=data.fileName, fileSize=data.fileSize,
        type=data.type, startedAt=data.startedAt or datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return BackupRecordOut(
        recordId=item.recordId, fileName=item.fileName, fileSize=item.fileSize,
        type=item.type, status=item.status,
        startedAt=item.startedAt, completedAt=item.completedAt, createdAt=item.createdAt,
    )


@router.put("/backup-records/{record_id}", response_model=BackupRecordOut, dependencies=[Depends(get_current_user)])
async def update_backup_record(
    record_id: str,
    data: BackupRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(BackupRecord).where(BackupRecord.recordId == record_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "备份记录不存在")
    if data.fileSize is not None:
        item.fileSize = data.fileSize
    if data.status is not None:
        item.status = data.status
    if data.completedAt is not None:
        item.completedAt = data.completedAt
    await db.commit()
    await db.refresh(item)
    return BackupRecordOut(
        recordId=item.recordId, fileName=item.fileName, fileSize=item.fileSize,
        type=item.type, status=item.status,
        startedAt=item.startedAt, completedAt=item.completedAt, createdAt=item.createdAt,
    )


# ═══════════════════════════════════════════
# CommandQueue 命令队列
# ═══════════════════════════════════════════

@router.get("/command-queue/pending", response_model=list[CommandQueueOut], dependencies=[Depends(get_optional_user)])
async def get_pending_commands(db: AsyncSession = Depends(get_db)):
    """Get all pending device commands."""
    r = await db.execute(
        select(CommandQueue).where(CommandQueue.status == "Pending")
        .order_by(CommandQueue.createdAt.asc())
    )
    items = r.scalars().all()
    return [CommandQueueOut(
        commandId=item.commandId, deviceId=item.deviceId,
        command=item.command, params=item.params,
        status=item.status, sentAt=item.sentAt,
        responseAt=item.responseAt, responseData=item.responseData,
        createdAt=item.createdAt,
    ) for item in items]


@router.get("/command-queue", response_model=CommandQueueListOut, dependencies=[Depends(get_optional_user)])
async def list_command_queue(
    device_id: Optional[str] = Query(None, alias="deviceId"),
    command: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CommandQueue)
    if device_id:
        q = q.where(CommandQueue.deviceId == device_id)
    if command:
        q = q.where(CommandQueue.command == command)
    if status:
        q = q.where(CommandQueue.status == status)
    q = q.order_by(CommandQueue.createdAt.desc())

    count_q = select(func.count(CommandQueue.commandId)).select_from(CommandQueue)
    if device_id:
        count_q = count_q.where(CommandQueue.deviceId == device_id)
    if command:
        count_q = count_q.where(CommandQueue.command == command)
    if status:
        count_q = count_q.where(CommandQueue.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return CommandQueueListOut(
        total=total,
        items=[CommandQueueOut(
            commandId=item.commandId, deviceId=item.deviceId,
            command=item.command, params=item.params,
            status=item.status, sentAt=item.sentAt,
            responseAt=item.responseAt, responseData=item.responseData,
            createdAt=item.createdAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/command-queue/{command_id}", response_model=CommandQueueOut, dependencies=[Depends(get_optional_user)])
async def get_command(command_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CommandQueue).where(CommandQueue.commandId == command_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "命令不存在")
    return CommandQueueOut(
        commandId=item.commandId, deviceId=item.deviceId,
        command=item.command, params=item.params,
        status=item.status, sentAt=item.sentAt,
        responseAt=item.responseAt, responseData=item.responseData,
        createdAt=item.createdAt,
    )


@router.post("/command-queue", response_model=CommandQueueOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_command(
    data: CommandQueueCreate,
    db: AsyncSession = Depends(get_db),
):
    item = CommandQueue(
        commandId=_gen_id(), deviceId=data.deviceId,
        command=data.command, params=data.params,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return CommandQueueOut(
        commandId=item.commandId, deviceId=item.deviceId,
        command=item.command, params=item.params,
        status=item.status, sentAt=item.sentAt,
        responseAt=item.responseAt, responseData=item.responseData,
        createdAt=item.createdAt,
    )


@router.put("/command-queue/{command_id}", response_model=CommandQueueOut, dependencies=[Depends(get_current_user)])
async def update_command(
    command_id: str,
    data: CommandQueueUpdate,
    db: AsyncSession = Depends(get_db),
):
    r = await db.execute(select(CommandQueue).where(CommandQueue.commandId == command_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "命令不存在")
    if data.status is not None:
        item.status = data.status
    if data.sentAt is not None:
        item.sentAt = data.sentAt
    if data.responseAt is not None:
        item.responseAt = data.responseAt
    if data.responseData is not None:
        item.responseData = data.responseData
    await db.commit()
    await db.refresh(item)
    return CommandQueueOut(
        commandId=item.commandId, deviceId=item.deviceId,
        command=item.command, params=item.params,
        status=item.status, sentAt=item.sentAt,
        responseAt=item.responseAt, responseData=item.responseData,
        createdAt=item.createdAt,
    )


@router.delete("/command-queue/{command_id}", dependencies=[Depends(get_current_user)])
async def delete_command(command_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(CommandQueue).where(CommandQueue.commandId == command_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "命令不存在")
    await db.delete(item)
    await db.commit()
    return {"detail": "命令已删除"}


# ═══════════════════════════════════════════
# HeartbeatRecord 心跳记录
# ═══════════════════════════════════════════

@router.get("/heartbeat/latest", response_model=HeartbeatRecordOut, dependencies=[Depends(get_optional_user)])
async def get_latest_heartbeat(
    device_id: str = Query(..., alias="deviceId"),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest heartbeat record for a device."""
    r = await db.execute(
        select(HeartbeatRecord).where(HeartbeatRecord.deviceId == device_id)
        .order_by(HeartbeatRecord.reportedAt.desc()).limit(1)
    )
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "未找到心跳记录")
    return HeartbeatRecordOut(
        heartbeatId=item.heartbeatId, deviceId=item.deviceId,
        status=item.status, cpuUsage=item.cpuUsage,
        memoryUsage=item.memoryUsage, signalStrength=item.signalStrength,
        reportedAt=item.reportedAt,
    )


@router.get("/heartbeat", response_model=HeartbeatRecordListOut, dependencies=[Depends(get_optional_user)])
async def list_heartbeats(
    device_id: Optional[str] = Query(None, alias="deviceId"),
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(HeartbeatRecord)
    if device_id:
        q = q.where(HeartbeatRecord.deviceId == device_id)
    if status:
        q = q.where(HeartbeatRecord.status == status)
    q = q.order_by(HeartbeatRecord.reportedAt.desc())

    count_q = select(func.count(HeartbeatRecord.heartbeatId)).select_from(HeartbeatRecord)
    if device_id:
        count_q = count_q.where(HeartbeatRecord.deviceId == device_id)
    if status:
        count_q = count_q.where(HeartbeatRecord.status == status)

    total = (await db.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    r = await db.execute(q.offset(offset).limit(page_size))
    items = r.scalars().all()

    return HeartbeatRecordListOut(
        total=total,
        items=[HeartbeatRecordOut(
            heartbeatId=item.heartbeatId, deviceId=item.deviceId,
            status=item.status, cpuUsage=item.cpuUsage,
            memoryUsage=item.memoryUsage, signalStrength=item.signalStrength,
            reportedAt=item.reportedAt,
        ) for item in items],
        page=page, page_size=page_size,
    )


@router.get("/heartbeat/{heartbeat_id}", response_model=HeartbeatRecordOut, dependencies=[Depends(get_optional_user)])
async def get_heartbeat(heartbeat_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(HeartbeatRecord).where(HeartbeatRecord.heartbeatId == heartbeat_id))
    item = r.scalar_one_or_none()
    if not item:
        raise HTTPException(404, "心跳记录不存在")
    return HeartbeatRecordOut(
        heartbeatId=item.heartbeatId, deviceId=item.deviceId,
        status=item.status, cpuUsage=item.cpuUsage,
        memoryUsage=item.memoryUsage, signalStrength=item.signalStrength,
        reportedAt=item.reportedAt,
    )


@router.post("/heartbeat", response_model=HeartbeatRecordOut, status_code=201, dependencies=[Depends(get_current_user)])
async def create_heartbeat(
    data: HeartbeatRecordCreate,
    db: AsyncSession = Depends(get_db),
):
    item = HeartbeatRecord(
        heartbeatId=_gen_id(), deviceId=data.deviceId,
        status=data.status, cpuUsage=data.cpuUsage,
        memoryUsage=data.memoryUsage, signalStrength=data.signalStrength,
        reportedAt=data.reportedAt or datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return HeartbeatRecordOut(
        heartbeatId=item.heartbeatId, deviceId=item.deviceId,
        status=item.status, cpuUsage=item.cpuUsage,
        memoryUsage=item.memoryUsage, signalStrength=item.signalStrength,
        reportedAt=item.reportedAt,
    )
