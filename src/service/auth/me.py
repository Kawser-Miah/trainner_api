from datetime import timezone

from src.models.accounts.user import User
from src.schemas.auth.me import UserProfileResponse


def get_user_profile(user: User) -> UserProfileResponse:
    created_at = user.created_at
    if created_at and created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone,
        address=getattr(user, "address", None),
        image=user.photo_url,
        role=user.role,
        is_verified=user.is_email_verified,
        is_completed=user.is_completed,
        coach_status=getattr(user, "coach_status", None),
        created_at=created_at.isoformat() if created_at else "",
    )
