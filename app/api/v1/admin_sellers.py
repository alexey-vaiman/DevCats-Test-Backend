import uuid
from typing import List
from fastapi import APIRouter, status, Response

from app.api.deps import SessionDep, AdminDep
from app.schemas.seller import AdminSellerCreate, AdminSellerUpdate, AdminSellerResponse
from app.services.seller_service import seller_service

router = APIRouter(prefix="/sellers", tags=["AdminSellers"])

@router.get("", response_model=List[AdminSellerResponse])
async def list_sellers(db: SessionDep, _admin: AdminDep):
    return await seller_service.get_sellers(db)

@router.post("", response_model=AdminSellerResponse, status_code=status.HTTP_201_CREATED)
async def create_seller(seller_in: AdminSellerCreate, db: SessionDep, _admin: AdminDep):
    return await seller_service.create_seller(db, seller_in)

@router.put("/{seller_id}", response_model=AdminSellerResponse)
async def update_seller(seller_id: uuid.UUID, seller_in: AdminSellerUpdate, db: SessionDep, _admin: AdminDep):
    return await seller_service.update_seller(db, seller_id, seller_in)

@router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: uuid.UUID, db: SessionDep, _admin: AdminDep):
    await seller_service.delete_seller(db, seller_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

from app.schemas.offer import AdminOfferResponse
from app.services.offer_service import offer_service

@router.get("/{seller_id}/offers", response_model=List[AdminOfferResponse])
async def list_offers_by_seller(seller_id: uuid.UUID, db: SessionDep, _admin: AdminDep):
    return await offer_service.get_offers_by_seller(db, seller_id)
