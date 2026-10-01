from datetime import datetime, timezone

from src.core.exceptions import InvalidOTPException
from src.data.users import users, otps
from src.schemas.auth.email_verify import VerifyEmailResponse
from src.utils.jwt import (
    create_access_token,
    create_refresh_token,
)


async def verify_email(
    user_id: str,
    code: str,
):
    # Find OTP
    otp_entry = None

    for item in otps:
        if item["user_id"] == user_id:
            otp_entry = item
            break

    if otp_entry is None:
        raise InvalidOTPException()

    # Check OTP
    if otp_entry["otp"] != code:
        raise InvalidOTPException()

    # Check OTP expiry
    if otp_entry["expires_at"] < datetime.now(timezone.utc):
        raise InvalidOTPException()

    # Find user
    user = None

    for item in users:
        if item["id"] == user_id:
            user = item
            break

    if user is None:
        raise InvalidOTPException()

    # Verify email
    user["is_verified"] = True

    # Remove OTP after successful verification
    otps.remove(otp_entry)

    # Generate tokens
    access_token, access_token_valid_till = create_access_token(
        user_id=user["id"],
        role=user["role"],
        full_name=user["full_name"]
    )

    refresh_token = create_refresh_token(
        user_id=user["id"]
    )

    return VerifyEmailResponse(
        access_token=access_token,
        access_token_valid_till=access_token_valid_till,
        refresh_token=refresh_token,
        user_id=user["id"],
        role=user["role"],
        is_completed=False,
        coach_status=None,
    )