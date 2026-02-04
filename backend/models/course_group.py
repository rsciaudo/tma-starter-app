"""
CourseGroup model for many-to-many relationship between courses and groups
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


class CourseGroup(Base):
    """
    Many-to-many relationship between courses and groups.
    Represents course assignments to groups.
    """

    __tablename__ = "course_groups"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordering = Column(Integer, nullable=False, default=0, index=True)
    date_assigned = Column(Date, nullable=False, default=date.today)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", backref="course_groups")
    group = relationship("Group", backref="course_groups")

    # Ensure a course can only be assigned to a group once
    __table_args__ = (
        UniqueConstraint("course_id", "group_id", name="uq_course_group"),
    )
