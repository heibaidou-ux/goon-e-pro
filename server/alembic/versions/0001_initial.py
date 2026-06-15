"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-16
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 初始schema由 SQLAlchemy Base.metadata.create_all() 创建
    # 此迁移文件标记数据库版本起点
    pass


def downgrade() -> None:
    pass
