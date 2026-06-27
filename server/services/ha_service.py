"""
Home Assistant REST API client + Mock data layer for IoT integration.
When HA_TOKEN is set, communicates with real HA at HA_URL.
Otherwise uses realistic mock data matching the 4-room 盈隆店 setup.

真实HA实体命名规则（v1.1规范）:
  switch.{房间}_relay_ch{1-8}   → 灯光继电器通道
  switch.{房间}_all_lights       → 一键全开/全关
  climate.{房间}                 → 空调温控器
  cover.{房间}_curtain            → 窗帘
  lock.{房间}_door                → 通通锁门锁
  sensor.{房间}_temp              → 室温
  sensor.{房间}_humidity          → 湿度
  input_boolean.{房间}_scene_xxx  → 场景切换
  input_boolean.{房间}_init        → 初始化复位

房间名对照:
  baishawa  大茶室（白沙瓦）
  bulage    中茶室（布拉格）
  feilengcui  小茶室（翡冷翠）
  fengshali   会议室（丰沙里）
"""
import json
import random
import re
import httpx
from datetime import datetime
from typing import Optional

from config import settings

# ── HA房间名映射（ERP room_id ↔ HA系统名）──
# 根据 ERP_IoT_API规范.md v1.1

HA_ROOM_MAP = {
    "RM001": "fengshali",       # 大会议室（丰沙里）
    "RM002": "bulage",          # 中茶室（布拉格）
    "RM003": "feilengcui",      # 小茶室（翡冷翠）
    "RM004": "baishawa",        # 大茶室（白沙瓦）
}
HA_ROOM_REVERSE = {v: k for k, v in HA_ROOM_MAP.items()}

ROOMS = [
    {"room_id": "RM001", "name": "大会议室·丰沙里", "type": "MeetingRoom"},
    {"room_id": "RM002", "name": "中茶室·布拉格", "type": "TeaRoom"},
    {"room_id": "RM003", "name": "小茶室·翡冷翠", "type": "TeaRoom"},
    {"room_id": "RM004", "name": "大茶室·白沙瓦", "type": "TeaRoom"},
]

# 各房间继电器通道配置（来自 盈隆茶室电路控制规则.md）
RELAY_CHANNELS = {
    "fengshali": [  # 会议室
        ("ch1", "筒灯1"), ("ch2", "筒灯2"), ("ch3", "吊灯"),
        ("ch4", "风扇1"), ("ch5", "风扇2"), ("ch6", "风扇3"),
        ("ch7", "功放"), ("ch8", "空"),
    ],
    "feilengcui": [  # 小茶室
        ("ch1", "吊灯"), ("ch2", "筒灯"), ("ch3", "换气扇"),
        ("ch4", "风扇"), ("ch5", "功放(小茶室)"), ("ch6", "功放(展厅)"),
        ("ch7", "备用"), ("ch8", "备用"),
    ],
    "bulage": [  # 中茶室
        ("ch1", "吊灯"), ("ch2", "筒灯"), ("ch3", "背景灯"),
        ("ch4", "风扇"), ("ch5", "功放"),
        ("ch6", "备用"), ("ch7", "备用"), ("ch8", "备用"),
    ],
    "baishawa": [  # 大茶室
        ("ch1", "吊灯"), ("ch2", "筒灯"), ("ch3", "背景灯"),
        ("ch4", "风扇"), ("ch5", "功放"),
        ("ch6", "备用"), ("ch7", "备用"), ("ch8", "备用"),
    ],
}

DEVICE_TEMPLATES = [
    # Lock
    {"type": "Lock", "name_template": "{room}门锁", "protocol": "Zigbee",
     "ha_entity_fn": lambda r: f"lock.{r}_door",
     "attributes": {"battery_level": 85, "locked": True}},
    # AC
    {"type": "AC", "name_template": "{room}空调", "protocol": "Modbus",
     "ha_entity_fn": lambda r: f"climate.{r}",
     "attributes": {"power": False, "mode": "cool", "target_temperature": 24, "current_temperature": 26}},
    # All-lights (software switch)
    {"type": "Light", "name_template": "{room}全屋灯光", "protocol": "Modbus",
     "ha_entity_fn": lambda r: f"switch.{r}_all_lights",
     "attributes": {"power": False, "channel": 0, "is_all_lights": True}},
    # Relay channels (1-8 per room)
    *[{"type": "Light", "name_template": "{room} " + name, "protocol": "Modbus",
       "ha_entity_fn": lambda r, ch=ch: f"switch.{r}_{ch}",
       "attributes": {"power": False, "channel": int(ch.replace("ch", ""))}}
      for _, ch_name in [("", "")]  # placeholder - filled below
      for ch, name in [("", "")]    # placeholder
     ][:0],  # empty list, channels added after room loop
    # Curtain
    {"type": "Curtain", "name_template": "{room}窗帘", "protocol": "Zigbee",
     "ha_entity_fn": lambda r: f"cover.{r}_curtain",
     "attributes": {"position": "closed", "current_position": 0}},
    # Temperature sensor
    {"type": "Sensor", "name_template": "{room}室温", "protocol": "Modbus",
     "ha_entity_fn": lambda r: f"sensor.{r}_temp",
     "attributes": {"value": 25.0, "unit": "°C"}},
    # Humidity sensor
    {"type": "Sensor", "name_template": "{room}湿度", "protocol": "Modbus",
     "ha_entity_fn": lambda r: f"sensor.{r}_humidity",
     "attributes": {"value": 60.0, "unit": "%"}},
]


