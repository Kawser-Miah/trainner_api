from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.core.exceptions import (
    AppException,
    InvalidTokenException,
    UserNotFoundException,
)
from src.models.accounts.user import User
from src.repository.auth.user_repository import get_user_by_id
from src.utils.jwt import verify_access_token


security = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token: str | None = None

    if credentials and credentials.credentials:
        token = credentials.credentials
    elif "authorization" in request.headers:
        auth_header = request.headers["authorization"]
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
        else:
            token = auth_header.strip()
    elif "token" in request.headers:
        token = request.headers["token"].strip()
    elif "x-access-token" in request.headers:
        token = request.headers["x-access-token"].strip()

    if not token:
        raise InvalidTokenException()

    payload = verify_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise UserNotFoundException()

    user = get_user_by_id(db=db, user_id=user_id)
    if user is None:
        raise UserNotFoundException()

    if not user.is_active:
        raise AppException(
            message="Your account is inactive.",
            status=403,
            error="ACCOUNT_INACTIVE",
        )

    return user

