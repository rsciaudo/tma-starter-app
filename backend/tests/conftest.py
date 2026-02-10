"""
Pytest configuration and fixtures for testing
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from auth import create_access_token, get_password_hash
from database import get_db
from models import Base, Role, User
from server import app

# Create test database (in-memory SQLite)
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=False,
)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# Override the get_db dependency to use test database
async def override_get_db():
    """Override get_db to use test database"""
    async with TestSessionLocal() as session:
        yield session


# Apply the override
app.dependency_overrides[get_db] = override_get_db


def create_auth_token(user: User) -> str:
    """
    Create a JWT token for a user object.

    Args:
        user: User object with username attribute

    Returns:
        JWT token string
    """
    return create_access_token(data={"sub": user.username})


def create_auth_headers(user: User) -> dict[str, str]:
    """
    Create authentication headers for a user object.

    Args:
        user: User object with username attribute

    Returns:
        Dictionary with Authorization header
    """
    token = create_auth_token(user)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def test_db():
    """Create and drop test database tables for each test"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed required roles
    async with TestSessionLocal() as session:

        # Create all required roles
        roles = [
            Role(name="user", description="Standard user role"),
            Role(name="manager", description="Group manager role"),
            Role(name="admin", description="Administrator role"),
        ]
        for role in roles:
            session.add(role)
        await session.commit()

    yield test_engine

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(test_db):
    """Create test client with test database"""
    from httpx import ASGITransport

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
async def admin_user(test_db):
    """Create an admin user for testing (roles already exist from test_db fixture)"""
    async with TestSessionLocal() as session:
        from sqlalchemy.future import select
        from sqlalchemy.orm import joinedload

        # Get admin role (already created by test_db fixture)
        result = await session.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalar_one()

        # Create admin user
        admin = User(
            username="admin",
            email="admin@test.com",
            hashed_password="$2b$12$dummy",  # Dummy hash for testing
            role_id=admin_role.id,
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)

        # Load role relationship
        result = await session.execute(
            select(User).where(User.id == admin.id).options(joinedload(User.role))
        )
        admin_with_role = result.scalar_one()

        yield admin_with_role


@pytest.fixture
async def auth_headers(admin_user):
    """Get authentication headers for admin user using JWT token"""
    return create_auth_headers(admin_user)


@pytest.fixture
async def regular_user(test_db):
    """
    Create a regular user (role: "user") for testing

    Use this when you need to test endpoints that should
    work for any authenticated user, or when testing that
    non-admin users are denied access to admin-only endpoints.
    """
    async with TestSessionLocal() as session:
        from sqlalchemy.future import select
        from sqlalchemy.orm import joinedload

        # Get user role
        result = await session.execute(select(Role).where(Role.name == "user"))
        user_role = result.scalar_one()

        plaintext_password = "hello"
        # Create regular user
        user = User(
            username="regular_user",
            email="user@test.com",
            hashed_password=get_password_hash(plaintext_password),
            role_id=user_role.id,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user.plaintext_password = plaintext_password
        # Load with role relationship
        result = await session.execute(
            select(User).where(User.id == user.id).options(joinedload(User.role))
        )
        user_with_role = result.scalar_one()

        yield user_with_role


@pytest.fixture
async def user_auth_headers(regular_user):
    """
    Get authentication headers for a regular user (non-admin) using JWT token

    Usage in tests:
        async def test_user_cannot_create_course(client, user_auth_headers):
            response = await client.post(
                "/courses",
                json={"name": "Test Course"},
                headers=user_auth_headers
            )
            assert response.status_code == 403  # Forbidden
    """
    return create_auth_headers(regular_user)


@pytest.fixture
def make_auth_headers():
    """
    Factory fixture to create auth headers for any user.

    Usage:
        async def test_something(client, make_auth_headers, admin_user, regular_user):
            admin_headers = make_auth_headers(admin_user)
            user_headers = make_auth_headers(regular_user)

            # Use both in the same test
            response1 = await client.get("/api/users", headers=admin_headers)
            response2 = await client.get("/api/users", headers=user_headers)
    """
    return create_auth_headers


# fixture for adding a course for testing
@pytest.fixture
async def create_course(admin_user, test_db):
    from datetime import datetime

    from models.course import Course

    async with TestSessionLocal() as session:
        course = Course(
            title="Test Course",
            description="A course for testing",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(course)
        await session.commit()
        await session.refresh(course)
        return course


@pytest.fixture
async def test_group_inaccessible_by_regular(test_db, admin_user):
    """Create a group for testing that is accessible by a manager or admin role user
    but not regular user
    use for testing getting, updating, deleting group by admin,
    and forbidden access by regular user
    """
    async with TestSessionLocal() as session:
        from models import Group

        # Create group
        group = Group(
            name="test_group:",
            description="A group for testing",
            created_by=admin_user.id,
        )
        session.add(group)
        await session.commit()
        await session.refresh(group)

        yield group


@pytest.fixture
async def test_group_accessible_by_regular(test_db, admin_user, regular_user):
    """Create a group for testing that is accessible by regular user
    use for testing getting, updating, deleting group by regular user"""
    async with TestSessionLocal() as session:
        from sqlalchemy.future import select
        from sqlalchemy.orm import joinedload

        from models import Group
        from models.user_group import UserGroup

        # Create group
        group = Group(
            name="test_group_accessible_by_regular",
            description="A group for testing accessible by regular user",
            created_by=admin_user.id,
        )
        session.add(group)
        await session.commit()
        await session.refresh(group)

        # Add regular user as member of the group
        membership = UserGroup(
            user_id=regular_user.id,
            group_id=group.id,
        )

        session.add(membership)
        await session.commit()

        # Load membership relationship
        # Load with role relationship
        result = await session.execute(
            select(UserGroup)
            .where(UserGroup.group_id == group.id)
            .options(joinedload(UserGroup.user))
        )
        group_with_members = result.scalar_one()

        yield group_with_members
