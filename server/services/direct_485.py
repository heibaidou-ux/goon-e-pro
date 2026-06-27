"""
Modbus RTU over TCP — 485直连网关服务

通过FRP隧道（localhost:7003）直接与茶室485总线通信，
绕过HA REST API实现关键操作的低延迟控制。

架构:
  ERP (VPS) → localhost:7003 (FRP) → M710Q → USB-485 → 485总线 → 设备

支持设备:
  - 聚英 JY-DAM0808D 8路继电器（FC05线圈控制）
  - 盈隆温控面板（FC03读/FC06写寄存器）

485设备地址表:
  8路继电器: 会议室0x01, 小茶室0x02, 中茶室0x03, 大茶室0x04
  温控面板:  会议室0x3C, 小茶室0x3D, 中茶室0x3E, 大茶室0x3F
  窗帘电机:  小茶室0x0B, 中茶室0x0C-0x0E, 大茶室0x0F-0x11
"""
import asyncio
import logging
import struct
from typing import Optional

from config import settings

logger = logging.getLogger("gaoan.erp.direct485")

# ── 485地址映射 ──
RELAY_ADDR = {
    "fengshali": 0x01,   # 会议室
    "feilengcui": 0x02,  # 小茶室
    "bulage": 0x03,      # 中茶室
    "baishawa": 0x04,    # 大茶室
}

THERMOSTAT_ADDR = {
    "fengshali": 0x3C,
    "feilengcui": 0x3D,
    "bulage": 0x3E,
    "baishawa": 0x3F,
}

# 通道号映射（HA实体 → 继电器通道号）
RELAY_CHANNEL_MAP = {
    "ch1": 0, "ch2": 1, "ch3": 2, "ch4": 3,
    "ch5": 4, "ch6": 5, "ch7": 6, "ch8": 7,
    "relay_ch1": 0, "relay_ch2": 1, "relay_ch3": 2, "relay_ch4": 3,
    "relay_ch5": 4, "relay_ch6": 5, "relay_ch7": 6, "relay_ch8": 7,
}

# ── 配置 ──
GATEWAY_HOST = settings.direct_485_host
GATEWAY_PORT = settings.direct_485_port
TIMEOUT = 3.0  # 单次485命令超时（秒）
INTER_CMD_DELAY = 0.05  # 命令间最小间隔（50ms，盈隆协议要求）

# ── CRC16-Modbus ──

