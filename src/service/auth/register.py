from sqlalchemy.orm import Session

from src.core.exceptions import EmailAlreadyExistsException
from src.repository.auth.user_repository import (
    create_user,
    get_user_by_email,
)
from src.repository.auth.otp_repository import create_otp
from src.schemas.auth.account import RegisterAccountRequest
from src.service.auth.email_service import send_otp_email
from src.utils.otp_generation import generate_otp, get_otp_expiry
from src.utils.security import hash_password


async def register_user(
    db: Session,
    register_account_request: RegisterAccountRequest,
):
    email = str(register_account_request.email)

    # Check whether email already exists
    existing_user = get_user_by_email(
        db=db,
        email=email,
    )

    if existing_user:
        raise EmailAlreadyExistsException()

    # Generate OTP
    otp_code = generate_otp()
    otp_expiry = get_otp_expiry()

    # Create user
    user = create_user(
        db=db,
        full_name=register_account_request.full_name,
        email=email,
        phone=register_account_request.phone,
        password_hash=hash_password(
            register_account_request.password
        ),
        role=register_account_request.role,
    )

    # Create OTP
    create_otp(
        db=db,
        user_id=user.id,
        otp_code=otp_code,
        expires_at=otp_expiry,
        purpose="EMAIL_VERIFICATION",
    )

    # Save user + OTP
    db.commit()

    # Send OTP
    await send_otp_email(
        email=user.email,
        otp=otp_code,
    )

    return user