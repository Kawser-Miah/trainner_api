from pathlib import Path
from sqlalchemy.orm import Session

from src.core.exceptions import InvalidPasswordException
from src.models.accounts.user import User
from src.repository.auth.user_repository import delete_user
from src.utils.security import verify_password


async def delete_user_account(
    db: Session,
    user: User,
    password: str,
) -> None:
    """
    Permanently delete the authenticated user's account and associated data
    after confirming their password.
    """
    # Verify account password
    if not verify_password(password, user.password_hash):
        raise InvalidPasswordException()

    # Clean up uploaded profile image if present
    if user.photo_url and "/media/profile_images/" in user.photo_url:
        try:
            filename = Path(user.photo_url).name
            file_path = Path("media") / "profile_images" / filename
            if file_path.is_file():
                file_path.unlink(missing_ok=True)
        except Exception:
            pass

    # Delete user (cascades to related tables like otp_verifications)
    delete_user(db=db, user=user)
    db.commit()
