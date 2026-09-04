from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., pattern="^(TRAVEL_PACKAGE|VENDOR_PRODUCT)$")
    base_price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(default=1, ge=0)


class ProductResponse(BaseModel):
    id: UUID
    vendor_id: UUID
    title: str
    description: Optional[str]
    category: str
    base_price: Decimal
    retail_price: Decimal
    stock_quantity: int
    is_active: bool

    model_config = {"from_attributes": True}
