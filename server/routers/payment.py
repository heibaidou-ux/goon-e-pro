"""微信支付 API — 统一下单/回调/查询"""
import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from config import settings
from database import get_db
from models.user import User
from services.auth_service import get_current_user
from services.payment_service import unified_order, get_pay_params, order_query, verify_notify

logger = logging.getLogger("gaoan.erp.payment")
router = APIRouter(prefix="/api/payment", tags=["支付"])

def _gen_order_no() -> str:
    return f"GA{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:10].upper()}"

@router.post("/wxpay/unified-order")
async def wxpay_unified_order(request: Request, current_user: User = Depends(get_current_user)):
    if not settings.wechat_mch_id or not settings.wechat_pay_key:
        raise HTTPException(400, "微信支付未配置")
    data = await request.json()
    total_fee = data.get("total_fee", 0)
    body = data.get("body", "高岸茶室-消费")
    openid = data.get("openid", "")
    if total_fee <= 0:
        raise HTTPException(400, "金额无效")
    if not openid and settings.debug:
        openid = "mock_openid_dev"
    out_trade_no = _gen_order_no()
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
async def wxpay_notify(request: Request):
    xml_data = (await request.body()).decode("utf-8")
    try:
        result = verify_notify(xml_data, settings.wechat_pay_key)
    except RuntimeError:
        return Response(content='<xml><return_code><![CDATA[FAIL]]></return_code></xml>', media_type="application/xml")
    if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
        logger.info(f"支付成功: {result.get('out_trade_no')}, ¥{int(result.get('total_fee',0))/100:.2f}")
    return Response(content='<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>', media_type="application/xml")

@router.get("/wxpay/query/{out_trade_no}")
async def wxpay_query(out_trade_no: str):
    if not settings.wechat_mch_id or not settings.wechat_pay_key:
        raise HTTPException(400, "微信支付未配置")
    result = await order_query(settings.wechat_appid, settings.wechat_mch_id, settings.wechat_pay_key, out_trade_no)
    return {"trade_state": result.get("trade_state",""), "total_fee": result.get("total_fee",0), "transaction_id": result.get("transaction_id","")}
