"""
ModulePost model for many-to-many relationship between modules and posts
"""

from datetime import date, datetime

from sqlalchemy import (
    TIMESTAMP,
    Column,
    Date,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class ModulePost(Base):
    """
    Many-to-many relationship between modules and posts.
    Represents the modules inclulded in a course.
    """

    __tablename__ = "module_posts"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordering = Column(Integer, nullable=False, default=0, index=True)
    date_assigned = Column(Date, nullable=False, default=date.today)  # likely metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    module = relationship("Module", backref="module_posts")
    post = relationship("Post", backref="module_posts")

    # Ensure a post can only be assigned to a module once
    __table_args__ = (UniqueConstraint("module_id", "post_id", name="uq_module_post"),)
