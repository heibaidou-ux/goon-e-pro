"""D08 技术域 — IoTDevice, DeviceEvent, SmartScene, AlertRule, AuditLog, CommandQueue 等"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class IoTDevice(Base):
    __tablename__ = "iot_devices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    deviceId = Column(String(50), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False, index=True)
    type = Column(String(30), nullable=False)  # Lock/AC/Light/Curtain/Speaker/Sensor/Relay/Gateway
    name = Column(String(100), nullable=False)
    haEntityId = Column(String(100))
    protocol = Column(String(20), default="Modbus")  # Modbus/Zigbee/IPAudio/WiFi
    slaveId = Column(Integer)
    subAddress = Column(Integer)
    status = Column(String(20), default="Offline")  # Online/Offline/Fault/Maintenance
    attributes = Column(Text)  # JSON
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DeviceEvent(Base):
    __tablename__ = "device_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    eventId = Column(String(32), unique=True, nullable=False, index=True)
    deviceId = Column(String(50), ForeignKey("iot_devices.deviceId"), nullable=False)
    roomId = Column(String(32), nullable=False)
    eventType = Column(String(30), nullable=False)  # Online/Offline/Command/Action/Alert
    eventData = Column(Text)  # JSON
    occurredAt = Column(DateTime, nullable=False)
    createdAt = Column(DateTime, server_default=func.now())


class SmartScene(Base):
    __tablename__ = "smart_scenes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sceneId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    label = Column(String(100))
    triggerType = Column(String(20), default="Manual")  # Auto/Manual/Schedule
    applicableRoomTypes = Column(Text)  # JSON array
    isActive = Column(Boolean, default=True)
    createdBy = Column(String(32), nullable=False)
    createdAt = Column(DateTime, server_default=func.now())

    rules = relationship("SceneRule", back_populates="scene", cascade="all, delete-orphan")


class SceneRule(Base):
    __tablename__ = "scene_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ruleId = Column(String(32), unique=True, nullable=False, index=True)
    sceneId = Column(String(32), ForeignKey("smart_scenes.sceneId"), nullable=False)
    conditionType = Column(String(20), nullable=False)  # DeviceState/Time/Schedule
    conditionParams = Column(Text)  # JSON
    actionType = Column(String(20), nullable=False)
    actionParams = Column(Text)  # JSON
    sortOrder = Column(Integer, default=0)
    isActive = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())

    scene = relationship("SmartScene", back_populates="rules")


class RoomSceneBinding(Base):
    __tablename__ = "room_scene_bindings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    bindingId = Column(String(32), unique=True, nullable=False, index=True)
    roomId = Column(String(32), ForeignKey("rooms.roomId"), nullable=False)
    sceneId = Column(String(32), ForeignKey("smart_scenes.sceneId"), nullable=False)
    isEnabled = Column(Boolean, default=True)
    customParams = Column(Text)  # JSON
    createdAt = Column(DateTime, server_default=func.now())


class UserAccount(Base):
    __tablename__ = "user_accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String(32), unique=True, nullable=False, index=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashedPassword = Column(String(255), nullable=False)
    displayName = Column(String(100), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), default="Active")  # Active/Disabled/Locked
    lastLogin = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    roleId = Column(String(32), unique=True, nullable=False, index=True)
    orgId = Column(String(32), ForeignKey("organizations.orgId"), nullable=True)
    name = Column(String(50), nullable=False)
    code = Column(String(30), nullable=False)  # System/StoreManager/Staff/Finance/HR
    description = Column(String(200))
    status = Column(String(20), default="Active")
    createdAt = Column(DateTime, server_default=func.now())


class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    permissionId = Column(String(32), unique=True, nullable=False, index=True)
    roleId = Column(String(32), ForeignKey("roles.roleId"), nullable=False)
    resource = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)  # Read/Write/Delete/Approve
    scope = Column(String(20), default="Self")  # All/Org/Store/Self
    effect = Column(String(10), default="Allow")  # Allow/Deny
    createdAt = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    logId = Column(String(32), unique=True, nullable=False, index=True)
    userId = Column(String(32), nullable=False)
    action = Column(String(50), nullable=False)
    resource = Column(String(50), nullable=False)
    resourceId = Column(String(32))
    detail = Column(Text)  # JSON
    ipAddress = Column(String(50))
    userAgent = Column(String(200))
    createdAt = Column(DateTime, server_default=func.now())


class AlertRule(Base):
    __tablename__ = "alert_rules"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ruleId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    deviceType = Column(String(30))
    condition = Column(String(500), nullable=False)
    severity = Column(String(20), default="Warning")  # Info/Warning/Critical
    enabled = Column(Boolean, default=True)
    createdAt = Column(DateTime, server_default=func.now())


class AlertRecord(Base):
    __tablename__ = "alert_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    alertId = Column(String(32), unique=True, nullable=False, index=True)
    ruleId = Column(String(32), ForeignKey("alert_rules.ruleId"), nullable=True)
    deviceId = Column(String(50), ForeignKey("iot_devices.deviceId"), nullable=True)
    roomId = Column(String(32))
    severity = Column(String(20), nullable=False)
    message = Column(String(300), nullable=False)
    detail = Column(Text)
    status = Column(String(20), default="Unresolved")  # Unresolved/Acknowledged/Resolved
    acknowledgedAt = Column(DateTime)
    resolvedAt = Column(DateTime)
    resolvedBy = Column(String(32))
    createdAt = Column(DateTime, server_default=func.now())


class SystemJob(Base):
    __tablename__ = "system_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jobId = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(30), nullable=False)  # Sync/Cleanup/Report/Backup/Notification
    schedule = Column(String(50))  # cron expression
    lastRunAt = Column(DateTime)
    nextRunAt = Column(DateTime)
    status = Column(String(20), default="Active")  # Active/Paused/Disabled
    createdAt = Column(DateTime, server_default=func.now())


class BackupRecord(Base):
    __tablename__ = "backup_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    recordId = Column(String(32), unique=True, nullable=False, index=True)
    fileName = Column(String(200), nullable=False)
    fileSize = Column(Integer)
    type = Column(String(20), default="Full")  # Full/Incremental
    status = Column(String(20), default="Running")  # Running/Success/Failed
    startedAt = Column(DateTime)
    completedAt = Column(DateTime)
    createdAt = Column(DateTime, server_default=func.now())


class CommandQueue(Base):
    __tablename__ = "command_queues"
    id = Column(Integer, primary_key=True, autoincrement=True)
    commandId = Column(String(32), unique=True, nullable=False, index=True)
    deviceId = Column(String(50), ForeignKey("iot_devices.deviceId"), nullable=False)
    command = Column(String(30), nullable=False)  # on/off/set_value
    params = Column(Text)  # JSON
    status = Column(String(20), default="Pending")  # Pending/Sent/Success/Failed
    sentAt = Column(DateTime)
    responseAt = Column(DateTime)
    responseData = Column(Text)  # JSON
    createdAt = Column(DateTime, server_default=func.now())


class HeartbeatRecord(Base):
    __tablename__ = "heartbeat_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    heartbeatId = Column(String(32), unique=True, nullable=False, index=True)
    deviceId = Column(String(50), ForeignKey("iot_devices.deviceId"), nullable=False)
    status = Column(String(10), nullable=False)  # Online/Offline
    cpuUsage = Column(Float)
    memoryUsage = Column(Float)
    signalStrength = Column(Integer)
    reportedAt = Column(DateTime, nullable=False)
