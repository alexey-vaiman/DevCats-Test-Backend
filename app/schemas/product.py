from pydantic import BaseModel, Field, AnyHttpUrl
from uuid import UUID
from datetime import date
from .common import Money
from .offer import Offer

class ProductAttribute(BaseModel):
    key: str = Field(..., examples=["Color", "Memory"])
    value: str = Field(..., examples=["Red", "256GB"])
    
    class Config:
        from_attributes = True

class ProductListItem(BaseModel):
    id: UUID = Field(..., examples=["0a7e0d1e-3d3c-4c6c-b7f8-0d12ab3bcb86"])
    name: str = Field(..., examples=["Wireless Headphones"])
    thumbnail_url: str | None = Field(None, examples=["http://localhost:9000/products/0a7e0d1e-thumb.jpg"])
    price: Money
    stock: int = Field(..., ge=0, examples=[15])
    nearest_delivery_date: date | None = Field(None, examples=["2026-02-26"])

class ProductDetails(BaseModel):
    id: UUID
    name: str
    image_url: str | None = None
    stock: int
    attributes: list[ProductAttribute] = []

    class Config:
        from_attributes = True

class AdminProductCreate(BaseModel):
    name: str
    price: Money
    stock: int = Field(..., ge=0)
    attributes: list[ProductAttribute] = []

class AdminProductUpdate(BaseModel):
    name: str | None = None
    price: Money | None = None
    stock: int | None = Field(None, ge=0)
    attributes: list[ProductAttribute] | None = None

class AdminProductResponse(BaseModel):
    id: UUID
    name: str
    price: Money
    stock: int
    image_url: str | None = None
    thumbnail_url: str | None = None
    attributes: list[ProductAttribute] = []
    
    class Config:
        from_attributes = True
