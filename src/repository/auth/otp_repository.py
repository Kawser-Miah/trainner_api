from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.accounts.otp import OTPVerification


def create_or_update_otp(
    db: Session,
    *,
    user_id: int,
    otp_code: str,
    expires_at: datetime,
) -> OTPVerification:
    """
    Create a new OTP for a user.

    If the user already has an OTP, update the
    existing OTP instead of creating another record.
    """

    result = db.execute(
        select(OTPVerification).where(
            OTPVerification.user_id == user_id
        )
    )

    otp = result.scalar_one_or_none()

    if otp is not None:
        otp.otp_code = otp_code
        otp.expires_at = expires_at

        db.flush()

        return otp

    otp = OTPVerification(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at,
    )

    db.add(otp)
    db.flush()

    return otp


def get_otp_by_user_id(
    db: Session,
    *,
    user_id: int,
) -> OTPVerification | None:
    """
    Get the OTP belonging to a user.
    """

    result = db.execute(
        select(OTPVerification).where(
            OTPVerification.user_id == user_id
        )
    )

    return result.scalar_one_or_none()


def delete_otp(
    db: Session,
    *,
    otp: OTPVerification,
) -> None:
    """
    Delete the user's OTP.
    """

    db.delete(otp)
    db.flush()