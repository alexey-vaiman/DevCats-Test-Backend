import uuid
from typing import List
from fastapi import APIRouter, Response, status

from app.api.deps import SessionDep, AdminDep
from app.schemas.offer import AdminOfferCreate, AdminOfferUpdate, AdminOfferResponse
from app.services.offer_service import offer_service

# Note: offers are nested under products in openapi for listing and creation, 
# but stand-alone for update and delete. We create two routers to map this exactly.

products_offers_router = APIRouter(prefix="/products/{product_id}/offers", tags=["AdminOffers"])

@products_offers_router.get("", response_model=List[AdminOfferResponse])
async def list_offers_for_product(product_id: uuid.UUID, db: SessionDep, _admin: AdminDep):
    return await offer_service.get_offers_by_product(db, product_id)

@products_offers_router.post("", response_model=AdminOfferResponse, status_code=status.HTTP_201_CREATED)
async def create_offer(product_id: uuid.UUID, offer_in: AdminOfferCreate, db: SessionDep, _admin: AdminDep):
    return await offer_service.create_offer(db, product_id, offer_in)


offers_router = APIRouter(prefix="/offers/{offer_id}", tags=["AdminOffers"])

@offers_router.put("", response_model=AdminOfferResponse)
async def update_offer(offer_id: uuid.UUID, offer_in: AdminOfferUpdate, db: SessionDep, _admin: AdminDep):
    return await offer_service.update_offer(db, offer_id, offer_in)

@offers_router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_offer(offer_id: uuid.UUID, db: SessionDep, _admin: AdminDep):
    await offer_service.delete_offer(db, offer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
