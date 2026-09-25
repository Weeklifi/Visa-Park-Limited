"""add phone_number and nid to users

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(20), nullable=True, unique=True))
    op.add_column("users", sa.Column("nid", sa.String(30), nullable=True, unique=True))
    op.create_index("idx_users_phone", "users", ["phone_number"])
    op.create_index("idx_users_nid", "users", ["nid"])


def downgrade() -> None:
    op.drop_index("idx_users_nid", table_name="users")
    op.drop_index("idx_users_phone", table_name="users")
    op.drop_column("users", "nid")
    op.drop_column("users", "phone_number")