def _build_devices_for_room(room: dict, ha_room: str) -> list[dict]:
    """为单个房间生成所有设备条目（含各继电器通道）。"""
    devices = []
    idx_base = ord(room["room_id"][-1]) * 10  # deterministic base

    relay_config = RELAY_CHANNELS.get(ha_room, [])
    devices.append({
        "device_id": f"DEV{idx_base}00",
        "room_id": room["room_id"],
        "type": "Lock",
        "name": f"{room['name']}门锁",
        "ha_entity_id": f"lock.{ha_room}_door",
        "protocol": "Zigbee",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"battery_level": random.randint(60, 100), "locked": True},
    })
    devices.append({
        "device_id": f"DEV{idx_base}01",
        "room_id": room["room_id"],
        "type": "AC",
        "name": f"{room['name']}空调",
        "ha_entity_id": f"climate.{ha_room}",
        "protocol": "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"power": False, "mode": "cool", "target_temperature": 24, "current_temperature": 26},
    })
    devices.append({
        "device_id": f"DEV{idx_base}02",
        "room_id": room["room_id"],
        "type": "Light",
        "name": f"{room['name']}全屋灯光",
        "ha_entity_id": f"switch.{ha_room}_all_lights",
        "protocol": "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"power": False, "channel": 0, "is_all_lights": True},
    })
    # Relay channels
    for ch_name, ch_desc in relay_config:
        ch_num = ch_name.replace("ch", "")
        devices.append({
            "device_id": f"DEV{idx_base}{10 + int(ch_num):02d}",
            "room_id": room["room_id"],
            "type": "Light",
            "name": f"{room['name']}{ch_desc}",
            "ha_entity_id": f"switch.{ha_room}_relay_{ch_name}",
            "protocol": "Modbus",
            "slave_id": None,
            "sub_address": None,
            "status": "Online",
            "attributes": {"power": False, "channel": int(ch_num)},
        })
    # Curtain
    devices.append({
        "device_id": f"DEV{idx_base}20",
        "room_id": room["room_id"],
        "type": "Curtain",
        "name": f"{room['name']}窗帘",
        "ha_entity_id": f"cover.{ha_room}_curtain",
        "protocol": "Zigbee",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"position": "closed", "current_position": 0},
    })
    # Sensors
    devices.append({
        "device_id": f"DEV{idx_base}30",
        "room_id": room["room_id"],
        "type": "Sensor",
        "name": f"{room['name']}室温",
        "ha_entity_id": f"sensor.{ha_room}_temp",
        "protocol": "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"value": round(random.uniform(22, 28), 1), "unit": "°C"},
    })
    devices.append({
        "device_id": f"DEV{idx_base}31",
        "room_id": room["room_id"],
        "type": "Sensor",
        "name": f"{room['name']}湿度",
        "ha_entity_id": f"sensor.{ha_room}_humidity",
        "protocol": "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": "Online",
        "attributes": {"value": round(random.uniform(40, 70), 1), "unit": "%"},
    })
    return devices


SCENES = [
    {"scene_id": "SCN_WELCOME", "name": "Welcome", "label": "迎宾模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "AC", "action": "On", "params": {}},
         {"sequence": 2, "device_type": "Light", "action": "AllOn", "params": {}},
         {"sequence": 3, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 4, "device_type": "Speaker", "action": "On", "params": {"volume": 30, "source": "背景音乐"}},
     ]},
    {"scene_id": "SCN_TEA", "name": "TeaSession", "label": "品茶模式", "trigger_type": "Manual",
     "applicable_room_types": ["TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "AllOn", "params": {}},
         {"sequence": 2, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 25}},
     ]},
    {"scene_id": "SCN_MEETING", "name": "Meeting", "label": "会议模式", "trigger_type": "Manual",
     "applicable_room_types": ["MeetingRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "AllOn", "params": {}},
         {"sequence": 2, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 24}},
     ]},
    {"scene_id": "SCN_KARAOKE", "name": "Karaoke", "label": "K歌模式", "trigger_type": "Manual",
     "applicable_room_types": ["TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "On", "params": {}},
         {"sequence": 2, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 22}},
         {"sequence": 4, "device_type": "Speaker", "action": "On", "params": {"volume": 60, "source": "K歌"}},
     ]},
    {"scene_id": "SCN_ENERGY_SAVE", "name": "EnergySave", "label": "节能模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "AllOff", "params": {}},
         {"sequence": 2, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Off", "params": {}},
         {"sequence": 4, "device_type": "Speaker", "action": "Off", "params": {}},
     ]},
    {"scene_id": "SCN_CHECKOUT", "name": "Checkout", "label": "退房模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "AC", "action": "Off", "params": {}},
         {"sequence": 2, "device_type": "Light", "action": "AllOff", "params": {}},
         {"sequence": 3, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 4, "device_type": "Speaker", "action": "Off", "params": {}},
         {"sequence": 5, "device_type": "Lock", "action": "Lock", "params": {}},
     ]},
    {"scene_id": "SCN_PREOPEN", "name": "PreOpen", "label": "预开模式", "trigger_type": "Schedule",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "AC", "action": "Temperature", "params": {"temperature": 24}},
     ]},
    {"scene_id": "SCN_CLEANUP", "name": "Cleanup", "label": "打扫完成", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "AllOff", "params": {}},
         {"sequence": 2, "device_type": "AC", "action": "Off", "params": {}},
         {"sequence": 3, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 4, "device_type": "Speaker", "action": "Off", "params": {}},
     ]},
]

# ── Mock state store ──

_mock_devices: list[dict] = []
_mock_alerts: list[dict] = []
_alert_counter = 0


def _build_mock_devices():
    """Generate realistic mock device list matching actual HA entity naming."""
    global _mock_devices
    if _mock_devices:
        return
    for room in ROOMS:
        ha_room = HA_ROOM_MAP.get(room["room_id"], room["room_id"])
        _mock_devices.extend(_build_devices_for_room(room, ha_room))


def _get_device(device_id: str) -> Optional[dict]:
    _build_mock_devices()
    for d in _mock_devices:
        if d["device_id"] == device_id:
            return d
    return None


def _get_device_by_entity(entity_id: str) -> Optional[dict]:
    """查找HA实体ID对应的mock设备。"""
    _build_mock_devices()
    for d in _mock_devices:
        if d["ha_entity_id"] == entity_id:
            return d
    return None


def _get_room_devices(room_id: str) -> list[dict]:
    _build_mock_devices()
    return [d for d in _mock_devices if d["room_id"] == room_id]


def _get_device_type_in_room(room_id: str, device_type: str) -> list[dict]:
    """Get all devices of given type in a room."""
    devices = _get_room_devices(room_id)
    return [d for d in devices if d["type"] == device_type]


# ── Public API ──


def is_mock_mode() -> bool:
    """Return True if no HA token is configured (mock mode)."""
    return not settings.ha_token


async def check_health() -> dict:
    """Check HA connectivity or mock health."""
    if is_mock_mode():
        return {"status": "ok", "mode": "mock", "device_count": len(_mock_devices) if _mock_devices else 30}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/",
                headers=_ha_headers()
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "mode": "ha", "code": resp.status_code}
    except Exception as e:
        return {"status": "error", "mode": "ha", "message": str(e), "ha_url": settings.ha_url}


async def get_devices(room_id: Optional[str] = None, device_type: Optional[str] = None,
                      status_filter: Optional[str] = None) -> list[dict]:
    """Get all IoT devices, optionally filtered."""
    if is_mock_mode():
        _build_mock_devices()
        result = list(_mock_devices)
        if room_id:
            result = [d for d in result if d["room_id"] == room_id]
        if device_type:
            result = [d for d in result if d["type"] == device_type]
        if status_filter:
            result = [d for d in result if d["status"] == status_filter]
        return result

    # Real HA mode
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/states",
                headers=_ha_headers()
            )
            if resp.status_code != 200:
                return []
            ha_states = resp.json()
            # Filter to only entities belonging to our rooms
            our_ha_rooms = set(HA_ROOM_REVERSE.keys())
            devices = []
            for state in ha_states:
                entity_id = state.get("entity_id", "")
                dev_type = _ha_entity_to_type(entity_id)
                if not dev_type:
                    continue
                ha_room = _ha_entity_to_room(entity_id)
                if not ha_room:
                    continue
                if room_id and ha_room != room_id:
                    continue
                if device_type and dev_type != device_type:
                    continue
                devices.append(_ha_state_to_device(state))
            return devices
    except Exception as e:
        return []


