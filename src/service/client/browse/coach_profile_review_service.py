from datetime import datetime
from sqlalchemy.orm import Session

from src.core.exceptions import AppException, CoachProfileNotFoundException
from src.models.accounts.user import User
from src.repository.client.browse.coach_profile_review_repository import (
    create_coach_profile_review,
    get_coach_profile_with_user_by_id,
    get_coach_review_by_user_and_coach,
)
from src.schemas.client.browse.coach_profile_review_schemas import (
    CoachProfileReviewCreateRequest,
)


def _format_iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.astimezone()
    else:
        dt = dt.astimezone()
    return dt.isoformat()


async def submit_coach_profile_review_service(
    db: Session,
    current_user: User,
    coach_profile_id: int,
    payload: CoachProfileReviewCreateRequest,
) -> dict:
    coach_profile = get_coach_profile_with_user_by_id(
        db=db,
        coach_profile_id=coach_profile_id,
    )
    if not coach_profile:
        raise CoachProfileNotFoundException()

    if coach_profile.user_id == current_user.id:
        raise AppException(
            message="You cannot review your own profile.",
            status=400,
            error="SELF_REVIEW_NOT_ALLOWED",
        )

    existing_review = get_coach_review_by_user_and_coach(
        db=db,
        coach_profile_id=coach_profile_id,
        user_id=current_user.id,
    )
    if existing_review:
        raise AppException(
            message="You have already submitted a review for this coach.",
            status=400,
            error="REVIEW_ALREADY_EXISTS",
        )

    review_obj = create_coach_profile_review(
        db=db,
        coach_profile=coach_profile,
        user_id=current_user.id,
        rating=payload.rating,
        review=payload.review.strip(),
    )

    coach_name = (
        coach_profile.user.full_name
        if coach_profile.user and coach_profile.user.full_name
        else ""
    )
    user_name = current_user.full_name or ""

    return {
        "id": review_obj.id,
        "coach": coach_profile.id,
        "coach_name": coach_name,
        "user": current_user.id,
        "user_name": user_name,
        "rating": review_obj.rating,
        "review": review_obj.review,
        "created_at": _format_iso(review_obj.created_at),
        "updated_at": _format_iso(review_obj.updated_at),
    }

