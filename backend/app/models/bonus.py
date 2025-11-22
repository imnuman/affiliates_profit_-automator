"""
Bonus delivery model
"""
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class Bonus(Base, TimestampMixin):
    """Bonus delivery model"""

    __tablename__ = "bonuses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_url = Column(String, nullable=True)  # S3 URL or external link
    delivery_method = Column(String, default="email")  # email, download
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, nullable=True)
    delivered_count = Column(UUID(as_uuid=True), default=0)
    last_delivered_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Bonus {self.name}>"
