from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.provider.blog.coach_blog import CoachBlog


def create_coach_blog(
    db: Session,
    *,
    coach_profile_id: int,
    category_id: int,
    title: str,
    content: str,
    image: str | None = None,
    status: str = "published",
) -> CoachBlog:
    blog = CoachBlog(
        coach_profile_id=coach_profile_id,
        category_id=category_id,
        title=title,
        content=content,
        image=image,
        status=status,
    )
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


def get_coach_blog_by_id(
    db: Session,
    blog_id: int,
) -> CoachBlog | None:
    stmt = (
        select(CoachBlog)
        .where(CoachBlog.id == blog_id)
        .options(
            selectinload(CoachBlog.category),
        )
    )
    return db.execute(stmt).scalar_one_or_none()


def get_coach_blogs_by_profile_id(
    db: Session,
    coach_profile_id: int,
    status: str | None = None,
) -> list[CoachBlog]:
    stmt = (
        select(CoachBlog)
        .where(CoachBlog.coach_profile_id == coach_profile_id)
        .options(
            selectinload(CoachBlog.category),
        )
    )
    if status is not None and status.strip():
        stmt = stmt.where(CoachBlog.status == status.strip())

    stmt = stmt.order_by(CoachBlog.id.desc())
    return list(db.execute(stmt).scalars().all())


def update_coach_blog(
    db: Session,
    *,
    blog: CoachBlog,
    category_id: int | None = None,
    title: str | None = None,
    content: str | None = None,
    image: str | None = None,
    status: str | None = None,
) -> CoachBlog:
    if category_id is not None:
        blog.category_id = category_id
    if title is not None:
        blog.title = title
    if content is not None:
        blog.content = content
    if image is not None:
        blog.image = image
    if status is not None:
        blog.status = status

    db.commit()
    db.refresh(blog)
    return blog


def delete_coach_blog(
    db: Session,
    blog: CoachBlog,
) -> int:
    blog_id = blog.id
    db.delete(blog)
    db.commit()
    return blog_id
