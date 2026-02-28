"""
Seed script to populate the database with test users, groups, and courses.

Usage:
    python -m scripts.seed_data
    or
    python backend/scripts/populate.py
"""

import argparse
import asyncio
import csv
import os
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import populate_helper  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from faker import Faker  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine  # noqa: E402
from sqlalchemy.future import select  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from auth import get_password_hash  # noqa: E402
from database.migrations import run_migrations, seed_initial_data  # noqa: E402

# Import all models to ensure they're registered with Base.metadata
from models import (  # noqa: E402, F401
    Base,
    Course,
    CourseGroup,
    CourseModule,
    Group,
    Module,
    ModulePost,
    Post,
    Role,
    User,
    UserGroup,
)

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL_DEV")
# DATABASE_URL = os.getenv("RAILWAY_DATABASE_URL_PROD")


if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not set in environment variables")
    sys.exit(1)

# Create engine and session
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Initialize Faker
fake = Faker()

# Get the sample_data directory path
SCRIPT_DIR = Path(__file__).parent
SAMPLE_DATA_DIR = SCRIPT_DIR / "sample_data"

# Design token colors for avatars (from ui/src/designTokens.ts)
AVATAR_COLORS = [
    "#996F9D",  # purple
    "#3C5E96",  # blue1
    "#669AC4",  # blue2
    "#4F71A3",  # blue3
    "#32396C",  # darkBlue
    "#746994",  # mutedPurple
    "#5F4483",  # purple2
    "#504468",  # darkPurple
    "#515251",  # gray
]


def get_avatar_color(name: str) -> str:
    """Get a deterministic avatar color based on the user's name"""
    # Hash the name to get a consistent color for each user
    hash_value = hash(name.lower())
    color_index = abs(hash_value) % len(AVATAR_COLORS)
    return AVATAR_COLORS[color_index].replace("#", "")  # Remove # for URL


def load_csv(filepath: Path) -> list[dict]:
    """Load a CSV file and return list of dictionaries, skipping comment lines"""
    if not filepath.exists():
        print(f"⚠️  CSV file not found: {filepath}")
        return []

    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        # Read all lines and filter out comment lines before parsing
        all_lines = f.readlines()
        # Find the header line (first non-comment, non-empty line)
        header_line = None
        data_lines = []
        for line in all_lines:
            stripped = line.strip()
            # Skip empty lines
            if not stripped:
                continue
            # Skip comment lines
            if stripped.startswith("#"):
                continue
            # First non-comment line is the header
            if header_line is None:
                header_line = stripped
                continue
            # Remaining lines are data
            data_lines.append(stripped)

        if header_line is None:
            return []

        # Now parse with the correct header
        reader = csv.DictReader([header_line] + data_lines)
        for row in reader:
            # Convert empty strings to None for optional fields
            cleaned_row = {}
            for k, v in row.items():
                if isinstance(v, list):
                    v = v[0] if v else ""
                v_str = str(v).strip() if v else ""
                cleaned_row[k] = v_str if v_str else None
            rows.append(cleaned_row)
    return rows


async def get_role_by_name(db: AsyncSession, role_name: str) -> Role:
    """Get a role by name"""
    result = await db.execute(select(Role).where(Role.name == role_name))
    role = result.scalar_one_or_none()
    if not role:
        raise ValueError(f"Role '{role_name}' not found in database")
    return role


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role_name: str = "user",
    email_verified: bool = True,
    first_name: str = None,
    last_name: str = None,
    avatar_url: str = None,
) -> User:
    """Create a user with the specified role, or update existing user's role"""
    # Check if user already exists
    existing = await db.execute(
        select(User).where((User.username == username) | (User.email == email))
    )
    existing_user = existing.scalar_one_or_none()

    # Get role
    role = await get_role_by_name(db, role_name)

    if existing_user:
        # Update role if it's different
        if existing_user.role_id != role.id:
            existing_user.role_id = role.id
            # Also update other fields if provided
            if first_name is not None:
                existing_user.first_name = first_name
            if last_name is not None:
                existing_user.last_name = last_name
            if avatar_url is not None:
                existing_user.avatar_url = avatar_url
            await db.flush()
            print(f"✅ Updated user {username} ({email}) role to {role_name}")
        else:
            print(
                f"⚠️  User {username} ({email}) already exists with role "
                f"{role_name}, skipping..."
            )
        return existing_user

    # Create new user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role_id=role.id,
        email_verified=email_verified,
        is_active=True,
        first_name=first_name,
        last_name=last_name,
        avatar_url=avatar_url,
    )
    db.add(user)
    await db.flush()  # Flush to get the user ID
    return user


