"""
Post Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

class PostBase(BaseModel):
    """Base schema with common post fields"""

    title: str
    description: Optional[str] = None

class PostCreate(PostBase):
    """Schema for creating a new post"""

    pass

class PostUpdate(BaseModel):
    """Schema for updating a post"""

    title: Optional[str] = None
    description: Optional[str] = None

class PostResponse(PostBase):
    """Post response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class ActivityInModule(BaseModel):
    """Activity information included in module""" 
    
    model_config = ConfigDict(from_attributes=True)

    post_id: int
    post_title: str
    post_description: Optional[str]

class PostDetailResponse(PostResponse):
    """Post detail response schema with activities"""

    model_config = ConfigDict(from_attributes=True)

    activities: List[ActivityInModule] = []