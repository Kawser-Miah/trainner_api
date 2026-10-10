from typing import Any
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.models.provider.category import Category
from src.models.provider.coach_profile import (
    CoachCertification,
    CoachProfile,
    CoachQualification,
)


def get_coach_profile_by_user_id(
    db: Session,
    user_id: int,
) -> CoachProfile | None:
    query = (
        select(CoachProfile)
        .options(
            joinedload(CoachProfile.user),
            selectinload(CoachProfile.categories),
            selectinload(CoachProfile.certifications),
            selectinload(CoachProfile.qualifications),
        )
        .where(CoachProfile.user_id == user_id)
    )
    return db.execute(query).scalar_one_or_none()


def create_coach_profile(
    db: Session,
    *,
    user_id: int,
    headline: str | None = None,
    about: str | None = None,
    introduction_video: str | None = None,
    introduction_video_duration: int | None = 0,
    introduction_video_thumbnail: str | None = None,
    linkedin_url: str | None = None,
    affiliate_commission_percent: str = "20.00",
    auto_approve_affiliates: bool = False,
    expertises: list[Any] | None = None,
    languages: list[Any] | None = None,
    status: str = "pending",
    is_completed: bool = True,
) -> CoachProfile:
    profile = CoachProfile(
        user_id=user_id,
        headline=headline,
        about=about,
        introduction_video=introduction_video,
        introduction_video_duration=introduction_video_duration or 0,
        introduction_video_thumbnail=introduction_video_thumbnail,
        linkedin_url=linkedin_url,
        affiliate_commission_percent=affiliate_commission_percent,
        auto_approve_affiliates=auto_approve_affiliates,
        expertises=expertises or [],
        languages=languages or [],
        status=status,
        is_completed=is_completed,
    )
    db.add(profile)
    db.flush()
    return profile


def set_coach_categories(
    db: Session,
    *,
    coach_profile: CoachProfile,
    categories: list[Category],
) -> None:
    coach_profile.categories = categories
    db.flush()


def replace_certifications(
    db: Session,
    *,
    coach_profile: CoachProfile,
    certifications_data: list[dict[str, Any]],
) -> None:
    # Clear existing certifications
    coach_profile.certifications.clear()
    db.flush()

    for item in certifications_data:
        name = item.get("name", "").strip()
        if not name:
            continue
        cert = CoachCertification(
            coach_profile_id=coach_profile.id,
            name=name,
            document=item.get("document"),
        )
        db.add(cert)
    db.flush()


def replace_qualifications(
    db: Session,
    *,
    coach_profile: CoachProfile,
    qualifications_data: list[dict[str, Any]],
) -> None:
    # Clear existing qualifications
    coach_profile.qualifications.clear()
    db.flush()

    for item in qualifications_data:
        name = item.get("name", "").strip()
        if not name:
            continue
        qual = CoachQualification(
            coach_profile_id=coach_profile.id,
            name=name,
            document=item.get("document"),
        )
        db.add(qual)
    db.flush()
