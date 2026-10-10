from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy.orm import Session

from src.core.exceptions import CoachProfileNotFoundException
from src.models.accounts.user import User
from src.repository.provider.coach_profile.coach_profile_repository import (
    get_coach_profile_by_user_id,
)
from src.repository.provider.coach_profile.coach_review_repository import (
    get_coach_reviews_by_profile_id,
)
from src.schemas.provider.coach_profile.coach_review import (
    CoachReviewItemResponse,
    CoachReviewsDataResponse,
)
from src.utils.media import build_media_url


def format_dt(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


async def get_provider_coach_reviews(
    db: Session,
    user: User,
    request: Request | None = None,
) -> CoachReviewsDataResponse:
    profile = get_coach_profile_by_user_id(db, user.id)
    if profile is None:
        raise CoachProfileNotFoundException()

    reviews_list = get_coach_reviews_by_profile_id(db, profile.id)

    breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    total_rating_sum = 0
    formatted_reviews: list[CoachReviewItemResponse] = []

    for rev in reviews_list:
        star_key = str(rev.rating)
        if star_key in breakdown:
            breakdown[star_key] += 1

        total_rating_sum += rev.rating

        u_name = rev.user.full_name if rev.user else "Anonymous"
        u_img = (
            build_media_url(rev.user.photo_url, request)
            if rev.user and rev.user.photo_url
            else None
        )

        formatted_reviews.append(
            CoachReviewItemResponse(
                id=rev.user_id,
                user_name=u_name,
                user_image=u_img,
                rating=rev.rating,
                review=rev.review,
                created_at=format_dt(rev.created_at),
            )
        )

    total_reviews = len(reviews_list)
    avg_rating = (
        round(total_rating_sum / total_reviews, 1) if total_reviews > 0 else 0.0
    )

    return CoachReviewsDataResponse(
        avg_rating=avg_rating,
        total_reviews=total_reviews,
        rating_breakdown=breakdown,
        reviews=formatted_reviews,
    )
