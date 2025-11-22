"""
User model
"""
import uuid
from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin


class UserStatus(str, enum.Enum):
    """User account status"""
    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELED = "canceled"


class UserTier(str, enum.Enum):
    """User subscription tier"""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"


class User(Base, TimestampMixin):
    """User model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    tier = Column(Enum(UserTier), default=UserTier.STARTER, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    status = Column(Enum(UserStatus), default=UserStatus.TRIAL, nullable=False)
    trial_ends_at = Column(DateTime(timezone=True), nullable=True)
    is_email_verified = Column(Boolean, default=False)

    # Relationships
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"
