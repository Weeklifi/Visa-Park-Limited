from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import CommissionPayoutResult, OrderCreateRequest, OrderResponse
from app.services.commission import process_order_commission

router = APIRouter(prefix="/orders", tags=["Orders & Payouts"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Product).where(Product.id == payload.product_id, Product.is_active.is_(True)).with_for_update()
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found or inactive")
    if product.stock_quantity < payload.quantity:
        raise HTTPException(status.HTTP_409_CONFLICT, "Insufficient stock")

    # Price is locked from the product row at this exact moment (FR-3.2); later
    # price changes to the product do not affect this order.
    order = Order(
        buyer_id=current_user.id,
        product_id=product.id,
        vendor_id=product.vendor_id,
        unit_base_price=product.base_price,
        unit_retail_price=product.retail_price,
        quantity=payload.quantity,
        total_amount=product.retail_price * payload.quantity,
        status="PENDING",
    )
    product.stock_quantity -= payload.quantity

    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


@router.get("", response_model=list[OrderResponse])
async def list_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order)
        .where((Order.buyer_id == current_user.id) | (Order.vendor_id == current_user.id))
        .order_by(Order.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/{order_id}/mark-paid", response_model=OrderResponse)
async def mark_order_paid(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulates payment confirmation (no real payment gateway in scope).

    Moves a buyer's own PENDING order to PAID so it becomes eligible for
    /process-payout.
    """
    result = await db.execute(select(Order).where(Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.buyer_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your order")
    if order.status != "PENDING":
        raise HTTPException(status.HTTP_409_CONFLICT, f"Order must be PENDING (current: {order.status})")

    order.status = "PAID"
    await db.commit()
    await db.refresh(order)
    return order


@router.post("/{order_id}/process-payout", response_model=CommissionPayoutResult)
async def process_payout(
    order_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Order).where(Order.id == order_id).with_for_update())
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    if order.status not in ("PAID",):
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Order must be PAID to process payout (current: {order.status})"
        )

    try:
        commission_result = await process_order_commission(db, order)
        await db.commit()
    except Exception:
        await db.rollback()
        raise

    return CommissionPayoutResult(**commission_result.__dict__)
