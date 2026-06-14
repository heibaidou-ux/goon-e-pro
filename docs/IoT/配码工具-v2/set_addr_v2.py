# -*- coding: utf-8 -*-
"""
盈隆485设备配码工具 v2 — 修复版
================================
支持: 聚英JY-DAM继电器(reg 0x03EA)、盈隆温控器(reg 0x0020)、盈隆开关面板(reg 0x1000)

用法: python set_addr.py [COM端口]
默认端口: COM4

配码流程:
  1. 485总线上只接1个设备
  2. 运行此脚本自动扫描
  3. 选择新地址 → 写入 → 验证 → 记录
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

def make_frame(slave, func, data):
    return bytes([slave, func]) + data + calc_crc(bytes([slave, func]) + data)

# ── 寄存器定义 ──
REG_RELAY_ADDR  = 0x03EA   # 聚英继电器地址寄存器
REG_THERM_ADDR  = 0x0020   # 盈隆温控器地址寄存器
REG_PANEL_ADDR  = 0x1000   # 盈隆开关面板地址寄存器
REG_PANEL_SAVE  = 0x100F   # 开关面板保存寄存器

# ── 地址规划（按现场实际修改）──
DEVICES = [
    # (addr, type, room, label)
    (0x01, "switch", "会议室", "面板1"), (0x02, "switch", "会议室", "面板2"),
    (0x03, "switch", "小茶室", "面板1"), (0x04, "switch", "小茶室", "面板2"),
    (0x05, "switch", "中茶室", "面板1"), (0x06, "switch", "中茶室", "面板2"),
    (0x07, "switch", "大茶室", "面板1"), (0x08, "switch", "大茶室", "面板2"),
    (0x09, "hvac",   "会议室", "空调"),  (0x0A, "hvac",   "小茶室", "空调"),
    (0x0B, "hvac",   "中茶室", "空调"),  (0x0C, "hvac",   "大茶室", "空调"),
    (0x10, "relay",  "会议室", "继电器"), (0x11, "relay",  "小茶室", "继电器"),
    (0x12, "relay",  "中茶室", "继电器"), (0x13, "relay",  "大茶室", "继电器"),
]
ADDR_MAP = {a: (t, r, l) for a, t, r, l in DEVICES}
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "配码记录.txt")

# ── 扫描函数 ──

def scan_relay(ser, addr):
    """扫描聚英继电器（寄存器0x03EA）"""
    cmd = make_frame(addr, 0x03, struct.pack('>HH', REG_RELAY_ADDR, 1))
    ser.reset_input_buffer(); ser.write(cmd); time.sleep(0.12)
    r = ser.read(1024)
    if r and len(r) >= 5 and r[0] == addr:
        return (r[3] << 8) | r[4]
    return None

def scan_thermostat(ser, addr):
    """扫描盈隆温控器（寄存器0x0020 - 设备地址）"""
    cmd = make_frame(addr, 0x03, struct.pack('>HH', REG_THERM_ADDR, 1))
    ser.reset_input_buffer(); ser.write(cmd); time.sleep(0.08)
    r = ser.read(32)
    if r and len(r) >= 5 and r[0] == addr:
        return r.hex()
    return None

def scan_switch_panel(ser, addr):
    """扫描盈隆开关面板（寄存器0x1000 - 面板地址）"""
    cmd = make_frame(addr, 0x03, struct.pack('>HH', REG_PANEL_ADDR, 1))
    ser.reset_input_buffer(); ser.write(cmd); time.sleep(0.08)
    r = ser.read(32)
    if r and len(r) >= 5 and r[0] == addr:
        return r.hex()
    return None

# ── 写入地址函数 ──

def write_relay_addr(ser, old, new):
    cmd = make_frame(old, 0x06, struct.pack('>HH', REG_RELAY_ADDR, new))
    ser.reset_input_buffer(); ser.write(cmd); time.sleep(0.3)
    r = ser.read(32)
    if r and len(r) >= 6:
        time.sleep(0.5)
        return scan_relay(ser, new) == new
    return False

def write_thermostat_addr(ser, old, new):
    """写温控器地址（寄存器0x0020）"""
    cmd = make_frame(old, 0x06, struct.pack('>HH', REG_THERM_ADDR, new))
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.5)  # 设备改址需要时间
    # 读写指令的响应（设备用新地址回复）
    r = ser.read(32)
    if r:
        print(f"  📡 写响应: {r.hex()}")
    time.sleep(0.3)
    # 验证：先扫旧地址（可能没变），再扫新地址
    if scan_thermostat(ser, new):
        return True
    if scan_thermostat(ser, old):
        print(f"  ⚠️ 设备仍在旧地址0x{old:02X}，可能未改成功")
    return False

def write_switch_panel_addr(ser, old, new):
    """写开关面板地址（寄存器0x1000）+ 保存（寄存器0x100F写0x00FE）"""
    cmd = make_frame(old, 0x06, struct.pack('>HH', REG_PANEL_ADDR, new))
    ser.reset_input_buffer()
    ser.write(cmd)
    ser.flush()
    time.sleep(0.5)
    r = ser.read(32)
    if r:
        print(f"  📡 改址响应: {r.hex()}")
    time.sleep(0.3)

    # 保存配置
    cmd_save = make_frame(new, 0x06, struct.pack('>HH', REG_PANEL_SAVE, 0x00FE))
    ser.reset_input_buffer(); ser.write(cmd_save); ser.flush(); time.sleep(0.3)
    _ = ser.read(32)
    time.sleep(0.5)

    if scan_switch_panel(ser, new):
        return True
    if scan_switch_panel(ser, old):
        print(f"  ⚠️ 面板仍在旧地址0x{old:02X}")
    return False

# ── 交互菜单 ──

def do_commission(ser, label, scan_fn, set_fn, valid_addrs):
    """通用配码流程：扫描→确认→改址→验证"""
    print(f"\n{'='*50}")
    print(f"配码: {label}")
    print(f"{'='*50}")

    # 默认地址优先
    default_addrs = [0x3C, 0x02, 0x01, 0x1E]
    found = None
    for a in default_addrs + [x+1 for x in range(20)]:  # 1-20 + 默认地址
        a_byte = a if isinstance(a, int) else a
        r = scan_fn(ser, a_byte)
        if r:
            found = a_byte
            print(f"  ✅ 找到设备 @ 0x{found:02X}")
            break
    if not found:
        print("  ❌ 未找到设备")
        print("  可能原因：")
        print("    • 485 A/B线接反了？")
        print("    • 面板没上电？")
        print("    • 波特率不是9600？")
        print("    • USB-485转换器驱动问题？")
        return

    print(f"\n可用地址列表：")
    for a, t, rm, lb in DEVICES:
        if a in valid_addrs:
            print(f"  0x{a:02X} ({a:3d})  {rm:10s}  {lb}")

    ns = input(f"\n新地址 (0=取消): ").strip()
    if not ns or ns == '0':
        print("已取消")
        return
    try:
        na = int(ns)
        if na not in valid_addrs:
            na = int(ns, 16)  # 试试16进制
        if na not in valid_addrs:
            print("❌ 无效地址，请从上面列表中选择")
            return
    except:
        print("❌ 无效输入")
        return

    t, rm, lb = ADDR_MAP[na]
    confirm = input(f"确认: 0x{found:02X} → 0x{na:02X} ({rm} {lb})? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    if set_fn(ser, found, na):
        print(f"  ✅ 配码成功！0x{found:02X} → 0x{na:02X} ({rm} {lb})")
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {label}: 0x{found:02X}→0x{na:02X} ({rm} {lb}) OK\n")
    else:
        print(f"  ❌ 配码失败！请检查接线后重试")

def do_scan_bus(ser):
    """扫描总线所有设备"""
    print("\n扫描总线...")

    print("  --- 继电器 (寄存器0x03EA) ---")
    for a in range(0x01, 0x15):
        v = scan_relay(ser, a)
        if v is not None:
            t, rm, lb = ADDR_MAP.get(a, ("relay","?","?"))
            print(f"    ✅ 0x{a:02X} ({a:3d}) → {rm} {lb}")

    print("  --- 温控器 (寄存器0x0020) ---")
    for a in list([0x3C]) + list(range(1, 61)):
        r = scan_thermostat(ser, a)
        if r:
            t, rm, lb = ADDR_MAP.get(a, ("hvac","?","?"))
            print(f"    ✅ 0x{a:02X} ({a:3d}) → {rm} {lb}  data={r}")

    print("  --- 开关面板 (寄存器0x1000) ---")
    for a in list([0x02]) + list(range(1, 43)):
        r = scan_switch_panel(ser, a)
        if r:
            t, rm, lb = ADDR_MAP.get(a, ("switch","?","?"))
            print(f"    ✅ 0x{a:02X} ({a:3d}) → {rm} {lb}  data={r}")

# ── 主程序 ──

port = 'COM4'
if len(sys.argv) > 1:
    port = sys.argv[1]

try:
    ser = serial.Serial(port, 9600, timeout=0.5)
    print(f"✅ {port} @ 9600 8N1 打开成功\n")
except Exception as e:
    print(f"❌ 无法打开 {port}: {e}")
    print("\n可用端口:")
    if sys.platform == 'win32':
        print("  COM1 ~ COM256")
        print("  在设备管理器查看实际端口号")
    else:
        import glob
        for p in sorted(glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyS*')):
            print(f"  {p}")
    sys.exit(1)

print("=" * 50)
print("  盈隆485配码工具 v2")
print("=" * 50)

while True:
    print("\n" + "-" * 50)
    print("1. 扫描总线（列出所有设备）")
    print("2. 配码：开关面板（寄存器0x1000改址+保存）")
    print("3. 配码：温控器（寄存器0x0020改址）")
    print("4. 配码：聚英继电器（寄存器0x03EA改址）")
    print("5. 查看地址规划表")
    print("6. 查看配码记录")
    print("0. 退出")
    c = input("请选择: ").strip()

    if c == '0':
        ser.close()
        print("再见")
        break
    elif c == '1':
        do_scan_bus(ser)
    elif c == '2':
        valid = sorted([a for a, t, _, _ in DEVICES if t in ("switch",)])
        do_commission(ser, "开关面板", scan_switch_panel, write_switch_panel_addr, valid)
    elif c == '3':
        valid = sorted([a for a, t, _, _ in DEVICES if t in ("hvac",)])
        do_commission(ser, "温控器", scan_thermostat, write_thermostat_addr, valid)
    elif c == '4':
        valid = sorted([a for a, t, _, _ in DEVICES if t in ("relay",)])
        do_commission(ser, "聚英继电器", scan_relay, write_relay_addr, valid)
    elif c == '5':
        print("\n地址规划表：")
        print(f"  {'地址':>6}  {'类型':<6}  {'房间':<8}  设备")
        for a, t, rm, lb in DEVICES:
            print(f"  0x{a:02X} ({a:3d})  {t:<6}  {rm:<8}  {lb}")
        print(f"\n默认地址：温控器=0x3C, 开关面板=0x02, 继电器=0x01")
    elif c == '6':
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                print("\n配码记录：")
                print(f.read())
        except:
            print("暂无记录")
