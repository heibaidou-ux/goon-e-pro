#!/usr/bin/env python3
"""
杜亚 DVQ24WF/J RS485 电机地址写入工具

通信参数: 9600 bps, 8N1
帧格式:   55 [ID_H] [ID_L] [CMD] [DATA_ADDR] [DATA_LEN] [DATA...] [CRC_L] [CRC_H]
CRC16:    Modbus CRC (poly=0x8005, reflected, init=0xFFFF), 校验范围包含 0x55 起始码
地址:     大端序 (ID_H 高字节在前, ID_L 低字节在后)
默认地址: 0xFEFE 或 0x0000 (不同批次可能不同)

使用方法:
    python3 dooya_485_set_address.py --port /dev/tty.usbserial-xxx --new-addr 1
    python3 dooya_485_set_address.py --port /dev/tty.usbserial-xxx --new-addr 0x01
    python3 dooya_485_set_address.py --port COM3 --new-addr 10 --old-addr 0xFEFE
    python3 dooya_485_set_address.py --port /dev/tty.usbserial-xxx --test
    python3 dooya_485_set_address.py --dry --new-addr 1       # 只看命令不发送
    python3 dooya_485_set_address.py --list                    # 列出可用串口
"""

import argparse
import struct
import sys
import time

try:
    import serial
except ImportError:
    print("请先安装 pyserial: pip3 install pyserial")
    sys.exit(1)


# ---------------------------------------------------------------------------
# CRC16 Modbus (reflected, poly=0x8005, init=0xFFFF)
# 校验范围: 包含 0x55 起始码，覆盖到数据内容的最后一个字节
# ---------------------------------------------------------------------------

def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def crc16_le(data: bytes) -> bytes:
    return struct.pack("<H", crc16(data))


# ---------------------------------------------------------------------------
# 命令构造
# ---------------------------------------------------------------------------

START = 0x55
FUNC_CONTROL = 0x03     # 控制命令 (上行/下行/停止/百分比)
FUNC_WRITE   = 0x02     # 写寄存器
FUNC_READ    = 0x01     # 读寄存器
FUNC_REQUEST = 0x04     # 从机请求分配地址

# 控制子命令
SUB_UP     = 0x01       # 上行 (部分固件用 0x02)
SUB_DOWN   = 0x02       # 下行 (部分固件用 0x01)
SUB_STOP   = 0x03       # 停止
SUB_PERCENT = 0x04      # 百分比控制


def pack_id(dev_id: int) -> bytes:
    """地址编码: ID_H, ID_L (大端序)"""
    return bytes([(dev_id >> 8) & 0xFF, dev_id & 0xFF])


def build_frame(dev_id: int, func: int, data_addr: int,
                data: bytes = b"") -> bytes:
    """
    构造完整帧: 55 + ID_H + ID_L + CMD + DATA_ADDR + DATA_LEN + [DATA] + CRC16

    CRC 覆盖范围: 从 0x55 到数据结束的全部字节
    """
    payload = bytes([START]) + pack_id(dev_id) \
              + bytes([func, data_addr, len(data)]) + data
    return payload + crc16_le(payload)


def build_write_addr_cmd(old_id: int, new_id: int) -> bytes:
    """
    写设备地址命令。
    寄存器 0x00 = 2 字节地址 (ID_H, ID_L)
    注意: 写地址时总线上只能有一台电机
    """
    return build_frame(old_id, FUNC_WRITE, 0x00, pack_id(new_id))


def build_control_cmd(dev_id: int, action: str) -> bytes:
    """
    电机控制命令。
    action: 'up' | 'down' | 'stop'
    """
    sub_cmd = {"up": SUB_UP, "down": SUB_DOWN, "stop": SUB_STOP}
    if action not in sub_cmd:
        raise ValueError(f"未知动作: {action}, 可选: {list(sub_cmd.keys())}")
    return build_frame(dev_id, FUNC_CONTROL, sub_cmd[action], b"")


def build_percent_cmd(dev_id: int, percent: int) -> bytes:
    """百分比控制命令 (0~100)"""
    if not (0 <= percent <= 100):
        raise ValueError("百分比必须为 0~100")
    return build_frame(dev_id, FUNC_CONTROL, SUB_PERCENT, bytes([percent]))


def build_read_cmd(dev_id: int, addr: int = 0x00, length: int = 0x05) -> bytes:
    """读寄存器命令。默认读 0x00~0x04 (状态/位置等)"""
    return build_frame(dev_id, FUNC_READ, addr, bytes([length]))


