"""
订单 ↔ IoT 场景联动服务
预订/支付/入住/退房流程中自动触发设备场景。
"""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.store_dev import Room, Store
from models.operations import Order
from services import ha_service

logger = logging.getLogger("gaoan.erp.order_iot")


async def on_order_paid(order_id: str, db: AsyncSession) -> dict:
    """订单支付成功 → 触发预开模式（提前开空调+背景音乐）"""
    r = await db.execute(select(Order).where(Order.orderId == order_id))
    order = r.scalar_one_or_none()
    if not order:
        return {"success": False, "message": "订单不存在"}

    if not order.roomId:
        logger.info(f"订单{order_id}无关联房间，跳过IoT联动")
        return {"success": True, "message": "跳过（无房间）"}

    logger.info(f"[IoT联动] 订单{order_id}已支付 → 房间{order.roomId} 预开模式")
    try:
        result = await ha_service.activate_scene(order.roomId, "PreOpen")
        if result.get("success"):
            logger.info(f"  预开模式触发成功: {result.get('message')}")
        else:
            logger.warning(f"  预开模式触发异常: {result.get('message')}")
        return result
    except Exception as e:
        logger.error(f"  预开模式触发失败: {e}")
        return {"success": False, "message": str(e)}


async def on_order_checkin(order_id: str, db: AsyncSession) -> dict:
    """客人签到入住 → 触发迎宾模式（全开灯+窗帘+空调+音乐）"""
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
    try:
        result = await ha_service.activate_scene(order.roomId, scene_name)
        if result.get("success"):
            logger.info(f"  {scene_name}触发成功")
        else:
            logger.warning(f"  {scene_name}触发异常: {result.get('message')}")
        return result
    except Exception as e:
        logger.error(f"  {scene_name}触发失败: {e}")
        return {"success": False, "message": str(e)}


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
