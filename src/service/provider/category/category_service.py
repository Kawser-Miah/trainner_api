from fastapi import Request
from sqlalchemy.orm import Session

from src.repository.provider.category_repository import get_all_categories
from src.schemas.provider.category.category import CategoryResponse
from src.utils.media import build_media_url


async def list_categories_service(
    db: Session,
    request: Request | None = None,
    is_active: bool | None = None,
) -> list[CategoryResponse]:
    categories = get_all_categories(db=db, is_active=is_active)
    return [
        CategoryResponse(
            id=cat.id,
            name=cat.name,
            description=cat.description,
            is_active=cat.is_active,
            image=build_media_url(cat.image, request),
        )
        for cat in categories
    ]
