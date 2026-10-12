from fastapi import Request
from sqlalchemy.orm import Session

from src.repository.client.browse.client_browse_repository import get_client_categories
from src.schemas.client.browse.category_schemas import UserCategoryItemResponse
from src.utils.media import build_media_url


async def get_user_category_list_service(
    db: Session,
    request: Request | None = None,
) -> list[UserCategoryItemResponse]:
    categories = get_client_categories(db=db, is_active=True)
    return [
        UserCategoryItemResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            is_active=cat.is_active,
            image=build_media_url(cat.image, request) if cat.image else None,
        )
        for cat in categories
    ]
