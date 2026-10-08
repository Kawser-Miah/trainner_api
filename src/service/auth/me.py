from datetime import timezone
from pathlib import Path
import re
from fastapi import Request, UploadFile
from sqlalchemy.orm import Session

from src.models.accounts.user import User
from src.schemas.auth.me import UserProfileResponse
from src.utils.media import build_media_url, get_base_url

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

    if image is not None and getattr(image, "filename", None):
        raw_name = Path(image.filename).name
        if raw_name:
            clean_name = re.sub(r"[^\w\.-]", "_", raw_name)
            media_dir = Path("media") / "profile_images"
            media_dir.mkdir(parents=True, exist_ok=True)
            file_path = media_dir / clean_name

            content = await image.read()
            if content and len(content) > 0:
                with open(file_path, "wb") as f:
                    f.write(content)
                user.photo_url = f"/media/profile_images/{clean_name}"

    db.commit()
    db.refresh(user)

    return get_user_profile(user=user, request=request)
