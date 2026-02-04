"""
UserCourse model for many-to-many relationship between users and courses
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


class UserCourse(Base):
    """
    Many-to-many relationship between users and courses.
    Represents the courses a user is enrolled in.
    Provides a way to track courses a user has or has not completed
    """

    __tablename__ = "user_courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    completed = Column(Boolean, default=False)
    date_assigned = Column(Date, nullable=False, default=date.today)
    completed_at = Column(TIMESTAMP)

    # Relationships
    user = relationship("User", backref="user_courses")
    course = relationship("Course", backref="user_courses")

    # Ensure a user can only be assigned to a course once
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course"),)
