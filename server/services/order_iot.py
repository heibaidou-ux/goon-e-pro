"""
订单 ↔ IoT 场景联动服务
预订/支付/入住/退房流程中自动触发设备场景。

#1 修改：支付成功不再立即开空调，而是检测是否在预定前5分钟内
   由前端预开调度器（app.js startPreheatScheduler）在预定前5分钟触发。
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.store_dev import Room, Store
from models.operations import Order
from services import ha_service

logger = logging.getLogger("gaoan.erp.order_iot")


async def on_order_paid(order_id: str, db: AsyncSession) -> dict:
    """订单支付成功 → 检查是否在预定前5分钟内，是则触发预开。"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        return {"success": False, "message": "订单不存在"}

    if not order.roomId:
        logger.info(f"订单{order_id}无关联房间，跳过IoT联动")
        return {"success": True, "message": "跳过（无房间）"}

    # 检查是否在预定开始前5分钟内
    now = datetime.utcnow()
    if order.bookingStartTime and order.bookingStartTime > now + timedelta(minutes=5):
        logger.info(f"[IoT联动] 订单{order_id}已支付，预定时间{order.bookingStartTime}距现在>5分钟，不预开")
        return {
            "success": True,
            "message": f"支付成功，预开空调将在预定时间前5分钟自动触发（{order.bookingStartTime - timedelta(minutes=5)}）",
            "scheduled": True,
        }

    logger.info(f"[IoT联动] 订单{order_id}已支付 → 房间{order.roomId} 预开模式")
    try:
        result = await ha_service.activate_scene(order.roomId, "PreOpen")
        if result.get("success"):
            logger.info(f"  预开模式触发成功")
        else:
            logger.warning(f"  预开模式触发异常: {result.get('message')}")
        return result
    except Exception as e:
        logger.error(f"  预开模式触发失败: {e}")
        return {"success": False, "message": str(e)}


async def on_order_checkin(order_id: str, db: AsyncSession) -> dict:
    """客人签到入住 → 触发迎宾模式（全开灯+窗帘+空调+开门）"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        return {"success": False, "message": "订单不存在"}

    if not order.roomId:
        return {"success": True, "message": "跳过（无房间）"}

    # 根据房间类型选择场景
    room_r = await db.execute(select(Room).where(Room.roomId == order.roomId))
    room = room_r.scalar_one_or_none()
    scene_name = "Welcome"
    if room and room.type == "TeaRoom":
        scene_name = "TeaSession"  # 茶室用品茶模式
    elif room and room.type == "MeetingRoom":
        scene_name = "Meeting"     # 会议室用会议模式

    logger.info(f"[IoT联动] 订单{order_id}签到 → 房间{order.roomId} {scene_name}模式")

    # 先开灯开空调（迎宾模式）
    results = []
    try:
        result = await ha_service.activate_scene(order.roomId, scene_name)
        results.append(result)
    except Exception as e:
        logger.error(f"  {scene_name}触发失败: {e}")
        results.append({"success": False, "message": str(e)})

    # #2 再开门锁（开门场景联动）
    try:
        lock_devices = await ha_service.get_devices(room_id=order.roomId, device_type="Lock")
        if lock_devices and len(lock_devices) > 0:
            for lock in lock_devices[:1]:  # 只开第一个门锁
                unlock_result = await ha_service.control_device(lock["device_id"], "unlock")
                results.append(unlock_result)
                if unlock_result.get("success"):
                    logger.info(f"  房间{order.roomId}门锁已远程开启")
    except Exception as e:
        logger.error(f"  开门失败: {e}")

    success_count = sum(1 for r in results if r.get("success"))
    return {
        "success": success_count > 0,
        "message": f"迎宾模式已激活，门锁已{'开启' if success_count > 1 else '尝试开启中'}",
        "results": results,
    }


async def on_order_checkout(order_id: str, db: AsyncSession) -> dict:
    """退房 → 触发退房模式（关所有设备+锁门）"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        return {"success": False, "message": "订单不存在"}
    if not order.roomId:
        return {"success": True, "message": "跳过（无房间）"}

    logger.info(f"[IoT联动] 订单{order_id}退房 → 房间{order.roomId} 退房模式")
    try:
        result = await ha_service.activate_scene(order.roomId, "Checkout")
        if result.get("success"):
            logger.info(f"  退房模式触发成功")
        else:
            logger.warning(f"  退房模式触发异常: {result.get('message')}")
        return result
    except Exception as e:
        logger.error(f"  退房模式触发失败: {e}")
        return {"success": False, "message": str(e)}


async def on_order_cancel(order_id: str, db: AsyncSession) -> dict:
    """取消订单 → 触发节能模式（如果设备已预开）"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order or not order.roomId:
        return {"success": True, "message": "跳过（无房间）"}

    logger.info(f"[IoT联动] 订单{order_id}取消 → 房间{order.roomId} 节能模式")
    try:
        result = await ha_service.activate_scene(order.roomId, "EnergySave")
        return result
    except Exception as e:
        logger.error(f"  节能模式触发失败: {e}")
        return {"success": False, "message": str(e)}
