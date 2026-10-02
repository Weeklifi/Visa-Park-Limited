"""add member_id (ID card number) to users

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Frozen copy of app.services.member_id so this migration never changes behaviour if app code does.
def _luhn_check_digit(digits: str) -> int:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - total % 10) % 10


def _format_member_id(year: int, serial: int) -> str:
    yy = f"{year % 100:02d}"
    sn = f"{serial:05d}"
    return f"VPL-{yy}-{sn}-{_luhn_check_digit(yy + sn)}"


def upgrade() -> None:
    op.execute("CREATE SEQUENCE member_serial_seq START 1")
    op.add_column("users", sa.Column("member_id", sa.String(16), nullable=True))

    bind = op.get_bind()
    rows = bind.execute(
        sa.text("SELECT id, created_at FROM users ORDER BY created_at, id")
    ).fetchall()
    for serial, (user_id, created_at) in enumerate(rows, start=1):
        bind.execute(
            sa.text("UPDATE users SET member_id = :mid WHERE id = :id"),
            {"mid": _format_member_id(created_at.year, serial), "id": user_id},
        )
    if rows:
        bind.execute(sa.text("SELECT setval('member_serial_seq', :n)"), {"n": len(rows)})

    op.alter_column("users", "member_id", nullable=False)
    op.create_unique_constraint("uq_users_member_id", "users", ["member_id"])
    op.create_index("idx_users_member_id", "users", ["member_id"])


def downgrade() -> None:
    op.drop_index("idx_users_member_id", table_name="users")
    op.drop_constraint("uq_users_member_id", "users", type_="unique")
    op.drop_column("users", "member_id")
    op.execute("DROP SEQUENCE member_serial_seq")
