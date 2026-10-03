from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.core.exceptions import (
    OTPNotExpiredException,
    UserNotFoundException,
)
from src.repository.auth.otp_repository import (
    create_otp,
    delete_otp,
    get_otp_by_user_id,
)
from src.repository.auth.user_repository import get_user_by_id
from src.service.auth.email_service import send_otp_email
from src.utils.otp_generation import (
    generate_otp,
    get_otp_expiry,
)


async def resend_otp(
    db: Session,
    user_id: str,
):
    database_user_id = int(user_id)

    # Find user
    user = get_user_by_id(
        db=db,
        user_id=database_user_id,
    )

    if user is None:
        raise UserNotFoundException()

    # Find existing OTP
    existing_otp = get_otp_by_user_id(
        db=db,
        user_id=database_user_id,
    )

    # Check previous OTP
    if existing_otp is not None:

        # Previous OTP is still valid
        if datetime.now(timezone.utc) < existing_otp.expires_at:
            raise OTPNotExpiredException()

        # Previous OTP has expired, remove it
        delete_otp(
            db=db,
            otp=existing_otp,
        )

    # Generate new OTP
    otp_code = generate_otp()
    otp_expires_at = get_otp_expiry()

    # Store new OTP
    create_otp(
        db=db,
        user_id=user.id,
        otp_code=otp_code,
        expires_at=otp_expires_at,
    )

    # Save changes
    db.commit()

    # Send new OTP
    await send_otp_email(
        email=user.email,
        otp=otp_code,
    )

    return {
        "user_id": str(user.id),
    }