async def create_group(
    db: AsyncSession,
    name: str,
    description: str,
    created_by: User,
) -> Group:
    """Create a group"""
    # Check if group already exists
    existing = await db.execute(select(Group).where(Group.name == name))
    existing_group = existing.scalar_one_or_none()
    if existing_group:
        print(f"⚠️  Group '{name}' already exists, skipping...")
        return existing_group

    group = Group(
        name=name,
        description=description,
        created_by=created_by.id,
    )
    db.add(group)
    await db.flush()

    # Add creator as owner
    user_group = UserGroup(
        user_id=created_by.id,
        group_id=group.id,
        role="owner",
    )
    db.add(user_group)
    await db.flush()

    return group


async def add_user_to_group(
    db: AsyncSession,
    user: User,
    group: Group,
    role: str = "member",
) -> UserGroup:
    """Add a user to a group"""
    # Check if user is already in group
    existing = await db.execute(
        select(UserGroup).where(
            UserGroup.user_id == user.id, UserGroup.group_id == group.id
        )
    )
    existing_user_group = existing.scalar_one_or_none()
    if existing_user_group:
        print(f"⚠️  User {user.username} already in group {group.name}, skipping...")
        return existing_user_group

    user_group = UserGroup(
        user_id=user.id,
        group_id=group.id,
        role=role,
    )
    db.add(user_group)
    await db.flush()
    return user_group


async def create_course(
    db: AsyncSession,
    title: str,
    description: str = None,
) -> Course:
    """Create a course"""
    # Check if course already exists
    existing = await db.execute(select(Course).where(Course.title == title))
    existing_course = existing.scalar_one_or_none()
    if existing_course:
        print(f"⚠️  Course '{title}' already exists, skipping...")
        return existing_course

    course = Course(title=title, description=description)
    db.add(course)
    await db.flush()
    return course


async def assign_course_to_group(
    db: AsyncSession,
    course: Course,
    group: Group,
    ordering: int = 0,
    date_assigned: date = None,
) -> CourseGroup:
    """Assign a course to a group"""
    # Check if course is already assigned to group
    existing = await db.execute(
        select(CourseGroup).where(
            CourseGroup.course_id == course.id, CourseGroup.group_id == group.id
        )
    )
    existing_course_group = existing.scalar_one_or_none()
    if existing_course_group:
        print(
            f"⚠️  Course '{course.title}' already assigned to group "
            f"'{group.name}', skipping..."
        )
        return existing_course_group

    if date_assigned is None:
        date_assigned = date.today()

    course_group = CourseGroup(
        course_id=course.id,
        group_id=group.id,
        ordering=ordering,
        date_assigned=date_assigned,
    )
    db.add(course_group)
    await db.flush()
    return course_group


async def generate_fake_user_data(count: int = 10) -> list[dict]:
    """Generate fake user data using Faker"""
    users = []
    used_usernames = set()
    used_emails = set()

    for i in range(count):
        # Generate profile fields
        first_name = fake.first_name()
        last_name = fake.last_name()

        # Generate username
        base_username = f"{first_name.lower()}_{last_name.lower()}"
        username = base_username
        username_counter = 1
        while username in used_usernames or len(username) > 50:
            username = f"{base_username}{username_counter}"
            username_counter += 1
        used_usernames.add(username)

        # Generate email
        base_email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        email = base_email
        email_counter = 1
        while email in used_emails:
            email = (
                f"{first_name.lower()}.{last_name.lower()}"
                f"{email_counter}@example.com"
            )
            email_counter += 1
        used_emails.add(email)

        # Generate avatar URL using ui-avatars.com API with design token color
        full_name = f"{first_name} {last_name}"
        avatar_color = get_avatar_color(full_name)
        avatar_url = (
            f"https://ui-avatars.com/api/?name={first_name}+{last_name}"
            f"&size=255&background={avatar_color}&color=fff&bold=true"
        )

        users.append(
            {
                "username": username,
                "email": email,
                "password": "password",
                "role": "user",
                "email_verified": "true",
                "first_name": first_name,
                "last_name": last_name,
                "avatar_url": avatar_url,
            }
        )

    return users


async def create_user_from_csv(db: AsyncSession, user_data: dict) -> User:
    """Create a user from CSV data"""
    return await create_user(
        db,
        user_data["username"],
        user_data["email"],
        user_data.get("password", "password"),
        user_data.get("role", "user"),
        user_data.get("email_verified", "true").lower() == "true",
        user_data.get("first_name"),
        user_data.get("last_name"),
        user_data.get("avatar_url"),
    )


