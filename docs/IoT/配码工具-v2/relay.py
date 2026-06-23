import serial, time, struct

port = input("COM端口号（如4）: ").strip()
port = f'COM{port}' if port.isdigit() else port
ser = serial.Serial(port, 9600, timeout=1)

def cmd(addr, func, reg, val):
    q = bytes([addr, func, (reg>>8)&0xFF, reg&0xFF])
    if func == 5:
        q += b'\xff\x00' if val else b'\x00\x00'
    crc = 0xFFFF
    for b in q:
        crc ^= b
        for _ in range(8):
            if crc & 1: crc = (crc>>1)^0xA001
            else: crc >>= 1
    return q + struct.pack('<H', crc)

print("1. 灯开  2. 灯关  3. 退出")
while True:
    c = input("\n选择: ").strip()
    if c == '1':
        ser.write(cmd(0x13, 5, 0, True))
        time.sleep(0.1)
        r = ser.read(8)
        print(f"回复: {r.hex(' ')}" if r else "✅ 灯开")
    elif c == '2':
        ser.write(cmd(0x13, 5, 0, False))
        time.sleep(0.1)
        r = ser.read(8)
        print(f"回复: {r.hex(' ')}" if r else "✅ 灯关")
    elif c == '3':
        break
ser.close()
