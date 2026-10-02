from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

PREFIX = "VPL"
SERIAL_SEQUENCE = "member_serial_seq"


def luhn_check_digit(digits: str) -> int:
    total = 0
    # Doubling starts from the rightmost payload digit, since the check digit is appended after it.
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - total % 10) % 10


def format_member_id(year: int, serial: int) -> str:
    yy = f"{year % 100:02d}"
    sn = f"{serial:05d}"
    return f"{PREFIX}-{yy}-{sn}-{luhn_check_digit(yy + sn)}"


def is_valid_member_id(member_id: str) -> bool:
    parts = member_id.strip().upper().split("-")
    if len(parts) != 4 or parts[0] != PREFIX:
        return False
    _, yy, sn, check = parts
    if not (len(yy) == 2 and len(sn) == 5 and len(check) == 1 and (yy + sn + check).isdigit()):
        return False
    return luhn_check_digit(yy + sn) == int(check)


async def generate_member_id(db: AsyncSession) -> str:
    serial = (await db.execute(select(func.nextval(SERIAL_SEQUENCE)))).scalar_one()
    return format_member_id(datetime.now(timezone.utc).year, serial)
