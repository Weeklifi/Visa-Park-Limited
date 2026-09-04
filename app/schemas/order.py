from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class OrderCreateRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: UUID
    buyer_id: UUID
    product_id: UUID
    vendor_id: UUID
    unit_base_price: Decimal
    unit_retail_price: Decimal
    quantity: int
    total_amount: Decimal
    status: str

    model_config = {"from_attributes": True}


class CommissionPayoutResult(BaseModel):
    order_id: UUID
    vendor_id: UUID
    vendor_total_payout: Decimal
    upward_ancestors_count: int
    per_ancestor_payout: Decimal
    root_remainder_credit: Decimal
    status: str
