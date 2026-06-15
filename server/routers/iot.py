"""IoT 管理 API — 基于 D08 新模型（tech.py）"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from database import get_db
from models.tech import IoTDevice, AlertRecord, SmartScene
from models.user import User
from schemas.iot import (
    DeviceOut, DeviceControlReq, SceneActivateReq,
    AlertOut, SceneOut, IoTStats,
)
from services.auth_service import get_current_user, get_optional_user
from services import ha_service

router = APIRouter(prefix="/api/iot", tags=["IoT管理"])


# ── Devices ──

@router.get("/health")
async def iot_health(current_user: Optional[User] = Depends(get_optional_user)):
    """Check HA connectivity (mock or real)."""
    return await ha_service.check_health()


@router.get("/devices", response_model=list[DeviceOut])
async def list_devices(
    room_id: Optional[str] = Query(None, alias="room_id"),
    device_type: Optional[str] = Query(None, alias="type"),
    status: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
):
    """List all IoT devices with live state from HA (or mock)."""
    devices = await ha_service.get_devices(
        room_id=room_id, device_type=device_type, status_filter=status
    )
    # Sync status to DB for persistence
    for dev in devices:
        await _upsert_device(db, dev)
    return [DeviceOut(
        device_id=d["device_id"],
        room_id=d["room_id"],
        type=d["type"],
        name=d["name"],
        ha_entity_id=d.get("ha_entity_id", ""),
        protocol=d.get("protocol", ""),
        slave_id=d.get("slave_id"),
        sub_address=d.get("sub_address"),
        status=d["status"],
        attributes=d.get("attributes", {}),
    ) for d in devices]


@router.get("/devices/{device_id}", response_model=DeviceOut)
async def get_device(
    device_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get single device detail."""
    dev = await ha_service.get_device(device_id)
    if not dev:
        raise HTTPException(status_code=404, detail="设备不存在")
    return DeviceOut(
        device_id=dev["device_id"],
        room_id=dev["room_id"],
        type=dev["type"],
        name=dev["name"],
        ha_entity_id=dev.get("ha_entity_id", ""),
        protocol=dev.get("protocol", ""),
        slave_id=dev.get("slave_id"),
        sub_address=dev.get("sub_address"),
        status=dev["status"],
        attributes=dev.get("attributes", {}),
    )


@router.post("/control")
async def control_device(
    req: DeviceControlReq,
    user: User = Depends(get_current_user),
):
    """Send control command to a device."""
    result = await ha_service.control_device(req.device_id, req.action, req.params)
    return result


# ── Room init (all-off reset) ──

@router.post("/rooms/{room_id}/init")
async def init_room(
    room_id: str,
    current_user: User = Depends(get_current_user),
):
    """Initialize/reset a room — all devices off, curtains closed, door locked."""
    return await ha_service.init_room(room_id)


# ── Scenes ──

@router.get("/scenes")
async def list_scenes(current_user: Optional[User] = Depends(get_optional_user)):
    """Get all scene templates."""
    scenes = await ha_service.get_scenes()
    return scenes


@router.post("/scenes/activate")
async def activate_scene(
    req: SceneActivateReq,
    user: User = Depends(get_current_user),
):
    """Activate a scene for the given room."""
    result = await ha_service.activate_scene(req.room_id, req.scene)
    return result


# ── Alerts ──

@router.get("/alerts")
async def list_alerts(
    room_id: Optional[str] = Query(None, alias="room_id"),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get IoT alerts."""
    alerts = await ha_service.get_alerts(
        room_id=room_id, severity=severity, status_filter=status
    )
    return alerts


# ── Room Status (sensors + all devices) ──

@router.get("/rooms/{room_id}/status")
async def get_room_status(
    room_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get full status for a room: devices + sensors."""
    devices = await ha_service.get_devices(room_id=room_id)
    sensors = [d for d in devices if d["type"] == "Sensor"]
    controls = [d for d in devices if d["type"] != "Sensor"]
    return {
        "room_id": room_id,
        "sensors": sensors,
        "devices": controls,
    }


@router.get("/sensors/{room_id}")
async def get_room_sensors(
    room_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
):
    """Get temperature and humidity sensors for a room."""
    devices = await ha_service.get_devices(room_id=room_id, device_type="Sensor")
    temp = None
    humidity = None
    for d in devices:
        eid = d.get("ha_entity_id", "")
        if "temp" in eid:
            temp = d
        elif "humidity" in eid:
            humidity = d
    return {
        "room_id": room_id,
        "temperature": temp,
        "humidity": humidity,
    }


# ── Stats ──

@router.get("/stats")
async def get_stats(current_user: Optional[User] = Depends(get_optional_user)):
    """Get IoT device statistics for dashboard."""
    return await ha_service.get_stats()


# ── Database helpers ──

async def _upsert_device(db: AsyncSession, dev: dict):
    """Persist device info to DB for reference/tracking."""
    result = await db.execute(
        select(IoTDevice).where(IoTDevice.deviceId == dev["device_id"])
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.status = dev.get("status", existing.status)
        existing.attributes = json.dumps(dev.get("attributes", {}), ensure_ascii=False)
    else:
        db.add(IoTDevice(
            deviceId=dev["device_id"],
            roomId=dev.get("room_id", ""),
            type=dev.get("type", ""),
            name=dev.get("name", ""),
            haEntityId=dev.get("ha_entity_id", ""),
            protocol=dev.get("protocol", "Modbus"),
            slaveId=dev.get("slave_id"),
            subAddress=dev.get("sub_address"),
            status=dev.get("status", "Offline"),
            attributes=json.dumps(dev.get("attributes", {}), ensure_ascii=False),
        ))
    await db.commit()
