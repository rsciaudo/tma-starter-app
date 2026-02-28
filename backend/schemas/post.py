"""
Post Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    """Base schema with common post fields"""

    title: str
    type: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    video_url: Optional[str] = None
    video_name: Optional[str] = None


class PostCreate(PostBase):
    """Schema for creating a new post"""

    pass


class PostUpdate(BaseModel):
    """Schema for updating a post"""

    title: Optional[str] = None
    text: Optional[str] = None


class PostResponse(PostBase):
    """Post response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
