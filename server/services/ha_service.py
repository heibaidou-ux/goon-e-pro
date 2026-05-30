"""
Home Assistant REST API client + Mock data layer for IoT integration.
When HA_TOKEN is set, communicates with real HA at HA_URL.
Otherwise uses realistic mock data matching the 5-room 盈隆店 setup.
"""
import json
import random
import httpx
from datetime import datetime
from typing import Optional

from config import settings

# ── Mock device data: 5 rooms × (2 lights, 1 AC, 1 curtain, relay, audio, lock) ──

ROOMS = [
    {"room_id": "RM001", "name": "大会议室", "type": "MeetingRoom"},
    {"room_id": "RM002", "name": "中茶室A", "type": "TeaRoom"},
    {"room_id": "RM003", "name": "中茶室B", "type": "TeaRoom"},
    {"room_id": "RM004", "name": "大茶室C", "type": "TeaRoom"},
    {"room_id": "RM005", "name": "展厅", "type": "Exhibition"},
]

DEVICE_TEMPLATES = [
    # Lock
    {"type": "Lock", "name_template": "{room}门锁", "protocol": "Zigbee", "slave_id": None, "sub_address": None,
     "ha_entity_id_template": "lock.{room_id}_door", "attributes": {"battery_level": 85, "locked": True}},
    # AC
    {"type": "AC", "name_template": "{room}空调", "protocol": "Modbus", "slave_base": 21, "sub_address": None,
     "ha_entity_id_template": "climate.{room_id}_ac", "attributes": {"temperature": 26, "mode": "auto", "fan_speed": "auto", "target_temperature": 24}},
    # Light 1 (main)
    {"type": "Light", "name_template": "{room}主灯", "protocol": "Modbus", "slave_base": 1, "sub_address": 1,
     "ha_entity_id_template": "light.{room_id}_light_main", "attributes": {"brightness": 80, "color_temp": 4000, "power": False}},
    # Light 2 (secondary)
    {"type": "Light", "name_template": "{room}辅灯", "protocol": "Modbus", "slave_base": 1, "sub_address": 2,
     "ha_entity_id_template": "light.{room_id}_light_secondary", "attributes": {"brightness": 60, "color_temp": 3500, "power": False}},
    # Curtain
    {"type": "Curtain", "name_template": "{room}窗帘", "protocol": "Modbus", "slave_base": 31, "sub_address": None,
     "ha_entity_id_template": "cover.{room_id}_curtain", "attributes": {"position": "closed", "current_position": 0}},
    # Speaker
    {"type": "Speaker", "name_template": "{room}音响", "protocol": "IPAudio", "slave_id": None, "sub_address": None,
     "ha_entity_id_template": "media_player.{room_id}_speaker", "attributes": {"volume": 30, "playing": False, "source": "空闲"}},
]

ROOM_SLAVE_MAP = {
    "RM001": {"relay": 1, "ac": 21, "curtain": 31},
    "RM002": {"relay": 2, "ac": 22, "curtain": 32},
    "RM003": {"relay": 3, "ac": 23, "curtain": 33},
    "RM004": {"relay": 4, "ac": 24, "curtain": 34},
    "RM005": {"relay": 5, "ac": 24, "curtain": 34},  # 展厅 shares with RM004
}

# ── Scenes ──

