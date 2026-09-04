from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreateRequest, ProductResponse
from app.services.pricing import compute_retail_price

router = APIRouter(prefix="/products", tags=["Products & Catalog"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    retail_price = compute_retail_price(payload.base_price, payload.category)
    product = Product(
        vendor_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        base_price=payload.base_price,
        retail_price=retail_price,
        stock_quantity=payload.stock_quantity,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.get("", response_model=list[ProductResponse])
async def list_products(category: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Product).where(Product.is_active.is_(True))
    if category:
        stmt = stmt.where(Product.category == category)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")
    if product.vendor_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your product")

    active_orders = await db.execute(
        select(Order.id).where(
            Order.product_id == product_id,
            Order.status.in_(("PENDING", "PAID")),
        )
    )
    if active_orders.first() is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Cannot remove a product with active, non-fulfilled orders"
        )

    product.is_active = False
    await db.commit()
