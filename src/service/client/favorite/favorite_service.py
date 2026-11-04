from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import AppException
from src.repository.client.favorite.favorite_repository import (
    add_favorite,
    get_coach_profile_by_id,
    get_favorite,
    get_user_favorite_coaches,
    remove_favorite,
)
from src.schemas.client.favorite.favorite_schemas import (
    CoachFavoriteToggleResponseData,
    CoachProfileListItemResponse,
)
from src.service.client.browse.coach_profile_list_service import serialize_coach_profile_list_item


def add_coach_favorite_service(
    db: Session,
    user_id: int,
    coach_profile_id: int,
) -> CoachFavoriteToggleResponseData:
    profile = get_coach_profile_by_id(db=db, coach_profile_id=coach_profile_id)
    if not profile:
        raise AppException(
            message="Coach profile not found.",
            status=404,
            error="COACH_PROFILE_NOT_FOUND",
        )

    add_favorite(db=db, user_id=user_id, coach_profile_id=coach_profile_id)
    return CoachFavoriteToggleResponseData(
        coach_id=coach_profile_id,
        is_favorited=True,
    )


def remove_coach_favorite_service(
    db: Session,
    user_id: int,
    coach_profile_id: int,
) -> CoachFavoriteToggleResponseData:
    profile = get_coach_profile_by_id(db=db, coach_profile_id=coach_profile_id)
    if not profile:
        raise AppException(
            message="Coach profile not found.",
            status=404,
            error="COACH_PROFILE_NOT_FOUND",
        )

    favorite = get_favorite(db=db, user_id=user_id, coach_profile_id=coach_profile_id)
    if favorite:
        remove_favorite(db=db, favorite=favorite)

    return CoachFavoriteToggleResponseData(
        coach_id=coach_profile_id,
        is_favorited=False,
    )


def get_user_favorites_service(
    db: Session,
    user_id: int,
    request: Request | None = None,
) -> list[CoachProfileListItemResponse]:
    profiles = get_user_favorite_coaches(db=db, user_id=user_id)
    return [
        serialize_coach_profile_list_item(
            profile=p,
            request=request,
            is_favorited=True,
        )
        for p in profiles
    ]