def build_request_addr_cmd() -> bytes:
    """广播请求分配地址 (固件自动发送, 也可手动触发)"""
    return build_frame(0x0000, FUNC_REQUEST, 0x00, b"")


# ---------------------------------------------------------------------------
# 串口通信
# ---------------------------------------------------------------------------

def open_serial(port: str) -> serial.Serial:
    return serial.Serial(
        port=port,
        baudrate=9600,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1.0,
    )


def send_cmd(ser: serial.Serial, cmd: bytes, label: str = "") -> bytes | None:
    hex_str = cmd.hex(" ").upper()
    prefix = f"  [发送] {label}: " if label else "  >>> "
    print(f"{prefix}{hex_str}")

    ser.flushInput()
    ser.write(cmd)
    time.sleep(0.25)

    reply = ser.read(64)
    if reply:
        print(f"  <<< 响应: {reply.hex(' ').upper()}")
    else:
        print(f"  <<< 无响应 (超时)")
    return reply if reply else None


# ---------------------------------------------------------------------------
# 交互式操作
# ---------------------------------------------------------------------------

def test_communication(ser: serial.Serial, dev_id: int) -> bool:
    """测试通讯: 上行 → 下行 → 停止"""
    print(f"\n{'='*50}")
    print(f"测试通讯 — 设备地址 = 0x{dev_id:04X} ({dev_id})")
    print(f"{'='*50}")

    ok = True
    for action, label in [("up", "上行"), ("down", "下行"), ("stop", "停止")]:
        print(f"\n  [{label}]")
        cmd = build_control_cmd(dev_id, action)
        reply = send_cmd(ser, cmd)
        time.sleep(0.8)
        if not reply:
            ok = False
    return ok


def write_address(ser: serial.Serial, old_id: int, new_id: int) -> bool:
    print(f"\n{'='*50}")
    print(f"写入设备地址: 0x{old_id:04X} → 0x{new_id:04X}")
    print(f"{'='*50}")
    print()
    print("操作步骤:")
    print(f"  1. 确保 RS485 总线上只接了一台电机")
    print(f"  2. 按住电机设置键约 2~5 秒, LED 闪烁后松开")
    print(f"  3. 此时按下 Enter 键发送写地址命令")
    print()
    input(">>> 准备好后按 Enter 发送命令 <<<")
    print()

    cmd = build_write_addr_cmd(old_id, new_id)
    reply = send_cmd(ser, cmd, label=f"写地址 0x{old_id:04X}→0x{new_id:04X}")
    return reply is not None


def scan_address(ser: serial.Serial) -> int | None:
    """用广播控制命令测试电机是否在总线上"""
    print(f"\n{'='*50}")
    print("扫描电机 — 发送广播上行/下行命令")
    print("如果电机有反应，说明通讯正常，默认地址可能为 0x0000")
    print(f"{'='*50}")

    for action, label in [("up", "上行(广播)"), ("down", "下行(广播)")]:
        print(f"\n  [{label}]")
        cmd = build_control_cmd(0x0000, action)
        send_cmd(ser, cmd)
        time.sleep(0.8)

    print("\n请观察电机是否有动作。如有动作 → 旧地址就是 0x0000")
    print("如无动作，尝试 --old-addr 0xFEFE 再试。")
    return None


