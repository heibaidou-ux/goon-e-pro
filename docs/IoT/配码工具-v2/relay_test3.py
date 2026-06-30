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
    """addr=地址, func=功能码, reg=16位寄存器地址, val=附加数据"""
    q = struct.pack('>BH', addr, func)  # 不对，Modbus是 big-endian
    return q

# 直接用 struct.pack 构造
def make_query(addr, func, reg, data=b''):
    """通用Modbus查询构建"""
    q = struct.pack('>BHB', addr, reg, func)  # 不，应该是 addr, func, reg_bytes
    return q

# 直接手写
def scan_reg(addr, reg):
    q = bytes([addr, 3]) + struct.pack('>HH', reg, 1)
    crc = 0xFFFF
    for b in q:
        crc ^= b
        for _ in range(8):
            if crc & 1: crc = (crc>>1)^0xA001
            else: crc >>= 1
    q += struct.pack('<H', crc)
    ser.reset_input_buffer()
    ser.write(q)
    time.sleep(0.15)
    r = ser.read(10)
    return r

def set_coil(addr, ch, on):
    q = bytes([addr, 5]) + struct.pack('>HB', ch, 0xFF if on else 0x00) + b'\x00'
    crc = 0xFFFF
    for b in q:
        crc ^= b
        for _ in range(8):
            if crc & 1: crc = (crc>>1)^0xA001
            else: crc >>= 1
    q += struct.pack('<H', crc)
    ser.reset_input_buffer()
    ser.write(q)
    time.sleep(0.3)
    return ser.read(10)

# 扫描
print("\n--- 扫描 ---", flush=True)
for reg, name in [(0x03EA, '继电器'), (0x1000, '面板')]:
    r = scan_reg(0x13, reg)
    print(f"  扫描{name}: {'回复='+r.hex(' ') if r else '无回复'}", flush=True)

# 逐通道开关
print("\n--- 逐通道测试 ---", flush=True)
for ch in range(8):
    print(f"\n通道{ch} 开...", flush=True)
    r = set_coil(0x13, ch, True)
    print(f"  回复: {r.hex(' ')}" if r else "  无回复", flush=True)
    time.sleep(2)
    
    print(f"通道{ch} 关", flush=True)
    r = set_coil(0x13, ch, False)
    print(f"  回复: {r.hex(' ')}" if r else "  无回复", flush=True)
    time.sleep(1)

ser.close()
print("\n✅ 完成，听哪个通道有咔哒声", flush=True)
input("按回车退出...")
