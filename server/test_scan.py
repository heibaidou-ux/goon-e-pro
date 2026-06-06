#!/usr/bin/env python
"""
高岸ERP 扫码消费API 测试脚本 — 覆盖8个API全部功能
Usage: python test_scan.py [--base-url http://localhost:8000]
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
    print(f"高岸ERP 扫码消费API测试 - {BASE_URL}")

    # ── 前置：登录获取token ──
    section("0. 前置：登录")
    login = req("POST", "/api/auth/login", {"username": "admin", "password": "admin123"})
    token = login.get("access_token", "")
    check(bool(token), f"Login OK: {login.get('user', {}).get('display_name')}")
    print()

    # ═══════════════════════════════════════════
    # API 1: 单房间QR码生成
    # ═══════════════════════════════════════════
    section("API 1 — GET /api/scan/qrcode/{room_id} 单房间QR码生成")

    # Get a known room first
    rooms = req("GET", "/api/rooms")
    if not rooms or len(rooms) == 0:
        print("  [SKIP] 无可用房间")
        return
    first_room_id = rooms[0]["room_id"]
    first_room_name = rooms[0]["name"]

    # Without table
    qr1 = req("GET", f"/api/scan/qrcode/{first_room_id}")
    check(qr1.get("roomId") == first_room_id, f"roomId = {first_room_id}")
    check(bool(qr1.get("qrPayload")), "qrPayload不为空")
    check(f"room_id={first_room_id}" in qr1.get("qrPayload", ""), "qrPayload含room_id参数")
    check(qr1.get("roomName") == first_room_name, f"roomName = {first_room_name}")
    print(f"     Payload: {qr1.get('qrPayload')}")
    print(f"     ScanUrl: {qr1.get('scanUrl')}")

    # With table
    qr2 = req("GET", f"/api/scan/qrcode/{first_room_id}?tableId=T1")
    check("table_id=T1" in qr2.get("qrPayload", ""), "qrPayload含table_id参数")

    # Non-existent room
    qr3 = req("GET", "/api/scan/qrcode/NONEXIST")
    check(qr3.get("error") == 404, "不存在的房间返回404")
    print()

    # ═══════════════════════════════════════════
    # API 2: 批量QR码生成
    # ═══════════════════════════════════════════
    section("API 2 — GET /api/scan/qrcode/batch 批量QR码生成")

    stores = req("GET", "/api/stores")
    if stores and len(stores) > 0:
        store_id = stores[0]["store_id"]
        batch = req("GET", f"/api/scan/qrcode/batch?storeId={store_id}", token=token)
        check(batch.get("storeId") == store_id, f"storeId = {store_id}")
        check(batch.get("count", 0) > 0, f"房间数 = {batch.get('count')}")
        check(len(batch.get("items", [])) > 0, "items列表不为空")
        for item in batch.get("items", [])[:2]:
            print(f"     - {item['roomName']}: {item['qrPayload'][:60]}...")
    else:
        print("  [SKIP] 无可用门店")
    print()

    # ═══════════════════════════════════════════
    # API 3: 换码
    # ═══════════════════════════════════════════
    section("API 3 — POST /api/scan/qrcode/{room_id}/renew 更换房间码")

    renew = req("POST", f"/api/scan/qrcode/{first_room_id}/renew", token=token)
    check(renew.get("roomId") == first_room_id, f"roomId = {first_room_id}")
    check(bool(renew.get("newRoomCode")), "newRoomCode不为空")
    check(bool(renew.get("qrPayload")), "新qrPayload不为空")
    check(renew.get("oldRoomCode") != renew.get("newRoomCode"), "新旧码不同")
    print(f"     旧码: {renew.get('oldRoomCode')}")
    print(f"     新码: {renew.get('newRoomCode')}")

    # Non-existent room
    renew2 = req("POST", "/api/scan/qrcode/NONEXIST/renew", token=token)
    check(renew2.get("error") == 404, "不存在的房间返回404")
    print()

    # ═══════════════════════════════════════════
    # API 4: 防误扫验证
    # ═══════════════════════════════════════════
    section("API 4 — GET /api/scan/room/{room_id} 防误扫验证")

    status = req("GET", f"/api/scan/room/{first_room_id}")
    check(status.get("roomId") == first_room_id, f"roomId = {first_room_id}")
    check(status.get("status") in ("Active", "Inactive", "Maintenance"), f"status = {status.get('status')}")
    check("message" in status, "有提示消息")
    print(f"     房间: {status.get('roomName')} ({status.get('status')})")
    print(f"     消息: {status.get('message')}")
    print(f"     有进行中订单: {status.get('hasActiveOrder')}")

    # Non-existent room
    status2 = req("GET", "/api/scan/room/NONEXIST")
    check(status2.get("error") == 404, "不存在的房间返回404")
    print()

    # ═══════════════════════════════════════════
    # API 5: 扫码下单/加购
    # ═══════════════════════════════════════════
    section("API 5 — POST /api/scan/order 扫码下单加购")

    # Prerequisite: room must have an active order. Try to create one first.
    # First check if there's already an active order
    active_orders = req("GET", "/api/orders/active")
    active_room_id = None
    if active_orders and len(active_orders) > 0:
        active_room_id = active_orders[0].get("room_id") or active_orders[0].get("roomId")
    if not active_room_id:
        # Create a room order first
        room_for_order = rooms[0]
        new_order = req("POST", "/api/orders", {
            "room_id": room_for_order["room_id"],
            "customer_name": "扫码测试",
            "date": "2026-06-06",
            "start_time": "10:00",
            "end_time": "12:00",
            "duration": 2.0,
            "total_amount": room_for_order.get("price_per_hour", 100) * 2,
            "source": "到店",
        }, token=token)
        if new_order.get("order_id"):
            active_room_id = room_for_order["room_id"]
            print(f"     创建房间订单: {new_order.get('order_id')}")

    if active_room_id:
        # Get product for order
        products = req("GET", "/api/products", token=token)
        items_payload = []
        if products.get("items") and len(products["items"]) > 0:
            p = products["items"][0]
            items_payload = [{"productId": p["id"], "quantity": 2, "unitPrice": p.get("retail_price", 68)}]
        else:
            # Fallback product
            items_payload = [{"productId": "T001", "quantity": 1, "unitPrice": 68}]

        scan_order = req("POST", "/api/scan/order", {
            "roomId": active_room_id,
            "storeId": stores[0]["store_id"] if stores else "ST001",
            "items": items_payload,
            "source": "ScanQR",
        })
        check(scan_order.get("orderId", "").startswith("SCAN") or bool(scan_order.get("orderId")),
              f"扫码订单已创建: {scan_order.get('orderId')} — ¥{scan_order.get('totalAmount')}")
        check(scan_order.get("itemCount", 0) > 0, f"商品数: {scan_order.get('itemCount')}")
        check(len(scan_order.get("tags", [])) > 0, f"标签: {scan_order.get('tags')}")
        print(f"     订单号: {scan_order.get('orderNumber')}")
        print(f"     消息: {scan_order.get('message')}")

        # Store for later cancel test
        global _scan_order_id
        _scan_order_id = scan_order.get("orderId", "")
    else:
        print("  [SKIP] 未找到进行中的房间订单，无法测试下单")
        _scan_order_id = ""
    print()

    # ═══════════════════════════════════════════
    # API 6: 查询房间账单
    # ═══════════════════════════════════════════
    section("API 6 — GET /api/scan/bill/{room_id} 查询房间账单")

    bill = req("GET", f"/api/scan/bill/{first_room_id}")
    check(bill.get("roomId") == first_room_id, f"roomId = {first_room_id}")
    check("billSummary" in bill, "有billSummary字段")
    check("scanOrders" in bill, "有scanOrders字段")
    summary = bill.get("billSummary", {})
    print(f"     房费: ¥{summary.get('roomCharge', 0)}")
    print(f"     加购总计: ¥{summary.get('scanTotal', 0)}")
    print(f"     待结算: ¥{summary.get('pendingPayment', 0)}")
    print(f"     订单数: {len(bill.get('scanOrders', []))}")

    # Non-existent room
    bill2 = req("GET", "/api/scan/bill/NONEXIST")
    check(bill2.get("error") == 404, "不存在的房间返回404")

    # Store bill for settle test
    global _bill_room_id
    _bill_room_id = first_room_id
    if bill.get("scanOrders") and len(bill["scanOrders"]) > 0:
        _bill_room_id = first_room_id
        _has_orders = True
    else:
        _has_orders = False
    print()

    # ═══════════════════════════════════════════
    # API 7: 撤销扫码订单
    # ═══════════════════════════════════════════
    section("API 7 — PUT /api/scan/order/{order_id}/cancel 撤销扫码订单")

    if _scan_order_id:
        cancel = req("PUT", f"/api/scan/order/{_scan_order_id}/cancel")
        check(cancel.get("success"), f"撤销成功: {cancel.get('orderId')}")
        check("无需退款" in cancel.get("refundStatus", ""), f"退款状态: {cancel.get('refundStatus')}")
        check(cancel.get("cancelledAt") is not None, "有撤销时间")
        print(f"     消息: {cancel.get('message')}")
    else:
        print("  [SKIP] 无可撤销订单")
    print()

    # ═══════════════════════════════════════════
    # API 8: 挂账结算
    # ═══════════════════════════════════════════
    section("API 8 — POST /api/scan/bill/{room_id}/settle 挂账结算")

    if _bill_room_id and _has_orders:
        # Full settle
        settle = req("POST", f"/api/scan/bill/{_bill_room_id}/settle", {
            "paymentMethod": "WxPay",
            "settleItems": "all",
            "useMemberBalance": False,
            "issueInvoice": True,
        })
        check(settle.get("success"), f"结算成功")
        check(settle.get("ordersSettled", 0) > 0, f"结算订单数: {settle.get('ordersSettled')}")
        check(settle.get("totalAmount", 0) > 0, f"结算金额: ¥{settle.get('totalAmount')}")
        print(f"     支付方式: {settle.get('paymentMethod')}")
        print(f"     金额: ¥{settle.get('totalAmount')} (余额: ¥{settle.get('memberBalanceUsed')} + 实付: ¥{settle.get('paymentAmount')})")
        if settle.get("invoiceNumber"):
            print(f"     发票号: {settle.get('invoiceNumber')}")
        print(f"     消息: {settle.get('message')}")

        # Verify bill is now settled
        bill_after = req("GET", f"/api/scan/bill/{_bill_room_id}")
        if bill_after.get("billStatus"):
            check(bill_after["billStatus"] == "Settled", f"结算后状态: {bill_after['billStatus']}")
    else:
        print("  [SKIP] 无可结算账单")

    # ═══════════════════════════════════════════
    # 汇总
    # ═══════════════════════════════════════════
    section("测试完成")
    print(f"  8个扫码消费API已覆盖测试")
    print(f"  API Base: {BASE_URL}")
    print(f"  详见 Swagger 文档: {BASE_URL}/docs")
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()
    BASE_URL = args.base_url

    # Global for cross-test data
    global _scan_order_id, _bill_room_id, _has_orders
    _scan_order_id = ""
    _bill_room_id = ""
    _has_orders = False

    main()