def read_status(ser: serial.Serial, dev_id: int) -> None:
    """读取电机状态"""
    print(f"\n读取设备 0x{dev_id:04X} 状态...")
    cmd = build_read_cmd(dev_id)
    reply = send_cmd(ser, cmd, label=f"读状态 0x{dev_id:04X}")
    if reply and len(reply) >= 7:
        # 解析状态
        data = reply[5:-2]  # 去掉 55+ID_H+ID_L+CMD+DATA_ADDR+DATA_LEN 和 CRC
        print(f"  数据: {data.hex(' ').upper()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def auto_int(x: str) -> int:
    if x.startswith("0x") or x.startswith("0X"):
        return int(x, 16)
    return int(x)


def main():
    parser = argparse.ArgumentParser(
        description="杜亚 DVQ24WF/J RS485 电机地址写入工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --port /dev/tty.usbserial-xxx --test              # 测试电机通讯
  %(prog)s --port /dev/tty.usbserial-xxx --new-addr 1        # 写地址(默认旧地址 0x0000)
  %(prog)s --port /dev/tty.usbserial-xxx -n 1 -o 0xFEFE     # 写地址(旧地址 0xFEFE)
  %(prog)s --port /dev/tty.usbserial-xxx --scan              # 广播扫描电机
  %(prog)s --dry --new-addr 0x0A                             # 只显示命令, 不发送
  %(prog)s --list                                             # 列出可用串口
        """,
    )
    parser.add_argument("--port", "-p",
                        help="串口路径, 如 /dev/tty.usbserial-xxx 或 COM3")
    parser.add_argument("--new-addr", "-n", type=str, default=None,
                        help="要写入的新地址 (十进制或 0x 十六进制)")
    parser.add_argument("--old-addr", "-o", type=str, default="0x0000",
                        help="电机当前地址, 出厂默认 0x0000 (也可尝试 0xFEFE)")
    parser.add_argument("--test", "-t", action="store_true",
                        help="测试电机通讯 (上行/下行/停止)")
    parser.add_argument("--scan", "-s", action="store_true",
                        help="广播扫描 — 用地址 0x0000 发送控制命令")
    parser.add_argument("--up", action="store_true", help="发送上行命令")
    parser.add_argument("--down", action="store_true", help="发送下行命令")
    parser.add_argument("--stop", action="store_true", help="发送停止命令")
    parser.add_argument("--percent", type=int, default=None,
                        help="百分比控制 (0~100)")
    parser.add_argument("--dry", action="store_true",
                        help="仅打印命令, 不打开串口")
    parser.add_argument("--list", "-l", action="store_true",
                        help="列出可用串口")

    args = parser.parse_args()

    # --list 不需要串口
    if args.list:
        from serial.tools import list_ports
        ports = list(list_ports.comports())
        if ports:
            print("可用串口:")
            for p in ports:
                print(f"  {p.device}  —  {p.description}")
        else:
            print("未检测到串口")
        return

    # --dry 不需要串口, 只打印命令
    if args.dry:
        old_id = auto_int(args.old_addr)
        print(f"旧地址: 0x{old_id:04X}\n")

        # 写地址命令
        if args.new_addr:
            new_id = auto_int(args.new_addr)
            cmd = build_write_addr_cmd(old_id, new_id)
            print(f"写地址 (0x{old_id:04X} → 0x{new_id:04X}):")
            print(f"  {cmd.hex(' ').upper()}")
            print()

        # 控制命令
        for dev_id, label in [(old_id, "旧"), (auto_int(args.new_addr) if args.new_addr else None, "新")]:
            if dev_id is None:
                continue
            print(f"{label}地址 0x{dev_id:04X} 命令:")
            for a in ["up", "down", "stop"]:
                c = build_control_cmd(dev_id, a)
                print(f"  {a:5s}: {c.hex(' ').upper()}")
            print()

        # 广播命令
        print("广播命令 (地址 0x0000):")
        for a in ["up", "down", "stop"]:
            c = build_control_cmd(0x0000, a)
            print(f"  {a:5s}: {c.hex(' ').upper()}")

        return

    if not args.port:
        parser.print_help()
        print("\n错误: 请指定 --port")
        sys.exit(1)

    # --- 打开串口 ---
    print(f"打开串口: {args.port}")
    try:
        ser = open_serial(args.port)
    except serial.SerialException as e:
        print(f"错误: 无法打开串口 — {e}")
        sys.exit(1)

    try:
        old_id = auto_int(args.old_addr)

        if args.scan:
            scan_address(ser)

        elif args.test:
            test_communication(ser, old_id)

        elif args.up or args.down or args.stop:
            for action, flag in [("up", args.up), ("down", args.down),
                                  ("stop", args.stop)]:
                if flag:
                    cmd = build_control_cmd(old_id, action)
                    send_cmd(ser, cmd, label=action)
                    time.sleep(0.5)

        elif args.percent is not None:
            cmd = build_percent_cmd(old_id, args.percent)
            send_cmd(ser, cmd, label=f"{args.percent}%")

        elif args.new_addr:
            new_id = auto_int(args.new_addr)
            if write_address(ser, old_id, new_id):
                print("\n✓ 地址写入命令已发送, 请检查 LED 是否闪烁 5 次确认成功")
                print(f"\n  用新地址 0x{new_id:04X} ({new_id}) 测试通讯:")
                time.sleep(1)
                test_communication(ser, new_id)
            else:
                print("\n✗ 写地址失败, 无响应")
                print("  常见原因:")
                print("  - 电机未进入设置模式 (重新按住设置键 2~5 秒)")
                print("  - 旧地址不正确 (尝试 --old-addr 0xFEFE)")
                print("  - RS485 A/B 线接反")
                print("  - 总线上有多台电机")

        else:
            parser.print_help()
    finally:
        ser.close()
        print("\n串口已关闭")


if __name__ == "__main__":
    main()
