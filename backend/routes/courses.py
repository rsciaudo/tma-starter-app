"""
Course API endpoints
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from auth import get_current_active_user, require_admin, security_scheme
from database import get_db
from models import Course, CourseGroup, CourseModule, Module, UserGroup
from schemas.course import (
    CourseCreate,
    CourseDetailResponse,
    CourseResponse,
    CourseUpdate,
)

# File upload functionality removed - students will implement

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get(
    "",
    response_model=List[CourseResponse],
    dependencies=[Security(security_scheme)],
)
async def get_all_courses(
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all courses assigned to the user's groups.
    Admins see all courses.
    """
    # Admins can see all courses
    if current_user.role.name == "admin":
        result = await db.execute(select(Course).order_by(Course.created_at))
        courses = result.scalars().all()
    else:
        # Regular users only see courses assigned to their groups
        # Get user's group IDs
        user_groups_result = await db.execute(
            select(UserGroup.group_id).where(UserGroup.user_id == current_user.id)
        )
        user_group_ids = [row[0] for row in user_groups_result.all()]

        if not user_group_ids:
            # User is not in any groups, return empty list
            return []

        # Get courses assigned to user's groups
        result = await db.execute(
            select(Course)
            .join(CourseGroup, Course.id == CourseGroup.course_id)
            .where(CourseGroup.group_id.in_(user_group_ids))
            .distinct()
            .order_by(Course.created_at)
        )
        courses = result.scalars().all()

    # File upload functionality removed - students will implement
    course_list = []
    for course in courses:
        course_dict = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "module_count": 0,  # Modules will be implemented by students
        }
        course_list.append(course_dict)

    return course_list


@router.get(
    "/{course_id}",
    response_model=CourseDetailResponse,
    dependencies=[Security(security_scheme)],
)
async def get_course(
    course_id: int,
    current_user=Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single course by ID. Modules will be implemented by students.
    """
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.course_modules).selectinload(CourseModule.module))
        .where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "module_count": len(course.course_modules),
        "modules": [
            {
                "module_id": cm.module_id,
                "module_title": cm.module.title if cm.module else "",
                "module_description": cm.module.description if cm.module else None,
                "module_color": cm.module.color if cm.module else None,
                "ordering": cm.ordering,
            }
            for cm in course.course_modules
        ],
    }


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(security_scheme)],
)
async def create_course(
    course_data: CourseCreate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new course. Admin only.
    File upload functionality will be implemented by students.
    """
    try:
        course = Course(
            title=course_data.title.strip(),
            description=(
                course_data.description.strip() if course_data.description else None
            ),
        )
        db.add(course)
        await db.commit()
        await db.refresh(course)

        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "module_count": 0,  # Modules will be implemented by students
        }
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create course: {str(e)}",
        )


@router.patch(
    "/{course_id}",
    response_model=CourseResponse,
    dependencies=[Security(security_scheme)],
)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a course. Admin only.
    """
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Update basic fields
    if course_data.title is not None:
        course.title = course_data.title.strip()
    if course_data.description is not None:
        course.description = (
            course_data.description.strip() if course_data.description else None
        )

    # File upload functionality will be implemented by students

    await db.commit()
    await db.refresh(course)

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "created_at": course.created_at,
        "updated_at": course.updated_at,
        "module_count": 0,  # Modules will be implemented by students
    }


@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(security_scheme)],
)
async def delete_course(
    course_id: int,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a course. Admin only.
    Deletes both the Course record and the associated file.
    """
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # File deletion will be implemented by students when file upload is added

    # Delete the Course
    await db.delete(course)
    await db.commit()
    return None


@router.post(
    "/{course_id}/modules/{module_id}",
    status_code=201,
    dependencies=[Security(security_scheme)],
)
async def add_module_to_course(
    course_id: int,
    module_id: int,
    db: AsyncSession = Depends(get_db),
):
    # Make sure the course exists
    result = await db.execute(select(Course).where(Course.id == course_id))
    course = result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found",
        )

    # Make sure the module exists
    result = await db.execute(select(Module).where(Module.id == module_id))
    module = result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found",
        )

    # Make sure the module is not already in the course
    result = await db.execute(
        select(CourseModule).where(
            CourseModule.course_id == course_id, CourseModule.module_id == module_id
        )
    )
    membership = result.scalar_one_or_none()

    if membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module {module_id} is already in course {course_id}",
        )

    # Add the module to the course
    membership = CourseModule(course_id=course_id, module_id=module_id)
    db.add(membership)
    await db.commit()

    return {
        "message": f"Module {module_id} added to course {course_id}",
    }