SCENES = [
    {"scene_id": "SCN_WELCOME", "name": "Welcome", "label": "迎宾模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Lock", "action": "Unlock", "params": {}},
         {"sequence": 2, "device_type": "Light", "action": "On", "params": {"brightness": 80, "color_temp": 3500}},
         {"sequence": 3, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 4, "device_type": "AC", "action": "Temperature", "params": {"temperature": 24}},
         {"sequence": 5, "device_type": "Speaker", "action": "On", "params": {"volume": 30, "source": "背景音乐"}},
     ]},
    {"scene_id": "SCN_TEA", "name": "TeaSession", "label": "品茶模式", "trigger_type": "Manual",
     "applicable_room_types": ["TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "On", "params": {"brightness": 60, "color_temp": 3000}},
         {"sequence": 2, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 25}},
         {"sequence": 4, "device_type": "Speaker", "action": "On", "params": {"volume": 25, "source": "古筝曲"}},
     ]},
    {"scene_id": "SCN_MEETING", "name": "Meeting", "label": "会议模式", "trigger_type": "Manual",
     "applicable_room_types": ["MeetingRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "On", "params": {"brightness": 90, "color_temp": 5000}},
         {"sequence": 2, "device_type": "Curtain", "action": "Open", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 24}},
     ]},
    {"scene_id": "SCN_KARAOKE", "name": "Karaoke", "label": "K歌模式", "trigger_type": "Manual",
     "applicable_room_types": ["TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "On", "params": {"brightness": 30, "color_temp": 2500}},
         {"sequence": 2, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 22}},
         {"sequence": 4, "device_type": "Speaker", "action": "On", "params": {"volume": 60, "source": "K歌"}},
     ]},
    {"scene_id": "SCN_ENERGY_SAVE", "name": "EnergySave", "label": "节能模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom", "Exhibition"],
     "rules": [
         {"sequence": 1, "device_type": "Light", "action": "Off", "params": {}},
         {"sequence": 2, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 3, "device_type": "AC", "action": "Temperature", "params": {"temperature": 26}},
         {"sequence": 4, "device_type": "Speaker", "action": "Off", "params": {}},
     ]},
    {"scene_id": "SCN_CHECKOUT", "name": "Checkout", "label": "退房模式", "trigger_type": "Auto",
     "applicable_room_types": ["MeetingRoom", "TeaRoom", "Exhibition"],
     "rules": [
         {"sequence": 1, "device_type": "AC", "action": "Off", "params": {}},
         {"sequence": 2, "device_type": "Light", "action": "Off", "params": {}},
         {"sequence": 3, "device_type": "Curtain", "action": "Close", "params": {}},
         {"sequence": 4, "device_type": "Speaker", "action": "Off", "params": {}},
         {"sequence": 5, "device_type": "Lock", "action": "Lock", "params": {}},
     ]},
    {"scene_id": "SCN_PREOPEN", "name": "PreOpen", "label": "预开模式", "trigger_type": "Schedule",
     "applicable_room_types": ["MeetingRoom", "TeaRoom"],
     "rules": [
         {"sequence": 1, "device_type": "AC", "action": "Temperature", "params": {"temperature": 24}},
         {"sequence": 2, "device_type": "Speaker", "action": "On", "params": {"volume": 15, "source": "轻音乐"}},
     ]},
]

# ── Mock state store (simulates HA states) ──

_mock_devices: list[dict] = []
_mock_alerts: list[dict] = []
_alert_counter = 0