async def get_device(device_id: str) -> Optional[dict]:
    """Get single device by ID (or HA entity_id in real mode)."""
    if is_mock_mode():
        return _get_device(device_id)
    ha_entity_id = device_id
    if not device_id.startswith(("switch.", "climate.", "cover.", "lock.", "sensor.", "input_boolean.")):
        dev = _get_device(device_id)
        if dev:
            ha_entity_id = dev.get("ha_entity_id", device_id)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/states/{ha_entity_id}",
                headers=_ha_headers()
            )
            if resp.status_code == 200:
                return _ha_state_to_device(resp.json())
    except Exception:
        pass
    return _get_device(device_id)


async def control_device(device_id: str, action: str, params: Optional[dict] = None) -> dict:
    """Send a control command to a device.

    Actions: on, off, open, close, stop, all_on, all_off,
             temperature, volume, unlock, lock, cool, heat, fan, dry
    """
    if is_mock_mode():
        return _mock_control(device_id, action, params or {})
    return await _ha_control(device_id, action, params or {})


def _mock_control(device_id: str, action: str, params: dict) -> dict:
    """模拟控制（脱机开发用）。"""
    device = _get_device(device_id)
    if not device:
        return {"success": False, "message": f"设备 {device_id} 不存在"}

    attrs = device["attributes"]
    old_state = dict(attrs)

    if device["type"] == "AC":
        if action == "off":
            attrs["power"] = False
            attrs["mode"] = "off"
        elif action == "on":
            attrs["power"] = True
        elif action in ("cool", "heat", "fan", "dry", "auto"):
            attrs["mode"] = action
            attrs["power"] = True
        elif action == "temperature":
            temp = params.get("temperature", 24)
            attrs["target_temperature"] = temp
            attrs["power"] = True
    elif device["type"] == "Light":
        if action == "on":
            attrs["power"] = True
        elif action == "off":
            attrs["power"] = False
        elif action == "all_on":
            attrs["power"] = True
            # Also turn on all relay channels in this room
            for d in _mock_devices:
                if d["room_id"] == device["room_id"] and d["type"] == "Light" and d.get("attributes", {}).get("channel", 0) > 0:
                    d["attributes"]["power"] = True
        elif action == "all_off":
            attrs["power"] = False
            for d in _mock_devices:
                if d["room_id"] == device["room_id"] and d["type"] == "Light" and d.get("attributes", {}).get("channel", 0) > 0:
                    d["attributes"]["power"] = False
    elif device["type"] == "Curtain":
        if action == "open":
            attrs["position"] = "open"
            attrs["current_position"] = 100
        elif action == "close":
            attrs["position"] = "closed"
            attrs["current_position"] = 0
        elif action == "stop":
            attrs["position"] = "open" if attrs.get("current_position", 0) > 50 else "closed"
    elif device["type"] == "Lock":
        if action == "unlock":
            attrs["locked"] = False
        elif action == "lock":
            attrs["locked"] = True

    device["status"] = "Online"
    return {
        "success": True,
        "message": f"指令执行成功: {device['name']} → {action}",
        "device_id": device_id,
        "action": action,
        "old_state": old_state,
        "new_state": dict(attrs),
    }


async def _ha_control(device_id: str, action: str, params: dict) -> dict:
    """Control device via real HA REST API.
    实体命名规范: switch.{room}_relay_ch{N}, climate.{room}, cover.{room}_curtain, lock.{room}_door
    """
    device = _get_device(device_id)
    ha_entity_id = device.get("ha_entity_id", device_id) if device else device_id
    device_type = device["type"] if device else _ha_entity_to_type(device_id) or "Unknown"

    service_data = _ha_build_service(device_type, action, params)
    if not service_data:
        return {"success": False, "message": f"不支持的动作: {device_type} → {action}"}

    # 如果是全开/全关，找 all_lights 实体
    if action in ("all_on", "all_off"):
        room = _ha_entity_to_room(ha_entity_id)
        if room:
            ha_name = HA_ROOM_MAP.get(room, room)
            ha_entity_id = f"switch.{ha_name}_all_lights"
        else:
            # 从entity_id推断房间名
            parts = ha_entity_id.split(".")
            if len(parts) > 1:
                prefix = parts[1].rsplit("_", 1)[0]  # baishawa_relay → baishawa
                ha_entity_id = f"switch.{prefix}_all_lights"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.ha_url}/api/services/{service_data['domain']}/{service_data['service']}",
                headers=_ha_headers(),
                json={"entity_id": ha_entity_id, **service_data.get("data", {})},
            )
            if resp.status_code == 200:
                return {"success": True, "message": f"HA指令已发送: {action}", "device_id": device_id}
            return {"success": False, "message": f"HA返回错误({resp.status_code})", "device_id": device_id}
    except Exception as e:
        return {"success": False, "message": f"HA请求失败: {str(e)}", "device_id": device_id}


def _ha_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.ha_token}",
        "Content-Type": "application/json",
    }


def _ha_build_service(device_type: str, action: str, params: dict) -> Optional[dict]:
    """Map ERP action to HA service call using actual HA entity types per v1.1 spec."""
    mapping = {
        ("AC", "on"): {"domain": "climate", "service": "turn_on"},
        ("AC", "off"): {"domain": "climate", "service": "turn_off"},
        ("AC", "cool"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "cool"}},
        ("AC", "heat"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "heat"}},
        ("AC", "fan_only"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "fan_only"}},
        ("AC", "auto"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "auto"}},
        ("AC", "temperature"): {"domain": "climate", "service": "set_temperature",
                                "data": {"temperature": params.get("temperature", 24)}},
        ("Light", "on"): {"domain": "switch", "service": "turn_on"},
        ("Light", "off"): {"domain": "switch", "service": "turn_off"},
        ("Light", "all_on"): {"domain": "switch", "service": "turn_on"},
        ("Light", "all_off"): {"domain": "switch", "service": "turn_off"},
        ("Curtain", "open"): {"domain": "cover", "service": "open_cover"},
        ("Curtain", "close"): {"domain": "cover", "service": "close_cover"},
        ("Curtain", "stop"): {"domain": "cover", "service": "stop_cover"},
        ("Curtain", "position"): {"domain": "cover", "service": "set_cover_position",
                                   "data": {"position": params.get("position", 50)}},
        ("Lock", "unlock"): {"domain": "lock", "service": "unlock"},
        ("Lock", "lock"): {"domain": "lock", "service": "lock"},
    }
    return mapping.get((device_type, action))


