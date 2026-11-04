from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.client.coach_favorite import CoachFavorite
from src.models.provider.coach_profile import CoachProfile


def get_coach_profile_by_id(db: Session, coach_profile_id: int) -> CoachProfile | None:
    query = select(CoachProfile).where(CoachProfile.id == coach_profile_id)
    return db.execute(query).scalar_one_or_none()


def get_favorite(
    db: Session,
    user_id: int,
    coach_profile_id: int,
) -> CoachFavorite | None:
    query = select(CoachFavorite).where(
        CoachFavorite.user_id == user_id,
        CoachFavorite.coach_profile_id == coach_profile_id,
    )
    return db.execute(query).scalar_one_or_none()


def is_coach_favorited(
    db: Session,
    user_id: int,
    coach_profile_id: int,
) -> bool:
    return get_favorite(db=db, user_id=user_id, coach_profile_id=coach_profile_id) is not None


def add_favorite(
    db: Session,
    user_id: int,
    coach_profile_id: int,
) -> CoachFavorite:
    existing = get_favorite(db=db, user_id=user_id, coach_profile_id=coach_profile_id)
    if existing:
        return existing

    favorite = CoachFavorite(
        user_id=user_id,
        coach_profile_id=coach_profile_id,
    )
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(
    db: Session,
    favorite: CoachFavorite,
) -> None:
    db.delete(favorite)
    db.commit()


def get_user_favorite_coaches(
    db: Session,
    user_id: int,
) -> list[CoachProfile]:
    query = (
        select(CoachProfile)
        .join(CoachFavorite, CoachFavorite.coach_profile_id == CoachProfile.id)
        .join(CoachProfile.user)
        .where(
            CoachFavorite.user_id == user_id,
            CoachProfile.status == "approved",
        )
        .order_by(CoachFavorite.created_at.desc(), CoachProfile.id.desc())
        .options(
            selectinload(CoachProfile.user),
            selectinload(CoachProfile.categories),
            selectinload(CoachProfile.services),
            selectinload(CoachProfile.availability),
            selectinload(CoachProfile.reviews),
        )
    )
    return list(db.execute(query).scalars().all())
