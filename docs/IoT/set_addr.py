# -*- coding: utf-8 -*-
"""
茶室485设备 配码 & 查询工具
支持：聚英继电器、盈隆开关面板、盈隆空调面板
"""
import serial, time, struct, os, sys
from datetime import datetime

def calc_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

REG_RELAY = 0x03EA   # 聚英继电器地址寄存器

# === 地址规划 ===
#             (地址, 类型,  房间,   标签)
DEVICES = [
    (0x01, "开关", "大会议室",   "开关面板1"),
    (0x02, "开关", "大会议室",   "开关面板2"),
    (0x03, "开关", "大茶室",   "开关面板1"),
    (0x04, "开关", "大茶室",   "开关面板2"),
    (0x05, "开关", "中茶室",   "开关面板1"),
    (0x06, "开关", "中茶室",   "开关面板2"),
    (0x07, "开关", "小茶室",   "开关面板1"),
    (0x08, "开关", "小茶室",   "开关面板2"),
    (0x09, "空调", "大会议室",   "空调面板"),
    (0x0A, "空调", "大茶室",   "空调面板"),
    (0x0B, "空调", "中茶室",   "空调面板"),
    (0x0C, "空调", "小茶室",   "空调面板"),
    (0x10, "继电器", "大会议室", "8路继电器"),
    (0x11, "继电器", "大茶室",   "8路继电器"),
    (0x12, "继电器", "中茶室",  "8路继电器"),
    (0x13, "继电器", "小茶室",  "8路继电器"),
]

ADDR_MAP = {addr: (typ, room, label) for addr, typ, room, label in DEVICES}
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "配码记录.txt")

# ── 设备检测 ──

def scan_relay(ser, addr):
    """检测聚英继电器"""
    cmd = bytes([addr, 0x03, (REG_RELAY>>8)&0xFF, REG_RELAY&0xFF, 0x00, 0x01])
    cmd += calc_crc(cmd)
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.12)
    resp = ser.read(1024)
    if resp and len(resp) >= 5 and resp[0] == addr and resp[2] == 2:
        return (resp[3] << 8) | resp[4]
    return None

def scan_yinglong(ser, addr):
    """检测盈隆设备（开关面板/空调面板）"""
    cmd = bytes([addr, 0x03, 0x00, 0x02, 0x00, 0x02])
    cmd += calc_crc(cmd)
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.12)
    resp = ser.read(1024)
    if resp and len(resp) >= 7 and resp[0] == addr:
        return resp[3:5]
    return None

def relay_change_addr(ser, old_addr, new_addr):
    """改聚英继电器地址"""
    cmd = bytes([old_addr, 0x06, (REG_RELAY>>8)&0xFF, REG_RELAY&0xFF, 0x00, new_addr])
    cmd += calc_crc(cmd)
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.3)
    resp = ser.read(1024)
    if resp and len(resp) >= 6:
        time.sleep(0.2)
        v = scan_relay(ser, new_addr)
        return v == new_addr
    return False

def yinglong_change_addr(ser, old_addr, new_addr):
    """改盈隆设备地址"""
    for reg in [0x00, 0x07, 0x08]:
        cmd = bytes([old_addr, 0x06, (reg>>8)&0xFF, reg&0xFF, 0x00, new_addr])
        cmd += calc_crc(cmd)
        ser.reset_input_buffer()
        ser.write(cmd)
        time.sleep(0.3)
        resp = ser.read(1024)
        if resp and len(resp) >= 6:
            time.sleep(0.2)
            ok = scan_yinglong(ser, new_addr)
            if ok:
                return True, reg
    return False, None

# ── 主菜单 ──

print("=" * 55)
print("  茶室485设备 配码 & 查询工具")
print("  聚英继电器 / 盈隆开关面板 / 盈隆空调面板")
print("=" * 55)

port = 'COM4'
ser = serial.Serial(port, 9600, timeout=0.5)
print(f"COM4 打开成功\n")

