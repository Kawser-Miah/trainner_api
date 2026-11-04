from fastapi import Request
from sqlalchemy.orm import Session

from src.repository.client.browse.client_browse_repository import get_browse_coach_profiles
from src.schemas.client.browse.coach_schemas import CoachProfileListItemResponse
from src.service.client.browse.coach_profile_list_service import serialize_coach_profile_list_item


async def get_recommended_coach_profile_list_service(
    db: Session,
    request: Request | None = None,
    user_id: int | None = None,
) -> list[CoachProfileListItemResponse]:
    profiles = get_browse_coach_profiles(
        db=db,
        recommended=True,
    )
    from src.service.client.browse.coach_profile_list_service import get_user_favorite_coach_ids

    fav_ids = get_user_favorite_coach_ids(db=db, user_id=user_id)
    return [
        serialize_coach_profile_list_item(
            p,
            request,
            is_favorited=(p.id in fav_ids),
        )
        for p in profiles
    ]
