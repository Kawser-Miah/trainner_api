from sqlalchemy.orm import Session

from src.core.exceptions import (
    EmailNotVerifiedException,
    InvalidCredentialsException,
)
from src.repository.auth.user_repository import get_user_by_email
from src.schemas.auth.email_verify import VerifyEmailResponse
from src.utils.jwt import (
    create_access_token,
    create_refresh_token,
)
from src.utils.security import verify_password


async def sign_in(
    db: Session,
    email: str,
    password: str,
):
    # Find user
    user = get_user_by_email(
        db=db,
        email=email,
    )

    if user is None:
        raise InvalidCredentialsException()

    # Check password
    if not verify_password(
        password,
        user.password_hash,
    ):
        raise InvalidCredentialsException()

    # Check email verification
    if not user.is_email_verified:
        raise EmailNotVerifiedException(user_id=user.id)

    # Check account status
    if not user.is_active:
        raise InvalidCredentialsException(
            message="Your account is inactive.",
        )

    # Generate access token
    access_token, access_token_valid_till = create_access_token(
        user_id=user.id,
        role=user.role,
        full_name=user.full_name,
    )

    # Generate refresh token
    refresh_token = create_refresh_token(
        user_id=user.id,
    )

    return VerifyEmailResponse(
        access_token=access_token,
        access_token_valid_till=access_token_valid_till,
        refresh_token=refresh_token,
        user_id=str(user.id),
        role=user.role,
        is_completed=user.is_completed,
        coach_status=None,
    )