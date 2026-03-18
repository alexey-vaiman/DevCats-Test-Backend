import uuid
from sqlalchemy import Column, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.database import Base

class Offer(Base):
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    seller_id = Column(UUID(as_uuid=True), ForeignKey("sellers.id"), nullable=False)
    price_amount = Column(Numeric(12, 2), nullable=False)
    price_currency = Column(String, nullable=False)
    delivery_date = Column(Date, nullable=False)

    product = relationship("Product", back_populates="offers")
    seller = relationship("Seller", back_populates="offers")

    @property
    def price(self):
        return {"amount": self.price_amount, "currency": self.price_currency}

