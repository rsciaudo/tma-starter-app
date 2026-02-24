"""
Course model for managing courses
"""

from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String, Text
from sqlalchemy.ext.associationproxy import association_proxy

from .base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Many-to-Many Joins
    modules = association_proxy("course_modules", "modules")
