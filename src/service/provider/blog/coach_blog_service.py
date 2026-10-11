import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import (
    CategoryNotFoundException,
    CoachBlogNotFoundException,
    CoachProfileNotFoundException,
)
from src.models.accounts.user import User
from src.models.provider.blog.coach_blog import CoachBlog
from src.repository.provider.category_repository import get_category_by_id
from src.repository.provider.coach_profile.coach_profile_repository import (
    get_coach_profile_by_user_id,
)
from src.repository.provider.blog.coach_blog_repository import (
    create_coach_blog,
    delete_coach_blog,
    get_coach_blog_by_id,
    get_coach_blogs_by_profile_id,
    update_coach_blog,
)
from src.schemas.provider.blog.coach_blog import (
    CoachBlogCategoryDetailsResponse,
    CoachBlogDataResponse,
    DeleteCoachBlogDataResponse,
)
from src.utils.media import build_media_url, delete_media_file


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


async def save_blog_image(file: Any) -> str | None:
    if not file or not hasattr(file, "filename") or not getattr(file, "filename", None):
        return None

    content = await file.read()
    if not content or len(content) == 0:
        return None

    ext = Path(file.filename).suffix or ".jpg"
    clean_stem = re.sub(r"[^\w\-]", "_", Path(file.filename).stem)
    unique_name = f"{clean_stem}_{uuid.uuid4().hex[:8]}{ext}"

    dest_dir = Path("media") / "coach" / "blogs"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / unique_name

    with open(dest_path, "wb") as f:
        f.write(content)

    return f"/media/coach/blogs/{unique_name}"


def map_blog_to_response(
    blog: CoachBlog,
    user_id: int,
    request: Request | None = None,
) -> CoachBlogDataResponse:
    category_details = None
    if blog.category:
        category_details = CoachBlogCategoryDetailsResponse(
            id=blog.category.id,
            name=blog.category.name,
            description=blog.category.description,
        )

    return CoachBlogDataResponse(
        id=blog.id,
        coach=user_id,
        category=blog.category_id,
        category_details=category_details,
        title=blog.title,
        content=blog.content,
        image=build_media_url(blog.image, request),
        status=blog.status,
        created_at=format_dt(blog.created_at),
        updated_at=format_dt(blog.updated_at),
    )


async def create_provider_blog(
    db: Session,
    user: User,
    *,
    title: str,
    category_id: int,
    content: str,
    status: str = "published",
    image: Any = None,
    request: Request | None = None,
) -> CoachBlogDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    category_obj = get_category_by_id(db, category_id)
    if category_obj is None:
        raise CategoryNotFoundException()

    image_path = await save_blog_image(image)

    blog = create_coach_blog(
        db=db,
        coach_profile_id=profile.id,
        category_id=category_id,
        title=title,
        content=content,
        image=image_path,
        status=status,
    )

    return map_blog_to_response(blog, user_id=user.id, request=request)


async def get_provider_blogs_list(
    db: Session,
    user: User,
    status: str | None = None,
    request: Request | None = None,
) -> list[CoachBlogDataResponse]:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    blogs = get_coach_blogs_by_profile_id(
        db=db,
        coach_profile_id=profile.id,
        status=status,
    )

    return [map_blog_to_response(b, user_id=user.id, request=request) for b in blogs]


async def get_provider_blog_detail(
    db: Session,
    user: User,
    blog_id: int,
    request: Request | None = None,
) -> CoachBlogDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    blog = get_coach_blog_by_id(db=db, blog_id=blog_id)
    if blog is None or blog.coach_profile_id != profile.id:
        raise CoachBlogNotFoundException()

    return map_blog_to_response(blog, user_id=user.id, request=request)


async def update_provider_blog(
    db: Session,
    user: User,
    blog_id: int,
    *,
    title: str | None = None,
    category_id: int | None = None,
    content: str | None = None,
    status: str | None = None,
    image: Any = None,
    request: Request | None = None,
) -> CoachBlogDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    blog = get_coach_blog_by_id(db=db, blog_id=blog_id)
    if blog is None or blog.coach_profile_id != profile.id:
        raise CoachBlogNotFoundException()

    if category_id is not None:
        category_obj = get_category_by_id(db, category_id)
        if category_obj is None:
            raise CategoryNotFoundException()

    new_image_path = None
    if image is not None and getattr(image, "filename", None):
        uploaded_path = await save_blog_image(image)
        if uploaded_path:
            if blog.image:
                delete_media_file(blog.image)
            new_image_path = uploaded_path

    updated_blog = update_coach_blog(
        db=db,
        blog=blog,
        category_id=category_id,
        title=title,
        content=content,
        image=new_image_path if new_image_path is not None else None,
        status=status,
    )

    return map_blog_to_response(updated_blog, user_id=user.id, request=request)


async def delete_provider_blog(
    db: Session,
    user: User,
    blog_id: int,
) -> DeleteCoachBlogDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    blog = get_coach_blog_by_id(db=db, blog_id=blog_id)
    if blog is None or blog.coach_profile_id != profile.id:
        raise CoachBlogNotFoundException()

    if blog.image:
        delete_media_file(blog.image)

    deleted_id = delete_coach_blog(db=db, blog=blog)
    return DeleteCoachBlogDataResponse(id=deleted_id)
