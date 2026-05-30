#!/usr/bin/env python
"""
高岸ERP API 综合测试脚本
Usage: python test_api.py [--base-url http://localhost:8000]
"""
import sys
import json
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"

def req(method, path, data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()}

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check(ok, msg):
    print(f"  {'[OK]' if ok else '[FAIL]'} {msg}")
    return ok

def main():
    print(f"高岸ERP API 测试 - {BASE_URL}")

    # 1. Health check
    section("1. 健康检查")
    health = req("GET", "/api/health")
    check(health.get("status") == "ok", f"API status: {health.get('status')}")

    # 2. Login
    section("2. 认证测试")
    login = req("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
    token = login.get("access_token", "")
    check(bool(token), f"Login OK: {login.get('user', {}).get('display_name')}")
    check(login.get("user", {}).get("role") == "admin", f"Role: admin")

    # 3. Categories
    section("3. 商品分类")
    cats = req("GET", "/api/products/categories")
    check(len(cats) > 0, f"Categories: {len(cats)}")
    for c in cats:
        print(f"     - {c['name']} ({len(c['subcategories'])} subcats)")

    # 4. Products
    section("4. 商品管理")
    products = req("GET", "/api/products", token=token)
    total = products.get("total", 0)
    check(total > 0, f"Products: {total}")
    if total > 0:
        first = products["items"][0]
        print(f"     First: {first['name']} (¥{first['retail_price']})")
        # Test single product
        pid = first["id"]
        single = req("GET", f"/api/products/{pid}")
        check(single.get("name") == first["name"], f"Get product #{pid}: {single.get('name')}")

    # 5. Stores & Rooms
    section("5. 门店与房间")
    stores = req("GET", "/api/stores")
    check(len(stores) > 0, f"Stores: {len(stores)}")
    for s in stores:
        print(f"     - {s['name']} ({len(s['rooms'])} rooms)")
        for r in s["rooms"]:
            print(f"         {r['name']} (¥{r['price_per_hour']}/h, cap:{r['capacity']})")

    rooms = req("GET", "/api/rooms")
    check(len(rooms) > 0, f"All rooms: {len(rooms)}")

    room = req("GET", f"/api/rooms/{rooms[0]['room_id']}")
    check(room.get("name") == rooms[0]["name"], f"Get room: {room.get('name')}")

    # 6. Orders
    section("6. 订单管理")
    orders = req("GET", "/api/orders", token=token)
    print(f"     Orders: {len(orders)}")

    active = req("GET", "/api/orders/active")
    print(f"     Active: {len(active)}")

    # 7. Create test order
    section("7. 创建订单")
    if len(rooms) > 0:
        new_order = req("POST", "/api/orders", {
            "room_id": rooms[0]["room_id"],
            "customer_name": "测试客人",
            "date": "2026-05-24",
            "start_time": "14:00",
            "end_time": "16:00",
            "duration": 2.0,
            "total_amount": rooms[0]["price_per_hour"] * 2,
            "scene": "品茶",
            "source": "到店",
        })
        check(new_order.get("order_id", "").startswith("ORD"),
              f"Order created: {new_order.get('order_id')} - ¥{new_order.get('total_amount')}")

    # 8. User info
    section("8. 用户信息")
    me = req("GET", "/api/auth/me", token=token)
    check(me.get("username") == "admin", f"Current user: {me.get('display_name')} ({me.get('role')})")

    # 9. IoT Devices
    section("9. IoT设备管理")
    iot_health = req("GET", "/api/iot/health")
    check(iot_health.get("status") == "ok", f"IoT mode: {iot_health.get('mode')}, devices: {iot_health.get('device_count')}")

    iot_devices = req("GET", "/api/iot/devices")
    check(len(iot_devices) > 0, f"IoT devices: {len(iot_devices)}")
    for d in iot_devices[:3]:
        print(f"     - {d['name']} ({d['type']}, {d['status']})")

    # IoT device filter by room
    room_devices = req("GET", "/api/iot/devices?room_id=RM001")
    check(len(room_devices) == 6, f"RM001 devices: {len(room_devices)}")

    # IoT device filter by type
    ac_devices = req("GET", "/api/iot/devices?type=AC")
    check(len(ac_devices) == 5, f"AC devices: {len(ac_devices)}")

    # IoT Stats
    iot_stats = req("GET", "/api/iot/stats")
    check(iot_stats.get("total", 0) > 0, f"Stats: {iot_stats['total']} devices, {iot_stats['online_rate']}% online")

    # IoT Scenes
    scenes = req("GET", "/api/iot/scenes")
    check(len(scenes) > 0, f"Scenes: {len(scenes)}")
    for s in scenes:
        print(f"     - {s['label']} ({s['trigger_type']}, {len(s['rules'])} steps)")

    # IoT Alerts
    alerts = req("GET", "/api/iot/alerts")
    print(f"     Alerts: {len(alerts)}")

    # IoT Device Control (requires auth)
    section("10. IoT设备控制")
    if len(iot_devices) > 0:
        ctrl = req("POST", "/api/iot/control", {
            "device_id": iot_devices[0]["device_id"],
            "action": "on",
            "params": {"brightness": 80},
        }, token=token)
        check(ctrl.get("success"), f"Control {iot_devices[0]['name']} → {ctrl.get('message', '')}")

    # IoT Scene Activation
    section("11. IoT场景激活")
    scene_result = req("POST", "/api/iot/scenes/activate", {
        "room_id": "RM001",
        "scene": "Meeting",
    }, token=token)
    check(scene_result.get("success"), f"Scene: {scene_result.get('scene_label', '')} ({scene_result.get('success_count', 0)}/{scene_result.get('total_steps', 0)} steps OK)")

    # Summary
    section("测试完成")
    print(f"  API Base: {BASE_URL}")
    print(f"  Login: admin / admin123")
    print(f"  See Swagger docs: {BASE_URL}/docs")
    print()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()
    BASE_URL = args.base_url
    main()
