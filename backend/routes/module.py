"""
Module API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import get_current_active_user, require_admin, security_scheme
from database import get_db
from models import CourseModule, Module, ModulePost, UserModule
from schemas.module import (
    ModuleCreate,
    ModuleDetailResponse,
    ModuleResponse,
    ModuleUpdate,
)

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get(
    "",
    response_model=List[ModuleResponse],
    dependencies=[Security(security_scheme)],
)
async def get_all_modules(
    course_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all modules assigned to user
    Admins see all modules (with added functionality to filter by course_id or keyword)
    Allows for query parameters at end of endpoint such as
    /modules?course_id=3
    /modules?keyword=age3
    /modules?course_id=3&keyword=age3
    """
    temp_query = select(
        Module
    )  # build the query with no parameters, doesn't touch db yet

    if current_user.role.name == "admin":
        if course_id is not None:  # allows filtering by course id
            temp_query = temp_query.join(CourseModule).where(
                CourseModule.course_id == course_id
            )

        if keyword is not None:  # allows filtering by keyword
            keyword = keyword.strip()
            temp_query = temp_query.where(
                or_(
                    Module.title.ilike(f"%{keyword}%"),
                    Module.description.ilike(f"%{keyword}%"),
                    # used ai with the prompt "sql alchemy .contains like 
                    # case insensitive query param" and found ilike()
                )
            )

        # allows filtering by user_id in module (I think should work
        # more for future proofing since hard to test now)
        if user_id is not None:
            temp_query = temp_query.join(UserModule).where(
                UserModule.user_id == user_id
            )

    else:
        # user is not admin, only shows modules assigned to them
        temp_query = temp_query.join(UserModule).where(
            UserModule.user_id == current_user.id
        )

    # query db after temp_query has been created either in admin or non-admin
    result = await db.execute(temp_query.order_by(Module.created_at))
    modules = result.scalars().all()

    module_list = []
    for module in modules:
        module_dict = {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "created_at": module.created_at,
            "updated_at": module.updated_at,
        }
        module_list.append(module_dict)

    return module_list