async def activate_scene(room_id: str, scene_name: str) -> dict:
    """Activate a scene for a specific room.

    Real HA mode: toggle input_boolean.{room}_scene_{scene}.
    Mock mode: Execute individual device commands.
    """
    scene = None
    for s in SCENES:
        if s["name"] == scene_name or s["scene_id"] == scene_name:
            scene = s
            break
    if not scene:
        return {"success": False, "message": f"场景不存在: {scene_name}"}

    if not is_mock_mode():
        ha_room = HA_ROOM_MAP.get(room_id, room_id)
        scene_key = scene["name"].lower()
        entity_id = f"input_boolean.{ha_room}_scene_{scene_key}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{settings.ha_url}/api/services/input_boolean/turn_on",
                    headers=_ha_headers(),
                    json={"entity_id": entity_id},
                )
                if resp.status_code == 200:
                    return {
                        "success": True,
                        "scene": scene["name"],
                        "scene_label": scene["label"],
                        "room_id": room_id,
                        "message": f"场景「{scene['label']}」已通过HA激活",
                    }
                return {"success": False, "message": f"HA场景激活失败: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"HA请求失败: {str(e)}"}

    # Mock mode: execute individual device commands
    results = []
    action_map = {
        "On": "on", "Off": "off", "AllOn": "all_on", "AllOff": "all_off",
        "Unlock": "unlock", "Lock": "lock",
        "Open": "open", "Close": "close", "Stop": "stop",
        "Temperature": "temperature",
        "Volume": "volume", "Mute": "mute",
    }

    for rule in scene["rules"]:
        dev_type = rule["device_type"]
        mapped_action = action_map.get(rule["action"], rule["action"].lower())

        devices = _get_device_type_in_room(room_id, dev_type)
        if not devices:
            continue
        for dev in devices:
            r = await control_device(dev["device_id"], mapped_action, rule["params"])
            results.append(r)

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "success": success_count > 0,
        "scene": scene["name"],
        "scene_label": scene["label"],
        "room_id": room_id,
        "total_steps": len(scene["rules"]),
        "success_count": success_count,
        "results": results,
    }


async def init_room(room_id: str) -> dict:
    """Initialize/reset a room: all off, curtains closed, door locked."""
    if not is_mock_mode():
        ha_room = HA_ROOM_MAP.get(room_id, room_id)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{settings.ha_url}/api/services/input_boolean/turn_on",
                    headers=_ha_headers(),
                    json={"entity_id": f"input_boolean.{ha_room}_init"},
                )
                if resp.status_code == 200:
                    return {"success": True, "room_id": room_id, "message": "房间已初始化复位"}
                return {"success": False, "room_id": room_id, "message": f"HA返回错误: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "room_id": room_id, "message": str(e)}

    # Mock mode
    devices = _get_room_devices(room_id)
    results = []
    for dev in devices:
        if dev["type"] == "Light" and dev["attributes"].get("power"):
            results.append(_mock_control(dev["device_id"], "off", {}))
        elif dev["type"] == "AC" and dev["attributes"].get("mode") != "off":
            results.append(_mock_control(dev["device_id"], "off", {}))
        elif dev["type"] == "Curtain" and dev["attributes"].get("position") != "closed":
            results.append(_mock_control(dev["device_id"], "close", {}))
        elif dev["type"] == "Lock" and not dev["attributes"].get("locked"):
            results.append(_mock_control(dev["device_id"], "lock", {}))
    return {"success": True, "room_id": room_id, "actions": len(results), "results": results}


async def get_scenes() -> list[dict]:
    return SCENES


async def get_alerts(room_id: Optional[str] = None, severity: Optional[str] = None,
                     status_filter: Optional[str] = None) -> list[dict]:
    """Get IoT alerts."""
    if is_mock_mode():
        _generate_mock_alerts()
        result = list(_mock_alerts)
        if room_id:
            result = [a for a in result if a["room_id"] == room_id]
        if severity:
            result = [a for a in result if a["severity"] == severity]
        if status_filter:
            result = [a for a in result if a["status"] == status_filter]
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)
    return []


