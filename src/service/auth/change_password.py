from sqlalchemy.orm import Session

from src.core.exceptions import InvalidOldPasswordException
from src.models.accounts.user import User
from src.repository.auth.user_repository import update_user_password
from src.schemas.auth.change_password import ChangePasswordRequest
from src.utils.security import hash_password, verify_password


async def change_password(
    db: Session,
    user: User,
    request: ChangePasswordRequest,
) -> dict:
    # Verify old password
    if not verify_password(
        request.old_password,
        user.password_hash,
    ):
        raise InvalidOldPasswordException()

    # Hash new password
    password_hash = hash_password(
        request.new_password
    )

    # Update password
    update_user_password(
        db=db,
        user=user,
        password_hash=password_hash,
    )

    # Save changes
    db.commit()

    return {
        "user_id": str(user.id),
    }
