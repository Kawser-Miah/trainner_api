from fastapi import Request
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.repository.client.browse.client_browse_repository import (
    get_all_app_ratings,
    get_app_rating_aggregate_stats,
    get_user_app_rating,
    upsert_app_rating,
)
from src.schemas.client.browse.app_rating_schemas import AppRatingCreateRequest
from src.service.client.browse.helpers import format_iso_datetime
from src.utils.media import build_media_url


async def get_app_rating_stats_service(
    db: Session,
    current_user: User,
) -> dict:
    avg_rating, total_ratings = get_app_rating_aggregate_stats(db)
    user_rating_record = get_user_app_rating(db, user_id=current_user.id)

    has_rated = user_rating_record is not None
    user_rating = user_rating_record.rating if user_rating_record else None

    if total_ratings == 0:
        formatted_avg = 0
    else:
        rounded = round(avg_rating, 1)
        formatted_avg = int(rounded) if rounded.is_integer() else rounded

    return {
        "average_rating": formatted_avg,
        "total_ratings": total_ratings,
        "has_rated": has_rated,
        "user_rating": user_rating,
    }


async def submit_app_rating_service(
    payload: AppRatingCreateRequest,
    db: Session,
    current_user: User,
) -> dict:
    rating_record = upsert_app_rating(
        db=db,
        user_id=current_user.id,
        rating=payload.rating,
        review=payload.review.strip(),
    )
    return {
        "id": rating_record.id,
        "user": current_user.id,
        "user_name": current_user.full_name or "",
        "rating": rating_record.rating,
        "review": rating_record.review,
        "created_at": format_iso_datetime(rating_record.created_at),
        "updated_at": format_iso_datetime(rating_record.updated_at),
    }


async def get_app_ratings_list_service(
    db: Session,
    current_user: User,
    request: Request | None = None,
) -> list[dict]:
    ratings = get_all_app_ratings(db)
    result = []
    for r in ratings:
        user = r.user
        image_url = (
            build_media_url(user.photo_url, request)
            if user and user.photo_url
            else None
        )
        result.append(
            {
                "id": r.id,
                "user": r.user_id,
                "user_name": user.full_name if user else "",
                "image": image_url,
                "rating": r.rating,
                "review": r.review,
                "created_at": format_iso_datetime(r.created_at),
                "updated_at": format_iso_datetime(r.updated_at),
            }
        )
    return result
