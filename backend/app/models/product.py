"""
Product model for ClickBank products
"""
import uuid
from sqlalchemy import Column, String, Numeric, Integer, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    """ClickBank Product model"""

    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clickbank_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    category = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    commission_rate = Column(Numeric(5, 2), nullable=True)  # Percentage
    commission_amount = Column(Numeric(10, 2), nullable=True)  # Dollar amount
    initial_sale_amount = Column(Numeric(10, 2), nullable=True)
    gravity = Column(Numeric(10, 2), nullable=True, index=True)
    refund_rate = Column(Numeric(5, 2), nullable=True)
    rebill = Column(Boolean, default=False)
    popularity_rank = Column(Integer, nullable=True)
    data_snapshot = Column(JSONB, nullable=True)  # Store full API response
    last_updated = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    campaigns = relationship("Campaign", back_populates="product")

    def __repr__(self):
        return f"<Product {self.clickbank_id}: {self.title}>"
