from sqlalchemy.orm import Session

from src.core.exceptions import UserNotFoundException
from src.repository.auth.user_repository import (
    get_user_by_id,
    update_user_password,
)
from src.schemas.auth.reset_password import ResetPasswordRequest
from src.utils.jwt import verify_access_token
from src.utils.security import hash_password


async def reset_password(
    db: Session,
    request: ResetPasswordRequest,
):
    # Verify access token
    payload = verify_access_token(
        request.secret_key
    )

    # Get user ID from access token
    user_id = payload.get("sub")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise UserNotFoundException()

    # Find user
    user = get_user_by_id(
        db=db,
        user_id=user_id,
    )

    if user is None:
        raise UserNotFoundException()

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