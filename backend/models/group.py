"""
Group model for managing user groups
"""

from datetime import datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )  # User who created the group (must be manager or admin)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_groups")
    # Many-to-many relationship with users through UserGroup
    members = relationship(
        "UserGroup", back_populates="group", cascade="all, delete-orphan"
    )


# # Moved UserGroup to its own file, to follow the file scheme of everything else
