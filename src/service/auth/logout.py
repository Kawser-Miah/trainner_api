from sqlalchemy.orm import Session

from src.core.exceptions import InvalidTokenException
from src.models.accounts.user import User
from src.utils.jwt import verify_refresh_token


async def logout_user(
    db: Session,
    user: User,
    refresh_token: str,
) -> None:
    """
    Log out an authenticated user by verifying their refresh token.
    """
    payload = verify_refresh_token(refresh_token)

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()

    # Ensure the refresh token belongs to the currently authenticated user
    if str(user_id) != str(user.id):
        raise InvalidTokenException()

