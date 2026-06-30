"""微信支付 API — 统一下单/回调/查询，含IoT场景联动"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import settings
from database import get_db
from models.user import User
from models.operations import Order
from services.auth_service import get_current_user
from services.payment_service import unified_order, get_pay_params, order_query, verify_notify
from services.order_iot import on_order_paid

logger = logging.getLogger("gaoan.erp.payment")
router = APIRouter(prefix="/api/payment", tags=["支付"])

def _gen_order_no() -> str:
    return f"GA{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:10].upper()}"

@router.post("/wxpay/unified-order")
async def wxpay_unified_order(request: Request, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not settings.wechat_mch_id or not settings.wechat_pay_key:
        raise HTTPException(400, "微信支付未配置")
    data = await request.json()
    total_fee = data.get("total_fee", 0)
    body = data.get("body", "高岸茶室-消费")
    order_id = data.get("order_id", "")  # 关联的房间订单ID（IoT联动用）
    if total_fee <= 0:
        raise HTTPException(400, "金额无效")

    # 获取openid（优先级: 1.用户已存储的wechat_openid 2.wx_login传的code 3.debug模式mock）
    openid = current_user.wechat_openid if current_user else ""
    wx_code = data.get("wx_code", "")
    if not openid and wx_code and settings.wechat_secret:
        # 用前端wx.login()获取的code换取openid
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"https://api.weixin.qq.com/sns/jscode2session"
                    f"?appid={settings.wechat_appid}&secret={settings.wechat_secret}"
                    f"&js_code={wx_code}&grant_type=authorization_code"
                )
                wx_data = resp.json()
                openid = wx_data.get("openid", "")
                logger.info(f"支付换取openid成功: {openid}")
        except Exception as e:
            logger.error(f"支付换取openid失败: {e}")
    if not openid and settings.debug:
        openid = "mock_openid_dev"
    if not openid:
        raise HTTPException(400, "微信支付需要用户先微信登录")
    out_trade_no = _gen_order_no()

    # 关联订单：将out_trade_no存入订单
    if order_id:
        r = await db.execute(select(Order).where(Order.orderId == order_id))
        order = r.scalar_one_or_none()
        if order:
            order.platformOrderId = out_trade_no
            await db.commit()
            logger.info(f"支付关联订单: {order_id} → {out_trade_no}")

    try:
        result = await unified_order(
            appid=settings.wechat_appid, mch_id=settings.wechat_mch_id,
            key=settings.wechat_pay_key, openid=openid,
            out_trade_no=out_trade_no, total_fee=total_fee,
            body=body, notify_url=f"{settings.erp_base_url}/api/payment/wxpay/notify",
        )
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    prepay_id = result.get("prepay_id", "")
    pay_params = get_pay_params(prepay_id, settings.wechat_appid, settings.wechat_pay_key)
    return {"success": True, "out_trade_no": out_trade_no, "prepay_id": prepay_id, "pay_params": pay_params}

@router.post("/wxpay/notify")
async def wxpay_notify(request: Request, db: AsyncSession = Depends(get_db)):
    xml_data = (await request.body()).decode("utf-8")
    try:
        result = verify_notify(xml_data, settings.wechat_pay_key)
    except RuntimeError:
        return Response(content='<xml><return_code><![CDATA[FAIL]]></return_code></xml>', media_type="application/xml")
    if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
        out_trade_no = result.get("out_trade_no", "")
        total_fee = int(result.get("total_fee", 0))
        logger.info(f"支付成功: {out_trade_no}, ¥{total_fee/100:.2f}")

        # 查找关联订单 → 更新状态 + IoT联动
        if out_trade_no:
            r = await db.execute(
                select(Order).where(Order.platformOrderId == out_trade_no)
            )
            order = r.scalar_one_or_none()
            if order and order.status == "PendingPay":
                order.status = "PendingUse"
                order.paidAmount = round(total_fee / 100, 2)
                order.paymentMethod = "WxPay"
                order.paymentTime = datetime.utcnow()
                import random
                order.doorPassword = str(random.randint(1000, 9999))
                await db.commit()
                logger.info(f"订单{order.orderId}已通过支付回调更新为PendingUse")
                # IoT联动：支付成功 → 预开模式
                await on_order_paid(order.orderId, db)
            elif not order:
                logger.warning(f"支付回调: 未找到关联订单 out_trade_no={out_trade_no}")

    return Response(content='<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>', media_type="application/xml")

@router.get("/wxpay/query/{out_trade_no}")
async def wxpay_query(out_trade_no: str):
    if not settings.wechat_mch_id or not settings.wechat_pay_key:
        raise HTTPException(400, "微信支付未配置")
    result = await order_query(settings.wechat_appid, settings.wechat_mch_id, settings.wechat_pay_key, out_trade_no)
    return {"trade_state": result.get("trade_state",""), "total_fee": result.get("total_fee",0), "transaction_id": result.get("transaction_id","")}
