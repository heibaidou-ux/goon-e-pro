import serial, time, struct

port = input("COM端口号（回车=COM4）: ").strip()
if not port: port = 'COM4'
elif port.isdigit(): port = f'COM{port}'

try:
    ser = serial.Serial(port, 9600, timeout=1)
    print(f"✅ 打开 {port} 成功", flush=True)
except Exception as e:
    print(f"❌ 打开 {port} 失败: {e}", flush=True)
    input("按回车退出...")
    exit()

def calc_crc(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1: crc = (crc>>1)^0xA001
            else: crc >>= 1
    return struct.pack('<H', crc)

def mkcmd(addr, func, reg, val=b''):
    q = bytes([addr, func, 0, reg]) + val
    q += calc_crc(q)
    return q

# 先扫描地址0x13
for reg, desc in [(0x03EA, '继电器'), (0x1000, '面板')]:
    q = mkcmd(0x13, 3, reg, b'\x00\x01')
    ser.reset_input_buffer()
    ser.write(q)
    time.sleep(0.15)
    r = ser.read(10)
    print(f"  扫 {desc}(0x{reg:04X}): {'回复='+r.hex(' ') if r else '无回复'}", flush=True)

print("\n逐通道测试 继电器@0x13，听天花板咔哒声 ↓")
ser.timeout = 0.5

for ch in range(8):
    # 开
    q = mkcmd(0x13, 5, ch, b'\xff\x00')
    ser.reset_input_buffer()
    ser.write(q)
    time.sleep(0.2)
    r = ser.read(8)
    print(f"  通道{ch} 开 → {'回复='+r.hex(' ') if r else '发送成功，等2秒...'}", flush=True)
    time.sleep(2)
    
    # 关
    q = mkcmd(0x13, 5, ch, b'\x00\x00')
    ser.reset_input_buffer()
    ser.write(q)
    r = ser.read(8)
    print(f"  通道{ch} 关 → {'回复='+r.hex(' ') if r else '关闭'}", flush=True)
    time.sleep(1)

ser.close()
print("\n✅ 完成，告诉我哪个通道有咔哒声", flush=True)
input("按回车退出...")
