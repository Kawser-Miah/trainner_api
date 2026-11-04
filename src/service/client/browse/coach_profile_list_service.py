from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.client.coach_favorite import CoachFavorite
from src.models.provider.coach_profile import CoachProfile
from src.repository.client.browse.client_browse_repository import get_browse_coach_profiles
from src.schemas.client.browse.coach_schemas import (
    ClientCoachUserResponse,
    CoachProfileListItemResponse,
)
from src.service.client.browse.helpers import (
    calculate_starting_price,
    format_iso_datetime,
)
from src.utils.media import build_media_url


def get_user_favorite_coach_ids(db: Session, user_id: int | None) -> set[int]:
    if not user_id:
        return set()
    res = db.execute(
        select(CoachFavorite.coach_profile_id).where(CoachFavorite.user_id == user_id)
    ).scalars().all()
    return set(res)


def serialize_coach_profile_list_item(
    profile: CoachProfile,
    request: Request | None = None,
    is_favorited: bool = False,
) -> CoachProfileListItemResponse:
    user = profile.user
    user_image = build_media_url(user.photo_url, request) if user and user.photo_url else None
    prof_photo = getattr(profile, "profile_photo", None)
    profile_photo = build_media_url(
        user.photo_url if user and user.photo_url else prof_photo,
        request,
    )
    intro_video = build_media_url(profile.introduction_video, request) if profile.introduction_video else None
    intro_thumb = (
        build_media_url(profile.introduction_video_thumbnail, request)
        if profile.introduction_video_thumbnail
        else None
    )

    user_resp = ClientCoachUserResponse(
        id=user.id if user else profile.user_id,
        full_name=user.full_name if user else "",
        email=user.email if user else "",
        phone_number=user.phone or "" if user else "",
        address=user.address if user else None,
        image=user_image,
    )

    categories = [cat.name for cat in (profile.categories or [])]
    starting_price = calculate_starting_price(profile.services)
    on_call = profile.availability.on_call_enabled if profile.availability else False

    return CoachProfileListItemResponse(
        id=profile.id,
        user=user_resp,
        categories=categories,
        avg_rating=float(profile.avg_rating or 0.0),
        review_count=int(profile.total_reviews or len(profile.reviews or [])),
        completed_sessions_count=int(profile.completed_sessions_count or 0),
        starting_price=starting_price,
        is_favorited=is_favorited,
        affiliate_status=None,
        affiliate_code=None,
        profile_photo=profile_photo,
        introduction_video=intro_video,
        introduction_video_duration=profile.introduction_video_duration,
        introduction_video_thumbnail=intro_thumb,
        linkedin_url=profile.linkedin_url or "",
        affiliate_commission_percent=profile.affiliate_commission_percent or "20.00",
        on_call_enabled=on_call,
        timezone=getattr(user, "timezone", "") or "" if user else "",
        auto_approve_affiliates=profile.auto_approve_affiliates,
        about=profile.about,
        headline=profile.headline or "",
        expertises=profile.expertises or [],
        languages=profile.languages or [],
        is_completed=profile.is_completed,
        status=profile.status,
        rejection_reason=profile.rejection_reason or "",
        created_at=format_iso_datetime(profile.created_at),
        updated_at=format_iso_datetime(profile.updated_at),
    )


async def get_coach_profile_list_service(
    db: Session,
    search: str | None = None,
    category: str | None = None,
    ordering: str | None = None,
    request: Request | None = None,
    user_id: int | None = None,
) -> list[CoachProfileListItemResponse]:
    profiles = get_browse_coach_profiles(
        db=db,
        search=search,
        category=category,
        ordering=ordering,
        recommended=False,
    )
    fav_ids = get_user_favorite_coach_ids(db=db, user_id=user_id)
    return [
        serialize_coach_profile_list_item(
            p,
            request,
            is_favorited=(p.id in fav_ids),
        )
        for p in profiles
    ]
