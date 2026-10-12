from datetime import datetime
from fastapi import Request

from src.models.accounts.user import User
from src.models.provider.coach_profile import CoachProfile
from src.utils.media import build_media_url


def format_iso_datetime(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def format_duration_display(duration_seconds: int | None) -> str:
    if not duration_seconds or duration_seconds <= 0:
        return "0:00"
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    return f"{minutes}:{seconds:02d}"


def get_coach_provider_details(
    coach_profile: CoachProfile,
    request: Request | None = None,
) -> dict:
    user = coach_profile.user
    prof_photo = getattr(coach_profile, "profile_photo", None)
    photo = build_media_url(
        user.photo_url if user and user.photo_url else prof_photo,
        request,
    )
    return {
        "id": user.id if user else coach_profile.user_id,
        "coach_profile_id": coach_profile.id,
        "full_name": user.full_name if user else "",
        "email": user.email if user else "",
        "phone_number": user.phone or "" if user else "",
        "address": user.address or "" if user else "",
        "rating": float(coach_profile.avg_rating or 0.0),
        "review_count": int(coach_profile.total_reviews or 0),
        "headline": coach_profile.headline or "",
        "profile_photo": photo,
        "about": coach_profile.about or "",
    }


def calculate_starting_price(services: list) -> str | None:
    published_prices = []
    for s in services or []:
        if getattr(s, "status", None) == "published" and getattr(s, "price", None):
            try:
                published_prices.append(float(s.price))
            except (ValueError, TypeError):
                continue
    if not published_prices:
        return None
    return f"{min(published_prices):.2f}"
