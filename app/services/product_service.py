import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductAttribute
from app.models.offer import Offer
from app.schemas.product import AdminProductCreate, AdminProductUpdate, ProductListItem, ProductDetails
from app.schemas.common import PaginatedResponse
from app.core.exceptions import NotFoundException

class ProductQueryService:
    @staticmethod
    async def get_public_products(
        db: AsyncSession, limit: int = 20, cursor: Optional[str] = None, offset: Optional[int] = 0, search: Optional[str] = None
    ) -> PaginatedResponse[ProductListItem]:
        
        current_offset = int(cursor) if cursor else offset or 0

        # Subquery to find the nearest delivery date exclusively within SQL
        subq = (
            select(Offer.product_id, func.min(Offer.delivery_date).label("nearest_date"))
            .group_by(Offer.product_id)
            .subquery()
        )

        stmt = (
            select(Product, subq.c.nearest_date)
            .outerjoin(subq, Product.id == subq.c.product_id)
            .order_by(Product.created_at.desc())
        )

        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))

        stmt = stmt.offset(current_offset).limit(limit)
        
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
            
        next_cursor = str(current_offset + limit) if len(items) == limit else None
        return PaginatedResponse(items=items, next_cursor=next_cursor)

    @staticmethod
    async def get_public_product_details(
        db: AsyncSession, product_id: uuid.UUID, offers_sort: str = "price"
    ) -> ProductDetails:
        stmt = (
            select(Product)
            .options(selectinload(Product.attributes), selectinload(Product.offers).selectinload(Offer.seller))
            .where(Product.id == product_id)
        )
        result = await db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if not product:
            raise NotFoundException(f"Product with id {product_id} not found")
            
        if offers_sort == "price":
            product.offers.sort(key=lambda o: float(o.price_amount))
        elif offers_sort == "delivery_date":
            product.offers.sort(key=lambda o: o.delivery_date)
            
        return ProductDetails.model_validate(product)

    @staticmethod
    async def admin_get_products(
        db: AsyncSession, limit: int = 50, cursor: Optional[str] = None, search: Optional[str] = None
    ):
        current_offset = int(cursor) if cursor else 0
        stmt = (
            select(Product)
            .options(selectinload(Product.attributes))
            .order_by(Product.created_at.desc())
        )

        if search:
            stmt = stmt.where(Product.name.ilike(f"%{search}%"))

        stmt = stmt.offset(current_offset).limit(limit)
        
        result = await db.execute(stmt)
        products = result.scalars().all()
        next_cursor = str(current_offset + limit) if len(products) == limit else None
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

# For backwards compatibility with routers before we refactor them
class _LegacyProductService:
    get_public_products = ProductQueryService.get_public_products
    get_public_product_details = ProductQueryService.get_public_product_details
    admin_get_products = ProductQueryService.admin_get_products
    admin_get_product = ProductQueryService.admin_get_product
    admin_create_product = ProductCommandService.admin_create_product
    admin_update_product = ProductCommandService.admin_update_product
    admin_delete_product = ProductCommandService.admin_delete_product
    admin_update_product_images = ProductCommandService.admin_update_product_images

product_service = _LegacyProductService()
