from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.models.provider.coach_profile.coach_profile import CoachProfile
from src.models.provider.coach_profile.coach_review import CoachReview


def get_coach_profile_with_user_by_id(
    db: Session,
    coach_profile_id: int,
) -> CoachProfile | None:
    return (
        db.query(CoachProfile)
        .options(joinedload(CoachProfile.user))
        .filter(CoachProfile.id == coach_profile_id)
        .first()
    )


def get_coach_review_by_user_and_coach(
    db: Session,
    coach_profile_id: int,
    user_id: int,
) -> CoachReview | None:
    return (
        db.query(CoachReview)
        .filter(
            CoachReview.coach_profile_id == coach_profile_id,
            CoachReview.user_id == user_id,
        )
        .first()
    )


def upsert_coach_profile_review(
    db: Session,
    coach_profile: CoachProfile,
    user_id: int,
    rating: int,
    review: str,
) -> CoachReview:
    existing = get_coach_review_by_user_and_coach(
        db=db,
        coach_profile_id=coach_profile.id,
        user_id=user_id,
    )
    now = datetime.now(timezone.utc)
    if existing:
        existing.rating = rating
        existing.review = review
        existing.updated_at = now
        review_obj = existing
    else:
        review_obj = CoachReview(
            coach_profile_id=coach_profile.id,
            user_id=user_id,
            rating=rating,
            review=review,
            created_at=now,
            updated_at=now,
        )
        db.add(review_obj)

    db.flush()

    # Recalculate coach_profile stats
    stats = (
        db.query(
            func.count(CoachReview.id).label("total"),
            func.avg(CoachReview.rating).label("avg"),
        )
        .filter(CoachReview.coach_profile_id == coach_profile.id)
        .one()
    )
    coach_profile.total_reviews = int(stats.total or 0)
    coach_profile.avg_rating = round(float(stats.avg or 0.0), 1)

    db.commit()
    db.refresh(review_obj)
    return review_obj
