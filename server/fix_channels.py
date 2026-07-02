import re
f = 'C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/server/services/ha_service.py'
with open(f, 'r', encoding='utf-8') as fh:
    c = fh.read()

# Replace feilengcui channels - remove 壁灯
old = '"feilengcui": [  # 翡冷翠5通道\n        ("ch1", "吊灯"), ("ch2", "筒灯"), ("ch3", "风扇"),\n        ("ch4", "换气扇"), ("ch5", "壁灯"),\n    ],'
new = '"feilengcui": [  # 翡冷翠4通道\n        ("ch1", "吊灯"), ("ch2", "筒灯"), ("ch3", "风扇"),\n        ("ch4", "换气扇"),\n    ],'
c = c.replace(old, new)

with open(f, 'w', encoding='utf-8') as fh:
    fh.write(c)
print('OK')
