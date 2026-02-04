"""
UserModule model for many-to-many relationship between users and modules
"""

from datetime import date

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    Column,
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class UserModule(Base):
    """
    Many-to-many relationship between users and modules.
    Represents the modules a user is enrolled in.
    Provides a way to track modules a user has or has not completed
    """

    __tablename__ = "user_modules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id = Column(
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed = Column(Boolean, default=False)
    date_assigned = Column(Date, nullable=False, default=date.today)
    completed_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", backref="user_modules")
    module = relationship("Module", backref="user_modules")

    # Ensure a user can only be assigned to a module once
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_user_module"),)
