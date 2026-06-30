from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import httpx
import uuid

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserOut, Token, LoginRequest, PhoneLoginRequest, WeChatLoginRequest
from config import settings
from services.auth_service import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, get_current_user, validate_password_strength,
)
from services.rate_limit import limiter, rate_limit

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserOut)
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db), _: bool = Depends(rate_limit(5, 60))):
    # 密码强度校验
    pwd_err = validate_password_strength(data.password)
    if pwd_err:
        raise HTTPException(status_code=400, detail=pwd_err)

    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已存在")

    if data.phone:
        result = await db.execute(select(User).where(User.phone == data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="手机号已注册")

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        display_name=data.display_name,
        role=data.role,
        phone=data.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db), _: bool = Depends(rate_limit(10, 60))):
    """账号密码登录（用于店员端/管理后台）"""
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")

    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token, user=UserOut.model_validate(user))


@router.post("/phone-login", response_model=Token)
async def phone_login(request: Request, data: PhoneLoginRequest, db: AsyncSession = Depends(get_db), _: bool = Depends(rate_limit(10, 60))):
    """手机号+验证码登录（用于客人端小程序）"""
    if data.code != "8888" and not settings.debug:
        # 生产环境应从短信服务校验
        raise HTTPException(status_code=401, detail="验证码错误")

    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()

    if not user:
        # 自动注册（手机号首次登录）
        display_name = data.phone[:3] + "****" + data.phone[-4:]
        user = User(
            username="user_" + data.phone[-8:],
            hashed_password=hash_password(data.phone + "_default"),
            display_name=display_name,
            role="guest",
            phone=data.phone,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")

    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token, user=UserOut.model_validate(user))


@router.post("/wechat-login", response_model=Token)
async def wechat_login(request: Request, data: WeChatLoginRequest, db: AsyncSession = Depends(get_db), _: bool = Depends(rate_limit(10, 60))):
    """微信一键登录：前端 wx.login() 获取 code，后端换取 openid，自动创建/登录用户"""
    openid = ""
    nickname = data.nickname or "微信用户"
    avatar = data.avatar or ""

    if settings.wechat_secret and not settings.debug:
        url = (
            f"https://api.weixin.qq.com/sns/jscode2session"
            f"?appid={settings.wechat_appid}"
            f"&secret={settings.wechat_secret}"
            f"&js_code={data.code}&grant_type=authorization_code"
        )
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail="微信登录服务不可用")
            wx_data = resp.json()
            if "errcode" in wx_data and wx_data["errcode"] != 0:
                raise HTTPException(status_code=401, detail=f"微信登录失败: {wx_data.get('errmsg', '未知错误')}")
            openid = wx_data.get("openid", "")
            if not openid:
                raise HTTPException(status_code=401, detail="微信登录失败：未获取到openid")
    else:
        openid = "dev_" + data.code[-12:] if len(data.code) > 12 else "dev_" + uuid.uuid4().hex[:12]

    result = await db.execute(select(User).where(User.wechat_openid == openid))
    user = result.scalar_one_or_none()

    if not user:
        username = "wx_" + openid[-12:] if len(openid) > 12 else "wx_" + uuid.uuid4().hex[:12]
        user = User(
            username=username,
            hashed_password=hash_password(uuid.uuid4().hex),
            display_name=nickname,
            role="guest",
            wechat_openid=openid,
            wechat_nickname=nickname,
            wechat_avatar=avatar,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        if nickname:
            user.wechat_nickname = nickname
        if avatar:
            user.wechat_avatar = avatar
        if nickname and (not user.display_name or user.display_name.startswith("wx_")):
            user.display_name = nickname
        await db.commit()

    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")

    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token_out = create_refresh_token({"sub": user.username})
    return Token(access_token=access_token, refresh_token=refresh_token_out, user=UserOut.model_validate(user))


@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """刷新Token（使用refresh_token）"""
    from fastapi import Body
    from jose import JWTError, jwt
    data = await request.json()
    refresh_token_str = data.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="缺少refresh_token")

    try:
        payload = jwt.decode(
            refresh_token_str, settings.secret_key,
            algorithms=[settings.algorithm],
            audience="gaoan-erp-refresh",
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的refresh_token")
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="refresh_token无效或已过期")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在")

    access_token = create_access_token({"sub": user.username, "role": user.role})
    new_refresh = create_refresh_token({"sub": user.username})
    return Token(access_token=access_token, refresh_token=new_refresh, user=UserOut.model_validate(user))


@router.post("/change-password")
async def change_password(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """修改密码"""
    data = await request.json()
    old_pwd = data.get("old_password")
    new_pwd = data.get("new_password")

    if not old_pwd or not new_pwd:
        raise HTTPException(status_code=400, detail="请提供旧密码和新密码")

    if not verify_password(old_pwd, user.hashed_password):
        raise HTTPException(status_code=400, detail="旧密码错误")

    pwd_err = validate_password_strength(new_pwd)
    if pwd_err:
        raise HTTPException(status_code=400, detail=pwd_err)

    user.hashed_password = hash_password(new_pwd)
    await db.commit()
    return {"success": True, "message": "密码已修改"}


@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user
