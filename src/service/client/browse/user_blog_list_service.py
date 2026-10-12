from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import get_browse_blogs
from src.service.client.browse.helpers import format_browse_blog_dict


async def get_user_blog_list_service(
    db: Session,
    current_user: User,
    category_id: int | None = None,
    search: str | None = None,
    request: Request | None = None,
) -> list[dict]:
    blogs = get_browse_blogs(
        db=db,
        category_id=category_id,
        search=search,
        status="published",
    )
    return [format_browse_blog_dict(b, request=request) for b in blogs]