def _generate_mock_alerts():
    global _mock_alerts, _alert_counter
    if _mock_alerts:
        return
    _build_mock_devices()

    offline = [d for d in _mock_devices if d["status"] == "Offline"]
    for dev in offline[:3]:
        _alert_counter += 1
        room_name = next((r["name"] for r in ROOMS if r["room_id"] == dev["room_id"]), dev["room_id"])
        _mock_alerts.append({
            "alert_id": f"ALT{_alert_counter:04d}",
            "device_id": dev["device_id"],
            "room_id": dev["room_id"],
            "room_name": room_name,
            "device_type": dev["type"],
            "device_code": dev["device_id"],
            "severity": "Warning",
            "type": "Offline",
            "message": f"{dev['name']} 离线",
            "status": "Unresolved",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    for dev in _mock_devices:
        if dev["type"] == "Lock" and dev["attributes"].get("battery_level", 100) < 70:
            _alert_counter += 1
            room_name = next((r["name"] for r in ROOMS if r["room_id"] == dev["room_id"]), dev["room_id"])
            _mock_alerts.append({
                "alert_id": f"ALT{_alert_counter:04d}",
                "device_id": dev["device_id"],
                "room_id": dev["room_id"],
                "room_name": room_name,
                "device_type": dev["type"],
                "device_code": dev["device_id"],
                "severity": "Info",
                "type": "BatteryLow",
                "message": f"{dev['name']} 电量不足 ({dev['attributes']['battery_level']}%)",
                "status": "Unresolved",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })


async def get_stats() -> dict:
    """Get IoT device stats (total, online, offline, fault, alert count)."""
    if is_mock_mode():
        _build_mock_devices()
        total = len(_mock_devices)
        online = sum(1 for d in _mock_devices if d["status"] == "Online")
        offline = sum(1 for d in _mock_devices if d["status"] == "Offline")
        fault = sum(1 for d in _mock_devices if d["status"] == "Fault")
        _generate_mock_alerts()
        unresolved = sum(1 for a in _mock_alerts if a["status"] == "Unresolved")
        return {
            "total": total, "online": online, "offline": offline, "fault": fault,
            "online_rate": round(online / total * 100, 1) if total else 0,
            "unresolved_alerts": unresolved, "total_alerts": len(_mock_alerts),
        }

    devices = await get_devices()
    total = len(devices)
    online = sum(1 for d in devices if d.get("status") == "Online")
    offline = sum(1 for d in devices if d.get("status") == "Offline")
    fault = sum(1 for d in devices if d.get("status") == "Fault")
    return {
        "total": total, "online": online, "offline": offline, "fault": fault,
        "online_rate": round(online / total * 100, 1) if total else 0,
        "unresolved_alerts": 0, "total_alerts": 0,
    }


# ── HA entity mapping helpers ──

# HA实体 → ERP设备类型映射表
_HA_DOMAIN_TYPE_MAP = {
    "lock": "Lock",
    "climate": "AC",
    "cover": "Curtain",
}

def _ha_entity_to_type(entity_id: str) -> Optional[str]:
    """Map HA entity_id to ERP device type.
    映射规则（v1.1规范）:
      lock.* → Lock
      climate.* → AC
      cover.*_curtain → Curtain
      switch.*_relay_ch* → Light
      switch.*_all_lights → Light
      sensor.*_temp → Sensor
      sensor.*_humidity → Sensor
      input_boolean.*_scene_* → System (场景)
      input_boolean.*_init → System
    """
    domain = entity_id.split(".")[0] if "." in entity_id else ""
    entity_name = entity_id.split(".")[1] if "." in entity_id else ""

    if domain in _HA_DOMAIN_TYPE_MAP:
        return _HA_DOMAIN_TYPE_MAP[domain]

    if domain == "switch":
        return "Light"

    if domain == "sensor":
        if "temp" in entity_name:
            return "Sensor"
        if "humidity" in entity_name:
            return "Sensor"
        return "Sensor"

    if domain == "input_boolean":
        return "System"

    if domain == "input_number":
        return "Sensor"

    if domain == "input_select":
        return "Speaker"

    return None


def _ha_entity_to_room(entity_id: str) -> Optional[str]:
    """从HA实体名提取ERP room_id。
    命名规范: {domain}.{room}_{suffix}
    房名: baishawa, bulage, feilengcui, fengshali
    """
    eid_lower = entity_id.lower()
    for ha_name, room_id in HA_ROOM_REVERSE.items():
        if ha_name in eid_lower:
            return room_id
    return None


def _ha_state_to_device(state: dict) -> dict:
    """Convert HA API state object to our device format."""
    entity_id = state.get("entity_id", "")
    attrs = dict(state.get("attributes", {}))
    device_type = _ha_entity_to_type(entity_id) or "Unknown"
    room_id = _ha_entity_to_room(entity_id) or ""
    domain = entity_id.split(".")[0]
    entity_name = entity_id.split(".")[1] if "." in entity_id else ""

    state_val = state.get("state", "")
    status = "Online" if state_val != "unavailable" else "Offline"

    if device_type == "Lock":
        attrs["locked"] = state_val == "locked"
        attrs["battery_level"] = attrs.get("battery_level", 85)
    elif device_type == "AC":
        attrs["mode"] = state_val
        attrs["current_temperature"] = attrs.get("current_temperature", 26)
        attrs["target_temperature"] = attrs.get("temperature", 24)
        attrs["power"] = state_val not in ("off", "unavailable")
    elif device_type == "Light":
        attrs["power"] = state_val == "on"
        if "all_lights" in entity_name:
            attrs["is_all_lights"] = True
            attrs["channel"] = 0
        else:
            ch_match = re.search(r"ch(\d)", entity_name)
            attrs["channel"] = int(ch_match.group(1)) if ch_match else None
    elif device_type == "Curtain":
        attrs["position"] = state_val
        attrs["current_position"] = attrs.get("current_position", 0)
    elif device_type == "Sensor":
        unit = attrs.get("unit_of_measurement", "")
        try:
            attrs["value"] = float(state_val) if state_val.replace(".", "").replace("-", "").lstrip("-").isdigit() else state_val
        except (ValueError, AttributeError):
            attrs["value"] = state_val
        attrs["unit"] = unit

    friendly_name = attrs.get("friendly_name", entity_id)
    return {
        "device_id": entity_id,
        "room_id": room_id,
        "type": device_type,
        "name": friendly_name,
        "ha_entity_id": entity_id,
        "protocol": "Zigbee" if domain == "lock" else "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": status,
        "attributes": attrs,
    }

# ── Mock state store (simulates HA states) ──

_mock_devices: list[dict] = []
_mock_alerts: list[dict] = []
_alert_counter = 0


def _build_mock_devices():
    """Generate realistic mock device list matching actual HA entity naming."""
    global _mock_devices
    if _mock_devices:
        return
    idx = 0
    for room in ROOMS:
        ha_room = HA_ROOM_MAP.get(room["room_id"], room["room_id"])
        for tpl in DEVICE_TEMPLATES:
            idx += 1
            attrs = dict(tpl["attributes"])
            # 使用ha_entity_fn生成HA实体ID
            try:
                ha_entity_id = tpl["ha_entity_fn"](ha_room)
            except Exception:
                ha_entity_id = f"{tpl['type'].lower()}.{ha_room}"

            # 随机化状态
            if tpl["type"] == "Lock":
                attrs["battery_level"] = random.randint(60, 100)
                attrs["locked"] = True
            elif tpl["type"] == "AC":
                if "temp" not in ha_entity_id:
                    attrs["power"] = random.choice([True, False])
                    attrs["mode"] = "cool"
                else:
                    attrs["value"] = random.randint(24, 28)
            elif tpl["type"] == "Light":
                attrs["power"] = random.choice([True, False])
            elif tpl["type"] == "Curtain":
                attrs["position"] = random.choice(["open", "closed"])
                attrs["current_position"] = 100 if attrs["position"] == "open" else 0
            elif tpl["type"] == "Sensor":
                attrs["value"] = round(random.uniform(22, 28), 1)

            _mock_devices.append({
                "device_id": f"DEV{idx:04d}",
                "room_id": room["room_id"],
                "type": tpl["type"],
                "name": tpl["name_template"].format(room=room["name"]),
                "ha_entity_id": ha_entity_id,
                "protocol": tpl["protocol"],
                "slave_id": None,
                "sub_address": None,
                "status": random.choices(["Online", "Online", "Online", "Offline"], weights=[85, 10, 3, 2])[0],
                "attributes": attrs,
            })


def _get_device(device_id: str) -> Optional[dict]:
    _build_mock_devices()
    for d in _mock_devices:
        if d["device_id"] == device_id:
            return d
    return None


def _get_room_devices(room_id: str) -> list[dict]:
    _build_mock_devices()
    return [d for d in _mock_devices if d["room_id"] == room_id]


def _get_device_type_in_room(room_id: str, device_type: str) -> Optional[dict]:
    """Get first device of given type in a room (or for Light, return the list)."""
    devices = _get_room_devices(room_id)
    matches = [d for d in devices if d["type"] == device_type]
    return matches


# ── Public API ──


def is_mock_mode() -> bool:
    """Return True if no HA token is configured (mock mode)."""
    return not settings.ha_token


async def check_health() -> dict:
    """Check HA connectivity or mock health."""
    if is_mock_mode():
        return {"status": "ok", "mode": "mock", "device_count": len(_mock_devices) if _mock_devices else 30}
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/",
                headers=_ha_headers()
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "mode": "ha", "code": resp.status_code}
    except Exception as e:
        return {"status": "error", "mode": "ha", "message": str(e), "ha_url": settings.ha_url}


async def get_devices(room_id: Optional[str] = None, device_type: Optional[str] = None,
                      status_filter: Optional[str] = None) -> list[dict]:
    """Get all IoT devices, optionally filtered."""
    if is_mock_mode():
        _build_mock_devices()
        result = list(_mock_devices)
        if room_id:
            result = [d for d in result if d["room_id"] == room_id]
        if device_type:
            result = [d for d in result if d["type"] == device_type]
        if status_filter:
            result = [d for d in result if d["status"] == status_filter]
        return result

    # Real HA mode
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/states",
                headers=_ha_headers()
            )
            if resp.status_code != 200:
                return []
            ha_states = resp.json()
            # Filter to only entities belonging to our rooms
            our_ha_rooms = set(HA_ROOM_REVERSE.keys())
            devices = []
            for state in ha_states:
                entity_id = state.get("entity_id", "")
                dev_type = _ha_entity_to_type(entity_id)
                if not dev_type:
                    continue
                ha_room = _ha_entity_to_room(entity_id)
                if not ha_room:
                    continue  # Skip entities not in our room set
                if room_id and ha_room != room_id:
                    continue
                if device_type and dev_type != device_type:
                    continue
                devices.append(_ha_state_to_device(state))
            return devices
    except Exception:
        return []


