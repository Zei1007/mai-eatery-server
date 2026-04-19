"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("image", sa.String(), nullable=True),
    )
    op.create_table(
        "inventory",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("minThreshold", sa.Float(), nullable=False),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("total", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
    )
    op.create_table(
        "order_items",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("order_id", sa.String(), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("productId", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
    )
    op.create_table(
        "stock_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("itemId", sa.String(), nullable=False),
        sa.Column("change", sa.Float(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("reason", sa.String(), nullable=True),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("details", sa.String(), nullable=False),
        sa.Column("user", sa.String(), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("stock_logs")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("inventory")
    op.drop_table("products")
