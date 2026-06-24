"""
高岸ERP 小程序码/二维码生成服务
- 开发模式: 用 qrcode 库生成本地二维码（指向小程序页面路径）
- 生产模式: 调用微信官方 API (wxacode.getUnlimited) 生成小程序码
"""
import io
import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger("gaoan.erp.qrcode")

# ── 生产模式：微信小程序码 API ──

async def get_wechat_access_token(appid: str, secret: str) -> str:
    """获取微信接口调用凭据"""
    import httpx
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            raise RuntimeError("微信API不可用")
        data = resp.json()
        if "errcode" in data and data["errcode"] != 0:
            raise RuntimeError(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
        return data.get("access_token", "")


async def generate_wechat_miniprogram_code(
    page: str,
    scene: str = "",
    appid: str = "",
    secret: str = "",
    width: int = 280,
    is_hybrid: bool = False,
) -> bytes:
    """
    调用微信 wxacode.getUnlimited 接口生成小程序码
    - page: 页面路径（如 "pages/scan-landing/scan-landing"）
    - scene: 场景值（如 "roomId=RM001&storeId=ST001"）
    - 返回 PNG 图片二进制数据
    """
    access_token = await get_wechat_access_token(appid, secret)
    url = f"https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={access_token}"

    payload = {
        "scene": scene,
        "page": page,
        "width": width,
        "check_path": False,  # 不检查路径，允许未上传的页面
        "env_version": "trial" if is_hybrid else "release",
    }

    import httpx
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(url, json=payload)
        content_type = resp.headers.get("content-type", "")

        if "image" in content_type:
            return resp.content  # PNG bytes
        else:
            # 错误响应
            err = resp.json()
            raise RuntimeError(f"生成小程序码失败: {err.get('errmsg', '未知错误')}")


# ── 开发模式：本地QR码生成 ──

def generate_local_qrcode(
    data: str,
    box_size: int = 10,
    border: int = 2,
    with_logo: bool = False,
) -> bytes:
    """
    生成本地二维码 PNG 图片
    - data: 编码内容（页面路径或URL）
    - 返回 PNG 图片二进制数据
    """
    import qrcode
    from qrcode.image.styledpil import StyledPilImage

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H if with_logo else qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    if with_logo:
        try:
            from PIL import Image
            img = qr.make_image(image_factory=StyledPilImage, embeded_image_path=None)
        except Exception:
            img = qr.make_image(fill_color="black", back_color="white")
    else:
        img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_room_qrcode_data(
    page_path: str,
    room_id: str,
    store_id: str,
    table_id: Optional[str] = None,
    base_url: str = "",
) -> str:
    """生成二维码编码内容 — 小程序页面路径 + 参数"""
    params = f"room_id={room_id}&store_id={store_id}"
    if table_id:
        params += f"&table_id={table_id}"

    if base_url:
        # H5模式：生成完整URL
        return f"{base_url}/prototype/customer-mp/pages/scan-landing/index.html?{params}"

    # 小程序模式：直接编码页面路径
    return f"{page_path}?{params}"


def save_qrcode_file(
    data: str,
    output_dir: str,
    filename: str,
    box_size: int = 10,
) -> str:
    """保存二维码到文件，返回文件路径"""
    os.makedirs(output_dir, exist_ok=True)
    img_bytes = generate_local_qrcode(data, box_size)
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    return filepath
