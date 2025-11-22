"""
Campaign model
"""
import uuid
import enum
from sqlalchemy import Column, String, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class CampaignStatus(str, enum.Enum):
    """Campaign status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DRAFT = "draft"


class Campaign(Base, TimestampMixin):
    """Campaign model"""

    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    name = Column(String, nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    funnel_type = Column(String, nullable=True)  # review, comparison, bonus, vsl
    affiliate_link = Column(Text, nullable=True)
    tracking_id = Column(String, nullable=True, unique=True)
    settings = Column(JSONB, nullable=True)  # Store campaign configuration

    # Relationships
    user = relationship("User", back_populates="campaigns")
    product = relationship("Product", back_populates="campaigns")
    content = relationship("Content", back_populates="campaign", cascade="all, delete-orphan")
    analytics = relationship("AnalyticsEvent", back_populates="campaign", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Campaign {self.name}>"
