from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.provider.coach_profile.coach_review import CoachReview


def get_coach_reviews_by_profile_id(
    db: Session, coach_profile_id: int
) -> list[CoachReview]:
    return list(
        db.execute(
            select(CoachReview)
            .options(joinedload(CoachReview.user))
            .where(CoachReview.coach_profile_id == coach_profile_id)
            .order_by(CoachReview.created_at.desc())
        )
        .scalars()
        .all()
    )


def create_coach_review(
    db: Session,
    coach_profile_id: int,
    user_id: int,
    rating: int,
    review: str,
) -> CoachReview:
    review_obj = CoachReview(
        coach_profile_id=coach_profile_id,
        user_id=user_id,
        rating=rating,
        review=review,
    )
    db.add(review_obj)
    db.commit()
    db.refresh(review_obj)
    return review_obj
