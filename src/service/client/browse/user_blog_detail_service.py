from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import get_browse_blog_detail
from src.service.client.browse.helpers import format_browse_blog_dict


async def get_user_blog_detail_service(
    blog_id: int,
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> dict:
    blog = get_browse_blog_detail(db=db, blog_id=blog_id)
    if not blog or blog.status != "published":
        raise AppException(
            status=404,
            message="Blog not found.",
            error="NOT_FOUND",
        )

    return format_browse_blog_dict(blog, request=request)
