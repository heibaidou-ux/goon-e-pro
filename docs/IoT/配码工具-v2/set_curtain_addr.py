#!/usr/bin/env python3
"""G24RTS485 窗帘电机配码工具"""
import sys, time, serial, os, json
from datetime import datetime

SERIAL_PORT = "COM4"
LOG_FILE = os.path.join(os.path.dirname(__file__) or '.', 'curtain_addr_log.json')

ADDR_MAP = {
    1: (0x14, "A组-电机1"),
    2: (0x15, "A组-电机2"),
    3: (0x16, "A组-电机3"),
    4: (0x17, "B组-电机1"),
    5: (0x18, "B组-电机2"),
    6: (0x19, "B组-电机3"),
    7: (0x1A, "C组-电机1"),
}

def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001: crc = (crc >> 1) ^ 0xA001
            else: crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])

def try_write(ser, frame, desc):
    ser.write(frame)
    time.sleep(0.2)
    resp = ser.read(256)
    if resp: print(f"  ✅ {desc}, 响应: {resp.hex()}")
    else: print(f"  ❌ {desc}, 无响应")
    return bool(resp)

def save_log(choice, addr, room, success):
    log = {}
    if os.path.exists(LOG_FILE):
        try: log = json.load(open(LOG_FILE))
        except: pass
    log[str(choice)] = {
        "addr_hex": f"0x{addr:02X}", "addr_dec": addr,
        "room": room, "success": success,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    json.dump(log, open(LOG_FILE, 'w'), indent=2, ensure_ascii=False)
    print(f"\n📝 已保存: {LOG_FILE}")

def show_log():
    if not os.path.exists(LOG_FILE):
        print("\n📭 尚无配码记录"); return
    log = json.load(open(LOG_FILE))
    print(f"\n📋 已配码 ({len(log)}台):")
    for k, v in sorted(log.items()):
        ok = "✅" if v['success'] else "❌"
        print(f"  [{k}] {v['room']} → {v['addr_hex']} {ok} ({v['time']})")

def main():
    print("="*50); print(" G24RTS485 窗帘电机配码工具"); print("="*50)
    show_log(); print()
    for n, (a, r) in ADDR_MAP.items():
        print(f"  [{n}] → 0x{a:02X} ({r})")
    print()
    choice = int(input("选择电机编号 (1-7): "))
    target, room = ADDR_MAP[choice]
    print(f"\n配码: {room} → 0x{target:02X}")
    ser = serial.Serial(SERIAL_PORT, 9600, timeout=1)
    ok = False
    for reg in [0x0100, 0x0000, 0x0200]:
        for fc in [6, 16]:
            frame = bytes([1, fc, (reg>>8)&0xFF, reg&0xFF])
            if fc == 6: frame += bytes([(target>>8)&0xFF, target&0xFF])
            else: frame += bytes([0, 1, 2, (target>>8)&0xFF, target&0xFF])
            frame += crc16(frame)
            if try_write(ser, frame, f"FC{fc:02X} reg=0x{reg:04X}"): ok = True
            time.sleep(0.15)
    time.sleep(0.3)
    read = bytes([target, 0x03, 0x00, 0x00, 0x00, 0x01]) + crc16(bytes([target, 0x03, 0x00, 0x00, 0x00, 0x01]))
    ser.write(read); time.sleep(0.3)
    v = bool(ser.read(256))
    ser.close()
    if v: print(f"\n🎉 成功！贴标签: {room} (0x{target:02X})")
    else: print(f"\n⚠️ 无验证响应，断电重启试试")
    save_log(choice, target, room, ok and v)

if __name__ == "__main__":
    main()
