with open('C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/server/services/ha_service.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Find the friendly name block and add reclassification before return
old_start = '    friendly_name = attrs.get("friendly_name", "")'
new_block = '''    friendly_name = attrs.get("friendly_name", "")
    if not friendly_name:
        ha_room_name = _ha_entity_to_room(entity_id)
        for ha_rn, erp_id in HA_ROOM_REVERSE.items():
            if ha_rn == ha_room_name:
                relay_config = RELAY_CHANNELS.get(ha_rn, [])
                for ch, desc in relay_config:
                    ch_str = ch.replace("ch", "")
                    if "_ch" + ch_str in entity_id or "_" + ch in entity_id:
                        friendly_name = desc
                        break
                if not friendly_name:
                    domain = entity_id.split(".")[0] if "." in entity_id else ""
                    short_name = entity_name.split(".")[1] if "." in entity_id else entity_id
                    friendly_name = short_name[:16]
    # 根据friendly_name重分类设备类型（HA的switch无法区分灯/风扇/功放）
    if device_type == "Light" and friendly_name:
        fn_lower = friendly_name.lower()
        if '换气扇' in fn_lower or '排气' in fn_lower:
            device_type = "ExhaustFan"
        elif '风扇' in fn_lower:
            device_type = "Fan"
        elif '功放' in fn_lower or '音箱' in fn_lower or '音响' in fn_lower or '喇叭' in fn_lower:
            device_type = "Speaker"
    return {'''

idx = c.find(old_start)
if idx >= 0:
    end = c.find('    return {', idx)
    c = c[:idx] + new_block + c[end+12:]
    with open('C:/Users/王晓东/Documents/高岸管理/盈隆/高岸智能管理系统/高岸ERP/server/services/ha_service.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print('OK: reclassification added')
else:
    print('ERROR')