def _build_mock_devices():
    """Generate realistic mock device list for all 5 rooms."""
    global _mock_devices
    if _mock_devices:
        return
    idx = 0
    for room in ROOMS:
        sm = ROOM_SLAVE_MAP[room["room_id"]]
        for tpl in DEVICE_TEMPLATES:
            idx += 1
            attrs = dict(tpl["attributes"])
            # Randomize some values for realism
            if tpl["type"] == "Lock":
                attrs["battery_level"] = random.randint(60, 100)
                attrs["locked"] = True
            elif tpl["type"] == "AC":
                attrs["temperature"] = random.randint(24, 28)
                attrs["target_temperature"] = 24
            elif tpl["type"] == "Light":
                attrs["power"] = random.choice([True, False])
            elif tpl["type"] == "Curtain":
                attrs["position"] = random.choice(["open", "closed"])
                attrs["current_position"] = 100 if attrs["position"] == "open" else 0

            slave_id = tpl.get("slave_base")
            if slave_id:
                slave_id = sm.get(tpl["type"].lower(), slave_id)

            _mock_devices.append({
                "device_id": f"DEV{idx:04d}",
                "room_id": room["room_id"],
                "type": tpl["type"],
                "name": tpl["name_template"].format(room=room["name"]),
                "ha_entity_id": tpl["ha_entity_id_template"].format(room_id=room["room_id"]),
                "protocol": tpl["protocol"],
                "slave_id": slave_id,
                "sub_address": tpl["sub_address"],
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
                headers={"Authorization": f"Bearer {settings.ha_token}"}
            )
            return {"status": "ok" if resp.status_code == 200 else "error", "mode": "ha", "code": resp.status_code}
    except Exception as e:
        return {"status": "error", "mode": "ha", "message": str(e)}


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
                headers={"Authorization": f"Bearer {settings.ha_token}"}
            )
            if resp.status_code != 200:
                return []
            ha_states = resp.json()
            # Map HA states to our device format
            devices = []
            for state in ha_states:
                entity_id = state.get("entity_id", "")
                dev_type = _ha_entity_to_type(entity_id)
                if not dev_type:
                    continue
                ha_room = _ha_entity_to_room(entity_id)
                if room_id and ha_room != room_id:
                    continue
                if device_type and dev_type != device_type:
                    continue
                devices.append(_ha_state_to_device(state))
            return devices
    except Exception:
        return []


async def get_device(device_id: str) -> Optional[dict]:
    """Get single device by ID."""
    if is_mock_mode():
        return _get_device(device_id)
    # In real mode, look up from HA
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.ha_url}/api/states",
                headers={"Authorization": f"Bearer {settings.ha_token}"}
            )
            if resp.status_code != 200:
                return None
            for state in resp.json():
                if state.get("attributes", {}).get("device_id") == device_id or \
                   state.get("entity_id") == device_id:
                    return _ha_state_to_device(state)
    except Exception:
        pass
    # Fallback to mock
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
            if "brightness" in params:
                attrs["brightness"] = params["brightness"]
            if "color_temp" in params:
                attrs["color_temp"] = params["color_temp"]
        elif action == "off":
            attrs["power"] = False
        elif action == "brightness":
            attrs["brightness"] = params.get("brightness", 80)
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
    """Control device via real HA REST API."""
    device = _get_device(device_id)
    if not device:
        return {"success": False, "message": f"设备 {device_id} 不存在"}
    ha_entity_id = device.get("ha_entity_id")
    if not ha_entity_id:
        return {"success": False, "message": f"设备 {device_id} 未映射到HA实体"}

    service_data = _ha_build_service(device["type"], action, params)
    if not service_data:
        return {"success": False, "message": f"不支持的动作: {device['type']} → {action}"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{settings.ha_url}/api/services/{service_data['domain']}/{service_data['service']}",
                headers={
                    "Authorization": f"Bearer {settings.ha_token}",
                    "Content-Type": "application/json",
                },
                json={"entity_id": ha_entity_id, **service_data.get("data", {})},
            )
            if resp.status_code == 200:
                return {"success": True, "message": f"HA指令已发送: {action}", "device_id": device_id}
            return {"success": False, "message": f"HA返回错误: {resp.status_code}", "device_id": device_id}
    except Exception as e:
        return {"success": False, "message": f"HA请求失败: {str(e)}", "device_id": device_id}