async def get_device(device_id: str) -> Optional[dict]:
    """Get single device by ID (or HA entity_id in real mode)."""
    if is_mock_mode():
        return _get_device(device_id)
    # In real mode, query HA for the specific entity
    # device_id could be an internal ID or the HA entity_id itself
    ha_entity_id = device_id
    if not device_id.startswith(("switch.", "climate.", "cover.", "lock.", "sensor.", "input_boolean.")):
        # Try looking up internal ID mapping in mock data first
        dev = _get_device(device_id)
        if dev:
            ha_entity_id = dev.get("ha_entity_id", device_id)
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/states/{ha_entity_id}",
                headers=_ha_headers()
            )
            if resp.status_code == 200:
                return _ha_state_to_device(resp.json())
    except Exception:
        pass
    return _get_device(device_id)


async def control_device(device_id: str, action: str, params: Optional[dict] = None) -> dict:
    """Send a control command to a device.

    Actions: on, off, open, close, stop, temperature, volume, unlock, lock, cool, heat, fan, dry
    """
    if is_mock_mode():
        return _mock_control(device_id, action, params or {})
    return await _ha_control(device_id, action, params or {})


def _mock_control(device_id: str, action: str, params: dict) -> dict:
    device = _get_device(device_id)
    if not device:
        return {"success": False, "message": f"设备 {device_id} 不存在"}

    attrs = device["attributes"]
    old_state = dict(attrs)

    if device["type"] == "AC":
        if action == "off":
            attrs["mode"] = "off"
        elif action in ("cool", "heat", "fan", "dry", "auto"):
            attrs["mode"] = action
        elif action == "temperature":
            temp = params.get("temperature", 24)
            attrs["target_temperature"] = temp
            if attrs.get("mode") in (None, "off"):
                attrs["mode"] = "auto"
        elif action == "fan_speed":
            attrs["fan_speed"] = params.get("fan_speed", "auto")
    elif device["type"] == "Light":
        if action == "on":
            attrs["power"] = True
        elif action == "off":
            attrs["power"] = False
            attrs["power"] = True
    elif device["type"] == "Curtain":
        if action == "open":
            attrs["position"] = "open"
            attrs["current_position"] = 100
        elif action == "close":
            attrs["position"] = "closed"
            attrs["current_position"] = 0
        elif action == "stop":
            attrs["position"] = "open" if attrs.get("current_position", 0) > 50 else "closed"
    elif device["type"] == "Lock":
        if action == "unlock":
            attrs["locked"] = False
        elif action == "lock":
            attrs["locked"] = True
    elif device["type"] == "Speaker":
        if action == "on" or action == "play":
            attrs["playing"] = True
            if "volume" in params:
                attrs["volume"] = params["volume"]
            if "source" in params:
                attrs["source"] = params["source"]
        elif action == "off" or action == "pause":
            attrs["playing"] = False
        elif action == "volume":
            attrs["volume"] = params.get("volume", 30)
        elif action == "mute":
            attrs["volume"] = 0
            attrs["playing"] = False

    device["status"] = "Online"
    return {
        "success": True,
        "message": f"指令执行成功: {device['name']} → {action}",
        "device_id": device_id,
        "action": action,
        "old_state": old_state,
        "new_state": dict(attrs),
    }


async def _ha_control(device_id: str, action: str, params: dict) -> dict:
    """Control device via real HA REST API.
    In real HA mode, device_id is the HA entity_id (e.g. lock.baishawa_door).
    """
    # Try to find the device in mock DB for type info, fallback to entity_id as-is
    device = _get_device(device_id)
    ha_entity_id = device.get("ha_entity_id", device_id) if device else device_id
    device_type = device["type"] if device else _ha_entity_to_type(device_id) or "Unknown"

    # Special handling: all_lights → use switch.*_all_lights entity
    if action == "all_on":
        ha_room = ha_entity_id.split("_")[0] if "." in ha_entity_id else ""
        ha_entity_id = f"switch.{ha_room}_all_lights"
        service_data = {"domain": "switch", "service": "turn_on"}
    elif action == "all_off":
        ha_room = ha_entity_id.split("_")[0] if "." in ha_entity_id else ""
        ha_entity_id = f"switch.{ha_room}_all_lights"
        service_data = {"domain": "switch", "service": "turn_off"}
    else:
        service_data = _ha_build_service(device_type, action, params)

    if not service_data:
        return {"success": False, "message": f"不支持的动作: {device_type} → {action}"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.ha_url}/api/services/{service_data['domain']}/{service_data['service']}",
                headers=_ha_headers(),
                json={"entity_id": ha_entity_id, **service_data.get("data", {})},
            )
            if resp.status_code == 200:
                return {"success": True, "message": f"HA指令已发送: {action}", "device_id": device_id}
            return {"success": False, "message": f"HA返回错误({resp.status_code})", "device_id": device_id}
    except Exception as e:
        return {"success": False, "message": f"HA请求失败: {str(e)}", "device_id": device_id}


def _ha_headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.ha_token}",
        "Content-Type": "application/json",
    }


