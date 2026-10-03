from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.core.exceptions import InvalidOTPException
from src.repository.auth.otp_repository import (
    delete_otp,
    get_otp_by_user_id,
)
from src.repository.auth.user_repository import (
    get_user_by_id,
)
from src.schemas.auth.email_verify import VerifyEmailResponse
from src.utils.jwt import (
    create_access_token,
    create_refresh_token,
)


async def verify_email(
    db: Session,
    user_id: int,
    code: str,
):
    # Find OTP
    otp_entry = get_otp_by_user_id(
        db=db,
        user_id=user_id,
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
        user_id=user_id,
    )

    if user is None:
        raise InvalidOTPException()

    # Verify email
    user.is_email_verified = True

    # Remove OTP after successful verification
    delete_otp(
        db=db,
        otp=otp_entry,
    )

    # Save changes
    db.commit()

    # Generate tokens
    access_token, access_token_valid_till = create_access_token(
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
    )

    refresh_token = create_refresh_token(
        user_id=user.id,
    )

    return VerifyEmailResponse(
        access_token=access_token,
        access_token_valid_till=access_token_valid_till,
        refresh_token=refresh_token,
        user_id=user.id,
        role=user.role,
        is_completed=user.is_completed,
        coach_status=None,
    )