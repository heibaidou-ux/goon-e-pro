import logging
from pathlib import Path
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings

logger = logging.getLogger("gaoan.erp.db")

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# ── SQLite 优化：WAL模式 + 外键 + 忙等待超时 ──
@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in settings.database_url:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """初始化数据库：运行迁移或创建表（幂等操作）。"""
    from models import all_models  # noqa: ensure all models registered

    # 优先尝试 Alembic 迁移（生产环境有 migration chain 时使用）
    alembic_ini = Path(__file__).parent / "alembic.ini"
    if alembic_ini.exists():
        try:
            from alembic.config import Config
            from alembic import command
            alembic_cfg = Config(str(alembic_ini))
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
            command.upgrade(alembic_cfg, "head")
            logger.info("数据库迁移完成 (alembic upgrade head)")
            return
        except Exception as e:
            logger.warning(f"Alembic迁移失败，回退到 create_all: {e}")

    # 回退方案：create_all（IF NOT EXISTS，幂等安全）
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建/验证完成 (create_all)")


async def close_db():
    await engine.dispose()
