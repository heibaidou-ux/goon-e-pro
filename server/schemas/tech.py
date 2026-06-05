"""D08 技术域 — Pydantic schemas for remaining entities"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ── DeviceEvent ──

class DeviceEventCreate(BaseModel):
    deviceId: str
    roomId: str
    eventType: str  # Online/Offline/Command/Action/Alert
    eventData: Optional[str] = None  # JSON
    occurredAt: Optional[datetime] = None


class DeviceEventOut(BaseModel):
    eventId: str
    deviceId: str
    roomId: str
    eventType: str
    eventData: Optional[str] = None
    occurredAt: datetime
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceEventListOut(BaseModel):
    total: int
    items: List[DeviceEventOut]
    page: int = 1
    page_size: int = 20


# ── SmartScene ──

class SmartSceneCreate(BaseModel):
    name: str
    label: Optional[str] = None
    triggerType: str = "Manual"
    applicableRoomTypes: Optional[str] = None  # JSON array
    createdBy: str


class SmartSceneUpdate(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    triggerType: Optional[str] = None
    applicableRoomTypes: Optional[str] = None
    isActive: Optional[bool] = None


class SmartSceneOut(BaseModel):
    sceneId: str
    name: str
    label: Optional[str] = None
    triggerType: str = "Manual"
    applicableRoomTypes: Optional[str] = None
    isActive: bool = True
    createdBy: str
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SmartSceneListOut(BaseModel):
    total: int
    items: List[SmartSceneOut]
    page: int = 1
    page_size: int = 20


# ── SceneRule ──

class SceneRuleCreate(BaseModel):
    sceneId: str
    conditionType: str  # DeviceState/Time/Schedule
    conditionParams: Optional[str] = None  # JSON
    actionType: str
    actionParams: Optional[str] = None  # JSON
    sortOrder: int = 0


class SceneRuleUpdate(BaseModel):
    conditionType: Optional[str] = None
    conditionParams: Optional[str] = None
    actionType: Optional[str] = None
    actionParams: Optional[str] = None
    sortOrder: Optional[int] = None
    isActive: Optional[bool] = None


class SceneRuleOut(BaseModel):
    ruleId: str
    sceneId: str
    conditionType: str
    conditionParams: Optional[str] = None
    actionType: str
    actionParams: Optional[str] = None
    sortOrder: int = 0
    isActive: bool = True
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SceneRuleListOut(BaseModel):
    total: int
    items: List[SceneRuleOut]
    page: int = 1
    page_size: int = 20


# ── RoomSceneBinding ──

class RoomSceneBindingCreate(BaseModel):
    roomId: str
    sceneId: str
    isEnabled: bool = True
    customParams: Optional[str] = None  # JSON


class RoomSceneBindingUpdate(BaseModel):
    isEnabled: Optional[bool] = None
    customParams: Optional[str] = None


class RoomSceneBindingOut(BaseModel):
    bindingId: str
    roomId: str
    sceneId: str
    isEnabled: bool = True
    customParams: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoomSceneBindingListOut(BaseModel):
    total: int
    items: List[RoomSceneBindingOut]
    page: int = 1
    page_size: int = 20


# ── UserAccount ──

class UserAccountCreate(BaseModel):
    orgId: Optional[str] = None
    username: str
    password: str  # plain text, will be hashed
    displayName: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UserAccountUpdate(BaseModel):
    displayName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class UserAccountOut(BaseModel):
    userId: str
    orgId: Optional[str] = None
    username: str
    displayName: str
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str = "Active"
    lastLogin: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserAccountListOut(BaseModel):
    total: int
    items: List[UserAccountOut]
    page: int = 1
    page_size: int = 20


# ── Role ──

class RoleCreate(BaseModel):
    orgId: Optional[str] = None
    name: str
    code: str
    description: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class RoleOut(BaseModel):
    roleId: str
    orgId: Optional[str] = None
    name: str
    code: str
    description: Optional[str] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleListOut(BaseModel):
    total: int
    items: List[RoleOut]
    page: int = 1
    page_size: int = 20


# ── Permission ──

class PermissionCreate(BaseModel):
    roleId: str
    resource: str
    action: str  # Read/Write/Delete/Approve
    scope: str = "Self"  # All/Org/Store/Self
    effect: str = "Allow"  # Allow/Deny


class PermissionUpdate(BaseModel):
    action: Optional[str] = None
    scope: Optional[str] = None
    effect: Optional[str] = None


class PermissionOut(BaseModel):
    permissionId: str
    roleId: str
    resource: str
    action: str
    scope: str = "Self"
    effect: str = "Allow"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class PermissionListOut(BaseModel):
    total: int
    items: List[PermissionOut]
    page: int = 1
    page_size: int = 20


# ── AuditLog ──

class AuditLogCreate(BaseModel):
    userId: str
    action: str
    resource: str
    resourceId: Optional[str] = None
    detail: Optional[str] = None  # JSON
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None


class AuditLogOut(BaseModel):
    logId: str
    userId: str
    action: str
    resource: str
    resourceId: Optional[str] = None
    detail: Optional[str] = None
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditLogListOut(BaseModel):
    total: int
    items: List[AuditLogOut]
    page: int = 1
    page_size: int = 20


# ── AlertRule ──

class AlertRuleCreate(BaseModel):
    name: str
    deviceType: Optional[str] = None
    condition: str
    severity: str = "Warning"  # Info/Warning/Critical
    enabled: bool = True


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    deviceType: Optional[str] = None
    condition: Optional[str] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None


class AlertRuleOut(BaseModel):
    ruleId: str
    name: str
    deviceType: Optional[str] = None
    condition: str
    severity: str = "Warning"
    enabled: bool = True
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertRuleListOut(BaseModel):
    total: int
    items: List[AlertRuleOut]
    page: int = 1
    page_size: int = 20


# ── AlertRecord ──

class AlertRecordUpdate(BaseModel):
    status: Optional[str] = None  # Unresolved/Acknowledged/Resolved
    acknowledgedAt: Optional[datetime] = None
    resolvedAt: Optional[datetime] = None
    resolvedBy: Optional[str] = None


class AlertRecordOut(BaseModel):
    alertId: str
    ruleId: Optional[str] = None
    deviceId: Optional[str] = None
    roomId: Optional[str] = None
    severity: str
    message: str
    detail: Optional[str] = None
    status: str = "Unresolved"
    acknowledgedAt: Optional[datetime] = None
    resolvedAt: Optional[datetime] = None
    resolvedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AlertRecordListOut(BaseModel):
    total: int
    items: List[AlertRecordOut]
    page: int = 1
    page_size: int = 20


# ── SystemJob ──

class SystemJobCreate(BaseModel):
    name: str
    type: str  # Sync/Cleanup/Report/Backup/Notification
    schedule: Optional[str] = None  # cron
    nextRunAt: Optional[datetime] = None


class SystemJobUpdate(BaseModel):
    name: Optional[str] = None
    schedule: Optional[str] = None
    lastRunAt: Optional[datetime] = None
    nextRunAt: Optional[datetime] = None
    status: Optional[str] = None


class SystemJobOut(BaseModel):
    jobId: str
    name: str
    type: str
    schedule: Optional[str] = None
    lastRunAt: Optional[datetime] = None
    nextRunAt: Optional[datetime] = None
    status: str = "Active"
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemJobListOut(BaseModel):
    total: int
    items: List[SystemJobOut]
    page: int = 1
    page_size: int = 20


# ── BackupRecord ──

class BackupRecordCreate(BaseModel):
    fileName: str
    fileSize: Optional[int] = None
    type: str = "Full"  # Full/Incremental
    startedAt: Optional[datetime] = None


class BackupRecordUpdate(BaseModel):
    fileSize: Optional[int] = None
    status: Optional[str] = None  # Running/Success/Failed
    completedAt: Optional[datetime] = None


class BackupRecordOut(BaseModel):
    recordId: str
    fileName: str
    fileSize: Optional[int] = None
    type: str = "Full"
    status: str = "Running"
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class BackupRecordListOut(BaseModel):
    total: int
    items: List[BackupRecordOut]
    page: int = 1
    page_size: int = 20


# ── CommandQueue ──

class CommandQueueCreate(BaseModel):
    deviceId: str
    command: str  # on/off/set_value
    params: Optional[str] = None  # JSON


class CommandQueueUpdate(BaseModel):
    status: Optional[str] = None  # Pending/Sent/Success/Failed
    sentAt: Optional[datetime] = None
    responseAt: Optional[datetime] = None
    responseData: Optional[str] = None  # JSON


class CommandQueueOut(BaseModel):
    commandId: str
    deviceId: str
    command: str
    params: Optional[str] = None
    status: str = "Pending"
    sentAt: Optional[datetime] = None
    responseAt: Optional[datetime] = None
    responseData: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommandQueueListOut(BaseModel):
    total: int
    items: List[CommandQueueOut]
    page: int = 1
    page_size: int = 20


# ── HeartbeatRecord ──

class HeartbeatRecordCreate(BaseModel):
    deviceId: str
    status: str  # Online/Offline
    cpuUsage: Optional[float] = None
    memoryUsage: Optional[float] = None
    signalStrength: Optional[int] = None
    reportedAt: Optional[datetime] = None


class HeartbeatRecordOut(BaseModel):
    heartbeatId: str
    deviceId: str
    status: str
    cpuUsage: Optional[float] = None
    memoryUsage: Optional[float] = None
    signalStrength: Optional[int] = None
    reportedAt: datetime

    class Config:
        from_attributes = True


class HeartbeatRecordListOut(BaseModel):
    total: int
    items: List[HeartbeatRecordOut]
    page: int = 1
    page_size: int = 20
