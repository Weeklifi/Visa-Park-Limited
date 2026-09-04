from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.user import User
from app.models.ledger import WalletLedger
from app.services.hierarchy import get_direct_ancestors
from app.services.pricing import DIRECT_MARKUP_SHARE, UPWARD_POOL_SHARE

CENT = Decimal("0.01")


@dataclass
class CommissionResult:
    order_id: UUID
    vendor_id: UUID
    vendor_total_payout: Decimal
    upward_ancestors_count: int
    per_ancestor_payout: Decimal
    root_remainder_credit: Decimal
    status: str


def _round(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)


async def process_order_commission(db: AsyncSession, order: Order) -> CommissionResult:
    """Executes the FR-3.3/FR-3.4 payout: base principal + vendor markup share to the
    vendor, and the upward pool split equally among direct ancestors with bankers'
    rounding, crediting any residual fraction to the Layer 0 root so total credits
    always equal the full markup pool (zero balance leakage).

    Caller is responsible for wrapping this in a DB transaction and holding row
    locks appropriate to the order/vendor being processed.
    """
    result = await db.execute(select(User).where(User.id == order.vendor_id).with_for_update())
    vendor = result.scalar_one()

    base_total = order.unit_base_price * order.quantity
    retail_total = order.unit_retail_price * order.quantity
    markup_total = retail_total - base_total

    base_principal = _round(base_total)
    vendor_markup_share = _round(markup_total * DIRECT_MARKUP_SHARE)
    upward_pool = _round(markup_total * UPWARD_POOL_SHARE)

    db.add(
        WalletLedger(
            user_id=vendor.id,
            order_id=order.id,
            amount=base_principal,
            entry_type="CREDIT",
            transaction_reason="BASE_PRINCIPAL",
        )
    )

    ancestors = await get_direct_ancestors(db, vendor)  # nearest-parent-first
    ancestor_count = len(ancestors)

    if ancestor_count == 0:
        # Layer 0 seller: no ancestors, vendor absorbs the full markup.
        db.add(
            WalletLedger(
                user_id=vendor.id,
                order_id=order.id,
                amount=vendor_markup_share + upward_pool,
                entry_type="CREDIT",
                transaction_reason="VENDOR_MARKUP_SHARE",
            )
        )
        vendor_total = base_principal + vendor_markup_share + upward_pool
        per_ancestor = Decimal("0.00")
        remainder = Decimal("0.00")
    else:
        db.add(
            WalletLedger(
                user_id=vendor.id,
                order_id=order.id,
                amount=vendor_markup_share,
                entry_type="CREDIT",
                transaction_reason="VENDOR_MARKUP_SHARE",
            )
        )
        vendor_total = base_principal + vendor_markup_share

        per_ancestor = _round(upward_pool / ancestor_count)
        distributed = per_ancestor * ancestor_count
        remainder = _round(upward_pool - distributed)

        for ancestor in ancestors:
            db.add(
                WalletLedger(
                    user_id=ancestor.id,
                    order_id=order.id,
                    amount=per_ancestor,
                    entry_type="CREDIT",
                    transaction_reason="UPWARD_COMMISSION",
                )
            )

        if remainder != Decimal("0.00"):
            root = ancestors[-1]  # nearest-parent-first => last is Layer 0
            db.add(
                WalletLedger(
                    user_id=root.id,
                    order_id=order.id,
                    amount=remainder,
                    entry_type="CREDIT",
                    transaction_reason="UPWARD_COMMISSION",
                )
            )

    order.status = "COMPLETED"
    await db.flush()

    return CommissionResult(
        order_id=order.id,
        vendor_id=vendor.id,
        vendor_total_payout=vendor_total,
        upward_ancestors_count=ancestor_count,
        per_ancestor_payout=per_ancestor,
        root_remainder_credit=remainder,
        status=order.status,
    )
