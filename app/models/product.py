import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, Integer, Boolean, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("category IN ('TRAVEL_PACKAGE', 'VENDOR_PRODUCT')", name="ck_products_category"),
        CheckConstraint("base_price > 0", name="ck_products_base_price"),
        CheckConstraint("stock_quantity >= 0", name="ck_products_stock"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    base_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    # retail_price is application-computed on write (see services/pricing.py) and persisted,
    # mirroring the DB GENERATED ALWAYS column in the DDL blueprint for portability across backends.
    retail_price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
