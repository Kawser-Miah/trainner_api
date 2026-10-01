from datetime import datetime, timezone

from src.core.exceptions import UserNotFoundException, OTPNotExpiredException
from src.data.users import users, otps
from src.utils.otp_generation import (
    generate_otp,
    get_otp_expiry,
)
from src.service.auth.email_service import send_otp_email


async def resend_otp(user_id: str):

    # Find user
    user = None

    for item in users:
        if item["id"] == user_id:
            user = item
            break

    if user is None:
        raise UserNotFoundException()

        # Find existing OTP
    existing_otp = None

    for item in otps:
        if item["user_id"] == user_id:
            existing_otp = item
            break

    # Check previous OTP
    if existing_otp is not None:

        # Previous OTP is still valid
        if datetime.now(timezone.utc) < existing_otp["expires_at"]:
            raise OTPNotExpiredException()

        # Previous OTP has expired, remove it
        otps.remove(existing_otp)


    # Generate new OTP
    otp_code = generate_otp()
    otp_expires_at = get_otp_expiry()

    # Remove old OTP
    otps[:] = [
        item
        for item in otps    
        if item["user_id"] != user_id
    ]

    # Store new OTP
    otps.append({
        "user_id": user_id,
        "otp": otp_code,
        "expires_at": otp_expires_at,
    })

    # Send new OTP
    await send_otp_email(
        email=user["email"],
        otp=otp_code,
    )

    return {
        "user_id": user_id,
    }