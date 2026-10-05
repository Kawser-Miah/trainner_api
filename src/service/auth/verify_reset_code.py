from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.core.exceptions import InvalidOTPException, UserNotFoundException
from src.repository.auth.otp_repository import (
    delete_otp,
    get_otp_by_user_id,
)
from src.repository.auth.user_repository import get_user_by_id
from src.utils.jwt import create_password_reset_token


async def verify_reset_code(
    db: Session,
    user_id: str | int,
    code: str,
) -> dict:
    try:
        database_user_id = int(user_id)
    except (TypeError, ValueError):
        raise UserNotFoundException()

    # Find OTP
    otp_entry = get_otp_by_user_id(
        db=db,
        user_id=database_user_id,
    )

    if otp_entry is None:
        raise InvalidOTPException()

    # Check OTP
    if otp_entry.otp_code != code:
        raise InvalidOTPException()

    # Check OTP expiry
    if otp_entry.expires_at < datetime.now(timezone.utc):
        raise InvalidOTPException()

    # Find user
    user = get_user_by_id(
        db=db,
        user_id=database_user_id,
    )

    if user is None:
        raise UserNotFoundException()

    # Delete OTP after successful verification
    delete_otp(
        db=db,
        otp=otp_entry,
    )

    # Save changes
    db.commit()

    # Generate dedicated, short-lived password reset token
    secret_key = create_password_reset_token(
        user_id=user.id,
    )


    return {
        "secret_key": secret_key,
        "user_id": str(user.id),
    }
