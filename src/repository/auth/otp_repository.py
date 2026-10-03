from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.accounts.otp import OTPVerification


def create_otp(
    db: Session,
    *,
    user_id: int,
    otp_code: str,
    expires_at: datetime,
    purpose: str,
) -> OTPVerification:
    otp = OTPVerification(
        user_id=user_id,
        otp_code=otp_code,
        expires_at=expires_at,
        purpose=purpose,
    )

    db.add(otp)
    db.flush()

    return otp


def get_otp_by_user_id(
    db: Session,
    *,
    user_id: int,
    purpose: str,
) -> OTPVerification | None:
    result = db.execute(
        select(OTPVerification)
        .where(
            OTPVerification.user_id == user_id,
            OTPVerification.purpose == purpose,
        )
        .order_by(
            OTPVerification.id.desc()
        )
    )

    return result.scalars().first()


def update_otp(
    db: Session,
    *,
    otp: OTPVerification,
    otp_code: str,
    expires_at: datetime,
) -> OTPVerification:
    otp.otp_code = otp_code
    otp.expires_at = expires_at

    db.flush()

    return otp


def delete_otp(
    db: Session,
    *,
    otp: OTPVerification,
) -> None:
    db.delete(otp)
    db.flush()