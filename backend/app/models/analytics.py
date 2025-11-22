"""
Analytics event model
"""
import uuid
import enum
from sqlalchemy import Column, String, Enum, Numeric, BigInteger, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


class EventType(str, enum.Enum):
    """Analytics event type"""
    CLICK = "click"
    CONVERSION = "conversion"
    REFUND = "refund"
    REBILL = "rebill"


class AnalyticsEvent(Base):
    """Analytics event model"""

    __tablename__ = "analytics_events"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True)
    event_type = Column(Enum(EventType), nullable=False, index=True)
    source = Column(String, nullable=True)  # traffic source
    metadata = Column(JSONB, nullable=True)  # Additional event data
    revenue = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="analytics")

    # Composite index for common queries
    __table_args__ = (
        Index('idx_analytics_user_campaign_type_date', 'user_id', 'campaign_id', 'event_type', 'created_at'),
    )

    def __repr__(self):
        return f"<AnalyticsEvent {self.event_type}>"
