import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
import base64
from datetime import datetime
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductAttribute
from app.models.offer import Offer
from app.schemas.product import AdminProductCreate, AdminProductUpdate, ProductListItem, ProductDetails
from app.schemas.common import PaginatedResponse
from app.core.exceptions import NotFoundException

def _decode_cursor(cursor: Optional[str]):
    if not cursor: return None, None
    try:
        dec = base64.b64decode(cursor).decode('utf-8')
        ts, uid = dec.split('|')
        return datetime.fromisoformat(ts), uid
    except:
        return None, None

def _encode_cursor(dt, uid) -> str:
    if not dt or not uid: return None
    return base64.b64encode(f"{dt.isoformat()}|{uid}".encode('utf-8')).decode('utf-8')

class ProductQueryService:
    @staticmethod
    async def get_public_products(
        db: AsyncSession, limit: int = 20, cursor: Optional[str] = None, offset: Optional[int] = 0, search: Optional[str] = None
    ) -> PaginatedResponse[ProductListItem]:
        
        cursor_dt, cursor_id = _decode_cursor(cursor)

        # Subquery to find the nearest delivery date exclusively within SQL
        subq = (
            select(Offer.product_id, func.min(Offer.delivery_date).label("nearest_date"))
            .group_by(Offer.product_id)
            .subquery()
        )

        stmt = (
            select(Product, subq.c.nearest_date)
            .outerjoin(subq, Product.id == subq.c.product_id)
            .order_by(Product.created_at.desc(), Product.id.desc())
        )

        if cursor_dt and cursor_id:
            stmt = stmt.where(
                or_(
                    Product.created_at < cursor_dt,
                    and_(Product.created_at == cursor_dt, Product.id < str(cursor_id))
                )
            )

        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))

        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        items = []
        for p, nearest_date in rows:
            items.append(ProductListItem(
                id=p.id,
                name=p.name,
                thumbnail_url=p.thumbnail_object_key,
                price={"amount": float(p.price_amount), "currency": p.price_currency},
                stock=p.stock,
                nearest_delivery_date=nearest_date
            ))
            
        next_cursor = _encode_cursor(rows[-1][0].created_at, rows[-1][0].id) if len(items) == limit else None
        return PaginatedResponse(items=items, next_cursor=next_cursor)

    @staticmethod
    async def get_public_product_details(
        db: AsyncSession, product_id: uuid.UUID
    ) -> ProductDetails:
        stmt = (
            select(Product)
            .options(selectinload(Product.attributes))
            .where(Product.id == product_id)
        )
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise NotFoundException(f"Product with id {product_id} not found")
            
        return ProductDetails.model_validate(product)

    @staticmethod
    async def get_product_offers(
        db: AsyncSession, product_id: uuid.UUID, offers_sort: str = "price"
    ):
        stmt = select(Offer).options(selectinload(Offer.seller)).where(Offer.product_id == product_id)
        if offers_sort == "price":
            stmt = stmt.order_by(Offer.price_amount.asc())
        elif offers_sort == "delivery_date":
            stmt = stmt.order_by(Offer.delivery_date.asc())
            
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def admin_get_products(
        db: AsyncSession, limit: int = 50, cursor: Optional[str] = None, search: Optional[str] = None
    ):
        cursor_dt, cursor_id = _decode_cursor(cursor)
        
        stmt = (
            select(Product)
            .options(selectinload(Product.attributes))
            .order_by(Product.created_at.desc(), Product.id.desc())
        )

        if cursor_dt and cursor_id:
            stmt = stmt.where(
                or_(
                    Product.created_at < cursor_dt,
                    and_(Product.created_at == cursor_dt, Product.id < str(cursor_id))
                )
            )

        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))

        stmt = stmt.limit(limit)
        
        result = await db.execute(stmt)
        products = result.scalars().all()
        next_cursor = _encode_cursor(products[-1].created_at, products[-1].id) if len(products) == limit else None
        return {"items": products, "next_cursor": next_cursor}

    @staticmethod
    async def admin_get_product(db: AsyncSession, product_id: uuid.UUID) -> Product:
        stmt = select(Product).options(selectinload(Product.attributes)).where(Product.id == product_id)
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        if not product:
            raise NotFoundException(f"Product {product_id} not found")
        return product


class ProductCommandService:
    @staticmethod
    async def admin_create_product(db: AsyncSession, product_in: AdminProductCreate) -> Product:
        db_product = Product(
            name=product_in.name,
            price_amount=product_in.price.amount,
            price_currency=product_in.price.currency,
            stock=product_in.stock,
        )
        db_product.attributes = []
        for attr in product_in.attributes:
            db_attr = ProductAttribute(key=attr.key, value=attr.value)
            db_product.attributes.append(db_attr)

        db.add(db_product)
        await db.commit()
        return db_product

    @staticmethod
    async def admin_update_product(
        db: AsyncSession, product_id: uuid.UUID, product_in: AdminProductUpdate
    ) -> Product:
        product = await ProductQueryService.admin_get_product(db, product_id)
        
        if product_in.name is not None:
            product.name = product_in.name
        if product_in.price is not None:
            product.price_amount = product_in.price.amount
            product.price_currency = product_in.price.currency
        if product_in.stock is not None:
            product.stock = product_in.stock
            
        if product_in.attributes is not None:
            stmt = select(ProductAttribute).where(ProductAttribute.product_id == product_id)
            result = await db.execute(stmt)
            for attr in result.scalars().all():
                await db.delete(attr)
            
            for attr in product_in.attributes:
                db_attr = ProductAttribute(product_id=product.id, key=attr.key, value=attr.value)
                db.add(db_attr)
                
        await db.commit()
        await db.refresh(product, ["attributes"])
        return product

    @staticmethod
    async def admin_delete_product(db: AsyncSession, product_id: uuid.UUID) -> None:
        product = await ProductQueryService.admin_get_product(db, product_id)
        await db.delete(product)
        await db.commit()

    @staticmethod
    async def admin_update_product_images(
        db: AsyncSession, product_id: uuid.UUID, image_url: str, thumbnail_url: str
    ):
        product = await ProductQueryService.admin_get_product(db, product_id)
        product.image_object_key = image_url
        product.thumbnail_object_key = thumbnail_url
        await db.commit()
        await db.refresh(product)
        return product

product_query = ProductQueryService()
product_command = ProductCommandService()
