"""
User API endpoints for user management (admin only)
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from auth import (
    get_password_hash,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    require_admin,
    security_scheme,
)
from database import get_db
from models.role import Role
from models.user import User
from schemas.auth import (
    UserCreate,
    UserDisableRequest,
    UserProfileUpdate,
    UserResponse,
    UserRoleChangeRequest,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=List[UserResponse],
    dependencies=[Security(security_scheme)],
)
async def get_all_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all users in the system.
    Requires admin role.
    """
    result = await db.execute(
        select(User).options(joinedload(User.role)).order_by(User.created_at)
    )
    users = result.unique().scalars().all()
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Security(security_scheme)],
)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single user by ID.
    Requires admin role.
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Reload with role relationship
    result = await db.execute(
        select(User).where(User.id == user_id).options(joinedload(User.role))
    )
    user = result.scalar_one()
    return user


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Security(security_scheme)],
)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.
    Requires admin role.
    """
    # Sanitize input
    username = user_data.username.strip()
    email = user_data.email.strip()
    password = user_data.password.strip()

    # Validate fields
    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty",
        )
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be empty",
        )
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password cannot be empty",
        )

    # Validate role
    role_name = (
        user_data.role.lower().strip()
        if user_data.role and user_data.role.strip()
        else "user"
    )
    valid_roles = ["admin", "manager", "user"]
    if role_name not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Get role from database
    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role '{role_name}' not found in database",
        )

    # Check if username already exists
    existing_user = await get_user_by_username(username, db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Check if email already exists
    existing_email = await get_user_by_email(email, db)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    # Create user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_id=role.id,
        email_verified=True,  # Admin-created users are auto-verified
        is_active=True,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        child_name=user_data.child_name,
        child_sex_assigned_at_birth=user_data.child_sex_assigned_at_birth,
        child_dob=user_data.child_dob,
        avatar_url=user_data.avatar_url,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Reload with role relationship
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.role))
    )
    user = result.scalar_one()

    return user


# @Dr. Sarah. This is the endpoint that currently only allows admin to update
# user profiles.
@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Security(security_scheme)],
)
async def update_user(
    user_id: int,
    profile_data: UserProfileUpdate,
    current_user: User = Depends(require_admin),  # Here is the admin dependency
    db: AsyncSession = Depends(get_db),  # Is there another dependency that checks to
    # see if the request is coming from the current user (I think I saw something like
    # that being used in /api/auth when I was reviewing Simon's PR). And how could we
    # do an either-or scenario with having to be an admin OR the current user (and
    # only allow them to change certain things based on their role)
):
    """
    Update a user's profile fields.
    Requires admin role.
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update profile fields if provided
    if profile_data.first_name is not None:
        user.first_name = (
            profile_data.first_name.strip() if profile_data.first_name else None
        )
    if profile_data.last_name is not None:
        user.last_name = (
            profile_data.last_name.strip() if profile_data.last_name else None
        )
    if profile_data.child_name is not None:
        user.child_name = (
            profile_data.child_name.strip() if profile_data.child_name else None
        )
    if profile_data.child_sex_assigned_at_birth is not None:
        user.child_sex_assigned_at_birth = (
            profile_data.child_sex_assigned_at_birth.strip()
            if profile_data.child_sex_assigned_at_birth
            else None
        )
    if profile_data.child_dob is not None:
        user.child_dob = profile_data.child_dob
    if profile_data.avatar_url is not None:
        user.avatar_url = (
            profile_data.avatar_url.strip() if profile_data.avatar_url else None
        )

    await db.commit()
    await db.refresh(user)

    # Reload with role relationship
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.role))
    )
    user = result.scalar_one()

    return user


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    dependencies=[Security(security_scheme)],
)
async def update_user_status(
    user_id: int,
    request: UserDisableRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Disable or enable a user account.
    Requires admin role.
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent disabling yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot disable your own account",
        )

    user.is_active = request.is_active
    await db.commit()
    await db.refresh(user)

    # Reload with role relationship
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.role))
    )
    user = result.scalar_one()

    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    dependencies=[Security(security_scheme)],
)
async def update_user_role(
    user_id: int,
    request: UserRoleChangeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Change a user's role.
    Requires admin role.
    """
    # Validate role name
    role_name = request.role.lower().strip()
    valid_roles = ["admin", "manager", "user"]
    if role_name not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}",
        )

    # Get the role from database
    role_result = await db.execute(select(Role).where(Role.name == role_name))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Role '{role_name}' not found in database",
        )

    # Get the user to update
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent changing your own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    user.role_id = role.id
    await db.commit()
    await db.refresh(user)

    # Reload with role relationship
    result = await db.execute(
        select(User).where(User.id == user.id).options(joinedload(User.role))
    )
    user = result.scalar_one()

    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(security_scheme)],
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user.
    Requires admin role.
    """
    user = await get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    await db.delete(user)
    await db.commit()

    return None
