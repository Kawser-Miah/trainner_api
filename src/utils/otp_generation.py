import secrets
from datetime import datetime, timedelta, timezone


OTP_EXPIRE_MINUTES = 2


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def get_otp_expiry():
    return datetime.now(timezone.utc) + timedelta(
        minutes=OTP_EXPIRE_MINUTES
    )