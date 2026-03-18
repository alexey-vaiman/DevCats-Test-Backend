from pydantic import BaseModel, Field
from uuid import UUID
from datetime import date
from .common import Money
from .seller import Seller

class Offer(BaseModel):
    id: UUID = Field(..., examples=["8cf37f2a-30e5-4a61-9f85-5cdb7a8f1f08"])
    seller: Seller
    price: Money
    delivery_date: date = Field(..., description="Nearest delivery date for this offer", examples=["2026-02-27"])

    class Config:
        from_attributes = True

class AdminOfferCreate(BaseModel):
    seller_id: UUID
    price: Money
    delivery_date: date

class AdminOfferUpdate(BaseModel):
    seller_id: UUID | None = None
    price: Money | None = None
    delivery_date: date | None = None

class AdminOfferResponse(BaseModel):
    id: UUID
    product_id: UUID
    seller_id: UUID
    price: Money
    delivery_date: date
    
    class Config:
        from_attributes = True
