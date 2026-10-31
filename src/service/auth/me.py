from datetime import timezone
from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.schemas.auth.me import UserProfileResponse
from src.utils.media import build_media_url, delete_media_file, get_base_url
from src.utils.uploads import save_upload

# Alias build_image_url to centralized build_media_url for backward compatibility
build_image_url = build_media_url



def get_user_profile(user: User, request: Request | None = None) -> UserProfileResponse:
    created_at = user.created_at
    if created_at:
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        created_at_str = created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    else:
        created_at_str = ""

    role = (
        user.role.capitalize()
        if user.role and user.role.lower() in ["user", "coach", "admin"]
        else (user.role or "")
    )

    return UserProfileResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone,
        address=getattr(user, "address", None),
        image=build_image_url(user.photo_url, request),
        role=role,
        is_verified=user.is_email_verified,
        is_completed=user.is_completed,
        coach_status=getattr(user, "coach_status", None),
        created_at=created_at_str,
    )


async def update_user_profile(
    db: Session,
    user: User,
    full_name: str | None = None,
    phone_number: str | None = None,
    address: str | None = None,
    image: UploadFile | None = None,
    request: Request | None = None,
) -> UserProfileResponse:
    if full_name is not None and full_name.strip():
        user.full_name = full_name.strip()

    if phone_number is not None:
        user.phone = phone_number.strip() if phone_number.strip() else None

    if address is not None:
        user.address = address.strip() if address.strip() else None

    saved = await save_upload(image, kind="image", subfolder="profile_images")
    replaced_photo = None
    if saved:
        replaced_photo = user.photo_url
        user.photo_url = saved.web_path

    try:
        db.commit()
    except Exception:
        # Don't leave the new file orphaned if the row could not be saved.
        db.rollback()
        if saved:
            delete_media_file(saved.web_path)
        raise
    db.refresh(user)

    # Remove the old photo only once the new one is safely stored.
    if replaced_photo:
        delete_media_file(replaced_photo)

    return get_user_profile(user=user, request=request)