while True:
    print("─" * 55)
    print("1. 扫描总线(列出所有已配码设备)")
    print("2. 查询设备归属")
    print("3. 配码盈隆设备(开关面板/空调面板)")
    print("4. 配码聚英继电器")
    print("5. 查看地址规划表")
    print("0. 退出")
    print("─" * 55)
    c = input("选择: ").strip()

    if c == '0':
        ser.close()
        print("再见")
        break

    elif c == '1':
        print("\n扫描总线...")
        found = []
        # 继电器地址
        for addr in range(0x10, 0x15):
            v = scan_relay(ser, addr)
            if v is not None:
                info = ADDR_MAP.get(addr, ("继电器", "?", "?"))
                found.append(("继电器", addr, v, info))
        # 盈隆地址 (1-16)
        for addr in list(range(0x01, 0x10)) + [0x3C]:
            d = scan_yinglong(ser, addr)
            if d:
                info = ADDR_MAP.get(addr, ("盈隆", "?", "?"))
                found.append(("盈隆", addr, d.hex(), info))

        if not found:
            print("  未找到任何设备")
        else:
            print(f"\n找到 {len(found)} 个设备:")
            for dev_type, addr, val, info in found:
                typ, room, label = info
                print(f"  {dev_type} 0x{addr:02X} -> {room} {label} (值:{val})")

    elif c == '2':
        print("\n查询设备归属")
        a = input("输入地址 (hex, 如 06): ").strip()
        try:
            addr = int(a, 16)
        except:
            print("无效"); continue

        v = scan_relay(ser, addr)
        if v is not None:
            info = ADDR_MAP.get(addr, ("?", "?", "?"))
            print(f"\n  类型: 聚英继电器  地址: 0x{addr:02X}")
            print(f"  房间: {info[1]}  设备: {info[2]}")
            continue

        d = scan_yinglong(ser, addr)
        if d:
            info = ADDR_MAP.get(addr, ("?", "?", "?"))
            print(f"\n  类型: 盈隆设备  地址: 0x{addr:02X}")
            print(f"  房间: {info[1]}  设备: {info[2]}")
            continue

        print("  该地址无响应")

    elif c == '3':
        print("\n配码盈隆设备（开关面板/空调面板）")
        print("每次只接1台到总线!\n")

        # 扫描默认地址
        found_addr = None
        for addr in list(range(0x01, 0x10)) + [0x3C]:
            d = scan_yinglong(ser, addr)
            if d:
                found_addr = addr
                break

        if found_addr is None:
            print("未找到盈隆设备")
            continue

        curr_info = ADDR_MAP.get(found_addr, ("盈隆", "?", "?"))
        print(f"找到盈隆设备 @ 0x{found_addr:02X}")
        if curr_info[1]:
            print(f"  当前归属: {curr_info[1]} {curr_info[2]}")
        print()

        print("可选地址:")
        valid = []
        for addr, typ, room, label in DEVICES:
            if typ in ("开关", "空调"):
                mark = " ← 当前" if addr == found_addr else ""
                print(f"  {addr:2d} (0x{addr:02X}) - {room} {label}{mark}")
                valid.append(addr)

        print()
        n = input("输入新地址编号 (或 0 取消): ").strip()
        if not n or n == '0': continue
        try:
            new_addr = int(n)
        except:
            print("无效"); continue
        if new_addr not in valid:
            print("无效地址"); continue

        _, room_name, label_name = ADDR_MAP[new_addr]
        print(f"\n0x{found_addr:02X} -> 0x{new_addr:02X} ({room_name} {label_name})")
        if input("确认? (y/n): ").strip().lower() != 'y': continue

        ok, reg = yinglong_change_addr(ser, found_addr, new_addr)
        if ok:
            print(f"  成功! (寄存器 0x{reg:04X})")
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] ")
                f.write(f"盈隆 0x{found_addr:02X} -> 0x{new_addr:02X} ({room_name} {label_name}) 成功\n")
        else:
            print("  失败! 试试手动断电重启后重试")

    elif c == '4':
        print("\n配码聚英继电器")
        found_addr = None
        for addr in [0x01, 0x10, 0x11, 0x12, 0x13]:
            v = scan_relay(ser, addr)
            if v is not None:
                found_addr = addr
                break
        if found_addr is None:
            print("未找到继电器"); continue

        curr_info = ADDR_MAP.get(found_addr, ("?", "?", "?"))
        print(f"找到继电器 @ 0x{found_addr:02X}")
        if curr_info[1]:
            print(f"  当前: {curr_info[1]} {curr_info[2]}")
        print("\n可选地址:")
        valid = []
        for addr, typ, room, label in DEVICES:
            if typ == "继电器":
                print(f"  {addr:2d} (0x{addr:02X}) - {room} {label}")
                valid.append(addr)
        print()
        n = input("输入新地址编号 (或 0 取消): ").strip()
        if not n or n == '0': continue
        try:
            new_addr = int(n)
        except:
            print("无效"); continue
        if new_addr not in valid:
            print("无效地址"); continue
        _, room_name, label_name = ADDR_MAP[new_addr]
        print(f"\n0x{found_addr:02X} -> 0x{new_addr:02X} ({room_name} {label_name})")
        if input("确认? (y/n): ").strip().lower() != 'y': continue
        ok = relay_change_addr(ser, found_addr, new_addr)
        if ok:
            print("  成功!")
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] ")
                f.write(f"继电器 0x{found_addr:02X} -> 0x{new_addr:02X} ({room_name} {label_name}) 成功\n")
        else:
            print("  失败!")

    elif c == '5':
        print("\n" + "=" * 55)
        print("  地址规划表")
        print("=" * 55)
        print(f"  {'地址':>6}  {'类型':<6}  {'房间':<8}  {'设备'}")
        print("  " + "-" * 45)
        for addr, typ, room, label in DEVICES:
            print(f"  0x{addr:02X}    {typ:<4}  {room:<6}  {label}")
        print("\n  盈隆出厂默认: 地址 0x3C")
        print("  聚英出厂默认: 地址 0x01 (广播 FE)")
