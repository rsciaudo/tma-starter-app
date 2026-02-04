"""
Role model for modules
"""

from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String, Text

from .base import Base


class Module(Base):
    __tablename__ = "modules"

    # Columns
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    color = Column(String(200))

    # Note: Relationships to Course and Post will be handled in the association tables
    # Relationships to users will be handled in ...
