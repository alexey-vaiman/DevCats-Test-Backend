import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.seller import Seller
from app.schemas.seller import AdminSellerCreate, AdminSellerUpdate
from app.core.exceptions import NotFoundException

class SellerService:
    @staticmethod
    async def get_sellers(db: AsyncSession) -> List[Seller]:
        stmt = select(Seller).order_by(Seller.name)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_seller(db: AsyncSession, seller_in: AdminSellerCreate) -> Seller:
        seller = Seller(
            name=seller_in.name, 
            description=seller_in.description, 
            rating=seller_in.rating
        )
        db.add(seller)
        await db.commit()
        await db.refresh(seller)
        return seller

    @staticmethod
    async def update_seller(db: AsyncSession, seller_id: uuid.UUID, seller_in: AdminSellerUpdate) -> Seller:
        seller = await SellerService.get_seller_by_id(db, seller_id)
        update_data = seller_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(seller, field, value)
        await db.commit()
        await db.refresh(seller)
        return seller

    @staticmethod
    async def delete_seller(db: AsyncSession, seller_id: uuid.UUID) -> None:
        seller = await SellerService.get_seller_by_id(db, seller_id)
        await db.delete(seller)
        await db.commit()

    @staticmethod
    async def get_seller_by_id(db: AsyncSession, seller_id: uuid.UUID) -> Seller:
        stmt = select(Seller).where(Seller.id == seller_id)
        result = await db.execute(stmt)
        seller = result.scalar_one_or_none()
        if not seller:
            raise NotFoundException(f"Seller {seller_id} not found")
        return seller

seller_service = SellerService()
