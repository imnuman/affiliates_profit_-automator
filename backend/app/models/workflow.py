"""
Workflow model for automation
"""
import uuid
import enum
from sqlalchemy import Column, String, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class WorkflowStatus(str, enum.Enum):
    """Workflow status"""
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"


class Workflow(Base, TimestampMixin):
    """Workflow automation model"""

    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    trigger_type = Column(String, nullable=False)  # manual, scheduled, event
    trigger_config = Column(JSONB, nullable=True)
    actions = Column(JSONB, nullable=False)  # List of actions to perform
    conditions = Column(JSONB, nullable=True)  # Conditions to check
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.DRAFT, nullable=False)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="workflows")

    def __repr__(self):
        return f"<Workflow {self.name}>"
