"""
Team and team member models
"""
import uuid
import enum
from sqlalchemy import Column, String, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class TeamRole(str, enum.Enum):
    """Team member role"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class Team(Base, TimestampMixin):
    """Team model for agency tier"""

    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    settings = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Team {self.name}>"


class TeamMember(Base, TimestampMixin):
    """Team member model"""

    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER, nullable=False)
    permissions = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    team = relationship("Team", back_populates="members")

    def __repr__(self):
        return f"<TeamMember {self.role}>"
