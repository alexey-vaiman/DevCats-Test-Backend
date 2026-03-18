from typing import Any, Generic, TypeVar, Literal
from pydantic import BaseModel, Field

CurrencyCode = Literal["RUB", "USD", "EUR"]

class Money(BaseModel):
    amount: float = Field(..., description="Price amount (decimal in backend)", examples=[1999.90])
    currency: CurrencyCode

class ErrorResponse(BaseModel):
    error: str = Field(..., examples=["validation_error", "not_found", "unauthorized"])
    message: str
    details: dict[str, Any] | None = None

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