def _ha_build_service(device_type: str, action: str, params: dict) -> Optional[dict]:
    """Map ERP action to HA service call.
    Uses actual HA entity types per v1.1 spec:
    - switch.*_relay_chN for lights
    - climate.* for AC
    - cover.*_curtain for curtains
    - lock.*_door for locks
    """
    mapping = {
        # ── AC (climate.*) ──
        ("AC", "on"): {"domain": "climate", "service": "turn_on"},
        ("AC", "off"): {"domain": "climate", "service": "turn_off"},
        ("AC", "cool"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "cool"}},
        ("AC", "heat"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "heat"}},
        ("AC", "fan_only"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "fan_only"}},
        ("AC", "auto"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "auto"}},
        ("AC", "temperature"): {"domain": "climate", "service": "set_temperature",
                                "data": {"temperature": params.get("temperature", 24)}},
        # ── Light (switch.*_relay_chN) ──
        ("Light", "on"): {"domain": "switch", "service": "turn_on"},
        ("Light", "off"): {"domain": "switch", "service": "turn_off"},
        # ── Curtain (cover.*_curtain) ──
        ("Curtain", "open"): {"domain": "cover", "service": "open_cover"},
        ("Curtain", "close"): {"domain": "cover", "service": "close_cover"},
        ("Curtain", "stop"): {"domain": "cover", "service": "stop_cover"},
        ("Curtain", "position"): {"domain": "cover", "service": "set_cover_position",
                                   "data": {"position": params.get("position", 50)}},
        # ── Lock (lock.*_door) ──
        ("Lock", "unlock"): {"domain": "lock", "service": "unlock"},
        ("Lock", "lock"): {"domain": "lock", "service": "lock"},
    }
    return mapping.get((device_type, action))


async def activate_scene(room_id: str, scene_name: str) -> dict:
    """Activate a scene for a specific room.

    Real HA mode: Toggle input_boolean.{room}_scene_{scene}.
    Mock mode: Execute individual device commands.
    """
    scene = None
    for s in SCENES:
        if s["name"] == scene_name or s["scene_id"] == scene_name:
            scene = s
            break
    if not scene:
        return {"success": False, "message": f"场景不存在: {scene_name}"}

    # Real HA mode: use input_boolean
    if not is_mock_mode():
        ha_room = HA_ROOM_MAP.get(room_id, room_id)
        scene_key = scene["name"].lower()
        entity_id = f"input_boolean.{ha_room}_scene_{scene_key}"
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{settings.ha_url}/api/services/input_boolean/turn_on",
                    headers=headers,
                    json={"entity_id": entity_id},
                )
                if resp.status_code == 200:
                    return {
                        "success": True,
                        "scene": scene["name"],
                        "scene_label": scene["label"],
                        "room_id": room_id,
                        "message": f"场景「{scene['label']}」已通过HA激活",
                    }
                return {"success": False, "message": f"HA场景激活失败: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"HA请求失败: {str(e)}"}

    # Mock mode: execute individual device commands
    results = []
    for rule in scene["rules"]:
        dev_type = rule["device_type"]
        action = rule["action"].lower()
        action_map = {"On": "on", "Off": "off", "Unlock": "unlock", "Lock": "lock",
                      "Open": "open", "Close": "close", "Temperature": "temperature",
                      "Volume": "volume", "Mute": "mute", "Stop": "stop"}
        mapped_action = action_map.get(rule["action"], rule["action"].lower())

        devices = _get_device_type_in_room(room_id, dev_type)
        if not devices:
            continue
        if isinstance(devices, list):
            for dev in devices:
                r = await control_device(dev["device_id"], mapped_action, rule["params"])
                results.append(r)
        else:
            r = await control_device(devices["device_id"], mapped_action, rule["params"])
            results.append(r)

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "success": success_count > 0,
        "scene": scene["name"],
        "scene_label": scene["label"],
        "room_id": room_id,
        "total_steps": len(scene["rules"]),
        "success_count": success_count,
        "results": results,
    }


async def init_room(room_id: str) -> dict:
    """Initialize/reset a room: all off, curtains closed, door locked.
    Real HA mode uses input_boolean.*_init. Mock mode controls each device.
    """
    if not is_mock_mode():
        ha_room = HA_ROOM_MAP.get(room_id, room_id)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    f"{settings.ha_url}/api/services/input_boolean/turn_on",
                    headers=_ha_headers(),
                    json={"entity_id": f"input_boolean.{ha_room}_init"},
                )
                if resp.status_code == 200:
                    return {"success": True, "room_id": room_id, "message": "房间已初始化复位"}
                return {"success": False, "room_id": room_id, "message": f"HA返回错误: {resp.status_code}"}
        except Exception as e:
            return {"success": False, "room_id": room_id, "message": str(e)}

    # Mock mode: turn everything off
    devices = _get_room_devices(room_id)
    results = []
    for dev in devices:
        if dev["type"] == "Light" and dev["attributes"].get("power"):
            results.append(_mock_control(dev["device_id"], "off", {}))
        elif dev["type"] == "AC" and dev["attributes"].get("mode") != "off":
            results.append(_mock_control(dev["device_id"], "off", {}))
        elif dev["type"] == "Curtain" and dev["attributes"].get("position") != "closed":
            results.append(_mock_control(dev["device_id"], "close", {}))
        elif dev["type"] == "Lock" and not dev["attributes"].get("locked"):
            results.append(_mock_control(dev["device_id"], "lock", {}))
    return {"success": True, "room_id": room_id, "actions": len(results), "results": results}


async def get_scenes() -> list[dict]:
    return SCENES


async def get_alerts(room_id: Optional[str] = None, severity: Optional[str] = None,
                     status_filter: Optional[str] = None) -> list[dict]:
    """Get IoT alerts."""
    if is_mock_mode():
        _generate_mock_alerts()
        result = list(_mock_alerts)
        if room_id:
            result = [a for a in result if a["room_id"] == room_id]
        if severity:
            result = [a for a in result if a["severity"] == severity]
        if status_filter:
            result = [a for a in result if a["status"] == status_filter]
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)
    return []


