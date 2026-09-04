from decimal import Decimal

from app.core.config import settings

VENDOR_MULTIPLIER = Decimal(settings.vendor_markup_multiplier)  # 1.80
DIRECT_MARKUP_SHARE = Decimal("0.20")  # of markup M, to vendor
UPWARD_POOL_SHARE = Decimal("0.60")  # of markup M, pooled upward


def compute_retail_price(base_price: Decimal, category: str) -> Decimal:
    if category == "VENDOR_PRODUCT":
        return (base_price * VENDOR_MULTIPLIER).quantize(Decimal("0.01"))
    return base_price.quantize(Decimal("0.01"))
