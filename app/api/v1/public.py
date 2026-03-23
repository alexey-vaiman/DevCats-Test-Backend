import uuid
from typing import Optional, Literal
from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.schemas.product import ProductListItem, ProductDetails
from app.schemas.common import PaginatedResponse
from app.services.product_service import product_query

router = APIRouter()

@router.get("/products", response_model=PaginatedResponse[ProductListItem])
async def list_public_products(
    db: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    cursor: Optional[str] = Query(None, description="Cursor from previous response"),
    offset: Optional[int] = Query(0, ge=0, description="Offset (if offset/limit pagination is used)"),
    search: Optional[str] = Query(None, description="Search by product name"),
):
    """List products for the main page (pagination for infinite scroll)"""
    return await product_query.get_public_products(db, limit=limit, cursor=cursor, offset=offset, search=search)

@router.get("/products/{product_id}", response_model=ProductDetails)
async def get_public_product(
    product_id: uuid.UUID,
    db: SessionDep,
):
    """Get product details"""
    return await product_query.get_public_product_details(db, product_id)

from app.schemas.offer import Offer as OfferSchema
@router.get("/products/{product_id}/offers", response_model=list[OfferSchema])
async def get_public_product_offers(
    product_id: uuid.UUID,
    db: SessionDep,
    offers_sort: Literal["price", "delivery_date"] = Query("price"),
):
    """Get product offers sorted"""
    return await product_query.get_product_offers(db, product_id, offers_sort=offers_sort)
