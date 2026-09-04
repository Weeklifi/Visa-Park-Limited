import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

ENTRY_TYPES = ("CREDIT", "DEBIT")
TRANSACTION_REASONS = (
    "BASE_PRINCIPAL",
    "VENDOR_MARKUP_SHARE",
    "UPWARD_COMMISSION",
    "WITHDRAWAL",
    "PURCHASE_PAYMENT",
)


class WalletLedger(Base):
    __tablename__ = "wallet_ledger"
    __table_args__ = (
        CheckConstraint(f"entry_type IN {ENTRY_TYPES}", name="ck_ledger_entry_type"),
        CheckConstraint(f"transaction_reason IN {TRANSACTION_REASONS}", name="ck_ledger_reason"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(10), nullable=False)
    transaction_reason: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
