"""
盈隆店 HA IoT — 查询所有实体状态
用法：python query_states.py [entity_id]
"""
import os, sys, json
import requests
from dotenv import load_dotenv

load_dotenv()
HA_URL = os.getenv("HA_URL", "http://192.168.2.65:8123")
TOKEN = os.getenv("HA_TOKEN")

if not TOKEN:
    print("错误：未设置 HA_TOKEN，请复制 .env.example 为 .env 并填入Token")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def get_all_states():
    """获取所有实体状态"""
    r = requests.get(f"{HA_URL}/api/states", headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def get_state(entity_id):
    """获取指定实体状态"""
    r = requests.get(f"{HA_URL}/api/states/{entity_id}", headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def main():
    if len(sys.argv) > 1:
        entity_id = sys.argv[1]
        state = get_state(entity_id)
        print(json.dumps(state, ensure_ascii=False, indent=2))
    else:
        states = get_all_states()
        # 过滤出 input_boolean 和相关的实体
        relevant = [
            s for s in states
            if s["entity_id"].startswith("input_boolean.")
            or s["entity_id"].startswith("input_number.")
            or s["entity_id"].startswith("sensor.")
            or s["entity_id"].startswith("binary_sensor.")
        ]
        if not relevant:
            print("未找到相关实体，显示所有状态：")
            relevant = states

        for s in relevant:
            eid = s["entity_id"]
            state = s["state"]
            attrs = s.get("attributes", {})
            friendly = attrs.get("friendly_name", eid)
            print(f"  {eid}")
            print(f"    名称: {friendly}")
            print(f"    状态: {state}")
            if "unit_of_measurement" in attrs:
                print(f"    单位: {attrs['unit_of_measurement']}")
            print()


if __name__ == "__main__":
    main()
