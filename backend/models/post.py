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
    type = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Generic Post fields
    image = Column(Text, nullable=True)

    # Attachment Post fields
    file_url = Column(Text, nullable=True)
    file_name = Column(Text, nullable=True)

    # Video Post fields
    video_url = Column(Text, nullable=True)
    video_name = Column(Text, nullable=True)
