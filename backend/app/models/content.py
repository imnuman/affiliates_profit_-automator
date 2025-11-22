"""
Content model
"""
import uuid
import enum
from sqlalchemy import Column, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class ContentType(str, enum.Enum):
    """Content type"""
    BLOG_POST = "blog_post"
    EMAIL = "email"
    SOCIAL_POST = "social_post"
    VIDEO_SCRIPT = "video_script"
    AD_COPY = "ad_copy"


class ContentStatus(str, enum.Enum):
    """Content status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    ARCHIVED = "archived"


class Content(Base, TimestampMixin):
    """Content model"""

    __tablename__ = "content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True, index=True)
    type = Column(Enum(ContentType), nullable=False)
    title = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)  # Store additional content data
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="content")
    campaign = relationship("Campaign", back_populates="content")

    def __repr__(self):
        return f"<Content {self.type}: {self.title}>"
