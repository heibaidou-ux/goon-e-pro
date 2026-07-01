"""Add balance column to users table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-01
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('balance', sa.Float(), nullable=True, server_default='0.0'))
    op.execute("UPDATE users SET balance = 0.0 WHERE balance IS NULL")


def downgrade():
    op.drop_column('users', 'balance')