def _crc16(data: bytes) -> bytes:
    """计算Modbus CRC16（poly 0xA001, init 0xFFFF, little-endian）。"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack("<H", crc)


def _build_frame(addr: int, func: int, data: bytes) -> bytes:
    """构建Modbus RTU帧 + CRC16。"""
    frame = bytes([addr, func]) + data
    return frame + _crc16(frame)


def _parse_response(resp: bytes, expected_func: int) -> Optional[bytes]:
    """解析Modbus RTU响应，返回数据部分。"""
    if len(resp) < 5:
        logger.warning(f"响应过短: {len(resp)} bytes")
        return None

    recv_addr = resp[0]
    recv_func = resp[1]

    # 检查错误响应
    if recv_func & 0x80:
        error_code = resp[2] if len(resp) > 2 else 0
        error_msgs = {1: "CRC错误", 2: "操作错误", 3: "只读", 4: "寄存器不存在", 5: "无效操作"}
        logger.warning(f"Modbus错误响应: addr={recv_addr:#x}, func={recv_func:#x}, code={error_code} ({error_msgs.get(error_code, '未知')})")
        return None

    if recv_func != expected_func:
        logger.warning(f"功能码不匹配: 期望{expected_func:#x}, 收到{recv_func:#x}")
        return None

    # 盈隆协议：2字节数据长度（非标准1字节）
    data_len = struct.unpack(">H", resp[2:4])[0] if len(resp) >= 4 else 0
    return resp[4:4 + data_len] if data_len > 0 else None


# ── TCP会话 ──

class ModbusSession:
    """Modbus RTU over TCP 会话（短连接，每次操作建连）。"""

    def __init__(self, host: str = GATEWAY_HOST, port: int = GATEWAY_PORT, timeout: float = TIMEOUT):
        self.host = host
        self.port = port
        self.timeout = timeout

    async def _send_frame(self, frame: bytes, resp_len: int = 256) -> Optional[bytes]:
        """发送Modbus帧并读取响应。"""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=self.timeout,
            )
        except (ConnectionRefusedError, OSError, asyncio.TimeoutError) as e:
            logger.warning(f"485网关连接失败 {self.host}:{self.port} → {e}")
            return None

        try:
            writer.write(frame)
            await writer.drain()

            resp = await asyncio.wait_for(reader.read(resp_len), timeout=self.timeout)
            return resp
        except asyncio.TimeoutError:
            logger.warning("485响应超时")
            return None
        except Exception as e:
            logger.warning(f"485通信异常: {e}")
            return None
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def read_coils(self, addr: int, start: int = 0, count: int = 8) -> Optional[list[bool]]:
        """FC01: 读取线圈状态（继电器各通道）。"""
        data = struct.pack(">HH", start, count)
        frame = _build_frame(addr, 0x01, data)
        resp = await self._send_frame(frame, resp_len=count + 5)
        if not resp or len(resp) < 4:
            return None
        # 标准Modbus响应: [addr][0x01][byte_count][data...][CRC]
        byte_count = resp[2]
        coil_bytes = resp[3:3 + byte_count]
        coils = []
        for i in range(count):
            byte_idx = i // 8
            bit_idx = i % 8
            if byte_idx < len(coil_bytes):
                coils.append(bool(coil_bytes[byte_idx] & (1 << bit_idx)))
            else:
                coils.append(False)
        return coils

    async def write_coil(self, addr: int, channel: int, state: bool) -> bool:
        """FC05: 写单个线圈（开关继电器通道）。"""
        value = 0xFF00 if state else 0x0000
        data = struct.pack(">HH", channel, value)
        frame = _build_frame(addr, 0x05, data)
        resp = await self._send_frame(frame, resp_len=8)
        return resp is not None and len(resp) >= 8

    async def write_multiple_coils(self, addr: int, states: list[bool]) -> bool:
        """FC15: 写多个线圈（批量设置继电器）。"""
        byte_count = (len(states) + 7) // 8
        coil_bytes = bytearray(byte_count)
        for i, s in enumerate(states):
            if s:
                coil_bytes[i // 8] |= (1 << (i % 8))
        data = struct.pack(">HHB", 0, len(states), byte_count) + bytes(coil_bytes)
        frame = _build_frame(addr, 0x0F, data)
        resp = await self._send_frame(frame, resp_len=8)
        return resp is not None and len(resp) >= 8

    async def read_holding_registers(self, addr: int, reg: int, count: int = 1) -> Optional[list[int]]:
        """FC03: 读保持寄存器（温控器温度/状态）。"""
        data = struct.pack(">HH", reg, count)
        frame = _build_frame(addr, 0x03, data)
        resp = await self._send_frame(frame, resp_len=count * 2 + 8)

        if not resp or len(resp) < 5:
            return None

        # 盈隆协议：2字节数据长度
        data_len = struct.unpack(">H", resp[2:4])[0]
        if data_len < 2:
            return None

        reg_data = resp[4:4 + data_len]
        values = []
        for i in range(0, len(reg_data), 2):
            values.append(struct.unpack(">H", reg_data[i:i + 2])[0])
        return values

    async def write_register(self, addr: int, reg: int, value: int) -> bool:
        """FC06: 写单个寄存器（温控器设温/开关）。"""
        data = struct.pack(">HH", reg, value)
        frame = _build_frame(addr, 0x06, data)
        resp = await self._send_frame(frame, resp_len=8)
        return resp is not None and len(resp) >= 8

    async def is_online(self) -> bool:
        """检查485网关是否可达。"""
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=1.0,
            )
            writer.close()
            await writer.wait_closed()
            return True
        except Exception:
            return False


# ── 高级控制API ──

_session: Optional[ModbusSession] = None


def _get_session() -> ModbusSession:
    global _session
    if _session is None:
        _session = ModbusSession()
    return _session


async def is_gateway_online() -> bool:
    """检查485网关是否可达（FRP隧道已通）。"""
    return await _get_session().is_online()


async def relay_control(ha_room: str, channel_key: str, state: bool) -> dict:
    """控制继电器通道开关（直接485，绕过HA）。

    Args:
        ha_room: HA房间名（baishawa/bulage/feilengcui/fengshali）
        channel_key: 通道标识（如 "ch1", "relay_ch3", 或通道号0-7）
        state: True=开, False=关
    """
    addr = RELAY_ADDR.get(ha_room)
    if addr is None:
        return {"success": False, "message": f"未知房间: {ha_room}"}

    # 解析通道号
    if isinstance(channel_key, int):
        channel = channel_key
    else:
        channel = RELAY_CHANNEL_MAP.get(channel_key)
        if channel is None:
            return {"success": False, "message": f"未知通道: {channel_key}"}

    session = _get_session()
    success = await session.write_coil(addr, channel, state)
    if success:
        return {"success": True, "message": f"{'开' if state else '关'} {ha_room} CH{channel + 1}"}
    return {"success": False, "message": f"485控制失败 {ha_room} CH{channel + 1}"}


async def relay_all_control(ha_room: str, state: bool, exclude_channels: Optional[list[int]] = None) -> dict:
    """批量控制房间所有继电器通道。

    Args:
        ha_room: HA房间名
        state: True=全开, False=全关
        exclude_channels: 排除的通道号列表（如小茶室CH3换气扇）
    """
    addr = RELAY_ADDR.get(ha_room)
    if addr is None:
        return {"success": False, "message": f"未知房间: {ha_room}"}

    exclude = exclude_channels or []
    states = [state] * 8
    for ch in exclude:
        if 0 <= ch < 8:
            states[ch] = not state  # 排除的通道保持反向

    session = _get_session()
    success = await session.write_multiple_coils(addr, states)
    if success:
        return {"success": True, "message": f"批量{'开' if state else '关'} {ha_room} (排除通道 {exclude})"}
    return {"success": False, "message": f"485批量控制失败 {ha_room}"}


async def thermostat_control(ha_room: str, action: str, value: Optional[float] = None) -> dict:
    """控制温控面板（直接485）。

    Actions:
      - "on": 开机（写寄存器0x0039=1）
      - "off": 关机（写寄存器0x0039=0）
      - "temperature": 设温（写寄存器0x0036）
      - "read_temp": 读取室温（读寄存器0x0033）
      - "read_status": 读取状态（读寄存器0x0030）
    """
    addr = THERMOSTAT_ADDR.get(ha_room)
    if addr is None:
        return {"success": False, "message": f"未知房间: {ha_room}"}

    session = _get_session()

    if action == "on":
        success = await session.write_register(addr, 0x0039, 1)
        return {"success": success, "message": "空调已开机" if success else "485控制失败"}

    elif action == "off":
        success = await session.write_register(addr, 0x0039, 0)
        return {"success": success, "message": "空调已关机" if success else "485控制失败"}

    elif action == "temperature":
        if value is None:
            return {"success": False, "message": "缺少温度值"}
        temp_int = int(round(value))
        temp_int = max(16, min(30, temp_int))  # 限幅16-30°C
        success = await session.write_register(addr, 0x0036, temp_int)
        return {"success": success, "message": f"设温 {temp_int}°C" if success else "485控制失败"}

    elif action == "read_temp":
        values = await session.read_holding_registers(addr, 0x0033)
        if values:
            return {"success": True, "temperature": float(values[0]), "unit": "°C"}
        return {"success": False, "message": "读取室温失败"}

    elif action == "read_status":
        values = await session.read_holding_registers(addr, 0x0030)
        if values:
            status = values[0]
            power = bool(status & 0x80)
            mode_map = {0: "cool", 1: "heat", 2: "vent"}
            mode = mode_map.get((status >> 4) & 0x03, "unknown")
            fan_map = {0: "low", 1: "mid", 2: "high", 3: "off"}
            fan = fan_map.get(status & 0x03, "unknown")
            return {
                "success": True,
                "power": power,
                "mode": mode,
                "fan": fan,
                "cool_valve": bool(status & 0x04),
                "heat_valve": bool(status & 0x08),
            }
        return {"success": False, "message": "读取状态失败"}

    return {"success": False, "message": f"未知操作: {action}"}


async def get_room_temperature(ha_room: str) -> Optional[float]:
    """快捷读取房间室温（直接485）。"""
    result = await thermostat_control(ha_room, "read_temp")
    if result.get("success"):
        return result.get("temperature")
    return None
