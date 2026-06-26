"""
微信支付服务层
支持: JSAPI支付（小程序内）、支付回调、退款
"""
import hashlib
import hmac
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from xml.etree import ElementTree

import httpx

logger = logging.getLogger("gaoan.erp.payment")


def _nonce_str() -> str:
    return uuid.uuid4().hex[:16]


def _sign(params: dict, key: str) -> str:
    """微信支付 MD5 签名"""
    sorted_keys = sorted(params.keys())
    raw = "&".join(f"{k}={params[k]}" for k in sorted_keys if params[k] != "")
    raw += f"&key={key}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def _build_xml(data: dict) -> str:
    root = ElementTree.Element("xml")
    for k, v in data.items():
        child = ElementTree.SubElement(root, k)
        child.text = str(v)
    return ElementTree.tostring(root, encoding="utf-8").decode()


def _parse_xml(xml_str: str) -> dict:
    root = ElementTree.fromstring(xml_str)
    return {child.tag: child.text for child in root}


async def unified_order(
    appid: str,
    mch_id: str,
    key: str,
    openid: str,
    out_trade_no: str,
    total_fee: int,  # 单位：分
    body: str,
    notify_url: str,
    spbill_create_ip: str = "127.0.0.1",
) -> dict:
    """
    微信支付统一下单 (JSAPI)
    返回 prepay_id 供前端调起支付
    """
    params = {
        "appid": appid,
        "mch_id": mch_id,
        "nonce_str": _nonce_str(),
        "body": body,
        "out_trade_no": out_trade_no,
        "total_fee": str(total_fee),
        "spbill_create_ip": spbill_create_ip,
        "notify_url": notify_url,
        "trade_type": "JSAPI",
        "openid": openid,
    }
    params["sign"] = _sign(params, key)
    xml_data = _build_xml(params)

    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, content=xml_data, headers={"Content-Type": "text/xml"})
        result = _parse_xml(resp.text)

    if result.get("return_code") != "SUCCESS":
        raise RuntimeError(f"微信支付通信失败: {result.get('return_msg')}")
    if result.get("result_code") != "SUCCESS":
        raise RuntimeError(f"微信支付业务失败: {result.get('err_code_des')}")

    return result


def get_pay_params(prepay_id: str, appid: str, key: str) -> dict:
    """生成小程序端调起支付所需的参数包"""
    params = {
        "appId": appid,
        "timeStamp": str(int(datetime.utcnow().timestamp())),
        "nonceStr": _nonce_str(),
        "package": f"prepay_id={prepay_id}",
        "signType": "MD5",
    }
    pay_sign = _sign(
        {
            "appId": params["appId"],
            "timeStamp": params["timeStamp"],
            "nonceStr": params["nonceStr"],
            "package": params["package"],
            "signType": params["signType"],
        },
        key,
    )
    params["paySign"] = pay_sign
    return params


async def order_query(
    appid: str, mch_id: str, key: str, out_trade_no: str
) -> dict:
    """查询订单状态"""
    params = {
        "appid": appid,
        "mch_id": mch_id,
        "out_trade_no": out_trade_no,
        "nonce_str": _nonce_str(),
    }
    params["sign"] = _sign(params, key)
    xml_data = _build_xml(params)
    url = "https://api.mch.weixin.qq.com/pay/orderquery"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, content=xml_data, headers={"Content-Type": "text/xml"})
        result = _parse_xml(resp.text)
    return result


async def refund(
    appid: str,
    mch_id: str,
    key: str,
    out_trade_no: str,
    out_refund_no: str,
    total_fee: int,
    refund_fee: int,
    cert_path: str = "",
) -> dict:
    """微信退款（需要商户证书）"""
    params = {
        "appid": appid,
        "mch_id": mch_id,
        "nonce_str": _nonce_str(),
        "out_trade_no": out_trade_no,
        "out_refund_no": out_refund_no,
        "total_fee": str(total_fee),
        "refund_fee": str(refund_fee),
    }
    params["sign"] = _sign(params, key)
    xml_data = _build_xml(params)
    url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
    async with httpx.AsyncClient(timeout=15, verify=cert_path or None) as client:
        resp = await client.post(url, content=xml_data, headers={"Content-Type": "text/xml"})
        result = _parse_xml(resp.text)
    return result


def verify_notify(xml_data: str, key: str) -> dict:
    """验证支付回调签名，返回解析后的数据"""
    result = _parse_xml(xml_data)
    sign = result.pop("sign", "")
    expected = _sign(result, key)
    if sign != expected:
        raise RuntimeError("回调签名验证失败")
    result["sign"] = sign
    return result
