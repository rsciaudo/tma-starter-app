"""
Post model for the higher-level broad description of a post
"""

from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String, Text

from .base import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Finer details of specific posts (refered to as "activities") to be handled
    # in subtables representing the individual types

    # Note: Relationship to Module and individal Activities will be hadled in
    # their association tables
    # Relationship to users will be handled in ...
