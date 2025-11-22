"""
Product endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.db.session import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductResponse, ProductSearch
from app.dependencies import get_current_user
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(None),
    category: str = Query(None),
    min_gravity: float = Query(None),
    max_refund_rate: float = Query(None),
    min_commission: float = Query(None),
    has_rebill: bool = Query(None),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search ClickBank products with filters
    """
    # Build query
    stmt = select(Product)

    # Apply filters
    if query:
        stmt = stmt.where(
            or_(
                Product.title.ilike(f"%{query}%"),
                Product.description.ilike(f"%{query}%")
            )
        )

    if category:
        stmt = stmt.where(Product.category == category)

    if min_gravity is not None:
        stmt = stmt.where(Product.gravity >= min_gravity)

    if max_refund_rate is not None:
        stmt = stmt.where(Product.refund_rate <= max_refund_rate)

    if min_commission is not None:
        stmt = stmt.where(Product.commission_amount >= min_commission)

    if has_rebill is not None:
        stmt = stmt.where(Product.rebill == has_rebill)

    # Order by gravity (descending)
    stmt = stmt.order_by(Product.gravity.desc())

    # Apply pagination
    stmt = stmt.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(stmt)
    products = result.scalars().all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get product details by ID
    """
    result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise NotFoundException("Product not found")

    return product
