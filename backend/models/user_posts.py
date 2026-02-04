"""
UserCourse model for many-to-many relationship between users and posts
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


class UserPost(Base):
    """
    Many-to-many relationship between users and posts.
    Represents the posts a user is enrolled in.
    Provides a way to track posts a user has or has not completed
    """

    __tablename__ = "user_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    post_id = Column(
        Integer,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed = Column(Boolean, default=False)
    date_assigned = Column(Date, nullable=False, default=date.today)
    completed_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", backref="user_posts")
    post = relationship("Post", backref="user_posts")

    # Ensure a user can only be assigned to a post once
    __table_args__ = (UniqueConstraint("user_id", "post_id", name="uq_user_post"),)
