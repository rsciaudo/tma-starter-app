"""
Module API endpoints
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Security, status
from post import Post
from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from auth import get_current_active_user, require_admin, security_scheme
from database import get_db
from models import CourseModule, Module, ModulePost, PostInModule, UserModule
from schemas.module import (
    ModuleCreate,
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
    before_date: Optional[date] = Query(None),
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all modules assigned to user
    Admins see all modules (with added functionality to filter by course_id or keyword)
    Allows for query parameters at end of endpoint such as
    /modules?course_id=3
    /modules?keyword=age3
    /modules?user_id=1
    /modules?course_id=3&keyword=age3&user_id=1
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

        if before_date is not None:
            temp_query = temp_query.where(Module.created_at < before_date)

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


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    dependencies=[Security(security_scheme)],
)
async def get_module(
    module_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single module by ID.
    """
    # show any module if user is admin
    if current_user.role.name == "admin":
        result = await db.execute(select(Module).where(Module.id == module_id))
        module = result.scalar_one_or_none()

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
            )

        return {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "created_at": module.created_at,
            "updated_at": module.updated_at,
        }
        # only show modules a user is associated with if non-admin
    else:
        result = await db.execute(
            select(Module)
            .join(UserModule)
            .where(
                UserModule.user_id == current_user.id,
                Module.id == module_id,
            )
        )

        module = result.scalar_one_or_none()

        if module is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Module Not Found"
            )

        return {
            "id": module.id,
            "title": module.title,
            "description": module.description,
            "created_at": module.created_at,
            "updated_at": module.updated_at,
        }


@router.post(
    "",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(security_scheme)],
)
async def create_module(
    module_data: ModuleCreate,
    module_posts: (
        List[PostInModule] | None
    ) = Body(  # allows optional posts in the schema
        default=None, embed=True  # forces "module_post": [...]" as the form
    ),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new module. Admin only.
    Has functionality to add a post associated with the module via PostInModule
    """
    try:
        new_module = Module(
            title=module_data.title.strip(),
            description=(
                module_data.description.strip() if module_data.description else None
            ),
        )

        db.add(new_module)
        await db.commit()
        await db.refresh(new_module)

        # if a list of modules is provided, create PostInModules for each new_module
        if module_posts:
            for post in module_posts:
                post_exists = await db.execute(  # check if post id exists
                    select(Post.id).where(Post.id == post.post_id)
                )
                if not post_exists.scalar_one_or_none():
                    continue  # if post id doesn't exist, skip to next post

                # if post id is valid, create new ModulePost
                new_module_post = ModulePost(
                    module_id=new_module.id,
                    post_id=post.post_id,
                    ordering=0,  # default ordering
                    date_assigned=date.today(),  # default to today
                )
                db.add(new_module_post)
        await db.commit()

        return {
            "id": new_module.id,
            "title": new_module.title,
            "description": new_module.description,
            "created_at": new_module.created_at,
            "updated_at": new_module.updated_at,
            # add color field
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create module: {str(e)}",
        )


@router.patch(
    "/{module_id}",
    response_model=ModuleResponse,
    dependencies=[Security(security_scheme)],
)
async def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    module_posts: List[PostInModule] | None = Body(
        default=None, embed=True  # forces "module_post": [...]" as the form
    ),  # allows addition of posts to module
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a module. Admin only. Can add post to the module
    """
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Module not found"
        )

    # Update basic fields
    if module_data.title is not None:
        module.title = module_data.title.strip()
    if module_data.description is not None:
        module.description = (
            module_data.description.strip() if module_data.description else None
        )

    # add ModulePost if field supplied
    try:
        if module_posts:
            for post in module_posts:
                post_exists = await db.execute(  # check if post id exists
                    select(Post.id).where(Post.id == post.post_id)
                )
                if not post_exists.scalar_one_or_none():
                    continue  # if post id doesn't exist, skip to next post

                # check if ModulePost already exists between this module and post
                result = await db.execute(
                    select(ModulePost).where(
                        ModulePost.module_id == module.id,
                        ModulePost.post_id == post.post_id,
                    )
                )
                existing = result.scalar_one_or_none()

                if existing:
                    continue  # skips making new ModulePost if it already exists

                new_module_post = ModulePost(
                    module_id=module.id,
                    post_id=post.post_id,
                    ordering=0,  # default ordering
                    date_assigned=date.today(),  # default to today
                )
                db.add(new_module_post)

        await db.commit()
        await db.refresh(module)

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update module: {str(e)}",
        )

    return {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "created_at": module.created_at,
        "updated_at": module.updated_at,
    }


@router.delete(
    "/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(security_scheme)],
)
async def delete_module(
    module_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a module. Admin only.
    Deletes both the module, and any ModulePosts associated with the module
    """
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="module not found"
        )
    try:
        # delete ModulePosts associated with this module
        await db.execute(delete(ModulePost).where(ModulePost.module_id == module_id))

        await db.delete(module)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete module: {str(e)}",
        )
