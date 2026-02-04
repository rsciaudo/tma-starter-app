"""
UserGroup model to show the users in a group
"""

from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class UserGroup(Base):
    """
    Many-to-many relationship between users and groups.
    Represents group membership.
    """

    __tablename__ = "user_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False, index=True)
    role = Column(
        String(20), nullable=False, default="member", index=True
    )  # 'member', 'moderator', or 'owner'
    joined_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", backref="group_memberships")
    group = relationship("Group", back_populates="members")

    # Ensure a user can only be in a group once
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)
