"""
CourseModule model for many-to-many relationship between courses and modules
"""

from datetime import date, datetime

from sqlalchemy import TIMESTAMP, Column, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class CourseModule(Base):
    """
    Many-to-many relationship between courses and modules.
    Represents the modules inclulded in a course.
    """

    __tablename__ = "course_modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_id = Column(
        Integer,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ordering = Column(Integer, nullable=False, default=0, index=True)
    date_assigned = Column(Date, nullable=False, default=date.today)  # likely metadata
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)

    # Relationships
    course = relationship("Course", backref="course_modules")
    module = relationship("Module", backref="course_modules")

    # Ensure a module can only be assigned to a course once
    # (The same module won't be in the same course twice)
    __table_args__ = (
        UniqueConstraint("course_id", "module_id", name="uq_course_module"),
    )
