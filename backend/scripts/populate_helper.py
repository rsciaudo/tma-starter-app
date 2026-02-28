# Helper functions to populate the database from CSVs

from sqlalchemy.ext.asyncio import AsyncSession

from models import (
    Course,
    CourseModule,
    Module,
    ModulePost,
    Post,
)


# Create module from CSV
async def create_module(
    db: AsyncSession,
    title: str,
    description: str,
) -> Module:
    module = Module(title=title, description=description)
    db.add(module)
    await db.flush()

    return module


async def create_module_from_csv(db: AsyncSession, module_data: dict) -> Module:
    return await create_module(
        db,
        module_data["title"],
        module_data.get("description"),
    )


# Create post from CSV
async def create_post(
    db: AsyncSession,
    title: str,
    type: str,
    text: str,
    image: str,
    file_url: str,
    file_name: str,
    video_url: str,
    video_name: str,
) -> Post:
    post = Post(
        title=title,
        type=type,
        text=text,
        image=image,
        file_url=file_url,
        file_name=file_name,
        video_url=video_url,
        video_name=video_name,
    )
    db.add(post)
    await db.flush()

    return post


async def create_post_from_csv(db: AsyncSession, post_data: dict) -> Post:
    return await create_post(
        db,
        post_data["title"],
        post_data.get("type"),
        post_data.get("text"),
        post_data.get("image"),
        post_data.get("file_url"),
        post_data.get("file_name"),
        post_data.get("video_url"),
        post_data.get("video_name"),
    )


# Add module to course
async def add_module_to_course(
    db: AsyncSession,
    course: Course,
    module: Module,
    ordering: int,
) -> CourseModule:
    course_module = CourseModule(
        course_id=course.id, module_id=module.id, ordering=ordering
    )
    db.add(course_module)
    await db.flush()

    return course_module


# Add post to module
async def add_post_to_module(
    db: AsyncSession,
    module: Module,
    post: Post,
    ordering: int,
) -> ModulePost:
    module_post = ModulePost(module_id=module.id, post_id=post.id, ordering=ordering)
    db.add(module_post)
    await db.flush()

    return module_post
