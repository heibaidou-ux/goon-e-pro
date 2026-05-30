from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, func
from database import Base


class IoTDevice(Base):
    __tablename__ = "iot_devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(50), unique=True, nullable=False, index=True)
    room_id = Column(String(20), nullable=False, index=True)
    type = Column(String(30), nullable=False)  # Lock, AC, Light, Curtain, Speaker, Sensor, Relay
    name = Column(String(100), nullable=False)
    ha_entity_id = Column(String(100))  # Home Assistant entity_id
    protocol = Column(String(20), default="Modbus")  # Modbus, Zigbee, IPAudio, WiFi
    slave_id = Column(Integer)  # Modbus slave ID
    sub_address = Column(Integer)  # For relay modules: which relay output
    status = Column(String(20), default="Offline")  # Online, Offline, Fault, Maintenance
    attributes = Column(Text)  # JSON
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class IoTAlert(Base):
    __tablename__ = "iot_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(30), unique=True, nullable=False, index=True)
    device_id = Column(String(50), ForeignKey("iot_devices.device_id"))
    room_id = Column(String(20))
    device_type = Column(String(30))
    severity = Column(String(20), default="Warning")  # Error, Warning, Info
    type = Column(String(50))  # Offline, BatteryLow, CommError
    message = Column(String(300))
    detail = Column(Text)
    status = Column(String(20), default="Unresolved")  # Unresolved, Acknowledged, Resolved
    assigned_role = Column(String(20))  # 客服, 技术
    assigned_name = Column(String(50))
    handling_method = Column(String(100))
    handling_note = Column(Text)
    acknowledged_at = Column(String(30))
    resolved_at = Column(String(30))
    resolved_by = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class IoTScene(Base):
    __tablename__ = "iot_scenes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scene_id = Column(String(30), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)  # Welcome, TeaSession, etc.
    label = Column(String(100))
    trigger_type = Column(String(20), default="Manual")  # Auto, Manual, Schedule
    applicable_room_types = Column(Text)  # JSON array
    rules = Column(Text)  # JSON array of {device_type, action, params}
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
