# Fix: replace BGM-only complement with full device complement
with open('C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/server/services/ha_service.py', 'r', encoding='utf-8') as f:
    c = f.read()

old = '''        # 补充缺失的背景音乐控件
        bgm_rooms = set()
        for d in devices:
            if d['type'] in ('Speaker', 'BGM'):
                bgm_rooms.add(d['room_id'])
        for room in ROOMS:
            if room['room_id'] not in bgm_rooms:
                ha_room = HA_ROOM_MAP.get(room['room_id'], '')
                devices.append({
                    'device_id': f'bgm_{room["room_id"]}',
                    'room_id': room['room_id'],
                    'type': 'Speaker',
                    'name': f'{room["name"]}背景音乐',
                    'ha_entity_id': f'switch.{ha_room}_bgm',
                    'protocol': 'IP', 'status': 'Online',
                    'attributes': {'playing': False, 'volume': 30},
                })
        return devices'''

new = '''        # 补充缺失的必需设备（HA未定义但ERP需要的）
        existing_types = {}
        for d in devices:
            existing_types.setdefault(d['room_id'], set()).add(d['type'])
        for room in ROOMS:
            rid = room['room_id']
            types = existing_types.get(rid, set())
            ha_room = HA_ROOM_MAP.get(rid, '')
            # 背景音乐
            if 'Speaker' not in types and 'BGM' not in types:
                devices.append({
                    'device_id': 'bgm_' + rid, 'room_id': rid,
                    'type': 'Speaker', 'name': room['name'] + '背景音乐',
                    'ha_entity_id': 'switch.' + ha_room + '_bgm',
                    'protocol': 'IP', 'status': 'Online',
                    'attributes': {'playing': False, 'volume': 30},
                })
            # 白沙瓦风扇
            if 'Fan' not in types and rid == 'RM004':
                devices.append({
                    'device_id': 'fan_' + rid, 'room_id': rid,
                    'type': 'Fan', 'name': room['name'] + '风扇',
                    'ha_entity_id': 'switch.' + ha_room + '_relay_fan',
                    'protocol': 'Modbus', 'status': 'Online',
                    'attributes': {'speed': 0},
                })
            # 翡冷翠换气扇
            if 'ExhaustFan' not in types and rid == 'RM003':
                devices.append({
                    'device_id': 'ef_' + rid, 'room_id': rid,
                    'type': 'ExhaustFan', 'name': room['name'] + '换气扇',
                    'ha_entity_id': 'switch.' + ha_room + '_relay_ef',
                    'protocol': 'Modbus', 'status': 'Online',
                    'attributes': {'speed': 0},
                })
        return devices'''

if old in c:
    c = c.replace(old, new)
    with open('C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/server/services/ha_service.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK: full device complement added')
else:
    print('ERROR: old text not found')
    # Show what's around that area
    idx = c.find('补充缺失')
    if idx >= 0:
        print(c[idx:idx+50])
