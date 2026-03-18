import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    price_amount = Column(Numeric(12, 2), nullable=False)
    price_currency = Column(String, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    image_object_key = Column(String, nullable=True)
    thumbnail_object_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    attributes = relationship("ProductAttribute", back_populates="product", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="product", cascade="all, delete-orphan")

    @property
    def price(self):
        return {"amount": self.price_amount, "currency": self.price_currency}

    @property
    def image_url(self):
        return self.image_object_key

    @property
    def thumbnail_url(self):
        return self.thumbnail_object_key

class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    key = Column(String, nullable=False)
    value = Column(String, nullable=False)

    product = relationship("Product", back_populates="attributes")
