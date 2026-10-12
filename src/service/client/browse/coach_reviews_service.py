from fastapi import Request
from sqlalchemy.orm import Session

from src.repository.client.browse.client_browse_repository import get_browse_coach_reviews
from src.schemas.client.browse.review_schemas import (
    ClientCoachReviewItem,
    ClientCoachReviewsResponse,
)
from src.service.client.browse.helpers import format_iso_datetime
from src.utils.media import build_media_url


async def get_coach_reviews_service(
    coach_profile_id: int,
    db: Session,
    request: Request | None = None,
) -> ClientCoachReviewsResponse:
    reviews = get_browse_coach_reviews(db=db, coach_profile_id=coach_profile_id)

    rating_breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    total_rating = 0
    items: list[ClientCoachReviewItem] = []

    for r in reviews:
        star_k = str(r.rating)
        if star_k in rating_breakdown:
            rating_breakdown[star_k] += 1
        total_rating += r.rating

        u_name = r.user.full_name if r.user else "Anonymous"
        u_image = build_media_url(r.user.photo_url, request) if r.user and r.user.photo_url else None
        items.append(
            ClientCoachReviewItem(
                id=r.id,
                user_name=u_name,
                user_image=u_image,
                rating=r.rating,
                review=r.review,
                created_at=format_iso_datetime(r.created_at),
            )
        )

    review_count = len(reviews)
    avg_rating = round(total_rating / review_count, 1) if review_count > 0 else 0.0

    return ClientCoachReviewsResponse(
        coach_profile_id=coach_profile_id,
        avg_rating=avg_rating,
        review_count=review_count,
        rating_breakdown=rating_breakdown,
        reviews=items,
    )
