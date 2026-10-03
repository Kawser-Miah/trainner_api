from src.core.exceptions import UserNotFoundException
from src.data.users import users
from src.schemas.auth.refresh_token import RefreshTokenResponse
from src.utils.jwt import (
    verify_refresh_token,
    create_access_token,
)


async def refresh_access_token(
    refresh_token: str,
):
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)

    user_id = payload.get("sub")
    database_user_id = int(user_id)

    # Find user
    user = None

    for item in users:
        if item["id"] == database_user_id:
            user = item
            break

    if user is None:
        raise UserNotFoundException()

    # Create new access token
    access_token, access_token_valid_till = create_access_token(
        user_id=user["id"],
        role=user["role"],
        full_name=user["full_name"],
    )

    return RefreshTokenResponse(
        access_token=access_token,
        access_token_valid_till=access_token_valid_till,
    )