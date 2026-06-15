from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserOut, Token, LoginRequest, PhoneLoginRequest
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
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="用户已被禁用")

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
