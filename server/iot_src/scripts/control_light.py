"""
盈隆店 HA IoT — 灯光控制

用法：
  python control_light.py list                      # 列出所有灯光
  python control_light.py on <entity_id>            # 开灯
  python control_light.py off <entity_id>           # 关灯
  python control_light.py toggle <entity_id>        # 切换
  python control_light.py scene <场景名>             # 应用场景
"""
import os, sys, json
import requests
from dotenv import load_dotenv

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://192.168.2.65:8123")
TOKEN = os.getenv("HA_TOKEN")

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 场景预设：房间 -> [(entity_id, target_state)]
SCENES = {
    "大茶室_全开": [
        ("input_boolean.大茶室总开关", "on"),
        ("input_boolean.大茶室筒灯", "on"),
        ("input_boolean.大茶室吊灯", "on"),
        ("input_boolean.大茶室背景灯", "on"),
    ],
    "大茶室_全关": [
        ("input_boolean.大茶室总开关", "off"),
        ("input_boolean.大茶室筒灯", "off"),
        ("input_boolean.大茶室吊灯", "off"),
        ("input_boolean.大茶室背景灯", "off"),
    ],
    "大会议_全开": [
        ("input_boolean.大会议室总开关", "on"),
        ("input_boolean.大会议室筒灯1", "on"),
        ("input_boolean.大会议室筒灯2", "on"),
        ("input_boolean.大会议室吊灯", "on"),
    ],
    "大会议_全关": [
        ("input_boolean.大会议室总开关", "off"),
        ("input_boolean.大会议室筒灯1", "off"),
        ("input_boolean.大会议室筒灯2", "off"),
        ("input_boolean.大会议室吊灯", "off"),
    ],
    "中茶室_全开": [
        ("input_boolean.中茶室总开关", "on"),
        ("input_boolean.中茶室筒灯", "on"),
        ("input_boolean.中茶室吊灯", "on"),
        ("input_boolean.中茶室背景灯", "on"),
    ],
    "中茶室_全关": [
        ("input_boolean.中茶室总开关", "off"),
        ("input_boolean.中茶室筒灯", "off"),
        ("input_boolean.中茶室吊灯", "off"),
        ("input_boolean.中茶室背景灯", "off"),
    ],
    "小茶室_全开": [
        ("input_boolean.小茶室总开关", "on"),
        ("input_boolean.小茶室筒灯", "on"),
        ("input_boolean.小茶室排风扇", "on"),
    ],
    "小茶室_全关": [
        ("input_boolean.小茶室总开关", "off"),
        ("input_boolean.小茶室筒灯", "off"),
        ("input_boolean.小茶室排风扇", "off"),
    ],
}


def call_service(domain, service, entity_id):
    """调用HA服务"""
    url = f"{HA_URL}/api/services/{domain}/{service}"
    payload = {"entity_id": entity_id}
    r = requests.post(url, json=payload, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def list_lights():
    """查询所有灯光实体"""
    r = requests.get(f"{HA_URL}/api/states", headers=HEADERS, timeout=10)
    r.raise_for_status()
    lights = [s for s in r.json() if s["entity_id"].startswith("input_boolean.")]
    if not lights:
        print("未找到 input_boolean 实体（HA未连接或配置有误）")
        return
    for s in lights:
        name = s["attributes"].get("friendly_name", s["entity_id"])
        print(f"  {s['entity_id']:45s} [{s['state']:3s}] {name}")
    print(f"\n共 {len(lights)} 个开关实体")


def apply_scene(name):
    """应用场景"""
    if name not in SCENES:
        print(f"未知场景：{name}")
        print(f"可用场景：{list(SCENES.keys())}")
        return
    actions = SCENES[name]
    print(f"应用场景：{name}")
    for entity_id, target in actions:
        service = "turn_on" if target == "on" else "turn_off"
        try:
            call_service("input_boolean", service, entity_id)
            print(f"  ✓ {entity_id} → {target}")
        except Exception as e:
            print(f"  ✗ {entity_id} 失败: {e}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list":
        list_lights()
    elif cmd == "scene":
        if len(sys.argv) < 3:
            print("请指定场景名")
            return
        apply_scene(" ".join(sys.argv[2:]))
    elif cmd in ("on", "off", "toggle"):
        if len(sys.argv) < 3:
            print("请指定 entity_id")
            return
        entity_id = sys.argv[2]
        service_map = {"on": "turn_on", "off": "turn_off", "toggle": "toggle"}
        result = call_service("input_boolean", service_map[cmd], entity_id)
        print(f"{cmd.upper()} {entity_id} → {result[0].get('state', 'ok')}")
    else:
        print(f"未知命令: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
