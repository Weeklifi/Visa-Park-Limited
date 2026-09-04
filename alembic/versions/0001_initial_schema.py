"""initial schema: users, products, orders, wallet_ledger

Revision ID: 0001
Revises:
Create Date: 2026-09-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # node_path uses the LTREE type, which the installed SQLAlchemy version does not
    # expose as a Python-side type object, so this table is created via raw DDL
    # matching the BRD's blueprint exactly.
    op.execute(
        """
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR(120) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            referral_code VARCHAR(20) UNIQUE NOT NULL,
            layer_level INT NOT NULL CHECK (layer_level BETWEEN 0 AND 4),
            parent_id UUID REFERENCES users(id) ON DELETE RESTRICT,
            node_path LTREE NOT NULL,
            child_count INT NOT NULL DEFAULT 0 CHECK (child_count <= 10),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    op.create_index("idx_users_node_path", "users", ["node_path"], postgresql_using="gist")
    op.create_index("idx_users_parent_id", "users", ["parent_id"])
    op.create_index("idx_users_referral", "users", ["referral_code"])

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("base_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("retail_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("category IN ('TRAVEL_PACKAGE', 'VENDOR_PRODUCT')", name="ck_products_category"),
        sa.CheckConstraint("base_price > 0", name="ck_products_base_price"),
        sa.CheckConstraint("stock_quantity >= 0", name="ck_products_stock"),
    )
    op.create_index("idx_products_category", "products", ["category"])
    op.create_index("idx_products_vendor", "products", ["vendor_id"])

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("unit_base_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("unit_retail_price", sa.Numeric(14, 2), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("quantity > 0", name="ck_orders_quantity"),
        sa.CheckConstraint(
            "status IN ('PENDING', 'PAID', 'COMPLETED', 'CANCELLED', 'REFUNDED')", name="ck_orders_status"
        ),
    )
    op.create_index("idx_orders_buyer", "orders", ["buyer_id"])
    op.create_index("idx_orders_vendor", "orders", ["vendor_id"])
    op.create_index("idx_orders_status", "orders", ["status"])

    op.create_table(
        "wallet_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("entry_type", sa.String(10), nullable=False),
        sa.Column("transaction_reason", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("entry_type IN ('CREDIT', 'DEBIT')", name="ck_ledger_entry_type"),
        sa.CheckConstraint(
            "transaction_reason IN ('BASE_PRINCIPAL', 'VENDOR_MARKUP_SHARE', 'UPWARD_COMMISSION', 'WITHDRAWAL', 'PURCHASE_PAYMENT')",
            name="ck_ledger_reason",
        ),
    )
    op.create_index("idx_ledger_user", "wallet_ledger", ["user_id"])
    op.create_index("idx_ledger_order", "wallet_ledger", ["order_id"])


def downgrade() -> None:
    op.drop_table("wallet_ledger")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("users")