def _ha_build_service(device_type: str, action: str, params: dict) -> Optional[dict]:
    """Map ERP action to HA service call."""
    mapping = {
        ("AC", "off"): {"domain": "climate", "service": "turn_off"},
        ("AC", "cool"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "cool"}},
        ("AC", "heat"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "heat"}},
        ("AC", "auto"): {"domain": "climate", "service": "set_hvac_mode", "data": {"hvac_mode": "auto"}},
        ("AC", "temperature"): {"domain": "climate", "service": "set_temperature",
                                "data": {"temperature": params.get("temperature", 24)}},
        ("Light", "on"): {"domain": "homeassistant", "service": "turn_on"},
        ("Light", "off"): {"domain": "homeassistant", "service": "turn_off"},
        ("Curtain", "open"): {"domain": "cover", "service": "open_cover"},
        ("Curtain", "close"): {"domain": "cover", "service": "close_cover"},
        ("Curtain", "stop"): {"domain": "cover", "service": "stop_cover"},
        ("Lock", "unlock"): {"domain": "lock", "service": "open"},
        ("Lock", "lock"): {"domain": "lock", "service": "lock"},
        ("Speaker", "on"): {"domain": "media_player", "service": "turn_on"},
        ("Speaker", "off"): {"domain": "media_player", "service": "turn_off"},
        ("Speaker", "volume"): {"domain": "media_player", "service": "volume_set",
                                "data": {"volume_level": params.get("volume", 30) / 100}},
        ("Speaker", "play"): {"domain": "media_player", "service": "media_play"},
        ("Speaker", "pause"): {"domain": "media_player", "service": "media_pause"},
    }
    return mapping.get((device_type, action))


async def activate_scene(room_id: str, scene_name: str) -> dict:
    """Activate a scene for a specific room.

    Returns list of control results for each step.
    """
    scene = None
    for s in SCENES:
        if s["name"] == scene_name or s["scene_id"] == scene_name:
            scene = s
            break
    if not scene:
        return {"success": False, "message": f"场景不存在: {scene_name}"}

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
    """Map HA entity_id prefix to our device type."""
    domain = entity_id.split(".")[0] if "." in entity_id else ""
    mapping = {
        "lock": "Lock", "climate": "AC", "light": "Light",
        "cover": "Curtain", "media_player": "Speaker", "sensor": "Sensor",
    }
    return mapping.get(domain)


def _ha_entity_to_room(entity_id: str) -> Optional[str]:
    """Extract room_id from HA entity_id (e.g. climate.rm001_ac → RM001)."""
    parts = entity_id.split(".")[1] if "." in entity_id else ""
    room_part = parts.split("_")[0] if "_" in parts else ""
    return room_part.upper() if room_part else None


def _ha_state_to_device(state: dict) -> dict:
    """Convert HA API state object to our device format."""
    entity_id = state.get("entity_id", "")
    attrs = state.get("attributes", {})
    device_type = _ha_entity_to_type(entity_id)
    room_id = _ha_entity_to_room(entity_id)
    domain = entity_id.split(".")[0]

    state_val = state.get("state", "")
    if device_type == "Lock":
        status = "Online" if state_val in ("locked", "unlocked", "opening", "jammed") else "Offline"
        attrs["locked"] = state_val == "locked"
    elif device_type == "AC":
        status = "Online" if state_val != "unavailable" else "Offline"
        attrs["mode"] = state_val
        attrs["temperature"] = attrs.get("current_temperature", 26)
        attrs["target_temperature"] = attrs.get("temperature", 24)
    elif device_type == "Light":
        status = "Online" if state_val != "unavailable" else "Offline"
        attrs["power"] = state_val == "on"
        attrs["brightness"] = attrs.get("brightness", 100)
    elif device_type == "Curtain":
        status = "Online" if state_val != "unavailable" else "Offline"
        attrs["position"] = state_val
        attrs["current_position"] = attrs.get("current_position", 0)
    elif device_type == "Speaker":
        status = "Online" if state_val != "unavailable" else "Offline"
        attrs["playing"] = state_val == "playing"
        attrs["volume"] = round(attrs.get("volume_level", 0) * 100)
    else:
        status = "Online" if state_val != "unavailable" else "Offline"

    return {
        "device_id": entity_id,
        "room_id": room_id or "",
        "type": device_type,
        "name": attrs.get("friendly_name", entity_id),
        "ha_entity_id": entity_id,
        "protocol": "Zigbee" if domain == "lock" else "Modbus",
        "slave_id": None,
        "sub_address": None,
        "status": status,
        "attributes": attrs,
    }
