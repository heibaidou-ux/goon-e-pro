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
from routers import auth, products, rooms, shop, iot


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

# Admin-web static files SPA handler (catch-all for non-API routes)
admin_web_dist = Path(__file__).parent.parent / "prototype" / "admin-web-dist"

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(rooms.router)
app.include_router(shop.router)
app.include_router(iot.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": settings.version, "app": settings.app_name}


# SPA catch-all: serve admin-web for any non-API route (must be last)
if admin_web_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(admin_web_dist / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("uploads/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(str(admin_web_dist / "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
