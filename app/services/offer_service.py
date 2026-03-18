import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.offer import Offer
from app.schemas.offer import AdminOfferCreate, AdminOfferUpdate
from app.core.exceptions import NotFoundException
from app.services.product_service import product_service
from app.services.seller_service import seller_service

class OfferService:
    @staticmethod
    async def get_offers_by_product(db: AsyncSession, product_id: uuid.UUID) -> List[Offer]:
        # ensure product exists
        await product_service.admin_get_product(db, product_id)
        
        stmt = select(Offer).where(Offer.product_id == product_id).order_by(Offer.price_amount)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def create_offer(db: AsyncSession, product_id: uuid.UUID, offer_in: AdminOfferCreate) -> Offer:
        # ensure product and seller exist
        await product_service.admin_get_product(db, product_id)
        await seller_service.get_seller_by_id(db, offer_in.seller_id)
        
        offer = Offer(
            product_id=product_id,
            seller_id=offer_in.seller_id,
            price_amount=offer_in.price.amount,
            price_currency=offer_in.price.currency,
            delivery_date=offer_in.delivery_date
        )
        db.add(offer)
        await db.commit()
        await db.refresh(offer)
        return offer

    @staticmethod
    async def get_offer(db: AsyncSession, offer_id: uuid.UUID) -> Offer:
        stmt = select(Offer).where(Offer.id == offer_id)
        result = await db.execute(stmt)
        offer = result.scalar_one_or_none()
        if not offer:
            raise NotFoundException(f"Offer {offer_id} not found")
        return offer

    @staticmethod
    async def update_offer(db: AsyncSession, offer_id: uuid.UUID, offer_in: AdminOfferUpdate) -> Offer:
        offer = await OfferService.get_offer(db, offer_id)
        
        if offer_in.seller_id is not None:
             await seller_service.get_seller_by_id(db, offer_in.seller_id)
             offer.seller_id = offer_in.seller_id
        if offer_in.price is not None:
             offer.price_amount = offer_in.price.amount
             offer.price_currency = offer_in.price.currency
        if offer_in.delivery_date is not None:
             offer.delivery_date = offer_in.delivery_date
             
        await db.commit()
        await db.refresh(offer)
        return offer

    @staticmethod
    async def delete_offer(db: AsyncSession, offer_id: uuid.UUID) -> None:
        offer = await OfferService.get_offer(db, offer_id)
        await db.delete(offer)
        await db.commit()

    @staticmethod
    async def get_offers_by_seller(db: AsyncSession, seller_id: uuid.UUID) -> List[Offer]:
        stmt = select(Offer).where(Offer.seller_id == seller_id).options(selectinload(Offer.product))
        result = await db.execute(stmt)
        return list(result.scalars().all())

offer_service = OfferService()
