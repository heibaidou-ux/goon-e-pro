from pydantic import BaseModel
from typing import Optional, Any


class DeviceOut(BaseModel):
    device_id: str
    room_id: str
    type: str
    name: str
    ha_entity_id: str = ""
    protocol: str = ""
    slave_id: Optional[int] = None
    sub_address: Optional[int] = None
    status: str = "Offline"
    attributes: dict = {}


class DeviceControlReq(BaseModel):
    device_id: str
    action: str  # on, off, open, close, temperature, etc.
    params: dict = {}


class SceneActivateReq(BaseModel):
    room_id: str
    scene: str  # scene name or scene_id


class AlertOut(BaseModel):
    alert_id: str
    device_id: str
    room_id: str
    room_name: str = ""
    device_type: str = ""
    device_code: str = ""
    severity: str
    type: str
    message: str
    detail: str = ""
    status: str
    assigned_role: str = ""
    assigned_name: str = ""
    created_at: str = ""


class SceneOut(BaseModel):
    scene_id: str
    name: str
    label: str
    trigger_type: str
    applicable_room_types: list[str]
    rules: list[dict]


class IoTStats(BaseModel):
    total: int = 0
    online: int = 0
    offline: int = 0
    fault: int = 0
    online_rate: float = 0
    unresolved_alerts: int = 0
    total_alerts: int = 0
