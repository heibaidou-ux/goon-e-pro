# -*- coding: utf-8 -*-
"""
JY-DAM0808D 继电器地址配置工具
茶室现场用 —— 双击配码工具.bat 运行
自动扫描总线，找到设备后配码
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

REG_ADDRESS = 0x03EA  # 地址寄存器
KNOWN_ADDRS = [0x01, 0xFE, 0x02, 0x03, 0x04, 0x05, 0x06]

ROOMS = [
    (0x01, "茶室1"),
    (0x02, "茶室2"),
    (0x03, "茶室3"),
    (0x04, "茶室4"),
    (0x05, "展厅"),
    (0x06, "会议室"),
]

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "配码记录.txt")

def scan_device(ser):
    """扫描总线上所有已知地址，返回 (找到的地址, 配置) 或 None"""
    for addr in KNOWN_ADDRS:
        cmd = bytes([addr, 0x03, (REG_ADDRESS>>8)&0xFF, REG_ADDRESS&0xFF, 0x00, 0x01])
        cmd += calc_crc(cmd)
        ser.reset_input_buffer()
        ser.write(cmd)
        time.sleep(0.15)
        resp = ser.read(1024)
        if resp and len(resp) >= 5 and resp[0] == addr:
            return addr, (resp[3] << 8) | resp[4]
    return None, None

def read_config(ser, addr):
    """读取设备配置"""
    cmd = bytes([addr, 0x03, 0x00, 0x00, 0x00, 0x0A])
    cmd += calc_crc(cmd)
    ser.reset_input_buffer()
    ser.write(cmd)
    time.sleep(0.15)
    return ser.read(1024)

# === 主程序 ===
print("=" * 50)
print("  JY-DAM0808D 继电器配码工具")
print("=" * 50)
print()
print("步骤: 插USB-485 → 接继电器(仅1台) → 通电 → 运行本工具")
print()

port = 'COM4'
ser = serial.Serial(port, 9600, timeout=0.5)
print(f"COM4 打开成功")
print()

# 扫描
print("扫描总线上设备...")
found_addr, reg_val = scan_device(ser)

if found_addr is None:
    print("未找到设备！")
    print("检查: A/B 线接对了吗？继电器通电了吗？")
    print("      一次只接了1台在总线上吗？")
    ser.close()
    input("按 Enter 退出...")
    sys.exit(1)

print(f"找到设备 @ 地址 0x{found_addr:02X}")
print(f"地址寄存器 = 0x{reg_val:04X} ({reg_val})")

# 读取更多信息
resp = read_config(ser, found_addr)
if resp and len(resp) > 10:
    print(f"设备型号信息: {resp.hex()}")

print()
print("可选房间:")
for addr, name in ROOMS:
    mark = " ← 当前" if addr == reg_val else ""
    print(f"  {addr} (0x{addr:02X}) - {name}{mark}")

print()
new_str = input("输入新地址编号 (1-6, 或 0 退出): ").strip()
if not new_str or new_str == '0':
    ser.close()
    print("已取消")
    sys.exit(0)

try:
    new_addr = int(new_str)
    if new_addr not in [a for a, n in ROOMS]:
        print(f"无效编号 {new_addr}")
        ser.close()
        sys.exit(1)
except:
    print("输入无效")
    ser.close()
    sys.exit(1)

room_name = "未知"
for a, n in ROOMS:
    if a == new_addr:
        room_name = n
        break

print(f"\n0x{found_addr:02X} → 0x{new_addr:02X} ({room_name})")
confirm = input("确认? (y/n): ").strip().lower()
if confirm != 'y':
    ser.close()
    print("已取消")
    sys.exit(0)

# 写新地址
cmd = bytes([found_addr, 0x06, (REG_ADDRESS>>8)&0xFF, REG_ADDRESS&0xFF, 0x00, new_addr])
cmd += calc_crc(cmd)
ser.reset_input_buffer()
ser.write(cmd)
time.sleep(0.3)
resp = ser.read(1024)

if resp and len(resp) >= 6:
    print("  写入成功!")
else:
    print("  写入失败!")
    ser.close()
    sys.exit(1)

# 验证
time.sleep(0.2)
cmd = bytes([new_addr, 0x03, (REG_ADDRESS>>8)&0xFF, REG_ADDRESS&0xFF, 0x00, 0x01])
cmd += calc_crc(cmd)
ser.reset_input_buffer()
ser.write(cmd)
time.sleep(0.2)
resp = ser.read(1024)

if resp and len(resp) >= 5 and resp[0] == new_addr:
    print(f"  验证通过! 新地址 0x{new_addr:02X} 通信正常")
else:
    print(f"  验证失败，新地址无响应(可能需要断电重启)")
    ser.close()
    sys.exit(1)

ser.close()

# 记日志
try:
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] ")
        f.write(f"0x{found_addr:02X} -> 0x{new_addr:02X} ({room_name}) 成功\n")
    print(f"\n已记录: {LOG_FILE}")
except:
    pass

print(f"\n{'='*50}")
print(f" 完成! {room_name} 继电器 = 地址 0x{new_addr:02X}")
print(f" 可以拔下来换下一台了")
print(f"{'='*50}")
input("按 Enter 退出...")
