from sqlalchemy.orm import Session

from src.core.exceptions import UserNotFoundException
from src.repository.auth.otp_repository import create_or_update_otp
from src.repository.auth.user_repository import get_user_by_email
from src.service.auth.email_service import send_otp_email
from src.utils.otp_generation import (
    generate_otp,
    get_otp_expiry,
)


async def forgot_password(
    db: Session,
    email: str,
):
    # Find user by email
    user = get_user_by_email(
        db=db,
        email=email,
    )

    if user is None:
        raise UserNotFoundException()

    # Generate password reset OTP
    otp_code = generate_otp()
    otp_expires_at = get_otp_expiry()

    # Store OTP
    create_or_update_otp(
        db=db,
        user_id=user.id,
        otp_code=otp_code,
        expires_at=otp_expires_at,
    )

    # Save changes
    db.commit()

    # Send OTP to email
    await send_otp_email(
        email=user.email,
        otp=otp_code,
    )

    # Convert expiry to milliseconds
    expires_at_ms = int(
        otp_expires_at.timestamp() * 1000
    )

    return {
        "user_id": str(user.id),
        "expires_at": expires_at_ms,
    }