def _generate_mock_alerts():
    """Generate/refresh mock alerts matching current device states."""
    global _mock_alerts, _alert_counter
    if _mock_alerts:
        return
    _build_mock_devices()

    offline = [d for d in _mock_devices if d["status"] == "Offline"]
    for dev in offline[:3]:
        _alert_counter += 1
        room_name = next((r["name"] for r in ROOMS if r["room_id"] == dev["room_id"]), dev["room_id"])
        _mock_alerts.append({
            "alert_id": f"ALT{_alert_counter:04d}",
            "device_id": dev["device_id"],
            "room_id": dev["room_id"],
            "room_name": room_name,
            "device_type": dev["type"],
            "device_code": dev["device_id"],
            "severity": "Warning",
            "type": "Offline",
            "message": f"{dev['name']} 离线",
            "detail": f"{room_name}的{dev['name']}({dev['device_id']})通信超时，可能原因：网络断开、模块断电或RS485线路故障。",
            "status": "Unresolved",
            "assigned_role": "技术",
            "assigned_name": "阿强",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    # Low battery alerts
    for dev in _mock_devices:
        if dev["type"] == "Lock" and dev["attributes"].get("battery_level", 100) < 70:
            _alert_counter += 1
            room_name = next((r["name"] for r in ROOMS if r["room_id"] == dev["room_id"]), dev["room_id"])
            _mock_alerts.append({
                "alert_id": f"ALT{_alert_counter:04d}",
                "device_id": dev["device_id"],
                "room_id": dev["room_id"],
                "room_name": room_name,
                "device_type": dev["type"],
                "device_code": dev["device_id"],
                "severity": "Info",
                "type": "BatteryLow",
                "message": f"{dev['name']} 电量不足 ({dev['attributes']['battery_level']}%)",
                "detail": f"{room_name}的{dev['name']}当前电量{dev['attributes']['battery_level']}%，建议及时更换电池。",
                "status": random.choices(["Unresolved", "Acknowledged", "Resolved"], weights=[3, 3, 4])[0],
                "assigned_role": "客服",
                "assigned_name": "客服小美",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

    _mock_alerts.sort(key=lambda x: x.get("created_at", ""), reverse=True)


async def get_stats() -> dict:
    """Get IoT device stats (total, online, offline, fault, alert count)."""
    if is_mock_mode():
        _build_mock_devices()
        total = len(_mock_devices)
        online = sum(1 for d in _mock_devices if d["status"] == "Online")
        offline = sum(1 for d in _mock_devices if d["status"] == "Offline")
        fault = sum(1 for d in _mock_devices if d["status"] == "Fault")
        _generate_mock_alerts()
        unresolved = sum(1 for a in _mock_alerts if a["status"] == "Unresolved")
        return {
            "total": total,
            "online": online,
            "offline": offline,
            "fault": fault,
            "online_rate": round(online / total * 100, 1) if total else 0,
            "unresolved_alerts": unresolved,
            "total_alerts": len(_mock_alerts),
        }

    devices = await get_devices()
    total = len(devices)
    online = sum(1 for d in devices if d.get("status") == "Online")
    offline = sum(1 for d in devices if d.get("status") == "Offline")
    fault = sum(1 for d in devices if d.get("status") == "Fault")
    return {
        "total": total,
        "online": online,
        "offline": offline,
        "fault": fault,
        "online_rate": round(online / total * 100, 1) if total else 0,
        "unresolved_alerts": 0,
        "total_alerts": 0,
    }


# ── HA entity mapping helpers ──

def _ha_entity_to_type(entity_id: str) -> Optional[str]:
    """Map HA entity_id to ERP device type.
    实际HA实体类型多样化，根据domain+name综合判断。
    """
    domain = entity_id.split(".")[0] if "." in entity_id else ""
    entity_name = entity_id.split(".")[1] if "." in entity_id else ""

    # 明确映射
    if domain == "lock":
        return "Lock"
    if domain == "climate":
        return "AC"
    if domain == "cover":
        return "Curtain"
    if domain == "switch":
        return "Light"  # 物理继电器开关=灯光
    if domain == "sensor":
        # 温度/湿度传感器
        if "shi_wen" in entity_name or "temp" in entity_name:
            return "Sensor"
        if "wen_kong" in entity_name:
            return "AC"  # 温控状态（空调）
        return "Sensor"
    if domain == "input_boolean":
        if entity_name.startswith("ac_"):
            return "AC"  # ac_dacha_power
        if entity_name.startswith("sim_"):
            return "Light"  # sim_dacha_main = 灯光模拟
        if entity_name.startswith("init_"):
            return "System"  # 初始化场景
        return "Light"
    if domain == "input_number":
        if "amplifier_volume" in entity_name:
            return "Speaker"
        if "ac_" in entity_name and "temp" in entity_name:
            return "AC"
        return "Sensor"
    if domain == "input_select":
        if "amplifier_source" in entity_name:
            return "Speaker"
        return "Speaker"
    if domain == "automation":
        return "System"
    return None


def _ha_entity_to_room(entity_id: str) -> Optional[str]:
    """Extract room_id from HA entity_id using substring matching.
    HA实体命名不规则，用包含匹配：
      *dacha* → RM004, *zhong* → RM002, *xiao* → RM003, *meeting* → RM001, *exhibition* → RM005
    """
    eid_lower = entity_id.lower()
    # 按完整度排序：先匹配更精确的
    if "exhibition" in eid_lower:
        return "RM005"
    if "meeting" in eid_lower:
        return "RM001"
    if "dacha" in eid_lower:
        return "RM004"
    if "zhong" in eid_lower and "xiao" not in eid_lower:
        # zhong_cha_shi, zhong 但排除 xiao_zhong 之类
        return "RM002"
    if "xiao" in eid_lower:
        # xiao_cha_shi, xiao
        return "RM003"
    return None


def _ha_state_to_device(state: dict) -> dict:
    """Convert HA API state object to our device format."""
    entity_id = state.get("entity_id", "")
    attrs = dict(state.get("attributes", {}))
    device_type = _ha_entity_to_type(entity_id)
    room_id = _ha_entity_to_room(entity_id)
    domain = entity_id.split(".")[0]
    entity_name = entity_id.split(".")[1] if "." in entity_id else ""

    state_val = state.get("state", "")
    status = "Online" if state_val != "unavailable" else "Offline"

    if device_type == "Lock":
        attrs["locked"] = state_val == "locked"
        attrs["battery_level"] = attrs.get("battery_level", 85)
    elif device_type == "AC":
        attrs["mode"] = state_val
        attrs["temperature"] = attrs.get("current_temperature", 26)
        attrs["target_temperature"] = attrs.get("temperature", 24)
    elif device_type == "Light":
        attrs["power"] = state_val == "on"
        # Extract channel number from entity name
        if "all_lights" in entity_name:
            attrs["is_all_lights"] = True
            attrs["channel"] = 0
        else:
            ch = entity_name.split("_ch")[-1]
            attrs["channel"] = int(ch) if ch.isdigit() else None
    elif device_type == "Curtain":
        attrs["position"] = state_val
        attrs["current_position"] = attrs.get("current_position", 0)
    elif device_type == "Sensor":
        unit = attrs.get("unit_of_measurement", "")
        attrs["value"] = float(state_val) if state_val.replace(".", "").replace("-", "").isdigit() else state_val
        attrs["unit"] = unit

    # Build a friendly name from entity
    friendly_name = attrs.get("friendly_name", entity_id)
    if room_id:
        room_name = next((r["name"] for r in ROOMS if r["room_id"] == room_id), room_id)

    return {
        "device_id": entity_id,
        "room_id": room_id or "",
        "type": device_type or "Unknown",
        "name": friendly_name,
        "ha_entity_id": entity_id,
        "protocol": "Zigbee" if domain == "lock" else "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": status,
        "attributes": attrs,
    }
