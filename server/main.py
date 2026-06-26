"""
高岸ERP API Server V1.1
Production-ready FastAPI backend with security, logging, and IoT integration.
"""
import sys
import os
import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure server/ is on the path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import settings
from database import init_db, close_db
from routers import auth, products, rooms, scan, shop, iot, finance, payment
from routers import brand, store_dev, operations, marketing, finance_ext, hr, tech

# ── Logging ──
os.makedirs(Path(__file__).parent / "logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s | %(levelname)-5s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "logs" / "erp.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("gaoan.erp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(Path(settings.upload_dir), exist_ok=True)
    logger.info("=" * 50)
    logger.info(f"高岸ERP {settings.version} 启动")
    logger.info(f"环境: {'开发' if settings.debug else '生产'}")
    logger.info(f"HA模式: {'真实' if settings.ha_token else '模拟'}")
    logger.info(f"CORS: {settings.cors_origins or '全开放(开发模式)'}")
    if settings.debug:
        logger.warning("⚠ Debug模式开启中，仅用于开发")
    await init_db()
    yield
    await close_db()
    logger.info("高岸ERP 已关闭")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

# ── CORS ──
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
else:
    # 开发模式：宽松
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.warning("⚠ CORS全开放（开发模式），生产环境需设置 CORS_ORIGINS")

# ── 请求日志中间件 ──
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    body = None
    if request.method in ("POST", "PUT", "PATCH"):
        try:
            body = await request.json()
            # 脱敏敏感字段
            if isinstance(body, dict):
                for key in ("password", "token", "ha_token", "secret"):
                    if key in body:
                        body[key] = "***"
        except Exception:
            body = "(不可解析)"
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info(
        f"{request.method:6s} {request.url.path:40s} | "
        f"{response.status_code} | {elapsed*1000:5.0f}ms"
        + (f" | body={body}" if body and settings.debug else "")
    )
    return response

# ── Static files ──
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ── Routers ──
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(rooms.router)
app.include_router(scan.router)
app.include_router(shop.router)
app.include_router(iot.router)
app.include_router(finance.router)
app.include_router(brand.router)
app.include_router(store_dev.router)
app.include_router(operations.router)
app.include_router(marketing.router)
app.include_router(finance_ext.router)
app.include_router(hr.router)
app.include_router(tech.router)
app.include_router(payment.router)


@app.get("/api/health")
async def health(request: Request):
    return {"status": "ok", "version": settings.version, "app": settings.app_name}


# ── SPA catch-all ──
PROTOTYPE_DIR = Path(__file__).parent.parent / "prototype"
staff_mp_dir = PROTOTYPE_DIR / "staff-mp"
customer_mp_dir = PROTOTYPE_DIR / "customer-mp"
admin_web_dist = PROTOTYPE_DIR / "admin-web-dist"

if PROTOTYPE_DIR.exists():

    @app.api_route("/{full_path:path}", methods=["GET"])
    async def serve_spa(request: Request, full_path: str):
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Serve prototype files: /prototype/<module>/<path>
        if full_path.startswith("prototype/"):
            rel_path = full_path[len("prototype/"):]
            file_path = PROTOTYPE_DIR / rel_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            parent_dir = file_path.parent if not file_path.suffix else file_path.parent
            dir_index = parent_dir / "index.html"
            if dir_index.exists():
                return FileResponse(str(dir_index))
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        if full_path.startswith("staff/"):
            if staff_mp_dir.exists():
                file_path = staff_mp_dir / "/".join(full_path.split("/")[1:])
                if file_path.exists() and file_path.is_file():
                    return FileResponse(str(file_path))
                return FileResponse(str(staff_mp_dir / "pages" / "dashboard" / "index.html"))

        if full_path.startswith("customer/"):
            if customer_mp_dir.exists():
                file_path = customer_mp_dir / "/".join(full_path.split("/")[1:])
                if file_path.exists() and file_path.is_file():
                    return FileResponse(str(file_path))

        if admin_web_dist.exists():
            asset_path = admin_web_dist / full_path
            if asset_path.exists() and asset_path.is_file():
                return FileResponse(str(asset_path))
            return FileResponse(str(admin_web_dist / "index.html"))

        return JSONResponse({"detail": "Not Found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    logger.info(f"启动服务器: http://0.0.0.0:{os.getenv('PORT', '8000')}")
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=settings.debug)
