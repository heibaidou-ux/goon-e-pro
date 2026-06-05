"""
盈隆店 HA IoT — 模拟墙面面板按键

模拟实体墙上的物理面板按键操作，每个按键对应一个 input_boolean 的 toggle。
实际部署后，物理面板 → 聚英继电器 → HA 将替代此脚本的模拟。

用法：
  python simulate_panel.py list                         # 列出所有面板按键
  python simulate_panel.py press <entity_id>             # 模拟按下按键
  python simulate_panel.py batch <entity_id1> <id2> ...  # 批量操作
"""
import os, sys
import requests
from dotenv import load_dotenv

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://192.168.2.65:8123")
TOKEN = os.getenv("HA_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 面板按键分组（按区域）
PANEL_GROUPS = {
    "大茶室": [
        "input_boolean.大茶室按键1",
        "input_boolean.大茶室按键2",
        "input_boolean.大茶室按键3",
        "input_boolean.大茶室按键4",
        "input_boolean.大茶室按键5",
        "input_boolean.大茶室按键6",
        "input_boolean.大茶室背景灯",
        "input_boolean.大茶室吊灯",
    ],
    "大会议室": [
        "input_boolean.大会议室总开关",
        "input_boolean.大会议室筒灯1",
        "input_boolean.大会议室筒灯2",
        "input_boolean.大会议室吊灯",
    ],
    "中茶室": [
        "input_boolean.中茶室总开关",
        "input_boolean.中茶室筒灯",
        "input_boolean.中茶室吊灯",
        "input_boolean.中茶室背景灯",
    ],
    "小茶室": [
        "input_boolean.小茶室总开关",
        "input_boolean.小茶室筒灯",
        "input_boolean.小茶室排风扇",
    ],
}


def toggle_entity(entity_id):
    """切换实体状态"""
    url = f"{HA_URL}/api/services/input_boolean/toggle"
    r = requests.post(url, json={"entity_id": entity_id}, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def get_state(entity_id):
    """获取实体状态"""
    r = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def list_panels():
    """列出所有面板及按键状态"""
    all_entities = []
    for group_name, entities in PANEL_GROUPS.items():
        all_entities.extend(entities)

    print("面板按键状态：\n")
    for group_name, entities in PANEL_GROUPS.items():
        print(f"【{group_name}】")
        for eid in entities:
            try:
                s = get_state(eid)
                state = s["state"]
                name = s["attributes"].get("friendly_name", eid)
                icon = "🟢" if state == "on" else "⚫"
                print(f"  {icon} {eid:45s} [{state:3s}] {name}")
            except Exception:
                print(f"  ❓ {eid:45s} [???] 连接失败")
        print()


def press_button(entity_id):
    """模拟按下单个按键（toggle）"""
    try:
        result = toggle_entity(entity_id)
        new_state = result[0].get("state", "unknown")
        icon = "🟢" if new_state == "on" else "⚫"
        print(f"{icon} {entity_id} → {new_state}")
    except Exception as e:
        print(f"✗ {entity_id} 失败: {e}")


def batch_press(entity_ids):
    """批量操作"""
    for eid in entity_ids:
        press_button(eid)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list":
        list_panels()
    elif cmd == "press":
        if len(sys.argv) < 3:
            print("请指定 entity_id")
            return
        press_button(sys.argv[2])
    elif cmd == "batch":
        if len(sys.argv) < 3:
            print("请指定至少一个 entity_id")
            return
        batch_press(sys.argv[2:])
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
