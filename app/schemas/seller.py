from pydantic import BaseModel, Field
from uuid import UUID

class Seller(BaseModel):
    id: UUID = Field(..., examples=["b6e6c8d0-0c76-4c34-b0ab-0f5b65f15f90"])
    name: str = Field(..., examples=["BestSeller LLC"])
    description: str | None = Field(None, examples=["A leading electronics provider."])
    rating: float = Field(..., ge=1, le=5, examples=[4.7])
    
    class Config:
        from_attributes = True

class AdminSellerCreate(BaseModel):
    name: str
    description: str | None = None
    rating: float = Field(..., ge=1, le=5)

class AdminSellerUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    rating: float | None = Field(None, ge=1, le=5)

class AdminSellerResponse(Seller):
    pass
