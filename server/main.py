"""
高岸ERP API Server V1.0
FastAPI backend with SQLite, JWT auth, image processing, IoT integration.
"""
import sys
from pathlib import Path

# Ensure server/ is on the path
sys.path.insert(0, str(Path(__file__).parent))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import settings
from database import init_db, close_db
from routers import auth, products, rooms, scan, shop, iot, finance
from routers import brand, store_dev, operations, marketing, finance_ext, hr, tech


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
uploads_dir = Path(settings.upload_dir)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Static file paths
staff_mp_dir = Path(__file__).parent.parent / "prototype" / "staff-mp"
admin_web_dist = Path(__file__).parent.parent / "prototype" / "admin-web-dist"

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(rooms.router)
app.include_router(scan.router)
app.include_router(shop.router)
app.include_router(iot.router)
app.include_router(finance.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.version, "app": settings.app_name}


# SPA catch-all: serve frontend pages for any non-API route (must be last)
if staff_mp_dir.exists() or admin_web_dist.exists():

    @app.api_route("/{full_path:path}", methods=["GET"])
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)

        # Staff-mp pages (店员端)
        if full_path.startswith("staff/") or full_path == "staff":
            if staff_mp_dir.exists():
                file_path = staff_mp_dir / "/".join(full_path.split("/")[1:])
                if file_path.exists() and file_path.is_file():
                    return FileResponse(str(file_path))
                return FileResponse(str(staff_mp_dir / "pages" / "dashboard" / "index.html"))

        # Customer-mp pages (客人端)
        if full_path.startswith("customer/") or full_path == "customer":
            customer_mp_dir = Path(__file__).parent.parent / "prototype" / "customer-mp"
            if customer_mp_dir.exists():
                file_path = customer_mp_dir / "/".join(full_path.split("/")[1:])
                if file_path.exists() and file_path.is_file():
                    return FileResponse(str(file_path))

        # Admin-web SPA (管理后台)
        if admin_web_dist.exists():
            # Check if it's a static asset file
            asset_path = admin_web_dist / full_path
            if asset_path.exists() and asset_path.is_file():
                return FileResponse(str(asset_path))
            return FileResponse(str(admin_web_dist / "index.html"))

        return JSONResponse({"detail": "Not Found"}, status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
