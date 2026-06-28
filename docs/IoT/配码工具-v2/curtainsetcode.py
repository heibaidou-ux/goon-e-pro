#!/usr/bin/env python3
"""
杜亚485窗帘电机地址管理工具 (Windows版)
协议: 0x55 + ID_L + ID_H + FC + Data + CRC16 (CRC含0x55头字节)
默认地址: 0xFEFE (广播)
FC01=读寄存器, FC02=写地址, FC03=控制(0x01开/0x02关/0x03停)
"""

import json, os, socket, serial, struct, sys, time
from argparse import ArgumentParser

CONFIG_PATH = os.path.expanduser("~/curtain_addresses.json")
GATEWAY_HOST = "100.111.33.20"
GATEWAY_PORT = 8801
SERIAL_PORT = "COM4"
SERIAL_BAUD = 9600

ROOM_LAYOUT = {
    "大茶室-A组": {"planned_addrs": [0x14, 0x15, 0x16], "note": "A组3台"},
    "中茶室-B组": {"planned_addrs": [0x17, 0x18, 0x19], "note": "B组3台中2台正常"},
    "小茶室-C组": {"planned_addrs": [0x1A], "note": "翡冷翠，方向与标准相反"},
}

def crc16(data):
    c = 0xFFFF
    for b in data:
        c ^= b
        for _ in range(8):
            c = ((c >> 1) ^ 0xA001) if c & 1 else (c >> 1)
    return struct.pack("<H", c)

def dooya_frame(id_l, id_h, fc, data=b""):
    payload = bytes([id_l, id_h, fc]) + data
    crc_val = crc16(bytes([0x55]) + payload)
    return bytes([0x55]) + payload + crc_val

def via_serial(frame, wait=0.3, timeout=0.5):
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=timeout)
        ser.reset_input_buffer()
        ser.write(frame)
        time.sleep(wait)
        resp = ser.read(256)
        ser.close()
        return resp
    except Exception as e:
        print("  \u274c \u4e32\u53e3\u9519\u8bef:", e)
        return b""

def load_addrs():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}

def save_addrs(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("  \U0001f4dd \u5df2\u4fdd\u5b58\u5230", CONFIG_PATH)

def addr_key(id_l, id_h):
    return "0x%02X%02X" % (id_l, id_h)

def cmd_scan():
    print("\n\U0001f50d \u626b\u63cf485\u603b\u7ebf\u7a97\u5e18\u7535\u673a...")
    found = False
    for id_l, id_h in [(0xFE, 0xFE)] + [(a, 0) for a in range(0x10, 0x30)]:
        resp = via_serial(dooya_frame(id_l, id_h, 0x01, bytes([0x02, 1])), 0.2, 0.3)
        if resp and len(resp) >= 3:
            k = addr_key(id_l, id_h)
            print("  \u2705 %s: %s" % (k, resp.hex().upper()))
            found = True
    if not found:
        print("  \u26a0\ufe0f \u672a\u53d1\u73b0\u7535\u673a\uff08\u53ef\u80fd\u9700\u8981\u6309\u914d\u7801\u6309\u94ae\uff09")

def cmd_write(new_addr_hex):
    new_val = int(new_addr_hex, 16)
    k = addr_key(new_val, 0)
    print("\n\u270d\ufe0f \u5199\u5730\u5740: 0xFEFE \u2192", k)
    print("  \u26a0\ufe0f \u8bf7\u786e\u4fdd\u7535\u673a\u5df2\u6309\u914d\u7801\u6309\u94ae(\u542c\u5230\u6ef4\u6ef4\u540e\u677e\u5f00)")
    print("  \u23f3 3\u79d2\u540e\u53d1\u9001...")
    time.sleep(3)
    resp = via_serial(dooya_frame(0xFE, 0xFE, 0x02, bytes([new_val, 0])), 0.5, 1)
    print("  %s: %s" % ("\u2705 \u6709\u54cd\u5e94" if resp else "\u26a0\ufe0f \u65e0\u54cd\u5e94", resp.hex().upper() if resp else ""))
    resp = via_serial(dooya_frame(new_val, 0, 0x01, bytes([0x02, 1])), 0.3, 0.5)
    if resp:
        print("  \u2705 %s \u9a8c\u8bc1\u901a\u8fc7" % k)
        addrs = load_addrs()
        addrs[k] = {"id_l": new_val, "id_h": 0, "addr_hex": k, "room": "", "note": "",
                    "direction_reversed": False, "written_at": time.strftime("%Y-%m-%d %H:%M:%S")}
        save_addrs(addrs)
    else:
        print("  \u274c %s \u9a8c\u8bc1\u5931\u8d25" % k)

def cmd_control(action, addr_hex="FEFE"):
    amap = {"open": 0x01, "close": 0x02, "stop": 0x03}
    if action not in amap:
        return
    print("\n\U0001f3af %s \u2192 %s" % (action, addr_hex))
    # 直接串口发（先STOP再方向）
    id_l = int(addr_hex[:2], 16)
    id_h = int(addr_hex[2:], 16)
    via_serial(dooya_frame(id_l, id_h, 0x03, bytes([0x03])), 0.15, 0.3)  # STOP
    time.sleep(0.15)
    val = amap[action]
    if val != 0x03:
        via_serial(dooya_frame(id_l, id_h, 0x03, bytes([val])), 0.3, 0.5)
print("  \u2705 \u5df2\u53d1\u9001")

def cmd_status(addr_hex="FEFE"):
    id_l = int(addr_hex[:2], 16)
    id_h = int(addr_hex[2:], 16)
    k = addr_key(id_l, id_h)
    addrs = load_addrs()
    info = addrs.get(k, {})
    print("\n\U0001f4ca %s  \u623f\u95f4:%s \u5907\u6ce8:%s \u53cd\u8f6c:%s" % (
        k, info.get("room",""), info.get("note",""), info.get("direction_reversed",False)))
    for reg, name in [(0x02, "\u4f4d\u7f6e"), (0x05, "\u72b6\u6001")]:
        resp = via_serial(dooya_frame(id_l, id_h, 0x01, bytes([reg, 1])), 0.3, 0.5)
        print("  %s: %s" % (name, resp.hex().upper() if resp else "\u65e0\u54cd\u5e94"))

def cmd_list():
    addrs = load_addrs()
    if not addrs:
        print("\n\U0001f4ed \u65e0\u8bb0\u5f55"); return
    print("\n\U0001f4cb \u7a97\u5e18\u5730\u5740 (%d\u53f0)" % len(addrs))
    for k, v in sorted(addrs.items()):
        rev = " \U0001f504" if v.get("direction_reversed") else ""
        print("  %s  \u2192 %s%s  %s" % (k, v.get("room",""), rev, v.get("note","")))

def main():
    p = ArgumentParser(description="\u675c\u4e9a485\u7a97\u5e18\u5730\u5740\u7ba1\u7406")
    p.add_argument("action", nargs="?", choices=["scan","write","batch-write","open","close","stop","status","list"])
    p.add_argument("addr", nargs="?", default="FEFE")
    a = p.parse_args()
    if a.action == "scan": cmd_scan()
    elif a.action == "write": cmd_write(a.addr)
    elif a.action == "batch-write": print("\u6682\u672a\u5b9e\u73b0\uff0c\u7528 write \u5355\u4e2a\u5199\u5165")
    elif a.action in ("open","close","stop"): cmd_control(a.action, a.addr)
    elif a.action == "status": cmd_status(a.addr)
    elif a.action == "list": cmd_list()
    else: p.print_help()

if __name__ == "__main__":
    main()