async def drop_all_tables(conn):
    """Drop all tables in the database"""
    print("\n🗑️  Dropping all tables...")
    result = await conn.execute(
        text(
            """
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename;
            """
        )
    )
    tables = [row[0] for row in result.fetchall()]

    if not tables:
        print("   ℹ️  No tables to drop")
        return

    # Drop tables with CASCADE to handle foreign key constraints
    for table in tables:
        try:
            await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE;'))
            print(f"   ✅ Dropped table: {table}")
        except Exception as e:
            print(f"   ⚠️  Warning: Could not drop table {table}: {e}")

    print(f"✅ Dropped {len(tables)} tables")


async def main(reset: bool = False):
    """Main seeding function - loads data from CSV files"""
    print("🌱 Starting database seeding from CSV files...")
    db_url_display = DATABASE_URL.split("@")[1] if "@" in DATABASE_URL else "hidden"
    print(f"📊 Database URL: {db_url_display}")
    print(f"📁 Sample data directory: {SAMPLE_DATA_DIR}")

    async with engine.begin() as conn:
        if reset:
            # Drop all tables first
            await drop_all_tables(conn)

        # Then ensure all tables exist by running migrations
        print("\n🔧 Running database migrations...")
        await conn.run_sync(Base.metadata.create_all)
        await run_migrations(conn)
        await seed_initial_data(conn)
    print("✅ Database migrations completed")

    async with AsyncSessionLocal() as db:
        try:
            # Get roles
            user_role = await get_role_by_name(db, "user")
            admin_role = await get_role_by_name(db, "admin")

            print(
                f"\n✅ Found roles: user (id={user_role.id}), admin (id={admin_role.id})"
            )

            # Load CSV files
            print("\n📂 Loading CSV files...")
            users_data = load_csv(SAMPLE_DATA_DIR / "users.csv")
            groups_data = load_csv(SAMPLE_DATA_DIR / "groups.csv")
            courses_data = load_csv(SAMPLE_DATA_DIR / "courses.csv")
            user_groups_data = load_csv(SAMPLE_DATA_DIR / "user_groups.csv")
            course_groups_data = load_csv(SAMPLE_DATA_DIR / "course_groups.csv")

            modules_data = load_csv(SAMPLE_DATA_DIR / "modules.csv")
            posts_data = load_csv(SAMPLE_DATA_DIR / "posts.csv")
            course_modules_data = load_csv(SAMPLE_DATA_DIR / "course_modules.csv")
            module_posts_data = load_csv(SAMPLE_DATA_DIR / "module_posts.csv")

            # Count how many regular users are already in CSV
            regular_users_in_csv = sum(
                1 for u in users_data if u.get("role", "user").lower() != "admin"
            )

            # Generate additional fake users to reach 10 total regular users
            fake_user_count = max(0, 10 - regular_users_in_csv)
            if fake_user_count > 0:
                print(f"\n👥 Generating {fake_user_count} fake regular users...")
                fake_users = await generate_fake_user_data(fake_user_count)
                users_data.extend(fake_users)
            else:
                print(
                    f"\n✅ Already have {regular_users_in_csv} regular users "
                    "in CSV, skipping fake generation"
                )

            # Create lookup dictionaries
            users_lookup = {}
            groups_lookup = {}
            courses_lookup = {}

            modules_lookup = {}
            posts_lookup = {}

            # Create users
            print("\n👤 Creating users...")
            for user_data in users_data:
                user = await create_user_from_csv(db, user_data)
                users_lookup[user.username] = user
                role_label = "admin" if user_data.get("role") == "admin" else "user"
                print(f"   ✅ Created {role_label}: {user.username} ({user.email})")

            await db.commit()
            print(f"\n✅ Created {len(users_lookup)} users total")

            # Refresh all users to get IDs
            for user in users_lookup.values():
                await db.refresh(user)

            # Create groups
            print("\n👥 Creating groups...")
            for group_data in groups_data:
                created_by_username = group_data.get("created_by_username")
                if not created_by_username:
                    group_name = group_data.get("name")
                    print(
                        f"   ⚠️  Skipping group {group_name}: " "no created_by_username"
                    )
                    continue

                creator = users_lookup.get(created_by_username)
                if not creator:
                    group_name = group_data.get("name")
                    print(
                        f"   ⚠️  Skipping group {group_name}: "
                        f"creator '{created_by_username}' not found"
                    )
                    continue

                group = await create_group(
                    db,
                    group_data["name"],
                    group_data.get("description", ""),
                    creator,
                )
                groups_lookup[group.name] = group
                print(f"   ✅ Created group: {group.name}")

            await db.commit()
            print(f"\n✅ Created {len(groups_lookup)} groups")

            # Refresh groups
            for group in groups_lookup.values():
                await db.refresh(group)

            # Create courses
            print("\n📚 Creating courses...")
            for course_data in courses_data:
                course = await create_course(
                    db,
                    course_data["title"],
                    course_data.get("description"),
                )
                courses_lookup[course.title] = course
                print(f"   ✅ Created course: {course.title}")

            await db.commit()

            # Create modules
            for module_data in modules_data:
                module = await populate_helper.create_module_from_csv(db, module_data)
                modules_lookup[module.title] = module

            await db.commit()

            for module in modules_lookup.values():
                await db.refresh(module)

            # Create posts
            for post_data in posts_data:
                post = await populate_helper.create_post_from_csv(db, post_data)
                posts_lookup[post.title] = post

            await db.commit()

            for post in posts_lookup.values():
                await db.refresh(post)

            # Add users to groups (from CSV and auto-generated)
            print("\n🔗 Adding users to groups...")
            # Process CSV user_groups (if any)
            for rel_data in user_groups_data:
                username = rel_data.get("username")
                group_name = rel_data.get("group_name")
                role = rel_data.get("role", "member")

                user = users_lookup.get(username)
                group = groups_lookup.get(group_name)

                if not user or not group:
                    continue  # Skip if not found

                await add_user_to_group(db, user, group, role)
                print(f"   ✅ Added {user.username} to {group.name} as {role}")

            # Auto-assign regular users to groups
            regular_users = [
                u for u in users_lookup.values() if u.role_id == user_role.id
            ]
            group_list = list(groups_lookup.values())

            if len(group_list) >= 2 and len(regular_users) >= 5:
                # First 3 users to group 1
                for user in regular_users[:3]:
                    await add_user_to_group(db, user, group_list[0], "member")
                    print(f"   ✅ Added {user.username} to {group_list[0].name}")

                # Users 4-5 to group 2
                for user in regular_users[3:5]:
                    await add_user_to_group(db, user, group_list[1], "member")
                    print(f"   ✅ Added {user.username} to {group_list[1].name}")

            await db.commit()

            # Assign courses to groups
            print("\n📚 Assigning courses to groups...")
            for rel_data in course_groups_data:
                course_title = rel_data.get("course_title")
                group_name = rel_data.get("group_name")
                ordering = int(rel_data.get("ordering", 0))
                date_assigned_str = rel_data.get("date_assigned")

                course = courses_lookup.get(course_title)
                group = groups_lookup.get(group_name)

                if not course or not group:
                    if not course:
                        print(
                            f"   ⚠️  Course '{course_title}' not found, "
                            "skipping assignment"
                        )
                    if not group:
                        print(
                            f"   ⚠️  Group '{group_name}' not found, "
                            "skipping assignment"
                        )
                    continue

                # Parse date_assigned if provided
                date_assigned = None
                if date_assigned_str:
                    try:
                        date_assigned = date.fromisoformat(date_assigned_str)
                    except ValueError:
                        print(
                            f"   ⚠️  Invalid date format '{date_assigned_str}', "
                            "using today's date"
                        )
                        date_assigned = date.today()

                await assign_course_to_group(
                    db, course, group, ordering=ordering, date_assigned=date_assigned
                )
                print(
                    f"   ✅ Assigned '{course.title}' to '{group.name}' "
                    f"(ordering={ordering})"
                )

            await db.commit()

            # Add modules to courses
            for rel_data in course_modules_data:
                course = courses_lookup[rel_data["course_title"]]
                module = modules_lookup[rel_data["module_title"]]
                ordering = int(rel_data["ordering"])
                await populate_helper.add_module_to_course(db, course, module, ordering)

            await db.commit()

            # Add posts to modules
            for rel_data in module_posts_data:
                module = modules_lookup[rel_data["module_title"]]
                post = posts_lookup[rel_data["post_title"]]
                ordering = int(rel_data["ordering"])
                await populate_helper.add_post_to_module(db, module, post, ordering)

            await db.commit()

            # Summary
            admin_count = sum(
                1 for u in users_lookup.values() if u.role_id == admin_role.id
            )
            regular_count = len(users_lookup) - admin_count
            course_group_count = len(course_groups_data)

            print("\n🎉 Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   - Created {admin_count} admin users")
            print(f"   - Created {regular_count} regular users")
            print(f"   - Created {len(groups_lookup)} groups")
            print(f"   - Created {len(courses_lookup)} course(s)")
            print(f"   - Created {course_group_count} course-group assignment(s)")
            print("\n🔑 Admin credentials:")
            for user in users_lookup.values():
                if user.role_id == admin_role.id:
                    print(f"   - {user.email} / {user.username} / password")

        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error during seeding: {e}")
            import traceback

            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the database with test data")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before seeding (WARNING: This will delete all data!)",
    )
    args = parser.parse_args()

    if args.reset:
        print("⚠️  WARNING: --reset flag is set. This will DELETE ALL DATA!")
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Aborted. No changes made.")
            sys.exit(0)

    asyncio.run(main(reset=args.reset))
